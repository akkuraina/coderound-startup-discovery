from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
import logging
import re
import asyncio
from typing import List, Dict, Any, Optional
from database import get_db
from models import User, Company
from schemas import CompanyResponse, DiscoveryResult
from utils.auth import decode_token
from services import tavily
from services import groq_enricher as groq
from services.groq_enricher import _is_invalid_company_name

logger = logging.getLogger(__name__)
router = APIRouter()

# Groq free tier = 30 req/min. We make 2 calls per company (enrich + description).
# So max ~14 companies per minute safely. 1.5s delay keeps us under the limit.
GROQ_RATE_LIMIT_DELAY = 1.5

_SKIP_DOMAINS = {
    "vcbacked", "vcback", "topstartups.io", "yutori", "seedtable",
    "growthlists", "tracxn", "crunchbase", "pitchbook", "fundraiseinsider",
    "startups.gallery", "growthlist", "wellfound", "f6s.com",
    "apollo.io", "cognism.com", "lusha.com", "zoominfo.com",
    "getlatka.com", "dealroom.co", "signal.nfx.com",
}

_AGGREGATOR_URL_DOMAINS = {
    "startups.gallery", "topstartups.io", "vcbacked.co", "vcback.co",
    "seedtable.com", "growthlists.com", "tracxn.com", "crunchbase.com",
    "pitchbook.com", "fundraiseinsider.com", "growthlist.co", "wellfound.com",
    "f6s.com", "yutori.com", "techcrunch.com", "alleywatch.com",
    "venturebeat.com", "forbes.com", "bloomberg.com", "businessinsider.com",
    "wamda.com", "siliconangle.com", "qubit.capital", "eu-startups.com",
    "sifted.eu", "axios.com", "theinformation.com",
    "apollo.io", "cognism.com", "lusha.com", "zoominfo.com",
    "getlatka.com", "dealroom.co", "signal.nfx.com",
}

VALID_URL_PATTERN = re.compile(
    r'^https?:\/\/'
    r'(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*'
    r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
    r'|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?(?:\/[^\s]*)?$',
    re.IGNORECASE
)


def _is_aggregator_url(url: str) -> bool:
    url_lower = url.lower()
    return any(domain in url_lower for domain in _AGGREGATOR_URL_DOMAINS)


def _clean_url(url: Optional[str], reject_aggregators: bool = False) -> Optional[str]:
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    url = re.sub(r'[\[\]\(\)\"\'`]', '', url)
    url = re.sub(r'%2F', '/', url)
    url = re.sub(r'%3A', ':', url)
    if '?' in url:
        url = url.split('?')[0]
    if '#' in url:
        url = url.split('#')[0]
    url = url.rstrip('/')
    if not url.startswith(('http://', 'https://')):
        if url.startswith('www.'):
            url = 'https://' + url
        else:
            return None
    if not VALID_URL_PATTERN.match(url):
        return None
    if len(url) > 500:
        return None
    if reject_aggregators and _is_aggregator_url(url):
        return None
    return url


def _clean_linkedin_url(url: Optional[str]) -> Optional[str]:
    url = _clean_url(url)
    if not url:
        return None
    match = re.search(r'linkedin\.com/company/([a-zA-Z0-9\-]+)', url, re.IGNORECASE)
    if match:
        return f'https://www.linkedin.com/company/{match.group(1)}'
    return None


def _clean_description(text: Optional[str]) -> str:
    """Strip markdown, pipes, URLs, HTML and boilerplate from scraped text."""
    if not text:
        return ""
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\*+([^*]*)\*+', r'\1', text)

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.count('|') >= 3:
            continue
        if re.search(r'\w+\*{3,}', line):
            continue
        lines.append(line)

    boilerplate = {
        "find newly funded", "handpicked gallery", "backed by top investors",
        "to get new clients", "close more deals", "pitch to these",
        "sales prospecting", "recently funded series", "funding via",
        "browse 10000", "recently funded startups from 100",
        "updated daily with funding", "funding amounts, investors, contacts",
        "source", "view jobs", "sign up", "newsletter", "subscribe",
        "learn more", "read more", "click here", "get started", "©",
        "cookie", "privacy policy", "enrich", "export", "crm",
    }
    clean_lines = []
    for line in lines:
        line_lower = line.lower()
        if any(bp in line_lower for bp in boilerplate):
            continue
        if len(line) < 20:
            continue
        clean_lines.append(line)

    clean = ' '.join(clean_lines)
    clean = re.sub(r'\s+', ' ', clean).strip()

    if len(clean) > 300:
        cut = clean[:300]
        last_period = cut.rfind('.')
        clean = cut[:last_period + 1] if last_period > 80 else cut + '...'

    return clean


TECH_SECTORS = {
    "software", "ai", "ml", "machine learning", "deep learning", "llm", "nlp",
    "saas", "cloud", "data", "analytics", "fintech", "crypto", "blockchain",
    "web3", "cybersecurity", "devops", "infrastructure", "biotech", "healthtech",
    "medtech", "edtech", "automation", "robotics", "iot", "gaming", "metaverse",
    "ar", "vr", "api", "platform", "marketplace", "developer tools",
}


def _is_tech_company(sector: Optional[str], description: Optional[str]) -> bool:
    text = (sector or description or "").lower()
    return any(kw in text for kw in TECH_SECTORS)


def _to_company_response(company: Company) -> CompanyResponse:
    response = CompanyResponse.from_orm(company)
    response.is_tech = _is_tech_company(company.sector, company.description)
    return response


def _should_skip_result(result: Dict[str, Any]) -> bool:
    """
    Skip aggregator LIST pages and directory pages.
    Do NOT skip news articles about individual companies — even from TechCrunch etc.
    The title is the reliable signal, not the domain.
    """
    title = result.get("title", "").lower()
    url = result.get("url", "").lower()

    # Skip pure aggregator/directory domains (not news sites)
    _PURE_AGGREGATORS = {
        "topstartups.io", "vcbacked.co", "vcback.co", "seedtable.com",
        "growthlists.com", "growthlist.co", "fundraiseinsider.com",
        "f6s.com", "wellfound.com", "apollo.io", "cognism.com",
        "lusha.com", "zoominfo.com", "getlatka.com", "signal.nfx.com",
        "startups.gallery",
    }
    if any(domain in url for domain in _PURE_AGGREGATORS):
        return True

    # Skip if title looks like a list/directory page (not a company-specific article)
    if _is_invalid_company_name(title):
        return True

    return False


def parse_tavily_result(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        title = result.get("title", "")
        content = result.get("content", "")
        text = f"{title} {content}"

        company_name = None
        for splitter in [" raises ", " announces ", " gets ", " secures ", " closes "]:
            if splitter in title.lower():
                candidate = title[: title.lower().index(splitter)].strip()
                # Reject if candidate contains a dash with domain-like suffix (article titles)
                if re.search(r'\s-\s\w+\.\w+$', candidate):
                    continue
                if 2 <= len(candidate) <= 50 and not _is_invalid_company_name(candidate):
                    company_name = candidate
                    break

        amount_match = re.search(r"\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)\b", text, re.IGNORECASE)
        funding_amount = 0.0
        if amount_match:
            try:
                amt = float(amount_match.group(1))
                unit = amount_match.group(2).upper()
                funding_amount = amt * 1_000_000_000 if unit in ("BILLION", "B") else amt * 1_000_000
            except ValueError:
                pass

        round_match = re.search(r"\b(Pre-Seed|Seed|Series\s+[A-Z](?:\+)?)\b", text, re.IGNORECASE)
        funding_round = round_match.group(1).strip() if round_match else "Seed"

        investors: List[str] = []
        inv_match = re.findall(
            r"(?:led by|from|backed by|investment from)\s+([A-Za-z\s&]+?)(?:\.|,|\band\b|$)",
            text, re.IGNORECASE,
        )
        if inv_match:
            investors = [i.strip() for i in inv_match[0].split(",") if i.strip()][:3]

        country_match = re.search(
            r"\b(USA|US|United States|UK|United Kingdom|India|Canada|Germany|"
            r"France|Australia|Singapore|Israel|Netherlands|Sweden|Brazil|Qatar)\b",
            text, re.IGNORECASE,
        )
        country = country_match.group(1) if country_match else "USA"

        source_url = result.get("url", "")
        clean_source_url = None if _is_aggregator_url(source_url) else _clean_url(source_url)

        return {
            "company_name": company_name,
            "funding_amount": funding_amount,
            "funding_round": funding_round,
            "investors": investors,
            "country": country,
            "url": clean_source_url,
        }

    except Exception as e:
        logger.error(f"parse_tavily_result error: {e}")
        return None


async def get_current_user(token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/discover", response_model=DiscoveryResult)
async def discover_startups(token: str = Query(...), db: Session = Depends(get_db)):
    """
    Discovery pipeline:
      1. Tavily → funding news results
      2. Pre-filter → skip aggregator/list pages (free)
      3. Groq call 1 → extract funding info + hiring status from article
      4. Tavily company search → fetch company's own website/LinkedIn content
      5. Groq call 2 → extract clean description from company's own content
      6. Upsert → always save/update, only skip if NOTHING changed at all
    """
    try:
        user = await get_current_user(token, db)
        logger.info(f"Discovery started by {user.email}")

        search_results = await tavily.search_recent_funding(limit=50)
        if not search_results:
            return DiscoveryResult(
                companies=[], total_found=0,
                processed_at=datetime.utcnow(),
                message="No recent funding announcements found",
            )

        logger.info(f"Tavily returned {len(search_results)} raw results")
        filtered = [r for r in search_results if not _should_skip_result(r)]
        logger.info(f"Pre-filter: {len(filtered)} kept, {len(search_results)-len(filtered)} skipped")

        discovered_companies = []
        groq_call_count = 0

        for result in filtered:
            try:
                raw_text = f"{result.get('title', '')} {result.get('content', '')}"

                # Rate limit pause (2 Groq calls per company, so be conservative)
                if groq_call_count > 0:
                    await asyncio.sleep(GROQ_RATE_LIMIT_DELAY)

                # --- Groq call 1: extract funding info from article ---
                enriched = await groq.enrich_company(raw_text)
                groq_call_count += 1

                base = parse_tavily_result(result) or {}

                company_name = enriched.get("company_name") or base.get("company_name")
                if not company_name or _is_invalid_company_name(company_name):
                    logger.info(f"Skipping — no valid company name for: {result.get('title', '')[:60]}")
                    continue

                company_name = company_name.strip()
                funding_amount = float(enriched.get("funding_amount") or base.get("funding_amount") or 0)
                funding_round = enriched.get("funding_round") or base.get("funding_round")
                sector = enriched.get("sector")
                # Filter out garbage investor names (censored/truncated)
                raw_investors = enriched.get("investors") or base.get("investors") or []
                investors = [
                    inv for inv in raw_investors
                    if inv and len(inv) > 2 and not re.search(r'\*{2,}', inv)
                ]
                country = enriched.get("country") or base.get("country") or "USA"
                hiring_status = enriched.get("hiring_status", 0)
                hiring_positions = enriched.get("hiring_positions") or []
                founder_name = enriched.get("founder_name")

                # Website from Groq or Tavily source (reject aggregators)
                website_raw = enriched.get("website") or base.get("url")
                website = _clean_url(website_raw, reject_aggregators=True)

                linkedin_url = _clean_linkedin_url(enriched.get("linkedin_url"))

                # --- Tavily company search → get real description ---
                description = ""
                await asyncio.sleep(GROQ_RATE_LIMIT_DELAY)  # pace before second Groq call

                company_search = await tavily.search_company_details(company_name)
                company_search_text = company_search.get("answer", "")
                for sr in company_search.get("search_results", [])[:3]:
                    sr_url = sr.get("url", "")
                    # Only use content from the company's own site or LinkedIn
                    if company_name.lower().replace(" ", "") in sr_url.lower() or "linkedin.com/company" in sr_url.lower():
                        company_search_text += f"\n{sr.get('content', '')}"

                if company_search_text.strip():
                    # --- Groq call 2: extract clean description from company's own content ---
                    description = await groq.extract_company_description(company_name, company_search_text)
                    groq_call_count += 1

                # Fallback: clean the article content if company search gave nothing
                if not description:
                    description = _clean_description(result.get("content", ""))

                # --- Upsert logic ---
                # Only skip if the company exists AND has all fields AND nothing changed.
                # New companies always get created. Existing ones update freely.
                existing = db.query(Company).filter(Company.name.ilike(company_name)).first()

                if existing:
                    funding_rounds_hierarchy = {
                        "Pre-Seed": 1, "Seed": 2, "Series A": 3, "Series B": 4,
                        "Series C": 5, "Series D": 6, "Series E": 7,
                    }
                    old_rank = funding_rounds_hierarchy.get(existing.funding_round or "", 0)
                    new_rank = funding_rounds_hierarchy.get(funding_round or "", 0)

                    # Only skip if truly nothing is new
                    nothing_new = (
                        new_rank <= old_rank
                        and not (funding_amount and existing.funding_amount and funding_amount > existing.funding_amount)
                        and hiring_status <= (existing.hiring_status or 0)
                        and existing.description  # already has a description
                        and existing.website      # already has a website
                    )
                    if nothing_new:
                        logger.info(f"Skipped {company_name}: no new data")
                        continue  # ← don't append, get_companies will show them via DB query

                    db_company = existing
                    update_type = "Updated"
                else:
                    db_company = Company(name=company_name)
                    update_type = "Created"

                if funding_amount:
                    db_company.funding_amount = funding_amount
                if funding_round:
                    db_company.funding_round = funding_round
                if not existing or funding_round or funding_amount:
                    db_company.funding_date = datetime.utcnow()
                if investors:
                    db_company.investors = investors
                if hiring_positions:
                    db_company.hiring_positions = hiring_positions
                if sector:
                    db_company.sector = sector
                if country:
                    db_company.country = country
                # Always update description if we got a better one
                if description:
                    db_company.description = description
                if website:
                    db_company.website = website
                elif not existing or not existing.website:
                    db_company.website = None
                if linkedin_url:
                    db_company.linkedin_url = linkedin_url

                # Store founder as initial decision maker
                if founder_name and founder_name.strip():
                    existing_makers = db_company.decision_makers or {}
                    if not existing_makers.get("decision_makers"):
                        existing_makers["decision_makers"] = []
                    founder_exists = any(
                        dm.get("name", "").lower() == founder_name.lower()
                        for dm in existing_makers.get("decision_makers", [])
                    )
                    if not founder_exists:
                        existing_makers["decision_makers"].insert(0, {
                            "name": founder_name,
                            "title": "Founder",
                            "linkedin_url": None
                        })
                    db_company.decision_makers = existing_makers

                db_company.hiring_status = max(db_company.hiring_status or 0, hiring_status)
                db_company.enriched_data = {
                    **(db_company.enriched_data or {}),
                    **base,
                    **{k: v for k, v in enriched.items() if v is not None}
                }
                db_company.last_enriched = datetime.utcnow()

                db.add(db_company)
                db.commit()
                db.refresh(db_company)
                discovered_companies.append(db_company)
                logger.info(
                    f"{update_type}: {company_name} | {funding_round} | "
                    f"${funding_amount:,.0f} | hiring={hiring_status} | "
                    f"desc={'yes' if description else 'no'}"
                )

            except Exception as e:
                logger.error(f"Error processing '{result.get('title', '')}': {e}", exc_info=True)
                db.rollback()
                continue

        logger.info(
            f"Discovery complete — {len(discovered_companies)} companies, "
            f"{groq_call_count} Groq calls used"
        )

        return DiscoveryResult(
            companies=[_to_company_response(c) for c in discovered_companies],
            total_found=len(discovered_companies),
            processed_at=datetime.utcnow(),
            message=f"Discovered {len(discovered_companies)} startup(s) ({groq_call_count} Groq calls used)",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Discovery process failed")


@router.get("", response_model=List[CompanyResponse])
async def get_companies(
    token: str = Query(...),
    hiring_status: int = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
):
    try:
        await get_current_user(token, db)
        query = db.query(Company)
        if hiring_status is not None:
            query = query.filter(Company.hiring_status == hiring_status)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Company.funding_date >= thirty_days_ago)
        companies = query.order_by(desc(Company.updated_at)).offset(skip).limit(limit).all()
        return [_to_company_response(c) for c in companies]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_companies error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch companies")


@router.get("/tech/hiring", response_model=List[CompanyResponse])
async def get_actively_hiring_tech_companies(
    token: str = Query(...),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
):
    try:
        await get_current_user(token, db)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        companies = db.query(Company).filter(
            Company.hiring_status == 2,
            Company.funding_date >= thirty_days_ago
        ).order_by(desc(Company.funding_date)).offset(skip).limit(limit * 2).all()
        tech = [_to_company_response(c) for c in companies if _is_tech_company(c.sector, c.description)]
        return tech[:limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_actively_hiring_tech_companies error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tech companies")


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    try:
        await get_current_user(token, db)
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return _to_company_response(company)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_company error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch company")


@router.post("/{company_id}/enrich-decision-makers", response_model=CompanyResponse)
async def enrich_company_decision_makers(
    company_id: int, token: str = Query(...), db: Session = Depends(get_db)
):
    try:
        await get_current_user(token, db)
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        company_info = f"""
Company: {company.name}
Website: {company.website or 'Unknown'}
Description: {company.description or 'Unknown'}
Funding: {company.funding_amount} in {company.funding_round}
"""
        decision_data = await groq.extract_decision_makers(company.name, company_info)

        if decision_data.get("decision_makers"):
            cleaned_makers = []
            for maker in decision_data["decision_makers"]:
                cleaned = {
                    "name": maker.get("name", "").strip(),
                    "title": maker.get("title", "").strip()
                }
                linkedin = _clean_linkedin_url(maker.get("linkedin_url"))
                if linkedin:
                    cleaned["linkedin_url"] = linkedin
                if cleaned["name"] and cleaned["title"]:
                    cleaned_makers.append(cleaned)

            if cleaned_makers:
                company.decision_makers = {
                    "decision_makers": cleaned_makers,
                    "confidence": decision_data.get("confidence", 0.0),
                    "enriched_at": datetime.utcnow().isoformat(),
                }
                company.last_enriched = datetime.utcnow()
                db.add(company)
                db.commit()
                db.refresh(company)

        return _to_company_response(company)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"enrich_decision_makers error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to enrich company")
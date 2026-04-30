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

# Delay between Groq calls (seconds). 
# Free tier = 30 req/min = 1 req per 2s to stay safe.
GROQ_RATE_LIMIT_DELAY = 2.0


# ---------------------------------------------------------------------------
# Regex pre-parser + pre-filter (zero API cost)
# ---------------------------------------------------------------------------

# URLs/domains that are aggregator sites — skip entirely before calling Groq
_SKIP_DOMAINS = {
    "vcbacked", "vcback", "topstartups.io", "yutori", "seedtable",
    "growthlists", "tracxn", "crunchbase", "pitchbook", "fundraiseinsider",
    "startups.gallery", "growthlist", "wellfound", "f6s.com",
}

def _should_skip_result(result: Dict[str, Any]) -> bool:
    """Return True if this Tavily result is obviously an aggregator page."""
    url = result.get("url", "").lower()
    title = result.get("title", "").lower()

    if any(domain in url for domain in _SKIP_DOMAINS):
        return True
    if _is_invalid_company_name(title):
        return True
    return False


def parse_tavily_result(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Cheap regex parse. Groq is authoritative; this fills fallback gaps."""
    try:
        title = result.get("title", "")
        content = result.get("content", "")
        text = f"{title} {content}"

        company_name = None
        for splitter in [" raises ", " announces ", " gets ", " secures ", " closes "]:
            if splitter in title.lower():
                candidate = title[: title.lower().index(splitter)].strip()
                if 2 <= len(candidate) <= 60 and not _is_invalid_company_name(candidate):
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
            r"France|Australia|Singapore|Israel|Netherlands|Sweden|Brazil)\b",
            text, re.IGNORECASE,
        )
        country = country_match.group(1) if country_match else "USA"

        return {
            "company_name": company_name,
            "funding_amount": funding_amount,
            "funding_round": funding_round,
            "investors": investors,
            "country": country,
            "description": content[:500],
            "url": result.get("url", ""),
        }

    except Exception as e:
        logger.error(f"parse_tavily_result error: {e}")
        return None


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/discover", response_model=DiscoveryResult)
async def discover_startups(token: str = Query(...), db: Session = Depends(get_db)):
    """
    Discover recently funded startups.
    Pipeline:
      1. Tavily  → raw search results
      2. Regex pre-filter → skip obvious aggregator pages (free, no API call)
      3. Groq    → ONE call per result: company name + funding + hiring status
      4. Regex fallback → fills any fields Groq left null
      5. Validate → skip if no valid company name
      6. MySQL   → upsert
    Rate limiting: {GROQ_RATE_LIMIT_DELAY}s delay between Groq calls.
    """
    try:
        user = await get_current_user(token, db)
        logger.info(f"Discovery started by {user.email}")

        search_results = await tavily.search_recent_funding(limit=20)
        if not search_results:
            return DiscoveryResult(
                companies=[], total_found=0,
                processed_at=datetime.utcnow(),
                message="No recent funding announcements found",
            )

        logger.info(f"Tavily returned {len(search_results)} raw results")

        # Pre-filter with regex — eliminates aggregator pages before touching Groq
        filtered = [r for r in search_results if not _should_skip_result(r)]
        skipped = len(search_results) - len(filtered)
        logger.info(f"Pre-filter: {len(filtered)} kept, {skipped} skipped (aggregator sites)")

        discovered_companies = []
        groq_call_count = 0

        for i, result in enumerate(filtered):
            try:
                raw_text = f"{result.get('title', '')} {result.get('content', '')}"

                # Rate limit: pause before each Groq call (except the first)
                if groq_call_count > 0:
                    await asyncio.sleep(GROQ_RATE_LIMIT_DELAY)

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
                investors = enriched.get("investors") or base.get("investors") or []
                country = enriched.get("country") or base.get("country") or "USA"
                hiring_status = enriched.get("hiring_status", 0)
                hiring_positions = enriched.get("hiring_positions") or []

                existing = db.query(Company).filter(Company.name.ilike(company_name)).first()
                db_company = existing or Company(name=company_name)

                if funding_amount:
                    db_company.funding_amount = funding_amount
                if funding_round:
                    db_company.funding_round = funding_round
                db_company.funding_date = datetime.utcnow()
                if investors:
                    db_company.investors = investors
                if hiring_positions:
                    db_company.hiring_positions = hiring_positions
                if country:
                    db_company.country = country
                db_company.description = base.get("description", "")
                db_company.website = base.get("url", "")
                db_company.hiring_status = hiring_status
                db_company.enriched_data = {
                    **base,
                    **{k: v for k, v in enriched.items() if v is not None}
                }
                db_company.last_enriched = datetime.utcnow()

                db.add(db_company)
                db.commit()
                db.refresh(db_company)
                discovered_companies.append(db_company)
                logger.info(
                    f"{'Updated' if existing else 'Created'}: {company_name} | "
                    f"{funding_round} | ${funding_amount:,.0f} | hiring={hiring_status}"
                )

            except Exception as e:
                logger.error(f"Error processing '{result.get('title', '')}': {e}")
                db.rollback()
                continue

        logger.info(f"Discovery complete — {len(discovered_companies)} companies saved, {groq_call_count} Groq calls used")

        return DiscoveryResult(
            companies=[CompanyResponse.from_orm(c) for c in discovered_companies],
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
        return [CompanyResponse.from_orm(c) for c in companies]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_companies error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch companies")


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    try:
        await get_current_user(token, db)
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return CompanyResponse.from_orm(company)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_company error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch company")
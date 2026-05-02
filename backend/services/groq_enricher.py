import json
import logging
import re
from typing import Dict, Any
from groq import Groq
from config import settings

logger = logging.getLogger(__name__)


_NEWS_SITES = {
    "techcrunch", "alleywatch", "vc news daily", "crunchbase", "forbes",
    "bloomberg", "reuters", "wsj", "wall street journal", "the information",
    "sifted", "eu-startups", "venturebeat", "business insider", "inc",
    "wired", "axios", "pitchbook", "startup news", "tech in asia",
    "vcbacked", "vcback", "yutori", "startups.gallery", "growthlists",
    "seedtable", "failory", "tracxn",
}

_TITLE_PHRASES = [
    "largest", "biggest", "top ", "funding rounds of", "best startups",
    "weekly roundup", "newsletter", "digest", "venture capital financings",
    "technology startups", "news daily", "report:", "recap:", "update –",
    "latest funding", "verified funding", "seed startups", "funded startups",
    "silicon valley startup", "startup funding", "recently funded",
    "best startups with", "startups with recent funding",
    "funding rounds &", "funding and investors",
]


def _is_invalid_company_name(name: str) -> bool:
    if not name:
        return True
    n = name.lower().strip()
    if len(n) > 50:
        return True
    if re.search(r'\b\d{1,2}\s+(largest|biggest|top|best)', n):
        return True
    if any(site in n for site in _NEWS_SITES):
        return True
    if any(phrase in n for phrase in _TITLE_PHRASES):
        return True
    return False


class GroqEnricher:
    MODEL = "llama-3.1-8b-instant"

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def _chat(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                max_tokens=max_tokens,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return ""

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        text = re.sub(r"```(?:json)?", "", text).strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}

    async def enrich_company(self, text: str) -> Dict[str, Any]:
        """
        Single Groq call: extracts funding info + hiring status from article text.
        company_description is intentionally left to a separate company-search call.
        """
        try:
            prompt = f"""Extract startup funding information from the text below. Return ONLY valid JSON.

STRICT RULES FOR URLS:
- website: ONLY include if you find a clear, clean URL like https://example.com or www.example.com
  DO NOT include news sites, aggregators, broken URLs, or partial URLs
  Only extract the main domain (remove /about /jobs etc paths)
  If unclear, set to null
- linkedin_url: ONLY if you find https://linkedin.com/company/[name] pattern. Null otherwise.

OTHER RULES:
- company_name: the STARTUP that received funding (NOT a news site, NOT an article title)
- If text covers multiple companies or is a list article, set company_name to null
- founder_name: Extract founder name if explicitly mentioned. Null if not found.
- hiring_status: 0=not hiring, 1=potentially hiring (scaling/growing), 2=actively hiring (job postings mentioned)
- sector: Primary industry (e.g. "AI/ML", "Fintech", "SaaS", "Biotech", "Climate Tech")
- Investors: NAMES ONLY, no titles

Text:
{text[:2000]}

JSON only, no markdown:
{{
    "company_name": "startup name or null",
    "founder_name": "founder full name or null",
    "funding_amount": <USD number e.g. 5000000, or null>,
    "funding_round": "Seed/Pre-Seed/Series A/Series B/etc or null",
    "investors": ["Name 1", "Name 2"],
    "lead_investor": "Name or null",
    "sector": "industry/sector or null",
    "website": "https://example.com or null",
    "linkedin_url": "https://linkedin.com/company/name or null",
    "country": "country name or null",
    "hiring_status": <0, 1, or 2>,
    "hiring_positions": ["role 1", "role 2"]
}}"""

            raw = self._chat(prompt, max_tokens=450)
            result = self._extract_json(raw)

            name = result.get("company_name")
            if name and _is_invalid_company_name(name):
                logger.warning(f"Groq returned bad company name, nulling: '{name}'")
                result["company_name"] = None

            if result.get("company_name"):
                logger.info(
                    f"Groq extracted: {result['company_name']} | "
                    f"Founder: {result.get('founder_name', 'N/A')} | "
                    f"{result.get('funding_round')} | ${result.get('funding_amount')} | "
                    f"sector={result.get('sector')} | hiring={result.get('hiring_status')}"
                )
            return result

        except Exception as e:
            logger.error(f"Groq enrich_company error: {e}", exc_info=True)
            return {}

    async def extract_company_description(
        self, company_name: str, company_search_text: str
    ) -> str:
        """
        Given search results from the company's own website/LinkedIn,
        extract a clean 1-2 sentence description of what the company does.
        This is separate from enrich_company to keep each call focused.
        """
        try:
            prompt = f"""Based on the search results below about the company "{company_name}", 
write a concise 1-2 sentence description of what this company does.

Rules:
- Describe the product/service and target customer
- Do NOT mention funding, investors, or financial info
- Do NOT copy boilerplate marketing text verbatim
- Be specific, not generic (avoid "innovative solutions" type language)
- If you cannot determine what the company does, return null

Search results:
{company_search_text[:1500]}

Return ONLY valid JSON:
{{"description": "1-2 sentence description or null"}}"""

            raw = self._chat(prompt, max_tokens=200)
            result = self._extract_json(raw)
            desc = result.get("description") or ""
            return desc.strip()

        except Exception as e:
            logger.error(f"Groq extract_company_description error for {company_name}: {e}")
            return ""

    async def generate_outreach_email(
        self,
        company_name: str,
        funding_info: Dict[str, Any],
        hiring_status: int,
    ) -> str:
        try:
            hiring_context = {
                0: "has recently received funding",
                1: "may be looking to expand their team",
                2: "is actively hiring",
            }.get(hiring_status, "has recently received funding")

            investors = funding_info.get("investors") or []
            investors_str = ", ".join(investors) if investors else "notable investors"
            amount = funding_info.get("funding_amount")
            amount_str = f"${amount:,.0f}" if amount else "an undisclosed amount"
            round_str = funding_info.get("funding_round") or "recent round"

            prompt = f"""Write a short outreach email to {company_name}.

Facts:
- They raised {amount_str} ({round_str})
- Investors: {investors_str}
- They {hiring_context}
- You are from CodeRound: a full-stack AI recruiter that helps fast-growing startups automate hiring and find the perfect candidate in 7 days

Requirements:
- Warm, human tone — NOT salesy or generic
- Acknowledge their funding milestone
- Briefly explain CodeRound's value
- Soft CTA: 15-minute intro call
- 150-180 words, email body only"""

            email = self._chat(prompt, max_tokens=350)
            return email.strip() if email else self._fallback_email(company_name)

        except Exception as e:
            logger.error(f"Groq generate_outreach_email error: {e}")
            return self._fallback_email(company_name)

    @staticmethod
    def _fallback_email(company_name: str) -> str:
        return f"""Hi there,

Congratulations on {company_name}'s recent funding — that's a huge milestone!

I'm reaching out from CodeRound, a full-stack AI recruiter built specifically for fast-growing startups. We help companies like yours automate the entire hiring cycle and land the perfect candidate fit in just 7 days.

Given your growth trajectory, I thought there might be a great fit here. Would you be open to a quick 15-minute intro call to explore how we can support your team's next chapter?

Looking forward to hearing from you.

Best,
CodeRound AI Team"""

    async def extract_decision_makers(self, company_name: str, company_info: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract key decision makers from this company information.

STRICT RULES:
- name: FULL NAME ONLY, no titles
- title: Job title ONLY (CEO/Founder/CTO etc), no company names
- linkedin_url: ONLY https://linkedin.com/in/[username] pattern. Null otherwise.

Company: {company_name}
Information:
{company_info[:1500]}

Return ONLY valid JSON:
{{
    "decision_makers": [
        {{
            "name": "Full Name",
            "title": "CEO/Founder/CTO/etc",
            "linkedin_url": "https://linkedin.com/in/... or null"
        }}
    ],
    "confidence": 0.0-1.0
}}"""

            raw = self._chat(prompt, max_tokens=300)
            result = self._extract_json(raw)

            if result.get("decision_makers"):
                logger.info(f"Extracted {len(result['decision_makers'])} decision makers for {company_name}")

            return result

        except Exception as e:
            logger.error(f"Groq extract_decision_makers error: {e}")
            return {"decision_makers": [], "confidence": 0.0}


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

async def enrich_company(text: str) -> Dict[str, Any]:
    return await GroqEnricher().enrich_company(text)

async def extract_company_description(company_name: str, search_text: str) -> str:
    return await GroqEnricher().extract_company_description(company_name, search_text)

async def extract_company_info(text: str) -> Dict[str, Any]:
    return await GroqEnricher().enrich_company(text)

async def analyze_hiring_status(company_name: str, results: str) -> Dict[str, Any]:
    return {"hiring_status": 0, "confidence": 0.5, "hiring_positions": []}

async def extract_decision_makers(company_name: str, company_info: str) -> Dict[str, Any]:
    return await GroqEnricher().extract_decision_makers(company_name, company_info)

async def generate_email(
    company_name: str,
    funding_info: Dict[str, Any],
    hiring_status: int,
) -> str:
    return await GroqEnricher().generate_outreach_email(company_name, funding_info, hiring_status)
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
]


def _is_invalid_company_name(name: str) -> bool:
    """Return True if the name looks like a news site or article title."""
    if not name:
        return True
    n = name.lower().strip()
    if len(n) > 60:
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
        ONE call that extracts company info AND hiring status together.
        Halves API usage vs calling extract + hiring separately.
        Returns merged dict with all fields needed by companies.py
        """
        try:
            prompt = f"""Extract startup funding information from the text below. Return ONLY valid JSON.

RULES:
- company_name: the STARTUP name that received funding (NOT a news site, NOT an article title)
- If text is about a news aggregator or list article with no single primary startup, set company_name to null
- hiring_status: 0=not hiring, 1=potentially hiring (scaling/growing mentioned), 2=actively hiring (job postings/open roles mentioned)

Text:
{text[:2000]}

JSON (no markdown, no explanation):
{{
    "company_name": "startup name or null",
    "funding_amount": <number in USD e.g. 5000000, or null>,
    "funding_round": "Seed or Pre-Seed or Series A or Series B etc, or null",
    "investors": ["investor 1", "investor 2"],
    "lead_investor": "name or null",
    "country": "country name or null",
    "hiring_status": <0, 1, or 2>,
    "hiring_positions": ["role 1", "role 2"]
}}"""

            raw = self._chat(prompt, max_tokens=400)
            result = self._extract_json(raw)

            # Validate company name
            name = result.get("company_name")
            if name and _is_invalid_company_name(name):
                logger.warning(f"Groq returned bad company name, nulling: '{name}'")
                result["company_name"] = None

            if result.get("company_name"):
                logger.info(
                    f"Groq extracted: {result['company_name']} | "
                    f"{result.get('funding_round')} | "
                    f"${result.get('funding_amount')} | "
                    f"hiring={result.get('hiring_status')}"
                )
            return result

        except Exception as e:
            logger.error(f"Groq enrich_company error: {e}")
            return {}

    async def generate_outreach_email(
        self,
        company_name: str,
        funding_info: Dict[str, Any],
        hiring_status: int,
    ) -> str:
        """Generate a personalised outreach email."""
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
- 150-180 words
- Email body only, no subject line"""

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


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

async def enrich_company(text: str) -> Dict[str, Any]:
    """Single call: returns company_name, funding info, AND hiring_status."""
    return await GroqEnricher().enrich_company(text)


# Keep these for outreach.py compatibility (generate_email is used there)
async def extract_company_info(text: str) -> Dict[str, Any]:
    """Alias for enrich_company — use enrich_company in new code."""
    return await GroqEnricher().enrich_company(text)


async def analyze_hiring_status(company_name: str, results: str) -> Dict[str, Any]:
    """
    Kept for compatibility. In new code, hiring_status comes from enrich_company.
    This is a no-op passthrough that returns a neutral result to avoid extra API calls.
    """
    return {"hiring_status": 0, "confidence": 0.5, "hiring_positions": []}


async def generate_email(
    company_name: str,
    funding_info: Dict[str, Any],
    hiring_status: int,
) -> str:
    return await GroqEnricher().generate_outreach_email(company_name, funding_info, hiring_status)
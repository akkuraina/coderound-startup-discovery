import httpx
import logging
from typing import List, Dict, Any
from config import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TavilySearcher:
    BASE_URL = "https://api.tavily.com/search"

    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY

    async def search_recent_funding(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for recent startup funding using date-specific and varied queries
        so each run fetches genuinely fresh results rather than the same cached articles.
        """
        now = datetime.now()
        year = now.year
        month = now.strftime("%B")          # e.g. "May"
        prev_month = (now.replace(day=1) - timedelta(days=1)).strftime("%B")  # e.g. "April"
        week = now.isocalendar()[1]         # ISO week number

        queries = [
            # Date-specific queries — change every month/week so results rotate
            f"startup raised funding {month} {year}",
            f"startup seed funding {month} {year} announcement",
            f"Series A funding round {month} {year}",
            f"startup funding news week {week} {year}",
            # Broader evergreen queries for variety
            f"new startup investment announced {month} {year}",
            f"tech startup raises capital {year}",
            f"startup funding {prev_month} {year} seed Series A",
            "recently funded startup hiring engineers",
        ]

        all_results: List[Dict[str, Any]] = []
        for query in queries:
            results = await self._search(query)
            all_results.extend(results)

        # Deduplicate by URL (more reliable than title)
        seen: set = set()
        unique: List[Dict[str, Any]] = []
        for item in all_results:
            key = item.get("url") or item.get("title", "")
            if key not in seen:
                seen.add(key)
                unique.append(item)

        logger.info(f"Tavily: {len(unique)} unique results from {len(queries)} queries")
        return unique

    async def _search(self, query: str) -> List[Dict[str, Any]]:
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "include_answer": True,
                "max_results": 10,
                "days": 30,            # Tavily restricts to last 30 days
            }
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Tavily API error for query '{query}': {e}")
            return []

    async def search_company_details(self, company_name: str) -> Dict[str, Any]:
        """Fetch the company's own website/LinkedIn content for description extraction."""
        try:
            # Search for company's own pages, not news about them
            query = f"{company_name} company about what we do product"
            payload = {
                "api_key": self.api_key,
                "query": query,
                "include_answer": True,
                "max_results": 5,
            }
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                return {
                    "company_name": company_name,
                    "search_results": data.get("results", []),
                    "answer": data.get("answer", ""),
                }
        except Exception as e:
            logger.error(f"Tavily company search error for {company_name}: {e}")
            return {"company_name": company_name, "search_results": [], "answer": ""}


async def search_recent_funding(limit: int = 20) -> List[Dict[str, Any]]:
    return await TavilySearcher().search_recent_funding(limit)

async def search_company_details(company_name: str) -> Dict[str, Any]:
    return await TavilySearcher().search_company_details(company_name)
import httpx
import logging
from typing import List, Dict, Any
from config import settings
from datetime import datetime

logger = logging.getLogger(__name__)


class TavilySearcher:
    """Tavily API client for web search."""

    BASE_URL = "https://api.tavily.com/search"

    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY

    async def search_recent_funding(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for recent startup funding announcements across multiple queries."""
        queries = [
            f"startup seed funding last 30 days {datetime.now().year}",
            f"Series A funding announcement {datetime.now().year}",
            "new startup investment news this month",
            "tech startup raised capital recently",
        ]

        all_results: List[Dict[str, Any]] = []
        for query in queries:
            results = await self._search(query)
            all_results.extend(results)

        # Deduplicate by title
        seen: set = set()
        unique: List[Dict[str, Any]] = []
        for item in all_results:
            title = item.get("title", "")
            if title not in seen:
                seen.add(title)
                unique.append(item)

        logger.info(f"Tavily: {len(unique)} unique results after dedup")
        return unique[:limit]

    async def _search(self, query: str) -> List[Dict[str, Any]]:
        """Execute a single Tavily search query."""
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "include_answer": True,
                "max_results": 10,
                "days": 30,
            }
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Tavily API error for query '{query}': {e}")
            return []

    async def search_company_details(self, company_name: str) -> Dict[str, Any]:
        """Fetch web details for a specific company (website, LinkedIn, hiring)."""
        try:
            query = f"{company_name} website linkedin hiring careers"
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


# Module-level helpers

async def search_recent_funding(limit: int = 20) -> List[Dict[str, Any]]:
    return await TavilySearcher().search_recent_funding(limit)


async def search_company_details(company_name: str) -> Dict[str, Any]:
    return await TavilySearcher().search_company_details(company_name)
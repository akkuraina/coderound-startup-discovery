import httpx
import json
import logging
from typing import List, Dict, Any
from config import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TavilySearcher:
    """Tavily API client for web search"""
    
    BASE_URL = "https://api.tavily.com/search"
    
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        
    async def search_recent_funding(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for recent startup funding announcements
        Returns list of relevant results
        """
        try:
            queries = [
                f"startup seed funding last 30 days {datetime.now().year}",
                "Series A funding announcement 2024",
                "new startup investment news",
                "tech startup raised capital recently"
            ]
            
            all_results = []
            
            for query in queries:
                result = await self._search(query)
                if result:
                    all_results.extend(result)
            
            # Remove duplicates based on title
            seen = set()
            unique_results = []
            for item in all_results:
                title = item.get("title", "")
                if title not in seen:
                    seen.add(title)
                    unique_results.append(item)
            
            logger.info(f"Found {len(unique_results)} funding results")
            return unique_results[:limit]
        
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []
    
    async def _search(self, query: str) -> List[Dict[str, Any]]:
        """Execute a single Tavily search"""
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "include_answer": True,
                "max_results": 10,
                "days": 30
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return data.get("results", [])
        
        except Exception as e:
            logger.error(f"Tavily API error for query '{query}': {e}")
            return []
    
    async def search_company_details(self, company_name: str) -> Dict[str, Any]:
        """Search for details about a specific company"""
        try:
            query = f"{company_name} website linkedin hiring careers"
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "include_answer": True,
                "max_results": 5
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                return {
                    "company_name": company_name,
                    "search_results": results,
                    "answer": data.get("answer", "")
                }
        
        except Exception as e:
            logger.error(f"Company search error for {company_name}: {e}")
            return {"company_name": company_name, "search_results": [], "answer": ""}

async def search_recent_funding(limit: int = 20) -> List[Dict[str, Any]]:
    """Helper function to search for recent funding"""
    searcher = TavilySearcher()
    return await searcher.search_recent_funding(limit)

async def search_company_details(company_name: str) -> Dict[str, Any]:
    """Helper function to search company details"""
    searcher = TavilySearcher()
    return await searcher.search_company_details(company_name)

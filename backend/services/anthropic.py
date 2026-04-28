import json
import logging
from typing import Dict, Any, List
from anthropic import Anthropic
from config import settings

logger = logging.getLogger(__name__)

class AnthropicEnricher:
    """Anthropic client for data enrichment"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-sonnet-20240229"
    
    async def extract_company_info(self, text: str) -> Dict[str, Any]:
        """
        Extract structured company information from unstructured text
        Returns: company_name, funding_amount, round, investors, etc.
        """
        try:
            prompt = f"""
Analyze the following text and extract company funding information in JSON format:

Text: {text}

Extract and return JSON with these fields (use null if not found):
{{
    "company_name": "string",
    "funding_amount": "number in USD",
    "funding_currency": "USD",
    "funding_round": "Seed/Series A/Series B/etc",
    "investors": ["array of investor names"],
    "lead_investor": "string",
    "announcement_date": "YYYY-MM-DD format",
    "use_of_funds": "string description",
    "country": "country name"
}}

Return ONLY valid JSON, no other text.
"""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Try to extract JSON from response
            try:
                # Find JSON in response (might have extra text)
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group())
                    logger.info(f"Extracted company info: {extracted_data.get('company_name')}")
                    return extracted_data
            except json.JSONDecodeError:
                pass
            
            return {}
        
        except Exception as e:
            logger.error(f"Anthropic extraction error: {e}")
            return {}
    
    async def analyze_hiring_status(self, company_name: str, search_results: str) -> Dict[str, Any]:
        """
        Analyze search results to determine hiring status
        Returns: hiring_status (0=not_hiring, 1=potentially, 2=actively), positions, confidence
        """
        try:
            prompt = f"""
Based on the following search results for {company_name}, determine their hiring status:

Search Results: {search_results}

Analyze and return JSON with:
{{
    "hiring_status": 0-2 (0=not hiring, 1=potentially hiring, 2=actively hiring),
    "confidence": 0-1 (confidence score),
    "hiring_positions": ["list of positions if hiring"],
    "reasoning": "brief explanation"
}}

Return ONLY valid JSON.
"""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    return analysis
            except json.JSONDecodeError:
                pass
            
            return {"hiring_status": 0, "confidence": 0, "hiring_positions": []}
        
        except Exception as e:
            logger.error(f"Hiring analysis error: {e}")
            return {}
    
    async def generate_outreach_email(
        self, 
        company_name: str, 
        funding_info: Dict[str, Any],
        hiring_status: int
    ) -> str:
        """
        Generate personalized outreach email
        Returns: email body content
        """
        try:
            hiring_context = {
                0: "has recently received funding",
                1: "may be looking to expand their team",
                2: "is actively hiring"
            }.get(hiring_status, "is an interesting prospect")
            
            prompt = f"""
Generate a professional but friendly outreach email to {company_name}.

Company Details:
- Funding: ${funding_info.get('funding_amount', 'unknown')} ({funding_info.get('funding_round', 'unknown')})
- Investors: {', '.join(funding_info.get('investors', ['Unknown']))}
- {hiring_context}

The email should:
1. Acknowledge their recent funding
2. Show genuine interest in their company
3. Explain how CodeRound helps fast-growing startups automate hiring
4. End with a call-to-action for a brief call
5. Be warm and not salesy

Keep it to 150-180 words, professional tone.
"""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            email_body = message.content[0].text
            logger.info(f"Generated email for {company_name}")
            return email_body
        
        except Exception as e:
            logger.error(f"Email generation error: {e}")
            return self._default_email_template(company_name)
    
    def _default_email_template(self, company_name: str) -> str:
        """Fallback email template"""
        return f"""Hi there,

I came across {company_name} and was impressed by your recent funding announcement. We've been working with fast-growing startups like yours to streamline their hiring process.

With CodeRound, you can automate your hiring cycles and find your perfect candidate fit in just 7 days.

Would you be interested in a quick 15-minute conversation about how we can support your team's growth?

Best regards,
CodeRound AI Team"""

async def extract_company_info(text: str) -> Dict[str, Any]:
    """Helper function"""
    enricher = AnthropicEnricher()
    return await enricher.extract_company_info(text)

async def analyze_hiring_status(company_name: str, results: str) -> Dict[str, Any]:
    """Helper function"""
    enricher = AnthropicEnricher()
    return await enricher.analyze_hiring_status(company_name, results)

async def generate_email(
    company_name: str,
    funding_info: Dict[str, Any],
    hiring_status: int
) -> str:
    """Helper function"""
    enricher = AnthropicEnricher()
    return await enricher.generate_outreach_email(company_name, funding_info, hiring_status)

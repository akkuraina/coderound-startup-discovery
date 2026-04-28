from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
import json
import logging
import re
from typing import List, Dict, Any

from database import get_db
from models import User, Company
from schemas import CompanyResponse, DiscoveryResult
from utils.auth import decode_token
from services import tavily
from utils.helpers import is_within_30_days

logger = logging.getLogger(__name__)
router = APIRouter()

def parse_tavily_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Tavily search result directly without Anthropic
    Extracts company info using regex and string matching
    """
    try:
        text = f"{result.get('title', '')} {result.get('content', '')}"
        
        # Extract company name (usually first part of title before "raises" or "announces")
        company_name = result.get('title', '').split(' raises ')[0].split(' announces ')[0].split(' gets ')[0].strip()
        if not company_name or len(company_name) < 2:
            return None
        
        # Extract funding amount (e.g., "$10 million", "$5M")
        amount_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)', text, re.IGNORECASE)
        funding_amount = 0
        if amount_match:
            try:
                amount = float(amount_match.group(1))
                unit = amount_match.group(2).upper()
                if unit in ['BILLION', 'B']:
                    funding_amount = amount * 1_000_000_000
                else:  # MILLION or M
                    funding_amount = amount * 1_000_000
            except:
                funding_amount = 0
        
        # Extract funding round (Seed, Series A, Series B, etc.)
        round_match = re.search(r'(Seed|Series\s+[A-Z]|Series\s+[A-Z]\+)', text, re.IGNORECASE)
        funding_round = round_match.group(1) if round_match else "Seed"
        
        # Extract investors (look for common patterns)
        investors = []
        # Look for "led by" or "from" patterns
        investor_matches = re.findall(r'(?:led by|from|backed by|investment from)\s+([A-Za-z\s&,]+?)(?:\.|,|$)', text, re.IGNORECASE)
        if investor_matches:
            investors = [inv.strip() for inv in investor_matches[0].split(',')[:3]]
        
        # Detect hiring status from keywords
        hiring_keywords_active = ['hiring', 'looking for', 'we are hiring', 'job openings', 'team expansion', 'recruiting']
        hiring_keywords_potential = ['expansion', 'growing', 'new hires', 'building team', 'scaling']
        
        text_lower = text.lower()
        hiring_status = 0  # default: not hiring
        
        if any(keyword in text_lower for keyword in hiring_keywords_active):
            hiring_status = 2  # actively hiring
        elif any(keyword in text_lower for keyword in hiring_keywords_potential):
            hiring_status = 1  # potentially hiring
        
        # Extract country if possible
        country_pattern = r'\b(USA|US|United States|UK|United Kingdom|India|Canada|Germany|France|Australia|Singapore|Israel)\b'
        country_match = re.search(country_pattern, text, re.IGNORECASE)
        country = country_match.group(1) if country_match else "USA"
        
        return {
            "company_name": company_name,
            "funding_amount": funding_amount,
            "funding_round": funding_round,
            "investors": investors,
            "country": country,
            "hiring_status": hiring_status,
            "description": result.get('content', ''),
            "url": result.get('url', '')
        }
    
    except Exception as e:
        logger.error(f"Error parsing Tavily result: {e}")
        return None

async def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """Get authenticated user from token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    email = decode_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/discover", response_model=DiscoveryResult)
async def discover_startups(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Discover recently funded startups
    Parses Tavily results directly (Anthropic bypassed for now)
    """
    try:
        # Validate user
        user = await get_current_user(token, db)
        
        logger.info(f"Starting discovery for user {user.email}")
        
        # Search for recent funding
        search_results = await tavily.search_recent_funding(limit=20)
        
        if not search_results:
            return DiscoveryResult(
                companies=[],
                total_found=0,
                processed_at=datetime.utcnow(),
                message="No recent funding announcements found"
            )
        
        logger.info(f"Found {len(search_results)} raw results from Tavily")
        
        discovered_companies = []
        
        for result in search_results:
            try:
                # Parse company info directly from Tavily result (no Anthropic)
                company_info = parse_tavily_result(result)
                
                if not company_info or not company_info.get("company_name"):
                    continue
                
                company_name = company_info.get("company_name", "").strip()
                
                # Check if company already exists
                existing = db.query(Company).filter(
                    Company.name.ilike(company_name)
                ).first()
                
                if existing:
                    # Update with new info if available
                    logger.info(f"Updating existing company: {company_name}")
                    db_company = existing
                else:
                    # Create new company record
                    logger.info(f"Creating new company: {company_name}")
                    db_company = Company(name=company_name)
                
                # Update company details from parsed info
                if company_info.get("funding_amount"):
                    db_company.funding_amount = float(company_info.get("funding_amount", 0))
                
                if company_info.get("funding_round"):
                    db_company.funding_round = company_info.get("funding_round")
                
                # Set funding date to today (since we don't have exact date from Tavily)
                db_company.funding_date = datetime.utcnow()
                
                if company_info.get("investors"):
                    db_company.investors = company_info.get("investors", [])
                
                if company_info.get("country"):
                    db_company.country = company_info.get("country")
                
                db_company.description = company_info.get("description", "")
                db_company.website = company_info.get("url", "")
                
                # Set hiring status from parsed data
                db_company.hiring_status = company_info.get("hiring_status", 0)
                
                db_company.enriched_data = company_info
                db_company.last_enriched = datetime.utcnow()
                
                # Save to database
                db.add(db_company)
                db.commit()
                db.refresh(db_company)
                
                discovered_companies.append(db_company)
                logger.info(f"Saved company: {company_name} (Hiring: {db_company.hiring_status})")
                
            except Exception as e:
                logger.error(f"Error processing result: {e}")
                db.rollback()
                continue
        
        logger.info(f"Discovery complete: {len(discovered_companies)} companies found and saved")
        
        company_responses = [CompanyResponse.from_orm(c) for c in discovered_companies]
        
        return DiscoveryResult(
            companies=company_responses,
            total_found=len(discovered_companies),
            processed_at=datetime.utcnow(),
            message=f"Found and parsed {len(discovered_companies)} startup(s) from Tavily results"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Discovery process failed"
        )

@router.get("", response_model=List[CompanyResponse])
async def get_companies(
    token: str = Query(...),
    hiring_status: int = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """
    Get all companies (with optional filters)
    Filters can be applied by hiring_status
    """
    try:
        user = await get_current_user(token, db)
        
        query = db.query(Company)
        
        # Filter by hiring status if specified
        if hiring_status is not None:
            query = query.filter(Company.hiring_status == hiring_status)
        
        # Filter to last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Company.funding_date >= thirty_days_ago)
        
        companies = query.order_by(desc(Company.updated_at)).offset(skip).limit(limit).all()
        
        return [CompanyResponse.from_orm(c) for c in companies]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get companies error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch companies"
        )

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get details for a specific company"""
    try:
        user = await get_current_user(token, db)
        
        company = db.query(Company).filter(Company.id == company_id).first()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.from_orm(company)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get company error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch company"
        )

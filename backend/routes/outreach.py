from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import json
import logging
from typing import List

from database import get_db
from models import User, Company, Outreach
from schemas import OutreachResponse, OutreachCreate, OutreachUpdate, OutreachGenerateEmailRequest
from utils.auth import decode_token
from services import anthropic, resend

logger = logging.getLogger(__name__)
router = APIRouter()

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

@router.post("/generate-email")
async def generate_outreach_email(
    req: OutreachGenerateEmailRequest,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Generate AI-powered outreach email for a company"""
    try:
        user = await get_current_user(token, db)
        
        # Get company details
        company = db.query(Company).filter(Company.id == req.company_id).first()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Prepare funding info
        funding_info = {
            "company_name": company.name,
            "funding_amount": company.funding_amount,
            "funding_round": company.funding_round,
            "investors": company.investors if company.investors else []
        }
        
        # Generate email
        email_body = await anthropic.generate_email(
            company.name,
            funding_info,
            company.hiring_status
        )
        
        logger.info(f"Generated email for company {company.id}")
        
        return {
            "subject": f"CodeRound - Streamline Hiring at {company.name}",
            "body": email_body,
            "company_id": req.company_id,
            "company_name": company.name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate email"
        )

@router.post("/send", response_model=OutreachResponse)
async def send_outreach_email(
    outreach: OutreachCreate,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Send outreach email to a company contact"""
    try:
        user = await get_current_user(token, db)
        
        # Validate company exists
        company = db.query(Company).filter(Company.id == outreach.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Convert email content to HTML
        html_content = resend.html_email_template(
            outreach.email_subject,
            outreach.email_content,
            user.name
        )
        
        # Send email via Resend
        send_result = await resend.send_email(
            to=outreach.email_sent_to,
            subject=outreach.email_subject,
            html_content=html_content
        )
        
        # Create outreach record
        db_outreach = Outreach(
            user_id=user.id,
            company_id=outreach.company_id,
            email_sent_to=outreach.email_sent_to,
            email_subject=outreach.email_subject,
            email_content=outreach.email_content,
            sent_at=datetime.utcnow()
        )
        
        db.add(db_outreach)
        db.commit()
        db.refresh(db_outreach)
        
        logger.info(f"Outreach email sent from {user.email} to {outreach.email_sent_to}")
        
        return OutreachResponse.from_orm(db_outreach)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send email error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

@router.get("", response_model=List[OutreachResponse])
async def get_outreach_history(
    token: str = Query(...),
    response_status: int = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get outreach history for current user"""
    try:
        user = await get_current_user(token, db)
        
        query = db.query(Outreach).filter(Outreach.user_id == user.id)
        
        if response_status is not None:
            query = query.filter(Outreach.response_status == response_status)
        
        outreaches = query.order_by(desc(Outreach.sent_at)).offset(skip).limit(limit).all()
        
        return [OutreachResponse.from_orm(o) for o in outreaches]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get outreach error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch outreach history"
        )

@router.patch("/{outreach_id}", response_model=OutreachResponse)
async def update_outreach(
    outreach_id: int,
    update_data: OutreachUpdate,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Update outreach status (track responses)"""
    try:
        user = await get_current_user(token, db)
        
        outreach = db.query(Outreach).filter(
            and_(
                Outreach.id == outreach_id,
                Outreach.user_id == user.id
            )
        ).first()
        
        if not outreach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outreach record not found"
            )
        
        # Update fields if provided
        if update_data.response_status is not None:
            outreach.response_status = update_data.response_status
            outreach.response_received_at = datetime.utcnow()
        
        if update_data.response_notes is not None:
            outreach.response_notes = update_data.response_notes
        
        db.commit()
        db.refresh(outreach)
        
        logger.info(f"Updated outreach {outreach_id}")
        
        return OutreachResponse.from_orm(outreach)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update outreach error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update outreach"
        )

# Import and operator
from sqlalchemy import and_

"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

# Company Schemas
class CompanyBase(BaseModel):
    name: str
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    funding_amount: Optional[float] = None
    funding_date: Optional[datetime] = None
    funding_round: Optional[str] = None
    investors: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    hiring_status: Optional[int] = None
    hiring_positions: Optional[str] = None
    enriched_data: Optional[dict] = None
    decision_makers: Optional[dict] = None

class CompanyResponse(CompanyBase):
    id: int
    hiring_status: int
    hiring_positions: Optional[str]
    enriched_data: Optional[dict]
    decision_makers: Optional[dict]
    created_at: datetime
    updated_at: datetime
    last_enriched: Optional[datetime]
    
    class Config:
        from_attributes = True

# Outreach Schemas
class OutreachGenerateEmailRequest(BaseModel):
    """Request to generate an outreach email"""
    company_id: int

class OutreachBase(BaseModel):
    company_id: int
    email_sent_to: str
    email_subject: str
    email_content: str

class OutreachCreate(OutreachBase):
    pass

class OutreachUpdate(BaseModel):
    response_status: Optional[int] = None
    response_notes: Optional[str] = None

class OutreachResponse(OutreachBase):
    id: int
    user_id: int
    response_status: int
    response_received_at: Optional[datetime]
    response_notes: Optional[str]
    sent_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Discovery Response
class DiscoveryResult(BaseModel):
    companies: List[CompanyResponse]
    total_found: int
    processed_at: datetime
    message: str

class HealthCheck(BaseModel):
    status: str
    service: str
    version: str

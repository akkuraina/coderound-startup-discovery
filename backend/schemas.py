from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List, Any
import json

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
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Company Schemas
# ---------------------------------------------------------------------------

class CompanyBase(BaseModel):
    name: str
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    funding_amount: Optional[float] = None
    funding_date: Optional[datetime] = None
    funding_round: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    hiring_status: Optional[int] = None
    hiring_positions: Optional[List[str]] = None
    enriched_data: Optional[dict] = None
    decision_makers: Optional[dict] = None


class CompanyResponse(CompanyBase):
    id: int
    hiring_status: int = 0

    # These come back as Python lists from the model @property,
    # but validators handle the case where raw DB text leaks through.
    investors: Optional[List[str]] = []
    hiring_positions: Optional[List[str]] = []

    # JSON columns — always dicts
    enriched_data: Optional[dict] = {}
    decision_makers: Optional[dict] = {}

    created_at: datetime
    updated_at: datetime
    last_enriched: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Validators — defensive coercion in case raw strings come through
    # ------------------------------------------------------------------

    @validator("investors", "hiring_positions", pre=True, always=True)
    def coerce_to_list(cls, v) -> List[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @validator("enriched_data", "decision_makers", pre=True, always=True)
    def coerce_to_dict(cls, v) -> dict:
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Outreach Schemas
# ---------------------------------------------------------------------------

class OutreachGenerateEmailRequest(BaseModel):
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
    response_received_at: Optional[datetime] = None
    response_notes: Optional[str] = None
    sent_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Auth Schemas
# ---------------------------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

class DiscoveryResult(BaseModel):
    companies: List[CompanyResponse]
    total_found: int
    processed_at: datetime
    message: str

class HealthCheck(BaseModel):
    status: str
    service: str
    version: str
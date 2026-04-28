"""
SQLAlchemy database models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship, synonym
from datetime import datetime
from database import Base
import json
import logging

logger = logging.getLogger(__name__)

def _ensure_dict(value):
    """Ensure value is a dict, not a JSON string"""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Could not parse JSON string: {value}")
            return {}
    return value or {}

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    outreaches = relationship("Outreach", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"

class Company(Base):
    """Company model for storing startup information"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    website = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    funding_amount = Column(Float, nullable=True)  # in USD
    funding_date = Column(DateTime, nullable=True)
    funding_round = Column(String(50), nullable=True)  # e.g., "Seed", "Series A"
    investors = Column(Text, nullable=True)  # JSON string of investor array
    country = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Hiring status: 0 = not_hiring, 1 = potentially_hiring, 2 = actively_hiring
    hiring_status = Column(Integer, default=0)  
    hiring_positions = Column(Text, nullable=True)  # JSON string of positions
    
    # Enriched data (always returns dict, never string)
    _enriched_data = Column("enriched_data", JSON, nullable=True)
    _decision_makers = Column("decision_makers", JSON, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_enriched = Column(DateTime, nullable=True)
    
    # Relationships
    outreaches = relationship("Outreach", back_populates="company", cascade="all, delete-orphan")
    
    @property
    def enriched_data(self):
        """Get enriched_data as dict, automatically parsing if string"""
        return _ensure_dict(self._enriched_data)
    
    @enriched_data.setter
    def enriched_data(self, value):
        """Set enriched_data as dict (never string)"""
        if isinstance(value, str):
            self._enriched_data = json.loads(value)
        else:
            self._enriched_data = value or None
    
    @property
    def decision_makers(self):
        """Get decision_makers as dict, automatically parsing if string"""
        return _ensure_dict(self._decision_makers)
    
    @decision_makers.setter
    def decision_makers(self, value):
        """Set decision_makers as dict (never string)"""
        if isinstance(value, str):
            self._decision_makers = json.loads(value)
        else:
            self._decision_makers = value or None
    
    def __repr__(self):
        return f"<Company {self.name}>"

class Outreach(Base):
    """Outreach model for tracking email campaigns"""
    __tablename__ = "outreach"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    email_sent_to = Column(String(255), nullable=False)
    email_subject = Column(String(255), nullable=False)
    email_content = Column(Text, nullable=False)
    
    # Status: 0 = pending, 1 = positive_response, 2 = negative_response, 3 = no_response
    response_status = Column(Integer, default=0)
    response_received_at = Column(DateTime, nullable=True)
    response_notes = Column(Text, nullable=True)
    
    # Tracking
    sent_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="outreaches")
    company = relationship("Company", back_populates="outreaches")
    
    def __repr__(self):
        return f"<Outreach {self.user_id}-{self.company_id}>"

"""
SQLAlchemy database models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import json
import logging

logger = logging.getLogger(__name__)


def _parse_json_list(value) -> list:
    """Safely coerce a value to a Python list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            result = json.loads(value)
            return result if isinstance(result, list) else []
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Could not parse JSON list string: {value!r}")
            return []
    return []


def _parse_json_dict(value) -> dict:
    """Safely coerce a value to a Python dict."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            result = json.loads(value)
            return result if isinstance(result, dict) else {}
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Could not parse JSON dict string: {value!r}")
            return {}
    return {}


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
    funding_amount = Column(Float, nullable=True)
    funding_date = Column(DateTime, nullable=True)
    funding_round = Column(String(50), nullable=True)

    # Stored as JSON text; always read back as Python list
    _investors = Column("investors", Text, nullable=True)
    _hiring_positions = Column("hiring_positions", Text, nullable=True)

    country = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # 0 = not_hiring, 1 = potentially_hiring, 2 = actively_hiring
    hiring_status = Column(Integer, default=0)

    # JSON columns — stored natively by SQLAlchemy JSON type
    enriched_data = Column("enriched_data", JSON, nullable=True)
    decision_makers = Column("decision_makers", JSON, nullable=True)

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_enriched = Column(DateTime, nullable=True)

    outreaches = relationship("Outreach", back_populates="company", cascade="all, delete-orphan")

    # ------------------------------------------------------------------
    # investors — stored as JSON text, exposed as Python list
    # ------------------------------------------------------------------

    @property
    def investors(self) -> list:
        return _parse_json_list(self._investors)

    @investors.setter
    def investors(self, value):
        if value is None:
            self._investors = None
        elif isinstance(value, str):
            # already a JSON string — validate it parses as a list
            self._investors = value
        else:
            self._investors = json.dumps(value)

    # ------------------------------------------------------------------
    # hiring_positions — stored as JSON text, exposed as Python list
    # ------------------------------------------------------------------

    @property
    def hiring_positions(self) -> list:
        return _parse_json_list(self._hiring_positions)

    @hiring_positions.setter
    def hiring_positions(self, value):
        if value is None:
            self._hiring_positions = None
        elif isinstance(value, str):
            self._hiring_positions = value
        else:
            self._hiring_positions = json.dumps(value)

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

    # 0 = pending, 1 = positive_response, 2 = negative_response, 3 = no_response
    response_status = Column(Integer, default=0)
    response_received_at = Column(DateTime, nullable=True)
    response_notes = Column(Text, nullable=True)

    sent_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="outreaches")
    company = relationship("Company", back_populates="outreaches")

    def __repr__(self):
        return f"<Outreach {self.user_id}-{self.company_id}>"
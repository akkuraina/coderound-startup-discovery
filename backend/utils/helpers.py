"""
Helper utilities
"""

import json
from typing import Any, List
import logging

logger = logging.getLogger(__name__)

def safe_json_parse(data: Any) -> dict:
    """Safely parse JSON data"""
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON: {data}")
            return {}
    return {}

def safe_json_dumps(data: Any) -> str:
    """Safely convert to JSON string"""
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to dump JSON: {e}")
        return "{}"

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    if amount is None:
        return "N/A"
    return f"${amount:,.0f}"

def days_ago(date) -> int:
    """Calculate days since a date"""
    from datetime import datetime
    if date is None:
        return None
    return (datetime.utcnow() - date).days

def is_within_30_days(date) -> bool:
    """Check if date is within last 30 days"""
    from datetime import datetime
    if date is None:
        return False
    return (datetime.utcnow() - date).days <= 30

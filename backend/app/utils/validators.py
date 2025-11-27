"""
Validation utilities
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_airport_code(code: str) -> bool:
    """Validate airport IATA code (3 letters)"""
    return bool(re.match(r'^[A-Z]{3}$', code.upper()))


def validate_phone(phone: str) -> bool:
    """Validate phone number (basic validation)"""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def validate_date_format(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


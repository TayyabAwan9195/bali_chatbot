# ============================================================
# FILE: validators.py
# PURPOSE: Input validation functions
# ============================================================

import re

def is_meaningless_message(message: str) -> bool:
    """Detect meaningless or invalid messages."""
    msg = message.strip().lower()
    if not msg:
        return True
    meaningless_patterns = [
        r'^what$', r'^ok$', r'^okay$', r'^\?$', r'^\?\?$', r'^\.\.\.$', r'^hmm$', r'^uh$', r'^idk$', r'^dunno$',
        r'^yes$', r'^no$', r'^yeah$', r'^nah$', r'^sure$', r'^maybe$', r'^k$', r'^lol$', r'^haha$', r'^brb$',
        r'^wtf$', r'^omg$', r'^wow$', r'^cool$', r'^nice$', r'^thanks$', r'^thank you$', r'^bye$', r'^goodbye$'
    ]
    for pattern in meaningless_patterns:
        if re.match(pattern, msg):
            return True
    # Check for very short messages or single characters
    if len(msg) <= 2 and not any(c.isalnum() for c in msg):
        return True
    return False

def validate_name(name: str) -> bool:
    """Validate name input."""
    name = name.strip()
    if len(name) < 2 or len(name) > 50:
        return False
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False
    return True

def validate_country(country: str) -> bool:
    """Validate country input."""
    country = country.strip()
    if len(country) < 3 or len(country) > 50:
        return False
    if not re.match(r"^[a-zA-Z\s\-']+$", country):
        return False
    return True

def validate_business_type(business: str) -> bool:
    """Validate business type input."""
    business = business.strip()
    if len(business) < 3 or len(business) > 100:
        return False
    # Must contain at least one alphabetic word
    if not re.search(r'[a-zA-Z]{3,}', business):
        return False
    return True

def validate_budget_response(response: str) -> bool:
    """Validate budget yes/no response."""
    lower = response.strip().lower()
    return any(word in lower for word in ["yes", "y", "ok", "sure", "sounds good", "within budget", "no", "not", "can't", "cannot", "too", "outside"])

def validate_start_date(date_str: str) -> bool:
    """Validate start date input."""
    date_str = date_str.strip().lower()
    if len(date_str) < 3 or len(date_str) > 50:
        return False
    # Allow common timeframes
    valid_phrases = ["month", "months", "week", "weeks", "year", "years", "soon", "immediately", "now", "later", "few", "tomorrow", "asap", "next month", "today", "ready"]
    return any(phrase in date_str for phrase in valid_phrases) or re.match(r"^\d+\s*(month|week|year)s?$", date_str)

def validate_shareholders(shareholders: str) -> bool:
    """Validate shareholders input."""
    shareholders = shareholders.strip()
    try:
        num = int(shareholders)
        return 1 <= num <= 10  # Reasonable range
    except ValueError:
        return False

def validate_company_status(status: str) -> bool:
    """Validate company status input."""
    status = status.strip().lower()
    return any(word in status for word in ["yes", "no", "already", "have", "need", "don't", "do not", "help"])

def is_question(message: str) -> bool:
    """Check if message is likely a question."""
    msg = message.strip().lower()
    return msg.endswith('?') or msg.startswith(('what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'do', 'is', 'are', 'does', 'will', 'would', 'could', 'should'))
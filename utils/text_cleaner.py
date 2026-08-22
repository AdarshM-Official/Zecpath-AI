import re

def clean_text(text: str) -> str:
    """Cleans transcript text by standardizing casing, spacing, and removing glitches."""
    if not isinstance(text, str):
        return ""
        
    text = text.lower()
    
    # Remove filler words completely surrounded by space/boundaries
    fillers = r'\b(uh|um|like|you know|i mean|so basically|sort of|kind of)\b'
    text = re.sub(fillers, '', text)
    
    # Lightweight PII Redaction (Ethics/Compliance)
    # Redact email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    # Redact phone numbers (simple pattern)
    text = re.sub(r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b', '[PHONE]', text)
    
    text = re.sub(r'\n+', ' ', text)
    
    # Remove special characters except common punctuation
    text = re.sub(r'[^\w\s\.\-\+]', ' ', text)
    
    # Normalize multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Deduplicate repeating words (e.g. 'the the the' -> 'the')
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)

    return text.strip()
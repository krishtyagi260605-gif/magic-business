import re
from fastapi import UploadFile, HTTPException

def validate_phone(phone: str) -> str:
    """
    Validate Indian and general phone formats.
    Accepts: +91 9876543210, 09876543210, 9876543210, etc.
    Returns cleaned 10-digit or international format.
    """
    cleaned = re.sub(r'[\s\-()]/', '', phone).strip()
    # Simple regex to check length
    if not cleaned:
        raise ValueError("Phone number cannot be empty")
        
    # Check if numbers only
    digits_only = re.sub(r'\+', '', cleaned)
    if not digits_only.isdigit():
        raise ValueError("Phone number must contain digits only")
        
    return cleaned

def validate_email(email: str) -> str:
    """Validate email format."""
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email

def validate_hex_color(hex_color: str) -> str:
    """Validate and normalize hex color codes."""
    hex_color = hex_color.strip()
    if not hex_color.startswith('#'):
        hex_color = '#' + hex_color
    
    pattern = r'^#[0-9a-fA-F]{6}$|^#[0-9a-fA-F]{3}$'
    if not re.match(pattern, hex_color):
        raise ValueError("Invalid hex color code")
    return hex_color

def validate_logo_file(file: UploadFile) -> bool:
    """Validate uploaded logo file (size < 5MB and standard formats)."""
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.svg'}
    filename = file.filename.lower()
    ext = os.path.splitext(filename)[1]
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed. Use PNG, JPG, JPEG, or SVG.")
        
    # Check file size (max 5MB)
    # We can check size by reading content and seeking back
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    max_size = 5 * 1024 * 1024  # 5MB
    if size > max_size:
        raise HTTPException(status_code=400, detail="Logo file size exceeds 5MB limit.")
        
    return True
import os

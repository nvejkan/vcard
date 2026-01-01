#!/usr/bin/env python3
"""
NFC vCard URL Generator
Generates URLs for the vCard web app
"""

from urllib.parse import urlencode, quote
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Contact:
    """Contact information for vCard generation"""
    # Required
    fn: str                          # First Name
    ln: str                          # Last Name
    
    # Local name (optional)
    lfn: Optional[str] = None        # Local First Name
    lln: Optional[str] = None        # Local Last Name
    np: Optional[str] = None         # Name Prefix (local)
    
    # Organization
    org: Optional[str] = None        # Organization
    bu: Optional[str] = None         # Business Unit
    title: Optional[str] = None      # Job Title
    
    # Contact
    email: Optional[str] = None      # Email
    tel: Optional[str] = None        # Main Tel
    mobile: Optional[str] = None     # Mobile
    tel2: Optional[str] = None       # Other Tel
    
    # Address
    company: Optional[str] = None    # Company name in address
    floor: Optional[str] = None      # Floor
    street: Optional[str] = None     # Street
    district: Optional[str] = None   # District
    city: Optional[str] = None       # City
    postal: Optional[str] = None     # Postal Code
    country: Optional[str] = None    # Country
    
    # Optional
    url: Optional[str] = None        # Website
    note: Optional[str] = None       # Note


def generate_url(base_url: str, contact: Contact) -> str:
    """
    Generate URL with contact parameters
    
    Args:
        base_url: Base URL of your GitHub Pages site
        contact: Contact dataclass with all info
    
    Returns:
        Complete URL string
    """
    # Remove trailing slash from base URL
    base_url = base_url.rstrip('/')
    
    # Convert dataclass to dict and filter None values
    params = {k: v for k, v in asdict(contact).items() if v is not None and v != ''}
    
    # Generate query string
    query_string = urlencode(params, quote_via=quote)
    
    return f"{base_url}?{query_string}"


def generate_urls_from_list(base_url: str, contacts: list[dict]) -> list[str]:
    """
    Generate URLs for multiple contacts
    
    Args:
        base_url: Base URL of your GitHub Pages site
        contacts: List of contact dictionaries
    
    Returns:
        List of URL strings
    """
    urls = []
    for contact_data in contacts:
        contact = Contact(**contact_data)
        urls.append(generate_url(base_url, contact))
    return urls


# ============================================================
# EXAMPLES
# ============================================================

if __name__ == "__main__":
    
    # Your GitHub Pages URL
    BASE_URL = "https://yourusername.github.io/vcard/"
    
    # ---------------------------------------------------------
    # Example 1: Simple contact
    # ---------------------------------------------------------
    simple_contact = Contact(
        fn="John",
        ln="Doe",
        email="john.doe@example.com",
        mobile="+1234567890"
    )
    
    print("=" * 60)
    print("Example 1: Simple Contact")
    print("=" * 60)
    print(generate_url(BASE_URL, simple_contact))
    print()
    
    # ---------------------------------------------------------
    # Example 2: Full contact with all fields
    # ---------------------------------------------------------
    full_contact = Contact(
        # English name
        fn="John",
        ln="Doe",
        
        # Local name (Thai example)
        np="คุณ",
        lfn="สมชาย",
        lln="ใจดี",
        
        # Organization
        org="Acme Corp",
        bu="Consulting",
        title="Senior Manager",
        
        # Contact
        email="john.doe@acme.com",
        tel="+6628441000",
        mobile="+66812345678",
        tel2="+6629999999",
        
        # Address
        company="Acme Thailand",
        floor="15th Floor",
        street="123 Main Street",
        district="Central District",
        city="Bangkok",
        postal="10120",
        country="Thailand",
        
        # Optional
        url="https://johndoe.com",
        note="Met at conference 2024"
    )
    
    print("=" * 60)
    print("Example 2: Full Contact")
    print("=" * 60)
    url = generate_url(BASE_URL, full_contact)
    print(url)
    print(f"\nURL Length: {len(url)} characters")
    print()
    
    # ---------------------------------------------------------
    # Example 3: Generate from dictionary
    # ---------------------------------------------------------
    contact_dict = {
        "fn": "Jane",
        "ln": "Smith",
        "org": "Tech Inc",
        "title": "CEO",
        "email": "jane@tech.com",
        "mobile": "+9876543210"
    }
    
    contact = Contact(**contact_dict)
    
    print("=" * 60)
    print("Example 3: From Dictionary")
    print("=" * 60)
    print(generate_url(BASE_URL, contact))
    print()
    
    # ---------------------------------------------------------
    # Example 4: Batch generation
    # ---------------------------------------------------------
    contacts_list = [
        {"fn": "Alice", "ln": "Wong", "email": "alice@example.com", "org": "Company A"},
        {"fn": "Bob", "ln": "Lee", "email": "bob@example.com", "org": "Company B"},
        {"fn": "Charlie", "ln": "Kim", "email": "charlie@example.com", "org": "Company C"},
    ]
    
    print("=" * 60)
    print("Example 4: Batch Generation")
    print("=" * 60)
    for i, url in enumerate(generate_urls_from_list(BASE_URL, contacts_list), 1):
        print(f"{i}. {url}")
    print()
    
    # ---------------------------------------------------------
    # Example 5: From CSV-like data
    # ---------------------------------------------------------
    print("=" * 60)
    print("Example 5: CSV Processing Example")
    print("=" * 60)
    
    # Simulating CSV data
    csv_data = """fn,ln,org,title,email,tel,mobile
John,Doe,Acme,Manager,john@acme.com,+111111,+222222
Jane,Smith,Beta,Director,jane@beta.com,+333333,+444444"""
    
    import csv
    from io import StringIO
    
    reader = csv.DictReader(StringIO(csv_data))
    for row in reader:
        # Filter empty values
        filtered_row = {k: v for k, v in row.items() if v}
        contact = Contact(**filtered_row)
        print(generate_url(BASE_URL, contact))
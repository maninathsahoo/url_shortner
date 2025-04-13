import hashlib
from urllib.parse import urlparse


def generate_short_code(url):
    """Generate a 6-character short code using MD5 hash"""
    return hashlib.md5(url.encode()).hexdigest()[:6]


def get_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc if parsed.netloc else "invalid_domain"

    except:
        return "invalid_domain"
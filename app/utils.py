import re
import uuid
from urllib.parse import urlparse, urljoin
from typing import Optional


def extract_doc_id(url: str) -> str:
    """
    Extract doc_id from URL.
    Patterns:
    - /help/platform/how_to_bind_app_to_proccess.html -> how_to_bind_app_to_proccess
    - /help/platform/360008121732.html -> 360008121732
    - Fallback to UUID if no pattern matches
    """
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    
    # Try to extract from filename (without extension)
    if path.endswith('.html'):
        # Remove .html extension
        path = path[:-5]
        # Extract last segment
        segments = path.split('/')
        if segments:
            last_segment = segments[-1]
            # Check if it's a valid identifier (alphanumeric, underscores, hyphens)
            if re.match(r'^[a-zA-Z0-9_-]+$', last_segment):
                return last_segment
    
    # Try to extract numeric ID
    numeric_match = re.search(r'/(\d+)\.html', url)
    if numeric_match:
        return numeric_match.group(1)
    
    # Try to extract from path segments (e.g., how_to_bind_app_to_proccess)
    if path:
        segments = path.split('/')
        for segment in reversed(segments):
            if segment and re.match(r'^[a-zA-Z0-9_-]+$', segment):
                return segment
    
    # Fallback to UUID
    return str(uuid.uuid4())


def normalize_url(url: str, base_url: str) -> str:
    """Normalize URL to absolute URL."""
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return urljoin(base_url, url)


def is_valid_help_url(url: str, base_url: str) -> bool:
    """Check if URL is a valid help documentation URL."""
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)
    
    # Must be same domain
    if parsed.netloc and parsed.netloc != base_parsed.netloc:
        return False
    
    # Must be under /help/ path
    if not parsed.path.startswith('/help/'):
        return False
    
    # Should be HTML page
    if parsed.path.endswith('.html') or not parsed.path.endswith('/'):
        return True
    
    return False


import aiohttp
import asyncio
import logging
from typing import Set, Dict, Optional, List
from datetime import datetime
from urllib.parse import urljoin, urlparse
from app.config import settings
from app.utils import extract_doc_id, normalize_url, is_valid_help_url
from app.crawler.parser import HTMLParser

logger = logging.getLogger(__name__)


class Crawler:
    """Recursive crawler for ELMA365 documentation."""
    
    def __init__(self):
        self.base_url = settings.CRAWL_BASE_URL
        self.max_depth = settings.CRAWL_MAX_DEPTH
        self.delay = settings.CRAWL_DELAY
        self.max_concurrent = settings.CRAWL_MAX_CONCURRENT
        self.parser = HTMLParser(self.base_url)
        
        # Crawling state
        self.visited_urls: Set[str] = set()
        self.queue: List[tuple[str, int]] = []  # (url, depth)
        self.semaphore: Optional[asyncio.Semaphore] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_crawling = False
        self.stats = {
            'total_crawled': 0,
            'total_failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ELMA365-Crawler/1.0)'
            }
        )
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def crawl_recursive(self, start_url: Optional[str] = None) -> List[Dict]:
        """
        Start recursive crawling from /help/ root or specified URL.
        Returns list of crawled documents.
        """
        if self.is_crawling:
            logger.warning("Crawler is already running")
            return []
        
        self.is_crawling = True
        self.stats['start_time'] = datetime.now()
        self.visited_urls.clear()
        self.queue.clear()
        
        # Determine start URL
        if start_url is None:
            start_url = urljoin(self.base_url, '/help/')
        else:
            start_url = normalize_url(start_url, self.base_url)
        
        # Initialize queue
        if is_valid_help_url(start_url, self.base_url):
            self.queue.append((start_url, 0))
        else:
            # If it's a directory, we'll discover pages from it
            self.queue.append((start_url, 0))
        
        crawled_docs = []
        
        try:
            while self.queue:
                # Get batch of URLs to crawl
                batch = []
                while self.queue and len(batch) < self.max_concurrent:
                    url, depth = self.queue.pop(0)
                    if url not in self.visited_urls and depth <= self.max_depth:
                        batch.append((url, depth))
                
                if not batch:
                    break
                
                # Crawl batch concurrently
                tasks = [self._crawl_url(url, depth) for url, depth in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Error crawling: {result}")
                        self.stats['total_failed'] += 1
                    elif result:
                        crawled_docs.append(result)
                        # Discover new URLs from this page
                        if result.get('links'):
                            await self._discover_urls(result['links'], result.get('depth', 0) + 1)
                
                # Rate limiting
                if self.delay > 0:
                    await asyncio.sleep(self.delay)
        
        finally:
            self.is_crawling = False
            self.stats['end_time'] = datetime.now()
        
        return crawled_docs
    
    async def crawl_url(self, url: str) -> Optional[Dict]:
        """Crawl a single URL."""
        url = normalize_url(url, self.base_url)
        if not is_valid_help_url(url, self.base_url):
            logger.warning(f"Invalid help URL: {url}")
            return None
        
        async with self:
            return await self._crawl_url(url, 0)
    
    async def _crawl_url(self, url: str, depth: int) -> Optional[Dict]:
        """Crawl a single URL (internal method)."""
        if url in self.visited_urls:
            return None
        
        async with self.semaphore:
            try:
                logger.info(f"Crawling: {url} (depth: {depth})")
                
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch {url}: status {response.status}")
                        self.stats['total_failed'] += 1
                        return None
                    
                    html = await response.text()
                    parsed_data = self.parser.parse(html, url)
                    
                    doc_id = extract_doc_id(url)
                    
                    doc_data = {
                        'doc_id': doc_id,
                        'url': url,
                        'title': parsed_data['title'],
                        'breadcrumbs': parsed_data['breadcrumbs'],
                        'section': parsed_data['section'],
                        'html': parsed_data['html'],
                        'plain_text': parsed_data['plain_text'],
                        'last_crawled': datetime.now(),
                        'links': parsed_data['links'],
                        'depth': depth
                    }
                    
                    self.visited_urls.add(url)
                    self.stats['total_crawled'] += 1
                    
                    return doc_data
            
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                self.stats['total_failed'] += 1
                return None
    
    async def _discover_urls(self, links: List[str], depth: int):
        """Discover and queue new URLs from links."""
        for link in links:
            normalized = normalize_url(link, self.base_url)
            if is_valid_help_url(normalized, self.base_url):
                if normalized not in self.visited_urls:
                    # Check if already in queue
                    if not any(url == normalized for url, _ in self.queue):
                        self.queue.append((normalized, depth))
    
    def get_status(self) -> Dict:
        """Get current crawling status."""
        return {
            'is_crawling': self.is_crawling,
            'visited_count': len(self.visited_urls),
            'queue_size': len(self.queue),
            'stats': self.stats.copy()
        }
    
    def add_url(self, url: str):
        """Manually add URL to crawl queue."""
        url = normalize_url(url, self.base_url)
        if is_valid_help_url(url, self.base_url):
            if url not in self.visited_urls:
                if not any(u == url for u, _ in self.queue):
                    self.queue.append((url, 0))
                    logger.info(f"Added URL to queue: {url}")
        else:
            logger.warning(f"Invalid help URL: {url}")


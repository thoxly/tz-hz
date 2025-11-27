from bs4 import BeautifulSoup
from typing import List, Optional, Dict
from urllib.parse import urljoin, urlparse
import re


class HTMLParser:
    """Parser for extracting data from ELMA365 documentation pages."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def parse(self, html: str, url: str) -> Dict:
        """Parse HTML and extract all relevant data."""
        # Убеждаемся, что HTML правильно декодирован
        if isinstance(html, bytes):
            html = html.decode('utf-8', errors='ignore')
        
        # Парсим HTML
        soup = BeautifulSoup(html, 'lxml')
        
        return {
            'title': self.extract_title(soup),
            'breadcrumbs': self.extract_breadcrumbs(soup),
            'section': self.extract_section(url, soup),
            'html': str(soup),
            'plain_text': self.extract_plain_text(soup),
            'links': self.extract_links(soup, url)
        }
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            text = h1.get_text(strip=True)
            if text:
                return text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            text = title_tag.get_text(strip=True)
            if text:
                return text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Try meta title
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            text = meta_title.get('content')
            if text:
                return text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return None
    
    def extract_breadcrumbs(self, soup: BeautifulSoup) -> List[str]:
        """Extract breadcrumb navigation."""
        breadcrumbs = []
        
        # Look for common breadcrumb patterns
        # Pattern 1: nav with breadcrumb class
        breadcrumb_nav = soup.find('nav', class_=re.compile(r'breadcrumb', re.I))
        if breadcrumb_nav:
            links = breadcrumb_nav.find_all('a')
            for link in links:
                text = link.get_text(strip=True)
                if text:
                    breadcrumbs.append(text)
        
        # Pattern 2: ol/ul with breadcrumb class
        breadcrumb_list = soup.find(['ol', 'ul'], class_=re.compile(r'breadcrumb', re.I))
        if breadcrumb_list:
            items = breadcrumb_list.find_all(['li', 'a'])
            for item in items:
                text = item.get_text(strip=True)
                if text and text not in breadcrumbs:
                    breadcrumbs.append(text)
        
        # Pattern 3: Look for structured data
        breadcrumb_script = soup.find('script', type='application/ld+json')
        if breadcrumb_script:
            try:
                import json
                data = json.loads(breadcrumb_script.string)
                if isinstance(data, dict) and 'itemListElement' in data:
                    for item in data['itemListElement']:
                        if 'name' in item:
                            breadcrumbs.append(item['name'])
            except:
                pass
        
        return breadcrumbs
    
    def extract_section(self, url: str, soup: BeautifulSoup) -> str:
        """Extract section information (breadcrumbs + URL segment)."""
        breadcrumbs = self.extract_breadcrumbs(soup)
        url_segment = self._extract_url_segment(url)
        
        parts = []
        if breadcrumbs:
            parts.append(' > '.join(breadcrumbs))
        if url_segment:
            parts.append(f"[{url_segment}]")
        
        return ' | '.join(parts) if parts else url_segment or ''
    
    def _extract_url_segment(self, url: str) -> str:
        """Extract section segment from URL."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        # Extract segment after /help/
        if '/help/' in path:
            parts = path.split('/help/')
            if len(parts) > 1:
                segment = parts[1].split('/')[0]
                return segment
        
        return ''
    
    def extract_plain_text(self, soup: BeautifulSoup) -> str:
        """Extract plain text from HTML, removing ALL tags and keeping only raw text."""
        # Создаем копию для работы
        soup_copy = BeautifulSoup(str(soup), 'lxml')
        
        # Удаляем все элементы, которые не нужны для основного контента
        elements_to_remove = [
            'script', 'style', 'nav', 'header', 'footer',
            '.navbar', '.menu', '.navigation', '.sidebar',
            '.header', '.footer', '.cookie', '.modal', '.popup',
            '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]',
            'noscript', 'iframe', 'embed', 'object'
        ]
        
        for selector in elements_to_remove:
            for element in soup_copy.select(selector):
                element.decompose()
        
        # Пытаемся найти основной контент
        main_content = None
        content_selectors = [
            'main', 'article', '.content', '.main-content',
            '#content', '.article-content', '[role="main"]',
            '.help-content', '.documentation-content'
        ]
        
        for selector in content_selectors:
            main_content = soup_copy.select_one(selector)
            if main_content:
                break
        
        # Если не нашли основной контент, используем body
        if not main_content:
            main_content = soup_copy.find('body') or soup_copy
        
        # Извлекаем ТОЛЬКО текст, удаляя все теги
        # Используем get_text() который автоматически удаляет все HTML теги
        text = main_content.get_text(separator='\n', strip=True)
        
        # Дополнительная очистка:
        # 1. Убираем множественные переносы строк
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 2. Убираем множественные пробелы и табы
        text = re.sub(r'[ \t]+', ' ', text)
        # 3. Убираем пробелы в начале и конце строк
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)  # Убираем пустые строки
        # 4. Убираем HTML entities если остались
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        # 5. Убеждаемся в правильной кодировке
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return text.strip()
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all links from the page."""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Normalize to absolute URL
            absolute_url = urljoin(current_url, href)
            links.append(absolute_url)
        return links


from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List, Dict, Optional, Union
import re
from datetime import datetime
from app.normalizer.extractors import SpecialBlockExtractor


class Normalizer:
    """Normalizer for cleaning and structuring HTML content."""
    
    # Common boilerplate selectors (ELMA365 specific patterns)
    BOILERPLATE_SELECTORS = [
        'nav',  # Navigation
        'header',  # Header
        'footer',  # Footer
        '.navbar',  # Navbar class
        '.footer',  # Footer class
        '.header',  # Header class
        '.sidebar',  # Sidebar
        '.menu',  # Menu
        '.navigation',  # Navigation
        'script',  # Scripts
        'style',  # Styles
        '.cookie',  # Cookie notices
        '.modal',  # Modals
        '.popup',  # Popups
    ]
    
    def __init__(self):
        self.extractor = SpecialBlockExtractor()
    
    def normalize(self, html: str, title: Optional[str] = None, breadcrumbs: Optional[List[str]] = None) -> Dict:
        """
        Normalize HTML content into structured blocks.
        
        Returns:
            {
                "blocks": [...],
                "metadata": {...}
            }
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove boilerplate
        cleaned_soup = self.remove_boilerplate(soup)
        
        # Parse into structured blocks
        blocks = self.parse_blocks(cleaned_soup)
        
        # Extract special blocks
        special_blocks = self.extractor.extract_special_blocks(cleaned_soup)
        
        # Integrate special blocks
        blocks = self.extractor.integrate_special_blocks(blocks, special_blocks)
        
        # Build metadata
        metadata = {
            'title': title or self._extract_title(cleaned_soup),
            'breadcrumbs': breadcrumbs or [],
            'extracted_at': datetime.now().isoformat(),
            'special_blocks_count': len(special_blocks)
        }
        
        return {
            'blocks': blocks,
            'metadata': metadata
        }
    
    def remove_boilerplate(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove boilerplate elements from HTML."""
        # Remove by selectors
        for selector in self.BOILERPLATE_SELECTORS:
            for element in soup.select(selector):
                element.decompose()
        
        # Remove common ELMA365 specific elements
        # Footer text patterns
        for element in soup.find_all(string=re.compile(r'©.*ELMA365', re.I)):
            parent = element.parent
            if parent:
                parent.decompose()
        
        # Remove empty elements
        for element in soup.find_all():
            if not element.get_text(strip=True) and not element.find(['img', 'svg']):
                element.decompose()
        
        return soup
    
    def parse_blocks(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse HTML into structured blocks."""
        blocks = []
        
        # Find main content area
        main_content = self._find_main_content(soup)
        if not main_content:
            main_content = soup.find('body') or soup
        
        # Process elements in order
        for element in main_content.children:
            if isinstance(element, Tag):
                block = self._parse_element(element)
                if block:
                    if isinstance(block, list):
                        blocks.extend(block)
                    else:
                        blocks.append(block)
        
        return blocks
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find main content area."""
        # Try common content selectors
        selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '#content',
            '.article-content',
            '[role="main"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
        
        return None
    
    def _parse_element(self, element: Tag) -> Optional[Union[Dict, List[Dict]]]:
        """Parse a single element into block(s)."""
        tag_name = element.name.lower()
        
        # Headers
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = element.get_text(strip=True)
            element_id = element.get('id', '')
            return {
                'type': 'header',
                'level': level,
                'text': text,
                'id': element_id
            }
        
        # Paragraphs
        elif tag_name == 'p':
            text = element.get_text(strip=True)
            if text:
                return {
                    'type': 'paragraph',
                    'text': text
                }
        
        # Code blocks
        elif tag_name in ['pre', 'code']:
            if tag_name == 'pre':
                code_element = element.find('code')
                if code_element:
                    code = code_element.get_text()
                    language = self._detect_language(code_element)
                else:
                    code = element.get_text()
                    language = None
            else:
                code = element.get_text()
                language = self._detect_language(element)
            
            return {
                'type': 'code_block',
                'language': language,
                'code': code
            }
        
        # Lists
        elif tag_name in ['ul', 'ol']:
            items = []
            for li in element.find_all('li', recursive=False):
                item_text = li.get_text(strip=True)
                if item_text:
                    items.append(item_text)
            
            if items:
                return {
                    'type': 'list',
                    'ordered': tag_name == 'ol',
                    'items': items
                }
        
        # Images
        elif tag_name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', '')
            return {
                'type': 'image',
                'src': src,
                'alt': alt
            }
        
        # Divs and sections - process children
        elif tag_name in ['div', 'section', 'article', 'main']:
            # Check if it has meaningful content
            text = element.get_text(strip=True)
            if text:
                # Process children recursively
                child_blocks = []
                for child in element.children:
                    if isinstance(child, Tag):
                        child_block = self._parse_element(child)
                        if child_block:
                            if isinstance(child_block, list):
                                child_blocks.extend(child_block)
                            else:
                                child_blocks.append(child_block)
                
                if child_blocks:
                    return child_blocks
        
        return None
    
    def _detect_language(self, code_element: Tag) -> Optional[str]:
        """Detect programming language from code element."""
        # Check class for language hint
        class_attr = code_element.get('class', [])
        for cls in class_attr:
            if cls.startswith('language-'):
                return cls.replace('language-', '')
            if cls.startswith('lang-'):
                return cls.replace('lang-', '')
        
        # Check data attributes
        lang = code_element.get('data-lang') or code_element.get('data-language')
        if lang:
            return lang
        
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract title from cleaned soup."""
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        return None


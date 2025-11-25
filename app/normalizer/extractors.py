from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Optional
import re


class SpecialBlockExtractor:
    """Extract special blocks from ELMA365 documentation."""
    
    # Patterns for special blocks
    SPECIAL_BLOCK_PATTERNS = {
        'В этой статье': [
            r'в этой статье',
            r'in this article',
            r'содержание',
            r'оглавление',
            r'table of contents'
        ],
        'Пример': [
            r'пример',
            r'example',
            r'примеры',
            r'examples'
        ],
        'API': [
            r'api',
            r'endpoint',
            r'endpoints',
            r'метод',
            r'методы'
        ]
    }
    
    def __init__(self):
        pass
    
    def extract_special_blocks(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all special blocks from HTML."""
        special_blocks = []
        
        for block_type, patterns in self.SPECIAL_BLOCK_PATTERNS.items():
            blocks = self._extract_blocks_by_type(soup, block_type, patterns)
            special_blocks.extend(blocks)
        
        return special_blocks
    
    def _extract_blocks_by_type(self, soup: BeautifulSoup, block_type: str, patterns: List[str]) -> List[Dict]:
        """Extract blocks of a specific type."""
        blocks = []
        
        # Compile regex patterns
        compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        
        # Search for headings or text that match patterns
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section']):
            text = element.get_text(strip=True)
            
            # Check if text matches any pattern
            for pattern in compiled_patterns:
                if pattern.search(text):
                    # Found a potential special block
                    block = self._extract_block_content(element, block_type)
                    if block:
                        blocks.append(block)
                    break
        
        return blocks
    
    def _extract_block_content(self, element: Tag, block_type: str) -> Optional[Dict]:
        """Extract content of a special block starting from the given element."""
        # Get the heading or trigger text
        heading_text = element.get_text(strip=True)
        
        # Find the content that follows this element
        content_elements = []
        current = element.next_sibling
        
        # Collect content until next heading of same or higher level
        if element.name and element.name.startswith('h'):
            heading_level = int(element.name[1])
        else:
            heading_level = 6  # Default to lowest level
        
        while current:
            if isinstance(current, Tag):
                # Stop at next heading of same or higher level
                if current.name and current.name.startswith('h'):
                    next_level = int(current.name[1])
                    if next_level <= heading_level:
                        break
                
                # Collect content
                text = current.get_text(strip=True)
                if text:
                    content_elements.append({
                        'tag': current.name,
                        'text': text,
                        'html': str(current)
                    })
            
            current = current.next_sibling
        
        # Also check parent's siblings if element is a heading
        if not content_elements and element.name and element.name.startswith('h'):
            # Look for next sibling element
            parent = element.parent
            if parent:
                found_element = False
                for sibling in parent.children:
                    if sibling == element:
                        found_element = True
                        continue
                    if found_element and isinstance(sibling, Tag):
                        text = sibling.get_text(strip=True)
                        if text:
                            content_elements.append({
                                'tag': sibling.name,
                                'text': text,
                                'html': str(sibling)
                            })
                            # Stop at next heading
                            if sibling.name and sibling.name.startswith('h'):
                                break
        
        if content_elements:
            return {
                'type': 'special_block',
                'kind': block_type,
                'heading': heading_text,
                'content': content_elements
            }
        
        return None
    
    def extract_table_of_contents(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract table of contents (В этой статье)."""
        toc_blocks = self._extract_blocks_by_type(
            soup,
            'В этой статье',
            self.SPECIAL_BLOCK_PATTERNS['В этой статье']
        )
        
        if toc_blocks:
            # Return the first one, or merge them
            return toc_blocks[0]
        
        return None
    
    def extract_examples(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract example blocks (Пример)."""
        return self._extract_blocks_by_type(
            soup,
            'Пример',
            self.SPECIAL_BLOCK_PATTERNS['Пример']
        )
    
    def extract_api_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract API documentation sections."""
        return self._extract_blocks_by_type(
            soup,
            'API',
            self.SPECIAL_BLOCK_PATTERNS['API']
        )
    
    def integrate_special_blocks(self, blocks: List[Dict], special_blocks: List[Dict]) -> List[Dict]:
        """
        Integrate special blocks into the main blocks list.
        Marks blocks that are part of special sections.
        """
        # Create a map of special block positions
        # For now, we'll append special blocks at the end
        # In a more sophisticated implementation, we could insert them at their original positions
        
        result = blocks.copy()
        
        # Add special blocks as separate entries
        for special_block in special_blocks:
            result.append(special_block)
        
        return result


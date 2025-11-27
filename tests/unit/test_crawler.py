import pytest
from app.crawler import Crawler, HTMLParser
from app.utils import extract_doc_id, is_valid_help_url, normalize_url
from app.config import settings


def test_extract_doc_id_from_url():
    """Test doc_id extraction from URLs."""
    # Test with filename pattern
    url1 = 'https://elma365.com/ru/help/platform/how_to_bind_app_to_proccess.html'
    doc_id1 = extract_doc_id(url1)
    assert doc_id1 == 'how_to_bind_app_to_proccess'
    
    # Test with numeric ID
    url2 = 'https://elma365.com/ru/help/platform/360008121732.html'
    doc_id2 = extract_doc_id(url2)
    assert doc_id2 == '360008121732'
    
    # Test with invalid URL (should generate UUID)
    url3 = 'https://elma365.com/invalid'
    doc_id3 = extract_doc_id(url3)
    assert doc_id3  # Should have some value


def test_is_valid_help_url():
    """Test URL validation."""
    base_url = settings.CRAWL_BASE_URL
    
    # Valid URLs
    assert is_valid_help_url('https://elma365.com/help/page.html', base_url)
    assert is_valid_help_url('/help/page.html', base_url)
    
    # Invalid URLs
    assert not is_valid_help_url('https://example.com/page.html', base_url)
    assert not is_valid_help_url('https://elma365.com/other/page.html', base_url)


def test_normalize_url():
    """Test URL normalization."""
    base_url = 'https://elma365.com'
    
    # Absolute URL
    assert normalize_url('https://elma365.com/page.html', base_url) == 'https://elma365.com/page.html'
    
    # Relative URL
    assert normalize_url('/help/page.html', base_url) == 'https://elma365.com/help/page.html'
    
    # Relative URL with base
    assert normalize_url('help/page.html', base_url) == 'https://elma365.com/help/page.html'


def test_html_parser_extract_title():
    """Test HTML parser title extraction."""
    parser = HTMLParser('https://elma365.com')
    
    html1 = '<html><head><title>Page Title</title></head><body></body></html>'
    result1 = parser.parse(html1, 'https://elma365.com/page.html')
    assert result1['title'] == 'Page Title'
    
    html2 = '<html><body><h1>Main Title</h1></body></html>'
    result2 = parser.parse(html2, 'https://elma365.com/page.html')
    assert result2['title'] == 'Main Title'


def test_html_parser_extract_breadcrumbs():
    """Test HTML parser breadcrumb extraction."""
    parser = HTMLParser('https://elma365.com')
    
    html = '''
    <html>
        <body>
            <nav class="breadcrumb">
                <a href="/">Home</a>
                <a href="/help">Help</a>
                <a href="/help/platform">Platform</a>
            </nav>
        </body>
    </html>
    '''
    
    result = parser.parse(html, 'https://elma365.com/page.html')
    breadcrumbs = result['breadcrumbs']
    
    # Should extract breadcrumbs
    assert len(breadcrumbs) > 0


def test_html_parser_extract_links():
    """Test HTML parser link extraction."""
    parser = HTMLParser('https://elma365.com')
    
    html = '''
    <html>
        <body>
            <a href="/help/page1.html">Link 1</a>
            <a href="/help/page2.html">Link 2</a>
        </body>
    </html>
    '''
    
    result = parser.parse(html, 'https://elma365.com/page.html')
    links = result['links']
    
    assert len(links) == 2
    assert all('elma365.com' in link for link in links)


@pytest.mark.asyncio
async def test_crawler_single_url():
    """Test crawling a single URL."""
    async with Crawler() as crawler:
        url = 'https://elma365.com/ru/help/platform/how_to_bind_app_to_proccess.html'
        result = await crawler.crawl_url(url)
        
        if result:
            assert 'doc_id' in result
            assert 'url' in result
            assert 'title' in result
            assert 'html' in result
            assert 'plain_text' in result


@pytest.mark.asyncio
async def test_crawler_status():
    """Test crawler status reporting."""
    crawler = Crawler()
    status = crawler.get_status()
    
    assert 'is_crawling' in status
    assert 'visited_count' in status
    assert 'queue_size' in status
    assert 'stats' in status


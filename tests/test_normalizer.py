import pytest
from app.normalizer import Normalizer, SpecialBlockExtractor


# Control pages for testing
CONTROL_PAGES = [
    {
        'name': 'how_to_bind_app_to_proccess',
        'url': 'https://elma365.com/ru/help/platform/how_to_bind_app_to_proccess.html',
        'expected_blocks': ['header', 'paragraph', 'list'],
        'expected_special_blocks': ['В этой статье']
    },
    {
        'name': 'numeric_id_page',
        'url': 'https://elma365.com/ru/help/platform/360008121732.html',
        'expected_blocks': ['header', 'paragraph'],
        'expected_special_blocks': []
    },
    # Add more control pages as needed
]


@pytest.fixture
def normalizer():
    return Normalizer()


@pytest.fixture
def extractor():
    return SpecialBlockExtractor()


@pytest.mark.asyncio
async def test_normalizer_removes_boilerplate(normalizer):
    """Test that normalizer removes boilerplate elements."""
    html = """
    <html>
        <head><title>Test</title></head>
        <body>
            <nav>Navigation</nav>
            <header>Header</header>
            <footer>Footer</footer>
            <main>
                <h1>Main Title</h1>
                <p>Main content</p>
            </main>
        </body>
    </html>
    """
    
    result = normalizer.normalize(html)
    
    # Check that boilerplate is removed
    blocks_text = ' '.join([str(b) for b in result['blocks']])
    assert 'Navigation' not in blocks_text
    assert 'Header' not in blocks_text
    assert 'Footer' not in blocks_text
    
    # Check that main content is preserved
    assert any(b.get('text') == 'Main Title' for b in result['blocks'] if b.get('type') == 'header')
    assert any(b.get('text') == 'Main content' for b in result['blocks'] if b.get('type') == 'paragraph')


def test_normalizer_parses_headers(normalizer):
    """Test that normalizer parses headers correctly."""
    html = """
    <html>
        <body>
            <h1>Title 1</h1>
            <h2>Title 2</h2>
            <h3>Title 3</h3>
        </body>
    </html>
    """
    
    result = normalizer.normalize(html)
    headers = [b for b in result['blocks'] if b.get('type') == 'header']
    
    assert len(headers) == 3
    assert headers[0]['level'] == 1
    assert headers[0]['text'] == 'Title 1'
    assert headers[1]['level'] == 2
    assert headers[2]['level'] == 3


def test_normalizer_parses_paragraphs(normalizer):
    """Test that normalizer parses paragraphs correctly."""
    html = """
    <html>
        <body>
            <p>First paragraph</p>
            <p>Second paragraph</p>
        </body>
    </html>
    """
    
    result = normalizer.normalize(html)
    paragraphs = [b for b in result['blocks'] if b.get('type') == 'paragraph']
    
    assert len(paragraphs) == 2
    assert paragraphs[0]['text'] == 'First paragraph'
    assert paragraphs[1]['text'] == 'Second paragraph'


def test_normalizer_parses_code_blocks(normalizer):
    """Test that normalizer parses code blocks correctly."""
    html = """
    <html>
        <body>
            <pre><code>def hello():
    print("Hello")</code></pre>
        </body>
    </html>
    """
    
    result = normalizer.normalize(html)
    code_blocks = [b for b in result['blocks'] if b.get('type') == 'code_block']
    
    assert len(code_blocks) == 1
    assert 'def hello()' in code_blocks[0]['code']
    assert 'print("Hello")' in code_blocks[0]['code']


def test_normalizer_parses_lists(normalizer):
    """Test that normalizer parses lists correctly."""
    html = """
    <html>
        <body>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <ol>
                <li>First</li>
                <li>Second</li>
            </ol>
        </body>
    </html>
    """
    
    result = normalizer.normalize(html)
    lists = [b for b in result['blocks'] if b.get('type') == 'list']
    
    assert len(lists) == 2
    assert lists[0]['ordered'] == False
    assert lists[0]['items'] == ['Item 1', 'Item 2']
    assert lists[1]['ordered'] == True
    assert lists[1]['items'] == ['First', 'Second']


def test_extractor_finds_special_blocks(extractor):
    """Test that special block extractor finds special blocks."""
    html = """
    <html>
        <body>
            <h2>В этой статье</h2>
            <ul>
                <li>Point 1</li>
                <li>Point 2</li>
            </ul>
            <h2>Пример</h2>
            <pre><code>example code</code></pre>
        </body>
    </html>
    """
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    blocks = extractor.extract_special_blocks(soup)
    
    assert len(blocks) >= 2
    block_kinds = [b['kind'] for b in blocks]
    assert 'В этой статье' in block_kinds
    assert 'Пример' in block_kinds


def test_normalizer_integrates_special_blocks(normalizer):
    """Test that normalizer integrates special blocks."""
    html = """
    <html>
        <body>
            <h1>Main Title</h1>
            <h2>В этой статье</h2>
            <ul>
                <li>Item 1</li>
            </ul>
        </body>
    </html>
    """
    
    result = normalizer.normalize(html)
    
    # Check that special blocks are included
    special_blocks = [b for b in result['blocks'] if b.get('type') == 'special_block']
    assert len(special_blocks) > 0
    assert any(b['kind'] == 'В этой статье' for b in special_blocks)


def test_normalizer_metadata(normalizer):
    """Test that normalizer includes proper metadata."""
    html = """
    <html>
        <body>
            <h1>Test Title</h1>
            <p>Content</p>
        </body>
    </html>
    """
    
    breadcrumbs = ['Платформа', 'API']
    result = normalizer.normalize(html, title='Custom Title', breadcrumbs=breadcrumbs)
    
    assert 'metadata' in result
    assert result['metadata']['title'] == 'Custom Title'
    assert result['metadata']['breadcrumbs'] == breadcrumbs
    assert 'extracted_at' in result['metadata']


# Integration test with actual pages (requires network)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_normalizer_with_real_page(normalizer):
    """Test normalizer with a real ELMA365 page."""
    import aiohttp
    
    url = 'https://elma365.com/ru/help/platform/how_to_bind_app_to_proccess.html'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                result = normalizer.normalize(html)
                
                # Verify structure
                assert 'blocks' in result
                assert 'metadata' in result
                assert len(result['blocks']) > 0
                
                # Verify we have headers
                headers = [b for b in result['blocks'] if b.get('type') == 'header']
                assert len(headers) > 0
                
                # Verify special blocks if present
                special_blocks = [b for b in result['blocks'] if b.get('type') == 'special_block']
                # May or may not have special blocks, but if present, should be valid
                for block in special_blocks:
                    assert 'kind' in block
                    assert block['kind'] in ['В этой статье', 'Пример', 'API']


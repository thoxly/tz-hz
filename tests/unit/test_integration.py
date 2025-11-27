"""
Integration tests for full crawl workflow, normalization pipeline, and database storage.
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import Base, Doc, Entity
from app.database import get_db
from app.crawler import Crawler, Storage
from app.normalizer import Normalizer, EntityExtractor
from app.config import settings


# Use in-memory SQLite for testing (or test PostgreSQL if available)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_full_crawl_workflow(test_db):
    """Test full crawl workflow: crawl -> save -> retrieve."""
    # This is a simplified test - in real scenario, you'd mock the HTTP requests
    storage = Storage()
    
    # Create mock document data
    doc_data = {
        'doc_id': 'test_doc_123',
        'url': 'https://elma365.com/ru/help/platform/test.html',
        'title': 'Test Document',
        'breadcrumbs': ['Платформа', 'Test'],
        'section': 'Платформа | [platform]',
        'html': '<html><body><h1>Test</h1><p>Content</p></body></html>',
        'plain_text': 'Test Content',
        'last_crawled': None,
        'links': [],
        'depth': 0
    }
    
    # Save to database
    result = await storage.save_to_db(test_db, doc_data)
    assert result is not None
    assert result.doc_id == 'test_doc_123'
    
    # Retrieve from database
    from sqlalchemy import select
    retrieved = await test_db.execute(
        select(Doc).where(Doc.doc_id == 'test_doc_123')
    )
    doc = retrieved.scalar_one_or_none()
    
    assert doc is not None
    assert doc.title == 'Test Document'
    assert doc.section == 'Платформа | [platform]'
    assert doc.content is not None
    assert 'html' in doc.content


@pytest.mark.asyncio
async def test_normalization_pipeline(test_db):
    """Test normalization pipeline: normalize -> extract entities -> save."""
    # Create a document in database
    doc = Doc(
        doc_id='test_normalize_123',
        url='https://elma365.com/test.html',
        title='Test Document',
        section='Test',
        content={
            'html': '''
            <html>
                <body>
                    <h1>Main Title</h1>
                    <p>First paragraph</p>
                    <h2>В этой статье</h2>
                    <ul>
                        <li>Point 1</li>
                        <li>Point 2</li>
                    </ul>
                    <pre><code>def test():
    pass</code></pre>
                </body>
            </html>
            ''',
            'plain_text': 'Test content',
            'breadcrumbs': ['Test']
        }
    )
    test_db.add(doc)
    await test_db.commit()
    
    # Normalize
    normalizer = Normalizer()
    normalized = normalizer.normalize(
        doc.content['html'],
        title=doc.title,
        breadcrumbs=doc.content.get('breadcrumbs', [])
    )
    
    # Verify normalization
    assert 'blocks' in normalized
    assert 'metadata' in normalized
    assert len(normalized['blocks']) > 0
    
    # Check for expected blocks
    block_types = [b.get('type') for b in normalized['blocks']]
    assert 'header' in block_types
    assert 'paragraph' in block_types
    assert 'list' in block_types
    assert 'code_block' in block_types
    
    # Check for special blocks
    special_blocks = [b for b in normalized['blocks'] if b.get('type') == 'special_block']
    assert len(special_blocks) > 0
    
    # Extract entities
    entity_extractor = EntityExtractor()
    entities = await entity_extractor.extract_and_save_entities(
        test_db,
        doc.doc_id,
        normalized
    )
    
    # Verify entities
    assert len(entities) > 0
    
    # Check entity types
    entity_types = [e.type for e in entities]
    assert 'header' in entity_types
    assert 'code_block' in entity_types
    assert 'special_block' in entity_types
    assert 'list' in entity_types
    
    # Verify entities in database
    from sqlalchemy import select
    retrieved_entities = await test_db.execute(
        select(Entity).where(Entity.doc_id == doc.doc_id)
    )
    db_entities = retrieved_entities.scalars().all()
    assert len(db_entities) == len(entities)


@pytest.mark.asyncio
async def test_database_storage_verification(test_db):
    """Test database storage and retrieval verification."""
    # Create multiple documents
    docs_data = [
        {
            'doc_id': f'test_doc_{i}',
            'url': f'https://elma365.com/test_{i}.html',
            'title': f'Test Document {i}',
            'section': f'Section {i}',
            'html': f'<html><body><h1>Title {i}</h1></body></html>',
            'plain_text': f'Content {i}',
            'last_crawled': None,
            'links': [],
            'depth': 0,
            'breadcrumbs': []
        }
        for i in range(5)
    ]
    
    storage = Storage()
    
    # Save all documents
    for doc_data in docs_data:
        await storage.save_to_db(test_db, doc_data)
    
    await test_db.commit()
    
    # Verify all documents are saved
    from sqlalchemy import select
    result = await test_db.execute(select(Doc))
    all_docs = result.scalars().all()
    
    assert len(all_docs) == 5
    
    # Verify each document
    for i, doc_data in enumerate(docs_data):
        result = await test_db.execute(
            select(Doc).where(Doc.doc_id == doc_data['doc_id'])
        )
        doc = result.scalar_one_or_none()
        assert doc is not None
        assert doc.title == doc_data['title']
        assert doc.section == doc_data['section']


@pytest.mark.asyncio
async def test_json_storage():
    """Test local JSON file storage."""
    import tempfile
    import os
    import json
    from pathlib import Path
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Storage()
        storage.output_dir = Path(tmpdir)
        
        doc_data = {
            'doc_id': 'test_json_123',
            'url': 'https://elma365.com/test.html',
            'title': 'Test Document',
            'breadcrumbs': ['Test'],
            'section': 'Test',
            'html': '<html><body>Test</body></html>',
            'plain_text': 'Test',
            'last_crawled': None,
            'links': [],
            'depth': 0
        }
        
        # Save to JSON
        json_path = storage.save_to_json(doc_data)
        
        assert json_path is not None
        assert os.path.exists(json_path)
        
        # Verify JSON content
        with open(json_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['doc_id'] == doc_data['doc_id']
        assert saved_data['url'] == doc_data['url']
        assert saved_data['title'] == doc_data['title']


@pytest.mark.asyncio
async def test_end_to_end_workflow(test_db):
    """Test end-to-end workflow: crawl -> normalize -> extract entities."""
    # This is a simplified end-to-end test
    # In a real scenario, you'd use mocked HTTP responses
    
    # Step 1: Create document (simulating crawl)
    doc_data = {
        'doc_id': 'e2e_test_123',
        'url': 'https://elma365.com/ru/help/platform/e2e_test.html',
        'title': 'E2E Test Document',
        'breadcrumbs': ['Платформа', 'E2E'],
        'section': 'Платформа | [platform]',
        'html': '''
        <html>
            <body>
                <h1>E2E Test</h1>
                <p>This is a test document.</p>
                <h2>В этой статье</h2>
                <ul>
                    <li>Introduction</li>
                    <li>Usage</li>
                </ul>
                <h2>Пример</h2>
                <pre><code>def example():
    return "test"</code></pre>
            </body>
        </html>
        ''',
        'plain_text': 'E2E Test This is a test document.',
        'last_crawled': None,
        'links': [],
        'depth': 0
    }
    
    # Step 2: Save to database
    storage = Storage()
    saved_doc = await storage.save_to_db(test_db, doc_data)
    assert saved_doc is not None
    
    # Step 3: Normalize
    normalizer = Normalizer()
    normalized = normalizer.normalize(
        doc_data['html'],
        title=doc_data['title'],
        breadcrumbs=doc_data['breadcrumbs']
    )
    
    # Step 4: Update document with normalized content
    saved_doc.content = normalized
    await test_db.commit()
    
    # Step 5: Extract entities
    entity_extractor = EntityExtractor()
    entities = await entity_extractor.extract_and_save_entities(
        test_db,
        doc_data['doc_id'],
        normalized
    )
    
    # Step 6: Verify everything
    assert len(normalized['blocks']) > 0
    assert len(entities) > 0
    
    # Verify entities in database
    from sqlalchemy import select
    result = await test_db.execute(
        select(Entity).where(Entity.doc_id == doc_data['doc_id'])
    )
    db_entities = result.scalars().all()
    assert len(db_entities) == len(entities)
    
    # Verify special blocks were extracted
    special_entities = [e for e in db_entities if e.type == 'special_block']
    assert len(special_entities) > 0


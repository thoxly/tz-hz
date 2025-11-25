# ELMA365 Documentation Crawler

FastAPI application for crawling, normalizing, and storing ELMA365 documentation pages.

## Features

- **Recursive Web Crawler**: Automatically discovers and crawls documentation pages from `/help/` root
- **Manual URL Addition**: Support for manually adding URLs to crawl queue
- **HTML Normalization**: Removes boilerplate and structures content into blocks (headers, paragraphs, code, lists)
- **Special Block Extraction**: Extracts special sections like "В этой статье", "Пример", "API"
- **Entity Extraction**: Extracts semantic elements (headers, code blocks, special blocks, lists) to entities table
- **Dual Storage**: Saves to PostgreSQL (JSONB) and local JSON files
- **RESTful API**: FastAPI endpoints for all operations

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── utils.py             # Utility functions (doc_id extraction, etc.)
│   ├── crawler/             # Crawler module
│   │   ├── crawler.py       # Main crawler logic
│   │   ├── parser.py        # HTML parsing with BeautifulSoup
│   │   └── storage.py       # Storage handler (DB + JSON)
│   ├── normalizer/          # Normalizer module
│   │   ├── normalizer.py    # Main normalization logic
│   │   ├── extractors.py    # Special block extractors
│   │   └── entity_extractor.py  # Entity extraction
│   ├── database/            # Database layer
│   │   ├── models.py         # SQLAlchemy models
│   │   └── database.py      # Database connection & session
│   └── api/                 # API endpoints
│       └── routes.py        # FastAPI routes
├── tests/                   # Test suite
│   ├── test_crawler.py      # Crawler tests
│   ├── test_normalizer.py   # Normalizer tests
│   ├── test_control_pages.py  # Control page tests
│   └── test_integration.py   # Integration tests
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd elma_tz_hz
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database URL and settings
```

5. Set up database:
```bash
# Make sure PostgreSQL is running
# Update DATABASE_URL in .env

# Run migrations
alembic upgrade head
```

## Configuration

Environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `CRAWL_BASE_URL`: Base URL for crawling (default: https://elma365.com)
- `CRAWL_MAX_DEPTH`: Maximum crawl depth (default: 10)
- `CRAWL_DELAY`: Delay between requests in seconds (default: 1.0)
- `CRAWL_MAX_CONCURRENT`: Maximum concurrent requests (default: 5)
- `OUTPUT_DIR`: Local JSON output directory (default: data/crawled)
- `LOG_LEVEL`: Logging level (default: INFO)

## Usage

### Start the API server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Crawling

- `POST /api/crawl/start` - Start recursive crawl from `/help/`
  ```json
  {
    "start_url": "https://elma365.com/ru/help/"  // optional
  }
  ```

- `POST /api/crawl/url` - Manually add URL to crawl queue
  ```json
  {
    "url": "https://elma365.com/ru/help/platform/page.html"
  }
  ```

- `GET /api/crawl/status` - Get crawling status

#### Normalization

- `POST /api/normalize/{doc_id}` - Normalize a specific document
- `POST /api/normalize/all` - Normalize all crawled documents

#### Data Retrieval

- `GET /api/docs` - List all documents (with pagination: `?skip=0&limit=100`)
- `GET /api/docs/{doc_id}` - Get document details
- `GET /api/entities/{doc_id}` - Get entities for a document

### Example Workflow

1. Start crawling:
```bash
curl -X POST "http://localhost:8000/api/crawl/start" \
  -H "Content-Type: application/json" \
  -d '{}'
```

2. Check status:
```bash
curl "http://localhost:8000/api/crawl/status"
```

3. Normalize all documents:
```bash
curl -X POST "http://localhost:8000/api/normalize/all"
```

4. Get documents:
```bash
curl "http://localhost:8000/api/docs"
```

## Database Schema

### docs table
- `id` (PK)
- `doc_id` (unique) - URL-based ID with UUID fallback
- `url` (unique)
- `title`
- `section` - Combined breadcrumbs + URL segment
- `content` (JSONB) - Normalized structured blocks
- `created_at`
- `last_crawled`

### entities table
- `id` (PK)
- `doc_id` (FK to docs.doc_id)
- `type` - Entity type (header, code_block, list, special_block, etc.)
- `data` (JSONB) - Entity-specific data
- `created_at`

### specifications table
- `id` (PK)
- `source_text`
- `analyst_json` (JSONB)
- `architect_json` (JSONB)
- `spec_markdown`
- `created_at`

## Testing

Run tests:

```bash
# All tests
pytest

# Unit tests only
pytest -m "not integration"

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/test_normalizer.py
```

## Normalized Content Structure

The normalizer produces structured JSON:

```json
{
  "blocks": [
    {
      "type": "header",
      "level": 1,
      "text": "Main Title",
      "id": "main-title"
    },
    {
      "type": "paragraph",
      "text": "Content text..."
    },
    {
      "type": "code_block",
      "language": "python",
      "code": "def example():\n    pass"
    },
    {
      "type": "list",
      "ordered": false,
      "items": ["Item 1", "Item 2"]
    },
    {
      "type": "special_block",
      "kind": "В этой статье",
      "heading": "В этой статье",
      "content": [...]
    }
  ],
  "metadata": {
    "title": "Document Title",
    "breadcrumbs": ["Платформа", "API"],
    "extracted_at": "2025-01-27T10:00:00",
    "special_blocks_count": 1
  }
}
```

## Development

### Running Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## License

[Your License Here]


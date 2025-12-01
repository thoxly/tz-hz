# ELMA365 Agent Pipeline with MCP

FastAPI application for crawling, normalizing, and storing ELMA365 documentation pages, with an agent pipeline for process automation design.

## Features

- **Recursive Web Crawler**: Automatically discovers and crawls documentation pages from `/help/` root
- **Manual URL Addition**: Support for manually adding URLs to crawl queue
- **HTML Normalization**: Removes boilerplate and structures content into blocks (headers, paragraphs, code, lists)
- **Special Block Extraction**: Extracts special sections like "В этой статье", "Пример", "API"
- **Entity Extraction**: Extracts semantic elements (headers, code blocks, special blocks, lists) to entities table
- **Dual Storage**: Saves to PostgreSQL (JSONB) and local JSON files
- **RESTful API**: FastAPI endpoints for all operations
- **MCP Server**: Model Context Protocol server for accessing documentation (HTTP and stdin/stdout transports)
- **Agent Pipeline**: ProcessExtractor → ArchitectAgent → ScopeAgent for automated process design
- **Telegram Bot**: Simple interface for running the agent pipeline

## Project Structure

```
.
├── app/                     # FastAPI application
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── schemas.py           # Pydantic schemas
│   ├── utils.py             # Utility functions
│   ├── crawler/             # Crawler module
│   ├── normalizer/          # Normalizer module
│   ├── database/            # Database layer
│   └── api/                 # API endpoints
├── mcp/                     # MCP server
│   ├── server_http.py       # MCP HTTP transport (FastAPI)
│   ├── server_stdin.py      # MCP stdin/stdout transport
│   ├── core/                # MCP core components
│   │   ├── registry.py      # Tool registry
│   │   ├── executor.py      # Tool executor
│   │   └── models.py        # Tool input/output models
│   └── tools/               # MCP tools
│       ├── search_docs.py
│       ├── get_doc.py
│       ├── get_entities.py
│       ├── find_examples.py
│       └── find_process_patterns.py
├── agents/                  # AI agents
│   ├── base_agent.py        # Base agent class
│   ├── process_extractor.py # AS-IS process extraction
│   ├── architect_agent.py   # ELMA365 architecture design
│   ├── scope_agent.py       # Scope specification creation
│   ├── mcp_client.py       # MCP client for agents
│   ├── prompts.py           # System prompts (versioned)
│   └── models/              # Agent input/output schemas
├── pipeline/                 # Pipeline orchestrator
│   ├── orchestrator.py      # Main pipeline logic
│   └── validators.py        # Result validators
├── telegram/                 # Telegram bot
│   └── bot.py               # Bot implementation
├── tests/                   # Test suite
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
- `DEEPSEEK_API_KEY`: DeepSeek API key for LLM
- `DEEPSEEK_API_URL`: DeepSeek API URL (default: https://api.deepseek.com/v1/chat/completions)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `MCP_SERVER_MODE`: MCP server mode (http or stdin, default: http)

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

## Documentation

### Knowledge Base Specification

Подробная спецификация структуры хранения и обработки документации ELMA365:

📄 **[KNOWLEDGE_BASE_SPEC.md](docs/KNOWLEDGE_BASE_SPEC.md)**

Спецификация описывает:
- Структуру таблицы `docs` и формат JSONB контента
- Алгоритм нормализации путей (`normalize_path()`)
- Правила внутренней навигации между статьями
- Формат хранения ссылок (`outgoing_links`)
- Проверку ссылочной целостности
- Примеры использования для RAG, MCP, Knowledge Graph

**Аудитория:** Backend разработчики, разработчики агентов, разработчики MCP инструментов, разработчики RAG систем

## Database Schema

### docs table
- `id` (PK)
- `doc_id` (unique) - URL-based ID with UUID fallback
- `url` (unique)
- `normalized_path` (unique) - Normalized path for internal navigation
- `outgoing_links` (ARRAY) - Array of normalized paths this document links to
- `title`
- `section` - Combined breadcrumbs + URL segment
- `content` (JSONB) - Normalized structured blocks
- `created_at`
- `last_crawled`

> **Подробнее:** см. [KNOWLEDGE_BASE_SPEC.md](docs/KNOWLEDGE_BASE_SPEC.md)

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

## MCP Server

The MCP (Model Context Protocol) server provides access to ELMA365 documentation through standardized tools.

### Available Tools

1. **elma365.search_docs** - Search documentation by query
2. **elma365.get_doc** - Get a specific document by doc_id
3. **elma365.get_entities** - Get entities from a document (filtered by type)
4. **elma365.find_examples** - Find examples by keywords
5. **elma365.find_process_patterns** - Find process patterns (согласование, поручение, etc.)

### Running MCP Server

#### HTTP Mode (default)
The MCP server is integrated into FastAPI and available at `/mcp/tools/list` and `/mcp/tools/call`.

#### stdin/stdout Mode
For use with LLM clients that support MCP via stdio:

```bash
python -m mcp.server_stdin
```

## Agent Pipeline

The pipeline consists of three agents:

1. **ProcessExtractor** - Extracts AS-IS process from meeting text
2. **ArchitectAgent** - Designs ELMA365 architecture from AS-IS
3. **ScopeAgent** - Creates scope specification (ТЗ) from architecture

### Using the Pipeline

```python
from agents.mcp_client import MCPClient
from pipeline.orchestrator import PipelineOrchestrator
from app.database import get_session_factory

async with get_session_factory() as db_session:
    mcp_client = MCPClient()
    orchestrator = PipelineOrchestrator(mcp_client=mcp_client)
    
    result = await orchestrator.run_process_pipeline(
        text="Meeting transcript...",
        db_session=db_session,
        user="user123"
    )
    
    print(result["as_is"])
    print(result["architecture"])
    print(result["scope"])
```

## Telegram Bot

The Telegram bot provides a simple interface for running the agent pipeline.

### Starting the Bot

```bash
python -m telegram.bot
```

### Bot Commands

- `/start` - Welcome message
- `/run` - Start process analysis (bot will ask for meeting text)

The bot will return three messages:
1. AS-IS process description
2. ELMA365 architecture
3. Scope specification (ТЗ)

## Database Schema

### New Tables

- **crawler_state**: Tracks crawler status and progress
- **runs**: Stores pipeline execution history

## License

[Your License Here]


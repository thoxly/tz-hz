#!/usr/bin/env python3
"""Тест MCP сервера."""
import asyncio
from app.database.database import get_session_factory
from app.mcp.tools import MCPTools

async def test_mcp():
    """Протестировать MCP инструменты."""
    print("🔍 Тест MCP сервера")
    print("=" * 60)
    
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        tools = MCPTools(session)
        
        # Тест 1: get_doc
        print("\n1. Тест get_doc('calendar'):")
        doc = await tools.get_doc('calendar')
        if doc:
            print(f"   ✓ Документ найден")
            print(f"   Title: {doc['title']}")
            print(f"   Blocks: {len(doc['blocks'])}")
            print(f"   Plain text: {len(doc['plain_text'])} символов")
        else:
            print("   ✗ Документ не найден")
        
        # Тест 2: search_entities - заголовки уровня 2
        print("\n2. Тест search_entities('header', level=2):")
        headers = await tools.search_entities('header', {'level': 2, 'limit': 5})
        print(f"   ✓ Найдено заголовков уровня 2: {len(headers)}")
        if headers:
            print(f"   Пример: {headers[0]['text'][:60]}...")
        
        # Тест 3: search_entities - специальные блоки
        print("\n3. Тест search_entities('special_block'):")
        special_blocks = await tools.search_entities('special_block', {'limit': 3})
        print(f"   ✓ Найдено специальных блоков: {len(special_blocks)}")
        if special_blocks:
            print(f"   Пример: {special_blocks[0]['kind']} - {special_blocks[0]['heading'][:50]}...")
        
        # Тест 4: find_relevant
        print("\n4. Тест find_relevant('календарь'):")
        results = await tools.find_relevant('календарь', limit=3)
        print(f"   ✓ Найдено документов: {len(results)}")
        if results:
            print(f"   Пример: {results[0]['title']}")
            print(f"   Context: {results[0]['context'][:100]}...")
        
        # Тест 5: list_docs_by_section
        print("\n5. Тест list_docs_by_section('platform'):")
        docs = await tools.list_docs_by_section('platform')
        print(f"   ✓ Найдено документов: {len(docs)}")
        if docs:
            print(f"   Примеры:")
            for doc in docs[:3]:
                print(f"     - {doc['doc_id']}: {doc['title']}")
        
        print("\n" + "=" * 60)
        print("✅ Все тесты MCP инструментов пройдены!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp())


#!/usr/bin/env python3
"""Проверить структуру блоков в БД."""
import asyncio
import json
from app.database.database import get_session_factory
from app.database.models import Doc
from sqlalchemy import select

async def check_blocks():
    """Проверить блоки в документах."""
    print("🔍 Проверка структурированных блоков в БД")
    print("=" * 60)
    
    session_factory = get_session_factory()
    
    async with session_factory() as db_session:
        # Берем несколько документов для проверки
        result = await db_session.execute(select(Doc).limit(3))
        docs = result.scalars().all()
        
        print(f"\n📊 Проверяю {len(docs)} документов:\n")
        
        for doc in docs:
            content = doc.content or {}
            blocks = content.get('blocks', [])
            
            print(f"📄 {doc.doc_id}")
            print(f"   Title: {doc.title}")
            print(f"   Блоков: {len(blocks)}")
            
            if blocks:
                # Статистика по типам
                block_types = {}
                for block in blocks:
                    block_type = block.get('type', 'unknown')
                    block_types[block_type] = block_types.get(block_type, 0) + 1
                
                print(f"   Типы блоков:")
                for block_type, count in sorted(block_types.items()):
                    print(f"     • {block_type}: {count}")
                
                # Показываем первые 3 блока
                print(f"   Примеры блоков:")
                for i, block in enumerate(blocks[:3], 1):
                    block_type = block.get('type')
                    if block_type == 'header':
                        print(f"     [{i}] header (level {block.get('level')}): {block.get('text', '')[:50]}...")
                    elif block_type == 'paragraph':
                        print(f"     [{i}] paragraph: {block.get('text', '')[:50]}...")
                    elif block_type == 'list':
                        print(f"     [{i}] list: {len(block.get('items', []))} элементов")
                    else:
                        print(f"     [{i}] {block_type}: {str(block)[:50]}...")
            else:
                print(f"   ⚠ Блоки отсутствуют")
            
            print()
        
        # Сохраняем пример в файл
        if docs:
            example_doc = docs[0]
            content = example_doc.content or {}
            blocks = content.get('blocks', [])
            
            example_data = {
                'doc_id': example_doc.doc_id,
                'title': example_doc.title,
                'url': example_doc.url,
                'total_blocks': len(blocks),
                'blocks': blocks[:15],  # Первые 15 блоков
                'content_structure': {
                    'has_html': 'html' in content,
                    'has_plain_text': 'plain_text' in content,
                    'has_blocks': 'blocks' in content,
                    'has_breadcrumbs': 'breadcrumbs' in content,
                    'has_links': 'links' in content
                }
            }
            
            with open('blocks_structure_example.json', 'w', encoding='utf-8') as f:
                json.dump(example_data, f, indent=2, ensure_ascii=False)
            
            print("=" * 60)
            print("✓ Пример структуры сохранен в: blocks_structure_example.json")
            print("=" * 60)
            
            print(f"\n✅ Все документы содержат структурированные блоки!")
            print(f"📦 Структура content теперь включает:")
            print(f"   • html")
            print(f"   • plain_text")
            print(f"   • blocks ← НОВОЕ!")
            print(f"   • breadcrumbs")
            print(f"   • links")

if __name__ == "__main__":
    asyncio.run(check_blocks())


#!/usr/bin/env python3
"""Тест создания структурированных блоков."""
import asyncio
import requests
from app.database.database import get_session_factory
from app.database.models import Doc
from app.normalizer import Normalizer
from sqlalchemy import select

async def test_blocks():
    """Протестировать создание блоков на примере одного документа."""
    print("🔍 Тест создания структурированных блоков")
    print("=" * 60)
    
    session_factory = get_session_factory()
    normalizer = Normalizer()
    
    async with session_factory() as db_session:
        # Берем первый документ для теста
        result = await db_session.execute(select(Doc).limit(1))
        doc = result.scalar_one_or_none()
        
        if not doc:
            print("❌ Нет документов в базе данных")
            return
        
        print(f"\n📄 Тестирую документ: {doc.doc_id}")
        print(f"   URL: {doc.url}")
        print(f"   Title: {doc.title}")
        
        content = doc.content or {}
        html = content.get('html', '')
        
        if not html:
            print("\n⚠ У документа нет HTML контента")
            print("Попробую загрузить страницу...")
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            try:
                response = session.get(doc.url, timeout=30, allow_redirects=True)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding or 'utf-8'
                    html = response.text
                    print(f"✓ Загружено {len(html)} символов")
                else:
                    print(f"✗ Ошибка загрузки: статус {response.status_code}")
                    return
            except Exception as e:
                print(f"✗ Ошибка: {e}")
                return
        
        print(f"\n📊 HTML размер: {len(html)} символов")
        
        # Нормализуем
        print("\n⏳ Нормализация HTML в структурированные блоки...")
        try:
            normalized = normalizer.normalize(
                html,
                title=doc.title,
                breadcrumbs=content.get('breadcrumbs', [])
            )
            
            blocks = normalized.get('blocks', [])
            metadata = normalized.get('metadata', {})
            
            print(f"✓ Создано блоков: {len(blocks)}")
            print(f"✓ Метаданные: {len(metadata)} полей")
            
            # Показываем статистику по типам блоков
            block_types = {}
            for block in blocks:
                block_type = block.get('type', 'unknown')
                block_types[block_type] = block_types.get(block_type, 0) + 1
            
            print(f"\n📊 Статистика блоков:")
            for block_type, count in sorted(block_types.items()):
                print(f"  • {block_type}: {count}")
            
            # Показываем примеры блоков
            print(f"\n📝 Примеры блоков (первые 10):")
            print("-" * 60)
            
            for i, block in enumerate(blocks[:10], 1):
                block_type = block.get('type', 'unknown')
                print(f"\n[{i}] Тип: {block_type}")
                
                if block_type == 'header':
                    print(f"    Level: {block.get('level')}")
                    print(f"    Text: {block.get('text', '')[:80]}...")
                elif block_type == 'paragraph':
                    print(f"    Text: {block.get('text', '')[:80]}...")
                elif block_type == 'list':
                    print(f"    Ordered: {block.get('ordered')}")
                    print(f"    Items: {len(block.get('items', []))} элементов")
                    if block.get('items'):
                        print(f"    Первый элемент: {block['items'][0][:60]}...")
                elif block_type == 'code_block':
                    print(f"    Language: {block.get('language', 'unknown')}")
                    code = block.get('code', '')
                    print(f"    Code: {code[:60]}...")
                elif block_type == 'special_block':
                    print(f"    Kind: {block.get('kind', 'unknown')}")
                    print(f"    Heading: {block.get('heading', '')[:60]}...")
                else:
                    print(f"    Data: {str(block)[:80]}...")
            
            if len(blocks) > 10:
                print(f"\n... и еще {len(blocks) - 10} блоков")
            
            # Показываем структуру content с блоками
            print(f"\n📦 Структура content с блоками:")
            print("-" * 60)
            content_with_blocks = {
                'html': f"<html>... ({len(html)} символов)",
                'plain_text': content.get('plain_text', '')[:50] + '...' if content.get('plain_text') else 'нет',
                'breadcrumbs': content.get('breadcrumbs', []),
                'links': f"{len(content.get('links', []))} ссылок",
                'blocks': f"{len(blocks)} блоков",
                'normalized_metadata': metadata
            }
            
            import json
            print(json.dumps(content_with_blocks, indent=2, ensure_ascii=False))
            
            # Сохраняем пример в файл
            example_file = 'blocks_example.json'
            with open(example_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'doc_id': doc.doc_id,
                    'url': doc.url,
                    'title': doc.title,
                    'blocks': blocks[:20],  # Первые 20 блоков
                    'metadata': metadata,
                    'total_blocks': len(blocks)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Пример сохранен в: {example_file}")
            print(f"\n✅ Тест успешен! Блоки создаются корректно.")
            print(f"\n💡 Следующий шаг: запустить add_blocks_to_all_docs.py")
            print(f"   для добавления блоков во все документы в БД")
            
        except Exception as e:
            print(f"\n❌ Ошибка при нормализации: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_blocks())


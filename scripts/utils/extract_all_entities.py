#!/usr/bin/env python3
"""Извлечь сущности из всех документов и сохранить в таблицу entities."""
import asyncio
from app.database.database import get_session_factory
from app.database.models import Doc
from app.normalizer import EntityExtractor
from sqlalchemy import select

async def extract_all_entities():
    """Извлечь сущности из всех документов."""
    print("🔄 Извлечение сущностей из всех документов...")
    print("=" * 60)
    
    session_factory = get_session_factory()
    entity_extractor = EntityExtractor()
    
    async with session_factory() as db_session:
        # Получаем все документы
        result = await db_session.execute(select(Doc))
        docs = result.scalars().all()
        
        total = len(docs)
        print(f"📊 Найдено документов: {total}")
        print("⏳ Извлечение сущностей...\n")
        
        total_entities = 0
        processed_count = 0
        error_count = 0
        
        for i, doc in enumerate(docs, 1):
            try:
                print(f"[{i}/{total}] {doc.doc_id[:50]}...", end=" ")
                
                content = doc.content or {}
                blocks = content.get('blocks', [])
                
                if not blocks:
                    print("⚠ (нет блоков)")
                    error_count += 1
                    continue
                
                # Формируем normalized_content для EntityExtractor
                normalized_content = {
                    'blocks': blocks,
                    'metadata': content.get('normalized_metadata', {})
                }
                
                # Извлекаем сущности
                try:
                    entities = await entity_extractor.extract_and_save_entities(
                        db_session,
                        doc.doc_id,
                        normalized_content,
                        doc_url=doc.url,
                        doc_breadcrumbs=content.get('breadcrumbs', [])
                    )
                    
                    total_entities += len(entities)
                    processed_count += 1
                    
                    # Статистика по типам
                    entity_types = {}
                    for entity in entities:
                        entity_type = entity.type
                        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
                    
                    types_str = ', '.join(f"{k}:{v}" for k, v in sorted(entity_types.items()))
                    print(f"✓ ({len(entities)} сущностей: {types_str})")
                    
                except Exception as e:
                    print(f"✗ ({str(e)[:30]})")
                    error_count += 1
                    await db_session.rollback()
                    continue
                    
            except Exception as e:
                print(f"✗ Ошибка: {str(e)[:50]}")
                error_count += 1
                continue
        
        print(f"\n" + "=" * 60)
        print(f"✅ ИЗВЛЕЧЕНИЕ ЗАВЕРШЕНО")
        print("=" * 60)
        print(f"📊 Статистика:")
        print(f"  Всего документов: {total}")
        print(f"  ✅ Обработано: {processed_count}")
        print(f"  ✗ Ошибок: {error_count}")
        print(f"  📦 Всего сущностей извлечено: {total_entities}")
        print("=" * 60)
        
        if processed_count > 0:
            print(f"\n✓ Сущности извлечены и сохранены в таблицу entities!")
            print(f"Теперь можно быстро искать:")
            print(f"  • Все заголовки уровня 2")
            print(f"  • Все блоки кода")
            print(f"  • Все специальные блоки ('В этой статье', 'Важно' и т.д.)")
            print(f"  • Все списки")
        
        return processed_count > 0

if __name__ == "__main__":
    print("🚀 Запуск извлечения сущностей...")
    print("Это создаст записи в таблице entities для быстрого поиска.\n")
    
    success = asyncio.run(extract_all_entities())
    
    if success:
        print("\n✓ Сущности извлечены!")
        print("Проверьте: http://127.0.0.1:8000/api/entities/{doc_id}")
    else:
        print("\n⚠ Завершено с ошибками")
        import sys
        sys.exit(1)


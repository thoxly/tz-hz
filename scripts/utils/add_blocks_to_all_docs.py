#!/usr/bin/env python3
"""Добавить структурированные блоки (blocks) во все документы в БД."""
import asyncio
import requests
from app.database.database import get_session_factory
from app.database.models import Doc
from app.normalizer import Normalizer
from sqlalchemy import select
from datetime import datetime

async def add_blocks_to_all_docs():
    """Добавить блоки во все документы."""
    print("🔄 Добавление структурированных блоков во все документы...")
    print("=" * 60)
    
    session_factory = get_session_factory()
    normalizer = Normalizer()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    async with session_factory() as db_session:
        # Получаем все документы
        result = await db_session.execute(select(Doc))
        docs = result.scalars().all()
        
        total = len(docs)
        print(f"📊 Найдено документов: {total}")
        print("⏳ Обработка...\n")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        docs_to_update = []
        
        for i, doc in enumerate(docs, 1):
            try:
                print(f"[{i}/{total}] {doc.doc_id[:50]}...", end=" ")
                
                content = doc.content or {}
                html = content.get('html', '')
                
                if not html:
                    print("⚠ (нет HTML)")
                    skipped_count += 1
                    continue
                
                # Нормализуем HTML для получения блоков
                try:
                    normalized = normalizer.normalize(
                        html,
                        title=doc.title,
                        breadcrumbs=content.get('breadcrumbs', [])
                    )
                    
                    blocks = normalized.get('blocks', [])
                    normalized_metadata = normalized.get('metadata', {})
                    
                    if blocks:
                        # Обновляем content с блоками
                        updated_content = content.copy()
                        updated_content['blocks'] = blocks
                        if normalized_metadata:
                            updated_content['normalized_metadata'] = normalized_metadata
                        
                        docs_to_update.append({
                            'doc_id': doc.doc_id,
                            'content': updated_content
                        })
                        
                        updated_count += 1
                        print(f"✓ ({len(blocks)} блоков)")
                    else:
                        print("⚠ (нет блоков)")
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"✗ ({str(e)[:30]})")
                    error_count += 1
                    continue
                    
            except Exception as e:
                print(f"✗ Ошибка: {str(e)[:50]}")
                error_count += 1
                continue
        
        # Сохраняем обновления в БД
        print(f"\n💾 Сохранение блоков в БД...")
        for update_data in docs_to_update:
            try:
                result = await db_session.execute(
                    select(Doc).where(Doc.doc_id == update_data['doc_id'])
                )
                doc = result.scalar_one_or_none()
                
                if doc:
                    doc.content = update_data['content']
                    doc.last_crawled = datetime.now()
                    await db_session.commit()
            except Exception as e:
                print(f"Ошибка при сохранении {update_data['doc_id']}: {e}")
                await db_session.rollback()
        
        print(f"\n" + "=" * 60)
        print(f"✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО")
        print("=" * 60)
        print(f"📊 Статистика:")
        print(f"  Всего документов: {total}")
        print(f"  ✅ Обновлено с блоками: {updated_count}")
        print(f"  ⚠ Пропущено: {skipped_count}")
        print(f"  ✗ Ошибок: {error_count}")
        print("=" * 60)
        
        if updated_count > 0:
            print(f"\n✓ {updated_count} документов теперь содержат структурированные блоки!")
            print("Структура content.blocks готова для работы с агент-архитектором.")
        
        return updated_count > 0

if __name__ == "__main__":
    print("🚀 Добавление структурированных блоков...")
    print("Это необходимо для работы агент-архитектора.\n")
    
    success = asyncio.run(add_blocks_to_all_docs())
    
    if success:
        print("\n✓ Блоки добавлены во все документы!")
        print("Проверьте: http://127.0.0.1:8000/api/docs")
    else:
        print("\n⚠ Завершено с ошибками")
        import sys
        sys.exit(1)


#!/usr/bin/env python3
"""Проверить структуру сущностей в БД."""
import asyncio
import json
from app.database.database import get_session_factory
from app.database.models import Entity, Doc
from sqlalchemy import select, func

async def check_entities():
    """Проверить сущности в БД."""
    print("🔍 Проверка сущностей в таблице entities")
    print("=" * 60)
    
    session_factory = get_session_factory()
    
    async with session_factory() as db_session:
        # Общая статистика
        result = await db_session.execute(
            select(func.count(Entity.id))
        )
        total_entities = result.scalar()
        
        print(f"\n📊 Всего сущностей в БД: {total_entities}")
        
        # Статистика по типам
        result = await db_session.execute(
            select(Entity.type, func.count(Entity.id))
            .group_by(Entity.type)
            .order_by(func.count(Entity.id).desc())
        )
        type_stats = result.all()
        
        print(f"\n📈 Статистика по типам:")
        for entity_type, count in type_stats:
            print(f"  • {entity_type}: {count}")
        
        # Примеры сущностей каждого типа
        print(f"\n📝 Примеры сущностей:")
        print("-" * 60)
        
        for entity_type, _ in type_stats[:5]:  # Первые 5 типов
            result = await db_session.execute(
                select(Entity)
                .where(Entity.type == entity_type)
                .limit(1)
            )
            entity = result.scalar_one_or_none()
            
            if entity:
                print(f"\n[{entity_type}]")
                print(f"  Doc ID: {entity.doc_id}")
                data = entity.data or {}
                print(f"  Data keys: {list(data.keys())}")
                
                if entity_type == 'header':
                    print(f"  Level: {data.get('level')}")
                    print(f"  Text: {data.get('text', '')[:80]}...")
                    print(f"  Breadcrumbs: {data.get('breadcrumbs', [])}")
                elif entity_type == 'special_block':
                    print(f"  Kind: {data.get('kind')}")
                    print(f"  Heading: {data.get('heading', '')[:60]}...")
                elif entity_type == 'list':
                    print(f"  Items count: {data.get('items_count', 0)}")
                    print(f"  Ordered: {data.get('ordered')}")
                    if data.get('items'):
                        print(f"  First item: {data['items'][0][:60]}...")
                elif entity_type == 'code_block':
                    print(f"  Language: {data.get('language', 'unknown')}")
                    code = data.get('code', '')
                    print(f"  Code preview: {code[:60]}...")
                elif entity_type == 'paragraph':
                    text = data.get('text', '')
                    print(f"  Text: {text[:80]}...")
        
        # Примеры для конкретного документа
        print(f"\n📄 Пример: сущности документа 'calendar'")
        print("-" * 60)
        
        result = await db_session.execute(
            select(Entity)
            .where(Entity.doc_id == 'calendar')
            .limit(5)
        )
        entities = result.scalars().all()
        
        for i, entity in enumerate(entities, 1):
            data = entity.data or {}
            print(f"\n[{i}] {entity.type}")
            if entity.type == 'header':
                print(f"    Level {data.get('level')}: {data.get('text', '')[:60]}...")
            elif entity.type == 'list':
                print(f"    {len(data.get('items', []))} элементов")
            elif entity.type == 'special_block':
                print(f"    {data.get('kind')}: {data.get('heading', '')[:60]}...")
            else:
                text = data.get('text', '')
                if text:
                    print(f"    {text[:60]}...")
        
        # Сохраняем пример структуры
        example_entity = entities[0] if entities else None
        if example_entity:
            example_data = {
                'id': example_entity.id,
                'doc_id': example_entity.doc_id,
                'type': example_entity.type,
                'data': example_entity.data,
                'created_at': example_entity.created_at.isoformat() if example_entity.created_at else None
            }
            
            with open('entity_example.json', 'w', encoding='utf-8') as f:
                json.dump(example_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Пример структуры сохранен в: entity_example.json")
        
        print(f"\n" + "=" * 60)
        print(f"✅ Таблица entities готова!")
        print("=" * 60)
        print(f"\n💡 Теперь можно быстро искать:")
        print(f"  • Все заголовки уровня 2 в разделе 'Платформа'")
        print(f"  • Все блоки кода на Python")
        print(f"  • Все специальные блоки 'В этой статье'")
        print(f"  • Все списки с определенными элементами")

if __name__ == "__main__":
    asyncio.run(check_entities())


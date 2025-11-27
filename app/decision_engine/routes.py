"""
API Routes для Decision Engine.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.decision_engine.models import BusinessRequirements, ArchitectureSolution
from app.decision_engine.engine import DecisionEngine

router = APIRouter()


@router.post("/decision-engine/design", response_model=ArchitectureSolution)
async def design_solution(
    requirements: BusinessRequirements,
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует архитектурное решение на основе бизнес-требований.
    
    Принимает структурированное бизнес-описание и возвращает
    формализованное архитектурное решение с ссылками на документацию.
    """
    try:
        engine = DecisionEngine(db)
        solution = await engine.design_solution(requirements)
        return solution
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации решения: {str(e)}")


@router.get("/decision-engine/health")
async def health_check():
    """Проверка работоспособности Decision Engine."""
    return {
        "status": "healthy",
        "service": "Decision Engine",
        "version": "1.0.0"
    }




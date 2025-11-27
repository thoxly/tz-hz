"""
API Routes для Technical Specification Generator.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal
from pydantic import BaseModel

from fastapi.responses import Response, StreamingResponse

from app.database import get_db
from app.decision_engine.models import ArchitectureSolution
from app.ts_generator.generator import TechnicalDesigner
from app.ts_generator.exporter import TSExporter

router = APIRouter()


class TSGenerateRequest(BaseModel):
    """Запрос на генерацию ТЗ."""
    architecture: ArchitectureSolution
    mode: Literal["deterministic", "verbose"] = "deterministic"


class TSGenerateResponse(BaseModel):
    """Ответ с сгенерированным ТЗ."""
    markdown: str
    mode: str
    timestamp: str


@router.post("/ts/generate", response_model=TSGenerateResponse)
async def generate_ts(
    request: TSGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует техническое задание на основе архитектурного решения.
    
    Принимает ArchitectureSolution от Decision Engine и возвращает
    формализованное ТЗ в формате Markdown.
    """
    try:
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(request.architecture, request.mode)
        
        return TSGenerateResponse(
            markdown=markdown,
            mode=request.mode,
            timestamp=designer.timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации ТЗ: {str(e)}")


@router.post("/ts/generate/deterministic")
async def generate_ts_deterministic(
    architecture: ArchitectureSolution,
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует строго формализованное ТЗ (deterministic режим).
    """
    try:
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode="deterministic")
        
        return {
            "markdown": markdown,
            "mode": "deterministic",
            "timestamp": designer.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации ТЗ: {str(e)}")


@router.post("/ts/generate/verbose")
async def generate_ts_verbose(
    architecture: ArchitectureSolution,
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует более человеческий текст ТЗ (verbose режим).
    """
    try:
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode="verbose")
        
        return {
            "markdown": markdown,
            "mode": "verbose",
            "timestamp": designer.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации ТЗ: {str(e)}")


@router.post("/ts/export/pdf")
async def export_ts_to_pdf(
    architecture: ArchitectureSolution,
    mode: Literal["deterministic", "verbose"] = Query("deterministic", description="Режим генерации ТЗ"),
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует ТЗ и экспортирует в PDF.
    
    Принимает ArchitectureSolution, генерирует ТЗ и возвращает PDF файл.
    """
    try:
        # Генерируем ТЗ
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode)
        
        # Экспортируем в PDF
        exporter = TSExporter()
        pdf_bytes = exporter.export_to_pdf(markdown)
        
        # Возвращаем файл
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="technical_specification_{designer.timestamp.replace(" ", "_")}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте в PDF: {str(e)}")


@router.post("/ts/export/docx")
async def export_ts_to_docx(
    architecture: ArchitectureSolution,
    mode: Literal["deterministic", "verbose"] = Query("deterministic", description="Режим генерации ТЗ"),
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует ТЗ и экспортирует в DOCX.
    
    Принимает ArchitectureSolution, генерирует ТЗ и возвращает DOCX файл.
    """
    try:
        # Генерируем ТЗ
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode)
        
        # Экспортируем в DOCX
        exporter = TSExporter()
        docx_bytes = exporter.export_to_docx(markdown)
        
        # Возвращаем файл
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="technical_specification_{designer.timestamp.replace(" ", "_")}.docx"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте в DOCX: {str(e)}")


@router.post("/ts/export/html")
async def export_ts_to_html(
    architecture: ArchitectureSolution,
    mode: Literal["deterministic", "verbose"] = Query("deterministic", description="Режим генерации ТЗ"),
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует ТЗ и экспортирует в HTML.
    
    Принимает ArchitectureSolution, генерирует ТЗ и возвращает HTML документ.
    """
    try:
        # Генерируем ТЗ
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode)
        
        # Экспортируем в HTML
        exporter = TSExporter()
        html = exporter.export_to_html(markdown, include_style=True)
        
        # Возвращаем HTML
        return Response(
            content=html,
            media_type="text/html",
            headers={
                "Content-Disposition": f'inline; filename="technical_specification_{designer.timestamp.replace(" ", "_")}.html"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте в HTML: {str(e)}")


@router.post("/ts/export/markdown")
async def export_ts_to_markdown(
    architecture: ArchitectureSolution,
    mode: Literal["deterministic", "verbose"] = Query("deterministic", description="Режим генерации ТЗ"),
    db: AsyncSession = Depends(get_db)
):
    """
    Генерирует ТЗ и возвращает в формате Markdown.
    
    Принимает ArchitectureSolution и возвращает Markdown файл.
    """
    try:
        # Генерируем ТЗ
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode)
        
        # Возвращаем Markdown
        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="technical_specification_{designer.timestamp.replace(" ", "_")}.md"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации Markdown: {str(e)}")


@router.get("/ts/health")
async def health_check():
    """Проверка работоспособности TS Generator."""
    exporter = TSExporter()
    dependencies = {
        "pdfkit": exporter.has_pdfkit,
        "weasyprint": exporter.has_weasyprint,
        "docx": exporter.has_docx,
        "markdown": exporter.has_markdown,
        "pypandoc": exporter.has_pypandoc
    }
    
    return {
        "status": "healthy",
        "service": "Technical Specification Generator",
        "version": "1.0.0",
        "dependencies": dependencies
    }


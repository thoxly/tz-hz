from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from app.database import init_db
from app.api.routes import router
from app.mcp.routes import router as mcp_router
from app.decision_engine.routes import router as decision_engine_router
from app.ts_generator.routes import router as ts_generator_router
from app.agents.routes import router as agents_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="ELMA365 Documentation Crawler",
    description="Crawler and normalizer for ELMA365 documentation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")
app.include_router(mcp_router, prefix="/api")
app.include_router(decision_engine_router, prefix="/api")
app.include_router(ts_generator_router, prefix="/api")
app.include_router(agents_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()
    logging.info("Application started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logging.info("Application shutting down")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ELMA365 Documentation Crawler API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


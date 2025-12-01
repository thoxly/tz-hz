from typing import Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from agents.process_extractor import ProcessExtractor
from agents.architect_agent import ArchitectAgent
from agents.scope_agent import ScopeAgent
from agents.mcp_client import MCPClient
from agents.models.schemas import (
    ProcessExtractorInput,
    ArchitectAgentInput,
    ScopeAgentInput
)
from pipeline.validators import (
    validate_as_is,
    validate_architecture,
    validate_scope,
    fix_format
)
from app.database.models import Run

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrator for the agent pipeline."""
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        self.process_extractor = ProcessExtractor(mcp_client=self.mcp_client)
        self.architect_agent = ArchitectAgent(mcp_client=self.mcp_client)
        self.scope_agent = ScopeAgent(mcp_client=self.mcp_client)
    
    async def run_process_pipeline(
        self,
        text: str,
        db_session: AsyncSession,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete process pipeline.
        
        Args:
            text: Input text from meeting/requirements
            db_session: Database session
            user: User identifier (e.g., Telegram user_id)
        
        Returns:
            Dict with as_is, architecture, and scope
        """
        logger.info("Starting process pipeline")
        
        try:
            # Step 1: ProcessExtractor
            logger.info("Step 1: Extracting AS-IS process")
            as_is_result = await self.process_extractor.extract(text)
            
            # Validate and fix AS-IS
            if not validate_as_is(as_is_result):
                logger.warning("AS-IS validation failed, attempting to fix")
                as_is_result = fix_format(as_is_result, "as_is")
            
            # Step 2: ArchitectAgent
            logger.info("Step 2: Designing architecture")
            architecture_result = await self.architect_agent.design(as_is_result)
            
            # Validate and fix architecture
            if not validate_architecture(architecture_result):
                logger.warning("Architecture validation failed, attempting to fix")
                architecture_result = fix_format(architecture_result, "architecture")
            
            # Step 3: ScopeAgent
            logger.info("Step 3: Creating scope specification")
            scope_result = await self.scope_agent.create_scope(architecture_result)
            
            # Validate and fix scope
            if not validate_scope(scope_result):
                logger.warning("Scope validation failed, attempting to fix")
                scope_result = fix_format(scope_result, "scope")
            
            # Step 4: Save to database
            logger.info("Step 4: Saving to database")
            run = Run(
                user=user,
                input_text=text,
                as_is=as_is_result,
                architecture=architecture_result,
                scope=scope_result
            )
            db_session.add(run)
            await db_session.commit()
            await db_session.refresh(run)
            
            logger.info(f"Pipeline completed successfully. Run ID: {run.id}")
            
            return {
                "run_id": run.id,
                "as_is": as_is_result,
                "architecture": architecture_result,
                "scope": scope_result
            }
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            await db_session.rollback()
            raise


import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from .models.schemas import ProcessExtractorInput, ProcessExtractorOutput
from .prompts import PROCESS_EXTRACTOR_PROMPT

logger = logging.getLogger(__name__)


class ProcessExtractor(BaseAgent):
    """Agent for extracting AS-IS processes from text."""
    
    async def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract AS-IS process from text.
        
        Args:
            text: Raw text from meeting/requirements
        
        Returns:
            Structured AS-IS process description
        """
        # Use MCP tools to find relevant documentation
        context_docs = []
        if self.mcp_client:
            try:
                # Search for relevant documentation
                search_result = await self.mcp_client.call_tool(
                    "elma365.search_docs",
                    {"query": "процесс бизнес workflow"}
                )
                if search_result.get("content"):
                    context_docs = search_result["content"][0].get("text", {}).get("results", [])
                
                # Find process patterns
                patterns_result = await self.mcp_client.call_tool(
                    "elma365.find_process_patterns",
                    {"pattern_type": "согласование"}
                )
                if patterns_result.get("content"):
                    patterns = patterns_result["content"][0].get("text", {}).get("patterns", [])
                    context_docs.extend(patterns[:3])  # Add top 3 patterns
            except Exception as e:
                logger.warning(f"Error using MCP tools: {e}")
        
        # Build user prompt with context
        user_prompt = f"""
Extract the AS-IS business process from the following text:

{text}

"""
        if context_docs:
            user_prompt += f"\nRelevant documentation context:\n{json.dumps(context_docs[:3], ensure_ascii=False, indent=2)}\n"
        
        user_prompt += "\nProvide the structured AS-IS process description in JSON format."
        
        # Call LLM
        response = await self._call_llm(
            system_prompt=PROCESS_EXTRACTOR_PROMPT,
            user_prompt=user_prompt
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response (might be wrapped in markdown)
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            as_is = json.loads(response)
            return as_is
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response as JSON: {e}")
            logger.error(f"Response: {response}")
            # Return a basic structure if parsing fails
            return {
                "process_name": "Unknown",
                "description": text[:500],
                "actors": [],
                "steps": [],
                "triggers": [],
                "outcomes": []
            }
    
    async def process(self, input_data: ProcessExtractorInput) -> ProcessExtractorOutput:
        """Process input and return output."""
        as_is = await self.extract(input_data.text)
        return ProcessExtractorOutput(as_is=as_is)


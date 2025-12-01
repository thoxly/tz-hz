import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from .models.schemas import ScopeAgentInput, ScopeAgentOutput
from .prompts import SCOPE_AGENT_PROMPT

logger = logging.getLogger(__name__)


class ScopeAgent(BaseAgent):
    """Agent for creating scope specifications from architecture."""
    
    async def create_scope(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create scope specification from architecture.
        
        Args:
            architecture: ELMA365 architecture design
        
        Returns:
            Scope specification
        """
        # Use MCP tools for terminology and examples
        examples = []
        
        if self.mcp_client:
            try:
                # Get examples for key components
                component_types = [comp.get("type", "") for comp in architecture.get("elma365_components", [])[:3]]
                if component_types:
                    examples_result = await self.mcp_client.call_tool(
                        "elma365.find_examples",
                        {"keywords": component_types}
                    )
                    if examples_result.get("content"):
                        examples = examples_result["content"][0].get("text", {}).get("examples", [])
            
            except Exception as e:
                logger.warning(f"Error using MCP tools: {e}")
        
        # Build user prompt
        user_prompt = f"""
Create a scope specification (ТЗ) for the following ELMA365 architecture:

{json.dumps(architecture, ensure_ascii=False, indent=2)}

"""
        if examples:
            user_prompt += f"\nRelevant examples for terminology:\n{json.dumps(examples[:2], ensure_ascii=False, indent=2)}\n"
        
        user_prompt += "\nProvide the scope specification in JSON format. Keep it concise and focused on what needs approval."
        
        # Call LLM
        response = await self._call_llm(
            system_prompt=SCOPE_AGENT_PROMPT,
            user_prompt=user_prompt
        )
        
        # Parse JSON response
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            scope = json.loads(response)
            return scope
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response as JSON: {e}")
            logger.error(f"Response: {response}")
            return {
                "project_name": architecture.get("process_name", "Unknown"),
                "objectives": [],
                "scope": {"in_scope": [], "out_of_scope": []},
                "deliverables": [],
                "success_criteria": [],
                "timeline": "TBD",
                "resources": []
            }
    
    async def process(self, input_data: ScopeAgentInput) -> ScopeAgentOutput:
        """Process input and return output."""
        scope = await self.create_scope(input_data.architecture)
        return ScopeAgentOutput(scope=scope)


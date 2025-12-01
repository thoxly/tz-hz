import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from .models.schemas import ArchitectAgentInput, ArchitectAgentOutput
from .prompts import ARCHITECT_AGENT_PROMPT

logger = logging.getLogger(__name__)


class ArchitectAgent(BaseAgent):
    """Agent for designing ELMA365 architecture from AS-IS process."""
    
    async def design(self, as_is: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design ELMA365 architecture from AS-IS process.
        
        Args:
            as_is: AS-IS process description
        
        Returns:
            ELMA365 architecture design
        """
        # Use MCP tools to find relevant documentation
        context_docs = []
        examples = []
        
        if self.mcp_client:
            try:
                # Get relevant documents
                process_name = as_is.get("process_name", "")
                if process_name:
                    search_result = await self.mcp_client.call_tool(
                        "elma365.search_docs",
                        {"query": process_name}
                    )
                    if search_result.get("content"):
                        results = search_result["content"][0].get("text", {}).get("results", [])
                        # Get full documents for top results
                        for result in results[:2]:
                            doc_id = result.get("doc_id")
                            if doc_id:
                                doc_result = await self.mcp_client.call_tool(
                                    "elma365.get_doc",
                                    {"doc_id": doc_id}
                                )
                                if doc_result.get("content"):
                                    doc = doc_result["content"][0].get("text", {}).get("doc", {})
                                    context_docs.append(doc)
                
                # Find examples
                keywords = [step.get("action", "") for step in as_is.get("steps", [])[:3]]
                if keywords:
                    examples_result = await self.mcp_client.call_tool(
                        "elma365.find_examples",
                        {"keywords": keywords}
                    )
                    if examples_result.get("content"):
                        examples = examples_result["content"][0].get("text", {}).get("examples", [])
                
                # Find process patterns
                patterns_result = await self.mcp_client.call_tool(
                    "elma365.find_process_patterns",
                    {"pattern_type": "согласование"}
                )
                if patterns_result.get("content"):
                    patterns = patterns_result["content"][0].get("text", {}).get("patterns", [])
                    context_docs.extend(patterns[:2])
            
            except Exception as e:
                logger.warning(f"Error using MCP tools: {e}")
        
        # Build user prompt
        user_prompt = f"""
Design an ELMA365 architecture for the following AS-IS process:

{json.dumps(as_is, ensure_ascii=False, indent=2)}

"""
        if context_docs:
            user_prompt += f"\nRelevant ELMA365 documentation:\n{json.dumps(context_docs[:3], ensure_ascii=False, indent=2)}\n"
        
        if examples:
            user_prompt += f"\nRelevant examples:\n{json.dumps(examples[:2], ensure_ascii=False, indent=2)}\n"
        
        user_prompt += "\nProvide the ELMA365 architecture design in JSON format."
        
        # Call LLM
        response = await self._call_llm(
            system_prompt=ARCHITECT_AGENT_PROMPT,
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
            
            architecture = json.loads(response)
            return architecture
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response as JSON: {e}")
            logger.error(f"Response: {response}")
            return {
                "process_name": as_is.get("process_name", "Unknown"),
                "elma365_components": [],
                "data_model": {},
                "integrations": [],
                "automation_rules": []
            }
    
    async def process(self, input_data: ArchitectAgentInput) -> ArchitectAgentOutput:
        """Process input and return output."""
        architecture = await self.design(input_data.as_is)
        return ArchitectAgentOutput(architecture=architecture)


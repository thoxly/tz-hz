from pydantic import BaseModel, Field
from typing import Dict, Any


class ProcessExtractorInput(BaseModel):
    text: str = Field(..., description="Raw text from meeting/requirements")


class ProcessExtractorOutput(BaseModel):
    as_is: Dict[str, Any] = Field(..., description="Structured AS-IS process description")


class ArchitectAgentInput(BaseModel):
    as_is: Dict[str, Any] = Field(..., description="AS-IS process description")


class ArchitectAgentOutput(BaseModel):
    architecture: Dict[str, Any] = Field(..., description="ELMA365 architecture design")


class ScopeAgentInput(BaseModel):
    architecture: Dict[str, Any] = Field(..., description="ELMA365 architecture")


class ScopeAgentOutput(BaseModel):
    scope: Dict[str, Any] = Field(..., description="Scope specification for approval")


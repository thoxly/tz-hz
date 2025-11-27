"""
Agents - три агента для обработки требований клиента.
"""
from .process_extractor import ProcessExtractor
from .architect_agent import ArchitectAgent
from .scope_agent import ScopeAgent

__all__ = ["ProcessExtractor", "ArchitectAgent", "ScopeAgent"]


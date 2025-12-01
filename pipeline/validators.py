from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def validate_as_is(data: Dict[str, Any]) -> bool:
    """
    Validate AS-IS process structure.
    
    Args:
        data: AS-IS process data
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["process_name", "description", "steps"]
    
    if not isinstance(data, dict):
        logger.warning("AS-IS data is not a dict")
        return False
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"AS-IS missing required field: {field}")
            return False
    
    # Validate steps structure
    steps = data.get("steps", [])
    if not isinstance(steps, list):
        logger.warning("AS-IS steps is not a list")
        return False
    
    for step in steps:
        if not isinstance(step, dict):
            logger.warning("AS-IS step is not a dict")
            return False
        if "step_number" not in step or "action" not in step:
            logger.warning("AS-IS step missing required fields")
            return False
    
    return True


def validate_architecture(data: Dict[str, Any]) -> bool:
    """
    Validate architecture structure.
    
    Args:
        data: Architecture data
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["process_name", "elma365_components"]
    
    if not isinstance(data, dict):
        logger.warning("Architecture data is not a dict")
        return False
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Architecture missing required field: {field}")
            return False
    
    # Validate components
    components = data.get("elma365_components", [])
    if not isinstance(components, list):
        logger.warning("Architecture components is not a list")
        return False
    
    return True


def validate_scope(data: Dict[str, Any]) -> bool:
    """
    Validate scope specification structure.
    
    Args:
        data: Scope data
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["project_name", "objectives", "scope"]
    
    if not isinstance(data, dict):
        logger.warning("Scope data is not a dict")
        return False
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Scope missing required field: {field}")
            return False
    
    # Validate scope structure
    scope = data.get("scope", {})
    if not isinstance(scope, dict):
        logger.warning("Scope.scope is not a dict")
        return False
    
    if "in_scope" not in scope:
        logger.warning("Scope.scope missing in_scope")
        return False
    
    return True


def fix_format(data: Dict[str, Any], format_type: str) -> Dict[str, Any]:
    """
    Automatically fix format issues in data.
    
    Args:
        data: Data to fix
        format_type: Type of data (as_is, architecture, scope)
    
    Returns:
        Fixed data
    """
    if not isinstance(data, dict):
        return data
    
    if format_type == "as_is":
        # Ensure required fields exist
        if "process_name" not in data:
            data["process_name"] = "Unknown Process"
        if "description" not in data:
            data["description"] = ""
        if "steps" not in data:
            data["steps"] = []
        if "actors" not in data:
            data["actors"] = []
        if "triggers" not in data:
            data["triggers"] = []
        if "outcomes" not in data:
            data["outcomes"] = []
    
    elif format_type == "architecture":
        # Ensure required fields exist
        if "process_name" not in data:
            data["process_name"] = "Unknown Process"
        if "elma365_components" not in data:
            data["elma365_components"] = []
        if "data_model" not in data:
            data["data_model"] = {}
        if "integrations" not in data:
            data["integrations"] = []
        if "automation_rules" not in data:
            data["automation_rules"] = []
    
    elif format_type == "scope":
        # Ensure required fields exist
        if "project_name" not in data:
            data["project_name"] = "Unknown Project"
        if "objectives" not in data:
            data["objectives"] = []
        if "scope" not in data:
            data["scope"] = {"in_scope": [], "out_of_scope": []}
        if "deliverables" not in data:
            data["deliverables"] = []
        if "success_criteria" not in data:
            data["success_criteria"] = []
        if "timeline" not in data:
            data["timeline"] = "TBD"
        if "resources" not in data:
            data["resources"] = []
    
    return data


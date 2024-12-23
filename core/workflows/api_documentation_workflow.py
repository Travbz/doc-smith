from typing import Dict, Any, List
from ..base import BaseWorkflow, WorkflowStatus
from ..utils.logging_config import setup_logger

logger = setup_logger(__name__)

class APIDocumentationWorkflow(BaseWorkflow):
    """Workflow for generating API documentation."""
    
    def __init__(self):
        super().__init__("api_documentation")
        
    def define_steps(self) -> List[Dict[str, Any]]:
        """Define the steps for API documentation generation."""
        return [
            {
                "name": "detect_api_framework",
                "handler": self._detect_api_framework,
                "required_keys": ["framework", "version"]
            },
            {
                "name": "extract_endpoints",
                "handler": self._extract_endpoints,
                "required_keys": ["endpoints"]
            },
            {
                "name": "generate_api_docs",
                "handler": self._generate_api_docs,
                "required_keys": ["documentation"]
            },
            {
                "name": "validate_api_docs",
                "handler": self._validate_api_docs,
                "required_keys": ["status", "validation_results"]
            }
        ]
        
    async def _detect_api_framework(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect the API framework used in the repository."""
        return await self.agency.delegate("tech_lead", "code_analyst", {
            "type": "detect_framework",
            "repo_info": params["repo_info"]
        })
        
    async def _extract_endpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract API endpoints and their specifications."""
        return await self.agency.delegate("tech_lead", "code_analyst", {
            "type": "extract_endpoints",
            "framework_info": params["previous_step"]
        })
        
    async def _generate_api_docs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API documentation."""
        return await self.agency.delegate("tech_lead", "code_analyst", {
            "type": "generate_api_docs",
            "endpoints": params["previous_step"]["endpoints"]
        })
        
    async def _validate_api_docs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated API documentation."""
        return await self.agency.delegate("tech_lead", "doc_reviewer", {
            "type": "validate_api_docs",
            "documentation": params["previous_step"]["documentation"]
        })
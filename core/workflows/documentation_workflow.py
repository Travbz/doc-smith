from typing import Dict, Any, List
from pathlib import Path
from ..base import BaseWorkflow, WorkflowStatus
from ..utils.logging_config import setup_logger
from ..output import DocumentGenerator
from ...config.settings import DOCS_DIR

logger = setup_logger(__name__)

class DocumentationWorkflow(BaseWorkflow):
    """Main workflow for documentation generation."""
    
    def __init__(self, agency):
        super().__init__("documentation")
        self.agency = agency
        self.doc_generator = DocumentGenerator(DOCS_DIR)
        
    def define_steps(self) -> List[Dict[str, Any]]:
        """Define the steps for documentation generation."""
        return [
            {
                "name": "prepare_repository",
                "handler": self._prepare_repository,
                "required_keys": ["repo_path", "structure"]
            },
            {
                "name": "analyze_code",
                "handler": self._analyze_code,
                "required_keys": ["analysis", "documentation"]
            },
            {
                "name": "generate_documentation",
                "handler": self._generate_documentation,
                "required_keys": ["documentation"]
            },
            {
                "name": "review_documentation",
                "handler": self._review_documentation,
                "required_keys": ["status", "feedback"]
            },
            {
                "name": "create_pull_request",
                "handler": self._create_pull_request,
                "required_keys": ["pr_url", "pr_number"]
            }
        ]
        
    async def _prepare_repository(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the repository for documentation."""
        return await self.agency.delegate("tech_lead", "github", {
            "type": "prepare_repository",
            "repo_url": params["repo_url"]
        })
        
    async def _analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code and gather documentation content."""
        analysis = await self.agency.delegate("tech_lead", "code_analyst", {
            "type": "analyze_repository",
            "repo_info": params["previous_step"]
        })
        
        # Enhance analysis with architecture information
        arch_analysis = await self.agency.delegate("tech_lead", "code_analyst", {
            "type": "analyze_architecture",
            "repo_info": params["previous_step"],
            "code_analysis": analysis
        })
        
        return {
            "analysis": analysis,
            "architecture": arch_analysis,
            "repo_info": params["previous_step"]
        }
        
    async def _generate_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation using analyzed content."""
        previous_step = params["previous_step"]
        
        # Prepare content for documentation generation
        content = {
            "description": previous_step["analysis"].get("description", ""),
            "features": previous_step["analysis"].get("features", []),
            "architecture_overview": previous_step["architecture"].get("overview", ""),
            "components": previous_step["architecture"].get("components", []),
            "has_api": previous_step["analysis"].get("has_api", False),
            "setup_overview": previous_step["analysis"].get("setup_instructions", ""),
            "installation_steps": previous_step["analysis"].get("installation", ""),
            "usage": previous_step["analysis"].get("usage", ""),
        }
        
        # Generate documentation files
        documentation = self.doc_generator.generate_documentation(
            content,
            previous_step["repo_info"]
        )
        
        return {
            "documentation": documentation,
            "repo_info": previous_step["repo_info"]
        }
        
    async def _review_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Review generated documentation."""
        review_result = await self.agency.delegate("tech_lead", "doc_reviewer", {
            "type": "review_documentation",
            "documentation": params["previous_step"]["documentation"],
            "repo_info": params["previous_step"]["repo_info"]
        })
        
        if review_result["status"] == "needs_revision":
            # Update documentation based on feedback
            updated_docs = await self.agency.delegate("tech_lead", "code_analyst", {
                "type": "update_documentation",
                "current_docs": params["previous_step"]["documentation"],
                "review_feedback": review_result["feedback"]
            })
            
            return {
                "documentation": updated_docs,
                "repo_info": params["previous_step"]["repo_info"],
                "status": "revised",
                "feedback": review_result["feedback"]
            }
            
        return {
            "documentation": params["previous_step"]["documentation"],
            "repo_info": params["previous_step"]["repo_info"],
            "status": "approved"
        }
        
    async def _create_pull_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create pull request with documentation changes."""
        return await self.agency.delegate("tech_lead", "github", {
            "type": "create_pull_request",
            "documentation": params["previous_step"]["documentation"],
            "repo_info": params["previous_step"]["repo_info"]
        })
        
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the documentation workflow."""
        try:
            logger.info(f"Starting documentation workflow for {params['repo_url']}")
            result = await super().execute(params)
            
            if result["status"] == WorkflowStatus.COMPLETED:
                logger.info("Documentation workflow completed successfully")
                return {
                    "status": "success",
                    "pr_url": result["steps"]["create_pull_request"]["pr_url"],
                    "documentation": result["steps"]["generate_documentation"]["documentation"]
                }
            else:
                logger.error(f"Documentation workflow failed: {result['error']}")
                return {
                    "status": "failed",
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"Error in documentation workflow: {str(e)}")
            raise
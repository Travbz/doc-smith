from typing import Dict, Any, Type
import asyncio
from ..base import BaseWorkflow
from ..utils.logging_config import setup_logger
from .documentation_workflow import DocumentationWorkflow
from .api_documentation_workflow import APIDocumentationWorkflow

logger = setup_logger(__name__)

class WorkflowCoordinator:
    """Coordinates and manages workflow execution."""
    
    def __init__(self):
        self._workflows: Dict[str, Type[BaseWorkflow]] = {
            "documentation": DocumentationWorkflow,
            "api_documentation": APIDocumentationWorkflow
        }
        self._running_workflows: Dict[str, BaseWorkflow] = {}
        
    async def start_workflow(
        self,
        workflow_type: str,
        params: Dict[str, Any]
    ) -> str:
        """Start a new workflow."""
        if workflow_type not in self._workflows:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
            
        workflow_class = self._workflows[workflow_type]
        workflow = workflow_class()
        
        # Generate a unique workflow ID
        workflow_id = f"{workflow_type}_{len(self._running_workflows)}"
        self._running_workflows[workflow_id] = workflow
        
        # Start workflow execution in background
        asyncio.create_task(self._execute_workflow(workflow_id, params))
        
        return workflow_id
        
    async def _execute_workflow(
        self,
        workflow_id: str,
        params: Dict[str, Any]
    ) -> None:
        """Execute a workflow."""
        workflow = self._running_workflows[workflow_id]
        
        try:
            result = await workflow.run(params)
            logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            raise
            
        finally:
            del self._running_workflows[workflow_id]
            
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow."""
        if workflow_id not in self._running_workflows:
            raise ValueError(f"Unknown workflow ID: {workflow_id}")
            
        workflow = self._running_workflows[workflow_id]
        return workflow.get_progress()
        
    def get_workflow_result(self, workflow_id: str) -> Dict[str, Any]:
        """Get the result of a completed workflow."""
        if workflow_id not in self._running_workflows:
            raise ValueError(f"Unknown workflow ID: {workflow_id}")
            
        workflow = self._running_workflows[workflow_id]
        return workflow.get_results()

# Create singleton instance
workflow_coordinator = WorkflowCoordinator()
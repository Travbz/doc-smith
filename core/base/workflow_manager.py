from typing import Dict, Type, Optional
from .workflow import BaseWorkflow
from ..utils.logging_config import setup_logger

logger = setup_logger(__name__)

class WorkflowManager:
    """Manages workflow registration and execution."""
    
    def __init__(self):
        self.workflows: Dict[str, Type[BaseWorkflow]] = {}
        self.active_workflows: Dict[str, BaseWorkflow] = {}
        
    def register_workflow(
        self,
        workflow_type: str,
        workflow_class: Type[BaseWorkflow]
    ) -> None:
        """Register a workflow class."""
        if not issubclass(workflow_class, BaseWorkflow):
            raise ValueError(
                f"Workflow class must inherit from BaseWorkflow: {workflow_class}"
            )
            
        self.workflows[workflow_type] = workflow_class
        logger.info(f"Registered workflow type: {workflow_type}")
        
    def create_workflow(
        self,
        workflow_type: str,
        workflow_id: Optional[str] = None
    ) -> BaseWorkflow:
        """Create a new workflow instance."""
        if workflow_type not in self.workflows:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
            
        workflow_class = self.workflows[workflow_type]
        workflow = workflow_class(workflow_type)
        
        if workflow_id:
            self.active_workflows[workflow_id] = workflow
            
        return workflow
        
    def get_workflow(self, workflow_id: str) -> Optional[BaseWorkflow]:
        """Get an active workflow by ID."""
        return self.active_workflows.get(workflow_id)
        
    def remove_workflow(self, workflow_id: str) -> None:
        """Remove an active workflow."""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            
    def get_registered_workflows(self) -> Dict[str, Type[BaseWorkflow]]:
        """Get all registered workflow types."""
        return self.workflows.copy()
        
    def get_active_workflows(self) -> Dict[str, BaseWorkflow]:
        """Get all active workflow instances."""
        return self.active_workflows.copy()

# Create singleton instance
workflow_manager = WorkflowManager()
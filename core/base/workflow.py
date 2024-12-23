from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from enum import Enum
from ..utils.logging_config import setup_logger
from ...config.models import get_workflow_model

logger = setup_logger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BaseWorkflow(ABC):
    """Base class for all workflows in the system."""
    
    def __init__(self, workflow_type: str):
        self.workflow_type = workflow_type
        self.model_config = get_workflow_model(workflow_type)
        self.status = WorkflowStatus.PENDING
        self.steps: List[Dict[str, Any]] = []
        self.current_step: int = 0
        self.results: Dict[str, Any] = {}
        
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with the given parameters."""
        pass
        
    @abstractmethod
    def define_steps(self) -> List[Dict[str, Any]]:
        """Define the steps for this workflow."""
        pass
        
    async def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run the workflow through all its steps."""
        try:
            self.status = WorkflowStatus.RUNNING
            self.steps = self.define_steps()
            
            # Execute each step
            for i, step in enumerate(self.steps):
                self.current_step = i
                step_result = await self._execute_step(step, params)
                self.results[step['name']] = step_result
                
                # Update params with step results for next step
                params.update({'previous_step': step_result})
                
            self.status = WorkflowStatus.COMPLETED
            return self.get_results()
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            logger.error(f"Workflow {self.workflow_type} failed: {str(e)}")
            raise
            
    async def _execute_step(
        self,
        step: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        logger.info(f"Executing step {step['name']} of {self.workflow_type}")
        
        try:
            if 'handler' not in step:
                raise ValueError(f"No handler defined for step {step['name']}")
                
            result = await step['handler'](params)
            
            if step.get('validate'):
                self._validate_step_result(result, step)
                
            return result
            
        except Exception as e:
            logger.error(f"Step {step['name']} failed: {str(e)}")
            raise
            
    def _validate_step_result(
        self,
        result: Dict[str, Any],
        step: Dict[str, Any]
    ) -> None:
        """Validate the result of a workflow step."""
        if not isinstance(result, dict):
            raise ValueError(f"Step {step['name']} must return a dictionary")
            
        required_keys = step.get('required_keys', [])
        missing_keys = [key for key in required_keys if key not in result]
        
        if missing_keys:
            raise ValueError(
                f"Step {step['name']} result missing required keys: {missing_keys}"
            )
            
    def get_progress(self) -> Dict[str, Any]:
        """Get the current progress of the workflow."""
        return {
            'status': self.status.value,
            'current_step': self.current_step,
            'total_steps': len(self.steps),
            'completed_steps': [step['name'] for step in self.steps[:self.current_step]]
        }
        
    def get_results(self) -> Dict[str, Any]:
        """Get the results of the workflow."""
        return {
            'status': self.status.value,
            'results': self.results
        }
        
    def reset(self) -> None:
        """Reset the workflow to its initial state."""
        self.status = WorkflowStatus.PENDING
        self.current_step = 0
        self.results.clear()
        
    @property
    def is_complete(self) -> bool:
        """Check if the workflow is complete."""
        return self.status == WorkflowStatus.COMPLETED
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio
from ..llm.openai_client import openai_client
from ..utils.logging_config import setup_logger
from ...config.models import get_agent_model
from ...config.prompts.base_prompts import load_prompt_template

logger = setup_logger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.model_config = get_agent_model(agent_type)
        self.state: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []
        
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task specific to this agent."""
        pass
        
    async def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a task, including pre and post processing."""
        logger.info(f"{self.agent_type} processing task: {task.get('type', 'unknown')}")
        
        # Validate task
        self._validate_task(task)
        
        # Pre-process task
        processed_task = await self._pre_process_task(task)
        
        # Process task
        result = await self.process_task(processed_task)
        
        # Post-process result
        final_result = await self._post_process_result(result)
        
        # Update task history
        self._update_task_history(task, final_result)
        
        return final_result
        
    async def get_completion(
        self,
        prompt_type: str,
        prompt_name: str,
        **kwargs: Any
    ) -> str:
        """Get a completion using the agent's configured model."""
        prompt_template = load_prompt_template(prompt_type, prompt_name)
        prompt = prompt_template.format(**kwargs)
        
        response = await openai_client.get_completion(
            prompt=prompt,
            model_config=self.model_config
        )
        
        return response.choices[0].message.content
        
    async def get_stream_completion(
        self,
        prompt_type: str,
        prompt_name: str,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Get a streaming completion using the agent's configured model."""
        prompt_template = load_prompt_template(prompt_type, prompt_name)
        prompt = prompt_template.format(**kwargs)
        
        async for chunk in openai_client.get_stream_completion(
            prompt=prompt,
            model_config=self.model_config
        ):
            yield chunk.content
            
    def _validate_task(self, task: Dict[str, Any]) -> None:
        """Validate the task input."""
        if not isinstance(task, dict):
            raise ValueError("Task must be a dictionary")
            
        if 'type' not in task:
            raise ValueError("Task must have a 'type' field")
            
    async def _pre_process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process the task before handling."""
        return task
        
    async def _post_process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process the result after handling."""
        return result
        
    def _update_task_history(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Update the task history."""
        self.task_history.append({
            'task': task,
            'result': result
        })
        
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent."""
        return self.state.copy()
        
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update the agent's state."""
        self.state.update(updates)
        
    def clear_state(self) -> None:
        """Clear the agent's state."""
        self.state.clear()
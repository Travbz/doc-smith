from typing import Dict, Type, Optional
from .agent import BaseAgent
from ..utils.logging_config import setup_logger

logger = setup_logger(__name__)

class AgentManager:
    """Manages agent registration and lifecycle."""
    
    def __init__(self):
        self.agents: Dict[str, Type[BaseAgent]] = {}
        self.active_agents: Dict[str, BaseAgent] = {}
        
    def register_agent(
        self,
        agent_type: str,
        agent_class: Type[BaseAgent]
    ) -> None:
        """Register an agent class."""
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(
                f"Agent class must inherit from BaseAgent: {agent_class}"
            )
            
        self.agents[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")
        
    def create_agent(
        self,
        agent_type: str,
        agent_id: Optional[str] = None
    ) -> BaseAgent:
        """Create a new agent instance."""
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        agent_class = self.agents[agent_type]
        agent = agent_class(agent_type)
        
        if agent_id:
            self.active_agents[agent_id] = agent
            
        return agent
        
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an active agent by ID."""
        return self.active_agents.get(agent_id)
        
    def remove_agent(self, agent_id: str) -> None:
        """Remove an active agent."""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
            
    def get_registered_agents(self) -> Dict[str, Type[BaseAgent]]:
        """Get all registered agent types."""
        return self.agents.copy()
        
    def get_active_agents(self) -> Dict[str, BaseAgent]:
        """Get all active agent instances."""
        return self.active_agents.copy()
        
    def cleanup(self) -> None:
        """Clean up all active agents."""
        self.active_agents.clear()

# Create singleton instance
agent_manager = AgentManager()
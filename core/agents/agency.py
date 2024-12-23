from typing import Dict, List, Tuple, Any
from agents import settings

class Agency:
    def __init__(self, 
                 communication_paths: List[Tuple[str, str]],
                 shared_instructions: str = None,
                 temperature: float = 0.5,
                 max_prompt_tokens: int = 4000):
        self.paths = set(communication_paths)
        self.shared_instructions = self._load_instructions(shared_instructions)
        self.temperature = temperature
        self.max_tokens = max_prompt_tokens
        self._initialize_agents()

    def _load_instructions(self, path: str) -> str:
        if not path:
            return ""
        with open(path, 'r') as f:
            return f.read()

    def _initialize_agents(self):
        from agents.TechLeadAgent import TechLeadAgent
        from agents.CodeAnalystAgent import CodeAnalystAgent
        from agents.DocReviewerAgent import DocReviewerAgent
        from agents.GitHubAgent import GitHubAgent

        self.agents = {
            "tech_lead": TechLeadAgent(self),
            "code_analyst": CodeAnalystAgent(self),
            "doc_reviewer": DocReviewerAgent(self),
            "github": GitHubAgent(self)
        }

    def can_communicate(self, sender: str, receiver: str) -> bool:
        return (sender, receiver) in self.paths

    async def delegate(self, sender: str, receiver: str, task: Dict[str, Any]) -> Dict:
        if not self.can_communicate(sender, receiver):
            raise ValueError(f"Communication not allowed: {sender} -> {receiver}")
        return await self.agents[receiver].handle_task(task)

    async def handle_task(self, task: Dict) -> Dict:
        initiator = task.get('initiator', 'tech_lead')
        return await self.agents[initiator].handle_task(task)
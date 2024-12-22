import os
from agency_swarm.agents import Agent

class TechLeadAgent(Agent):
    def __init__(self):
        # Get environment variables or use defaults
        max_tokens = int(os.getenv('DOCSMITH_TECHLEAD_MAX_TOKENS', '25000'))
        temperature = float(os.getenv('DOCSMITH_TECHLEAD_TEMPERATURE', '0.3'))

        super().__init__(
            name="TechLeadAgent",
            description="The TechLead agent is responsible for analyzing repositories, coordinating documentation tasks, and ensuring high-quality technical documentation through agent collaboration.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools_folder="./tools",
            temperature=temperature,
            max_prompt_tokens=max_tokens,
        )
import os
from agency_swarm.agents import Agent

class CodeAnalystAgent(Agent):
    def __init__(self):
        # Get environment variables or use defaults
        max_tokens = int(os.getenv('DOCSMITH_ANALYST_MAX_TOKENS', '25000'))
        temperature = float(os.getenv('DOCSMITH_ANALYST_TEMPERATURE', '0.4'))

        super().__init__(
            name="CodeAnalystAgent",
            description="The Code Analyst agent specializes in analyzing source code to provide comprehensive understanding for documentation purposes.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools_folder="./tools",
            temperature=temperature,
            max_prompt_tokens=max_tokens,
        )
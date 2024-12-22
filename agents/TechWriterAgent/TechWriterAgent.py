import os
from agency_swarm.agents import Agent

class TechWriterAgent(Agent):
    def __init__(self):
        # Get environment variables or use defaults
        max_tokens = int(os.getenv('DOCSMITH_WRITER_MAX_TOKENS', '25000'))
        temperature = float(os.getenv('DOCSMITH_WRITER_TEMPERATURE', '0.4'))
        docs_path = os.getenv('DOCSMITH_DOCS_PATH', 'docs/')

        super().__init__(
            name="TechWriterAgent",
            description="The Tech Writer agent specializes in transforming technical analysis into clear, comprehensive documentation.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools_folder="./tools",
            temperature=temperature,
            max_prompt_tokens=max_tokens,
        )
        self.docs_path = docs_path
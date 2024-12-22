import os
from agency_swarm.agents import Agent

class GitHubAgent(Agent):
    def __init__(self):
        # Get environment variables or use defaults
        max_tokens = int(os.getenv('DOCSMITH_GITHUB_MAX_TOKENS', '25000'))
        temperature = float(os.getenv('DOCSMITH_GITHUB_TEMPERATURE', '0.2'))
        github_token = os.getenv('GITHUB_TOKEN')
        base_branch = os.getenv('DOCSMITH_GITHUB_BASE_BRANCH', 'main')
        pr_draft = os.getenv('DOCSMITH_GITHUB_PR_DRAFT', 'false').lower() == 'true'
        pr_labels = os.getenv('DOCSMITH_GITHUB_PR_LABELS', 'documentation,automated').split(',')

        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")

        super().__init__(
            name="GitHubAgent",
            description="The GitHub agent manages all GitHub operations for documentation updates.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools_folder="./tools",
            temperature=temperature,
            max_prompt_tokens=max_tokens,
        )
        
        self.github_token = github_token
        self.base_branch = base_branch
        self.pr_draft = pr_draft
        self.pr_labels = pr_labels
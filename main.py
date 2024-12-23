import asyncio
import sys
import os
from pathlib import Path
from typing import List, Tuple

# Import from core package using absolute imports
from core.utils.logging_config import setup_logger
from core.llm.cost_calculator import cost_tracker
from core.base.agent_manager import agent_manager
from core.base.workflow_manager import workflow_manager
from core.agents.tech_lead import TechLeadAgent
from core.agents.doc_reviewer import DocReviewerAgent
from core.agents.github_agent import GitHubAgent
from core.agents.code_analyst import CodeAnalystAgent

logger = setup_logger(__name__)

class Agency:
    """Central agency for managing agent communication and workflow."""
    
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
        """Initialize all agents with proper communication paths."""
        # Register agents
        agent_manager.register_agent("tech_lead", TechLeadAgent)
        agent_manager.register_agent("doc_reviewer", DocReviewerAgent)
        agent_manager.register_agent("github", GitHubAgent)
        agent_manager.register_agent("code_analyst", CodeAnalystAgent)
        
        # Create agent instances
        self.tech_lead = agent_manager.create_agent("tech_lead", "tech_lead_main")
        self.doc_reviewer = agent_manager.create_agent("doc_reviewer", "doc_reviewer_main")
        self.github_agent = agent_manager.create_agent("github", "github_main")
        self.code_analyst = agent_manager.create_agent("code_analyst", "code_analyst_main")

    def can_communicate(self, sender: str, receiver: str) -> bool:
        """Check if two agents can communicate."""
        return (sender, receiver) in self.paths

    async def delegate(self, sender: str, receiver: str, task: dict) -> dict:
        """Delegate a task from one agent to another."""
        if not self.can_communicate(sender, receiver):
            raise ValueError(f"Communication not allowed: {sender} -> {receiver}")
            
        agent = getattr(self, receiver.replace("-", "_"))
        return await agent.handle_task(task)

    async def process_repository(self, repo_url: str) -> dict:
        """Main entry point for repository processing."""
        logger.info(f"Starting documentation process for {repo_url}")
        
        try:
            # Start with TechLead agent
            result = await self.tech_lead.handle_task({
                "type": "document_repository",
                "repo_url": repo_url
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing repository: {str(e)}")
            raise

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = {
        'OPENAI_API_KEY': 'Set your OpenAI API key',
        'GITHUB_TOKEN': 'Set your GitHub personal access token',
        'GITHUB_USERNAME': 'Set your GitHub username'
    }

    missing = []
    for var, message in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var}: {message}")

    if missing:
        print("Error: Missing required environment variables:")
        for msg in missing:
            print(f"  - {msg}")
        print("\nPlease ensure these variables are set in your environment.")
        sys.exit(1)

async def main(repo_url: str) -> None:
    try:
        # Initialize agency with communication paths
        agency = Agency(
            communication_paths=[
                ("tech_lead", "code_analyst"),
                ("tech_lead", "doc_reviewer"),
                ("tech_lead", "github"),
                ("code_analyst", "doc_reviewer"),
                ("code_analyst", "github"),
                ("doc_reviewer", "code_analyst")
            ],
            shared_instructions='core/agents/agency_manifesto.md'
        )
        
        print(f"\nStarting documentation generation for {repo_url}")
        print("=" * 50)
        
        # Process the repository
        result = await agency.process_repository(repo_url)
        
        # Print results
        print("\nDocumentation Generation Complete!")
        print("-" * 30)
        if "pr_url" in result:
            print(f"Pull Request: {result['pr_url']}")
        
        # Print cost summary
        cost_summary = cost_tracker.get_summary()
        print("\nCost Summary:")
        print("-" * 30)
        print(f"Total Cost: ${cost_summary['total_cost']:.4f}")
        print(f"Total Tokens: {cost_summary['total_tokens']}")
        print(f"Total Requests: {cost_summary['total_requests']}")
        
    except Exception as e:
        logger.error(f"Error processing repository: {str(e)}")
        print(f"\nError: {str(e)}")
        raise

def print_usage():
    print("Usage: python main.py <username/repository>")
    print("Example: python main.py Travbz/consensus-engine")
    sys.exit(1)

if __name__ == "__main__":
    # Check environment
    check_environment()

    if len(sys.argv) != 2:
        print_usage()
    
    # Extract repository URL
    repo_arg = sys.argv[1]
    if "/" not in repo_arg:
        print("Error: Repository must be in format username/repository")
        print_usage()
        
    # Add https:// prefix if not a full URL
    if not repo_arg.startswith(('http://', 'https://', 'git@')):
        repo_url = f"https://github.com/{repo_arg}"
    else:
        repo_url = repo_arg

    try:
        asyncio.run(main(repo_url))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
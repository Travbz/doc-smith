from typing import Dict, Any
import asyncio
from pathlib import Path
from .base import agent_manager, workflow_coordinator
from .utils.logging_config import setup_logger
from .agents.tech_lead import TechLeadAgent
from .agents.doc_reviewer import DocReviewerAgent
from .agents.github_agent import GitHubAgent
from .agents.code_analyst import CodeAnalystAgent
from ...config.settings import MAX_CONCURRENT_TASKS

logger = setup_logger(__name__)

class Orchestrator:
    def __init__(self):
        self.agent_manager = agent_manager
        self.workflow_coordinator = workflow_coordinator
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize all components."""
        # Register agents
        self.agent_manager.register_agent("tech_lead", TechLeadAgent)
        self.agent_manager.register_agent("doc_reviewer", DocReviewerAgent)
        self.agent_manager.register_agent("github", GitHubAgent)
        self.agent_manager.register_agent("code_analyst", CodeAnalystAgent)

    async def process_repository(self, repo_url: str) -> Dict[str, Any]:
        """Process a repository for documentation."""
        logger.info(f"Starting documentation process for {repo_url}")

        try:
            # Start documentation workflow
            workflow_id = await self.workflow_coordinator.start_workflow(
                "documentation",
                {
                    "repo_url": repo_url,
                    "workflow_id": f"doc_{len(self.workflow_coordinator._running_workflows)}"
                }
            )

            # Wait for workflow completion
            result = await self._wait_for_workflow(workflow_id)

            if result["status"] == "success":
                logger.info(f"Successfully generated documentation for {repo_url}")
                logger.info(f"Pull request created: {result['pr_url']}")
                return result
            else:
                error_msg = f"Documentation generation failed: {result.get('error', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"Error processing repository {repo_url}: {str(e)}")
            raise

    async def _wait_for_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Wait for a workflow to complete."""
        while True:
            status = self.workflow_coordinator.get_workflow_status(workflow_id)
            
            if status["status"] in ["completed", "failed"]:
                return self.workflow_coordinator.get_workflow_result(workflow_id)
                
            await asyncio.sleep(1)

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Cancel running workflows
            for workflow_id in self.workflow_coordinator._running_workflows:
                logger.info(f"Cancelling workflow {workflow_id}")
                # Add workflow cancellation logic here

            # Cleanup agents
            self.agent_manager.cleanup()

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise

# Create singleton instance
orchestrator = Orchestrator()
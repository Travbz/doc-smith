from typing import Dict, Any, Optional
from datetime import datetime
import os
from pathlib import Path
from git import Repo
from github import Github
from ...base import BaseAgent
from ...utils.logging_config import setup_logger
from ...utils.error_handler import retry_with_exponential_backoff
from .tools.github_manager import GitHubManager
from ...config.settings import GITHUB_TOKEN, REPO_CLONE_PATH

logger = setup_logger(__name__)

class GitHubAgent(BaseAgent):
    def __init__(self, agency):
        super().__init__("github")
        self.agency = agency
        self.manager = GitHubManager(GITHUB_TOKEN)
        self.repos: Dict[str, Repo] = {}

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitHub-related tasks."""
        task_types = {
            "prepare_repository": self._prepare_repository,
            "create_pull_request": self._create_pull_request,
            "update_documentation": self._update_documentation
        }

        handler = task_types.get(task["type"])
        if not handler:
            raise ValueError(f"Unknown task type: {task['type']}")

        return await handler(task)

    @retry_with_exponential_backoff()
    async def _prepare_repository(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a repository for documentation."""
        repo_url = task["repo_url"]

        # Clone or update repository
        repo_info = await self.manager.setup_repository(repo_url)
        self.repos[repo_url] = repo_info

        # Generate repository metadata using LLM
        metadata = await self._generate_repo_metadata(repo_info)
        repo_info.update(metadata)

        return repo_info

    @retry_with_exponential_backoff()
    async def _create_pull_request(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pull request with documentation changes."""
        repo_url = task["repo_url"]
        documentation = task["documentation"]
        repo_info = self.repos.get(repo_url)

        if not repo_info:
            raise ValueError(f"Repository not prepared: {repo_url}")

        # Create documentation branch
        branch_name = await self.manager.setup_documentation_branch(
            repo_info["path"]
        )

        # Write documentation files
        await self.manager.write_documentation(
            repo_info["path"],
            documentation
        )

        # Create commit and PR
        commit_sha = await self.manager.commit_documentation(
            documentation,
            "docs: Update documentation"
        )

        pr_info = await self.manager.create_pull_request(
            title="Documentation Update",
            body=await self._generate_pr_description(documentation)
        )

        return {
            "pr_number": pr_info["pr_number"],
            "pr_url": pr_info["pr_url"],
            "branch": branch_name,
            "commit": commit_sha
        }

    @retry_with_exponential_backoff()
    async def _update_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update documentation in an existing PR."""
        repo_url = task["repo_url"]
        documentation = task["documentation"]
        pr_number = task["pr_number"]
        repo_info = self.repos.get(repo_url)

        if not repo_info:
            raise ValueError(f"Repository not prepared: {repo_url}")

        # Update documentation files
        await self.manager.write_documentation(
            repo_info["path"],
            documentation
        )

        # Create commit
        commit_sha = await self.manager.commit_documentation(
            documentation,
            "docs: Update documentation based on review"
        )

        return {
            "status": "updated",
            "pr_number": pr_number,
            "commit": commit_sha
        }

    async def _generate_repo_metadata(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate repository metadata using LLM."""
        metadata = await self.get_completion(
            "github",
            "analyze_repository",
            repo_info=repo_info
        )
        return metadata

    async def _generate_pr_description(self, documentation: Dict[str, str]) -> str:
        """Generate pull request description using LLM."""
        description = await self.get_completion(
            "github",
            "generate_pr_description",
            documentation=documentation
        )
        return description
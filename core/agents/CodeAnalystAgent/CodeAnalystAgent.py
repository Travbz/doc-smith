from typing import Dict, Any
from ...base import BaseAgent
from ...utils.logging_config import setup_logger
from ...utils.error_handler import retry_with_exponential_backoff
from .tools.code_analyzer import CodeAnalyzer

logger = setup_logger(__name__)

class CodeAnalystAgent(BaseAgent):
    def __init__(self, agency):
        super().__init__("code_analysis")
        self.agency = agency
        self.analyzer = CodeAnalyzer()

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process tasks for code analysis."""
        task_types = {
            "analyze_repository": self._analyze_repo,
            "update_documentation": self._update_docs,
            "handle_review": self._handle_review
        }
        
        handler = task_types.get(task["type"])
        if not handler:
            raise ValueError(f"Unknown task type: {task['type']}")
            
        return await handler(task)

    @retry_with_exponential_backoff()
    async def _analyze_repo(self, task: Dict) -> Dict:
        """Analyze repository and generate documentation."""
        docs = self._generate_initial_docs(task["repo_info"])
        
        # Get documentation review
        review = await self.agency.delegate("code_analyst", "doc_reviewer", {
            "type": "review_documentation",
            "documentation": docs,
            "repo_info": task["repo_info"]
        })

        if review["status"] == "approved":
            return docs
            
        # If review wasn't approved, handle the review feedback
        return await self._handle_review(review)

    def _generate_initial_docs(self, repo_info: Dict) -> Dict:
        """Generate initial documentation."""
        docs = {
            "README.md": self._generate_readme(repo_info),
            "docs/overview.md": self._generate_overview(repo_info)
        }
        return docs

    async def _generate_readme(self, repo_info: Dict) -> str:
        """Generate README.md using LLM."""
        readme_content = await self.get_completion(
            "code_analysis",
            "generate_readme",
            repo_info=repo_info
        )
        return readme_content

    async def _generate_overview(self, repo_info: Dict) -> str:
        """Generate overview.md using LLM."""
        overview_content = await self.get_completion(
            "code_analysis",
            "generate_overview",
            repo_info=repo_info
        )
        return overview_content

    async def _update_docs(self, task: Dict) -> Dict:
        """Update documentation based on review feedback."""
        docs = task["current_docs"]
        changes = await self._process_feedback(task["review_feedback"])
        return await self._apply_changes(docs, changes)

    async def _process_feedback(self, feedback: Dict) -> Dict:
        """Process review feedback using LLM."""
        processed_feedback = await self.get_completion(
            "code_analysis",
            "process_feedback",
            feedback=feedback
        )
        return processed_feedback

    async def _apply_changes(self, docs: Dict, changes: Dict) -> Dict:
        """Apply changes to documentation."""
        updated_docs = docs.copy()
        
        for file_path, change_list in changes.items():
            if file_path in updated_docs:
                updated_content = await self.get_completion(
                    "code_analysis",
                    "apply_changes",
                    original_content=docs[file_path],
                    changes=change_list
                )
                updated_docs[file_path] = updated_content
                
        return updated_docs

    async def _handle_review(self, review: Dict) -> Dict:
        """Handle review feedback and update documentation."""
        if not review["issues"]:
            return review["documentation"]
            
        changes = await self._process_feedback(review["feedback"])
        return await self._apply_changes(review["documentation"], changes)
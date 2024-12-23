from typing import Dict, Any, List
from ...base import BaseAgent
from ...utils.logging_config import setup_logger
from ...utils.error_handler import retry_with_exponential_backoff
from .tools.doc_reviewer import DocReviewer

logger = setup_logger(__name__)

class DocReviewerAgent(BaseAgent):
    def __init__(self, agency):
        super().__init__("doc_reviewer")
        self.agency = agency
        self.reviewer = DocReviewer()

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process review tasks."""
        task_types = {
            "review_documentation": self._review_documentation,
            "validate_api_docs": self._validate_api_docs
        }

        handler = task_types.get(task["type"])
        if not handler:
            raise ValueError(f"Unknown task type: {task['type']}")

        return await handler(task)

    @retry_with_exponential_backoff()
    async def _review_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review and validate documentation."""
        documentation = task["documentation"]
        repo_info = task.get("repo_info", {})

        # Extract claims for verification
        claims = self.reviewer.extract_claims(documentation)
        verification_results = []

        for claim in claims:
            # Verify each claim against the codebase
            evidence = await self._find_evidence(claim, repo_info)
            result = self.reviewer.verify_claim(claim, evidence)
            verification_results.append(result)

        # Generate feedback based on verification results
        feedback = await self._generate_feedback(verification_results)

        if feedback["requires_changes"]:
            return {
                "status": "needs_revision",
                "feedback": feedback["suggestions"],
                "documentation": documentation,
                "verification": verification_results
            }

        return {
            "status": "approved",
            "documentation": documentation,
            "verification": verification_results
        }

    @retry_with_exponential_backoff()
    async def _validate_api_docs(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API documentation."""
        documentation = task["documentation"]

        # Validate API endpoints
        endpoints = await self._extract_endpoints(documentation)
        validation_results = await self._validate_endpoints(endpoints)

        # Generate feedback for API documentation
        feedback = await self._generate_api_feedback(validation_results)

        if feedback["requires_changes"]:
            return {
                "status": "needs_revision",
                "feedback": feedback["suggestions"],
                "documentation": documentation,
                "validation": validation_results
            }

        return {
            "status": "approved",
            "documentation": documentation,
            "validation": validation_results
        }

    async def _find_evidence(
        self, 
        claim: str, 
        repo_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find supporting evidence for a documentation claim."""
        evidence = await self.get_completion(
            "doc_reviewer",
            "find_evidence",
            claim=claim,
            repo_info=repo_info
        )
        return evidence

    async def _generate_feedback(
        self,
        verification_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate feedback based on verification results."""
        feedback = await self.get_completion(
            "doc_reviewer",
            "generate_feedback",
            verification_results=verification_results
        )
        return feedback

    async def _extract_endpoints(
        self,
        documentation: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Extract API endpoints from documentation."""
        endpoints = await self.get_completion(
            "doc_reviewer",
            "extract_endpoints",
            documentation=documentation
        )
        return endpoints

    async def _validate_endpoints(
        self,
        endpoints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate extracted API endpoints."""
        validation_results = []
        for endpoint in endpoints:
            result = await self.get_completion(
                "doc_reviewer",
                "validate_endpoint",
                endpoint=endpoint
            )
            validation_results.append(result)
        return validation_results

    async def _generate_api_feedback(
        self,
        validation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate feedback for API documentation."""
        feedback = await self.get_completion(
            "doc_reviewer",
            "generate_api_feedback",
            validation_results=validation_results
        )
        return feedback
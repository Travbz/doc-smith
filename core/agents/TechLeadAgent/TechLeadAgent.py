from typing import Dict, Any, List
from ...base import BaseAgent
from ...utils.logging_config import setup_logger
from ...utils.error_handler import retry_with_exponential_backoff
from ...workflows.workflow_coordinator import workflow_coordinator
from .tools.repo_analyzer import RepoAnalyzer

logger = setup_logger(__name__)

class TechLeadAgent(BaseAgent):
    def __init__(self, agency):
        super().__init__("tech_lead")
        self.agency = agency
        self.analyzer = RepoAnalyzer()

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process tasks as the technical lead."""
        task_types = {
            "document_repository": self._document_repository,
            "analyze_architecture": self._analyze_architecture,
            "review_documentation": self._review_documentation_plan,
            "coordinate_updates": self._coordinate_updates
        }

        handler = task_types.get(task["type"])
        if not handler:
            raise ValueError(f"Unknown task type: {task['type']}")

        return await handler(task)

    @retry_with_exponential_backoff()
    async def _document_repository(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate repository documentation process."""
        # Analyze repository first
        repo_analysis = await self._analyze_repository(task)

        # Determine required documentation workflows
        workflows = await self._plan_documentation_workflows(repo_analysis)

        # Execute workflows in appropriate order
        results = {}
        for workflow in workflows:
            workflow_id = await workflow_coordinator.start_workflow(
                workflow["type"],
                {**workflow["params"], "repo_analysis": repo_analysis}
            )
            results[workflow["type"]] = await self._monitor_workflow(workflow_id)

        # Compile final documentation
        return await self._compile_documentation(results)

    async def _analyze_repository(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository structure and characteristics."""
        repo_info = await self.agency.delegate("tech_lead", "github", {
            "type": "prepare_repository",
            "repo_url": task["repo_url"]
        })

        analysis = await self.get_completion(
            "tech_lead",
            "analyze_repository",
            repo_info=repo_info
        )

        return {**repo_info, "analysis": analysis}

    async def _plan_documentation_workflows(
        self,
        repo_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Plan which documentation workflows to run."""
        workflows = [{
            "type": "documentation",
            "params": {"priority": "high"}
        }]

        # Check if API documentation is needed
        if repo_analysis["analysis"].get("has_api", False):
            workflows.append({
                "type": "api_documentation",
                "params": {"priority": "high"}
            })

        # Additional workflows based on repository characteristics
        if repo_analysis["analysis"].get("is_complex", False):
            workflows.append({
                "type": "architecture_documentation",
                "params": {"priority": "high"}
            })

        if repo_analysis["analysis"].get("has_deployment", False):
            workflows.append({
                "type": "deployment_documentation",
                "params": {"priority": "medium"}
            })

        return workflows

    async def _monitor_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Monitor a workflow until completion."""
        while True:
            status = workflow_coordinator.get_workflow_status(workflow_id)
            if status["status"] in ["completed", "failed"]:
                return workflow_coordinator.get_workflow_result(workflow_id)
            await asyncio.sleep(1)

    async def _compile_documentation(
        self,
        workflow_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compile documentation from all workflows."""
        compiled_docs = {}
        
        for workflow_type, result in workflow_results.items():
            if result.get("status") == "completed":
                compiled_docs.update(result.get("documentation", {}))

        # Create pull request with compiled documentation
        pr_info = await self.agency.delegate("tech_lead", "github", {
            "type": "create_pull_request",
            "documentation": compiled_docs
        })

        return {
            "status": "completed",
            "documentation": compiled_docs,
            "pr_info": pr_info
        }

    @retry_with_exponential_backoff()
    async def _analyze_architecture(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository architecture."""
        arch_analysis = await self.analyzer.analyze_architecture(
            task["repo_path"]
        )

        # Enhance analysis with LLM insights
        enhanced_analysis = await self.get_completion(
            "tech_lead",
            "analyze_architecture",
            analysis=arch_analysis
        )

        return enhanced_analysis

    async def _review_documentation_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review and validate documentation plan."""
        plan_review = await self.get_completion(
            "tech_lead",
            "review_doc_plan",
            plan=task["documentation_plan"],
            repo_analysis=task["repo_analysis"]
        )

        if plan_review.get("needs_changes", False):
            updated_plan = await self._revise_documentation_plan(
                task["documentation_plan"],
                plan_review["suggestions"]
            )
            return {
                "status": "revised",
                "plan": updated_plan
            }

        return {
            "status": "approved",
            "plan": task["documentation_plan"]
        }

    async def _coordinate_updates(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate documentation updates."""
        current_docs = task["current_documentation"]
        required_updates = task["required_updates"]

        # Plan updates
        update_plan = await self.get_completion(
            "tech_lead",
            "plan_updates",
            current_docs=current_docs,
            required_updates=required_updates
        )

        # Execute updates through appropriate agents
        updated_docs = await self._execute_update_plan(update_plan)

        return {
            "status": "completed",
            "documentation": updated_docs
        }

    async def _execute_update_plan(
        self,
        update_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a documentation update plan."""
        results = {}
        
        for update in update_plan["updates"]:
            result = await self.agency.delegate(
                "tech_lead",
                update["agent"],
                {
                    "type": update["type"],
                    **update["params"]
                }
            )
            results[update["id"]] = result

        return self._merge_update_results(results)
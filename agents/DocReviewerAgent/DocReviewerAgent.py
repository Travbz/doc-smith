from typing import Dict, Any
import json
from .tools.doc_reviewer import DocReviewer

class DocReviewerAgent:
    def __init__(self, agency):
        self.agency = agency
        self.reviewer = DocReviewer()

    async def handle_task(self, task: Dict[str, Any]) -> Dict:
        if task["type"] != "review_documentation":
            raise ValueError(f"Unknown task type: {task['type']}")

        review_result = self.reviewer.review_documentation(
            task["documentation"],
            task["repo_info"]
        )

        if review_result["status"] == "needs_revision":
            await self.agency.delegate("doc_reviewer", "code_analyst", {
                "type": "handle_review",
                "review": review_result
            })

        return review_result
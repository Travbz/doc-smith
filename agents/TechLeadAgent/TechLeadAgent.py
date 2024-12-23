from typing import Dict, Any

class TechLeadAgent:
    def __init__(self, agency):
        self.agency = agency

    async def handle_task(self, task: Dict[str, Any]) -> Dict:
        if task["type"] == "document_repository":
            # TechLead delegates to GitHub agent
            repo_info = await self.agency.delegate("tech_lead", "github", {
                "type": "prepare_repository",
                "repo_url": task["repo_url"]
            })
            
            # TechLead delegates to CodeAnalyst
            docs = await self.agency.delegate("tech_lead", "code_analyst", {
                "type": "analyze_repository",
                "repo_info": repo_info
            })
            
            return docs
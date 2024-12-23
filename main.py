import asyncio
from agents.agency import Agency
from typing import Dict

async def main(repo_url: str) -> Dict:
    agency = Agency(
        communication_paths=[
            ("tech_lead", "code_analyst"),
            ("tech_lead", "doc_reviewer"),
            ("tech_lead", "github"),
            ("code_analyst", "doc_reviewer"),
            ("code_analyst", "github"),
            ("doc_reviewer", "code_analyst")
        ],
        shared_instructions='agents/agency_manifesto.md',
        temperature=0.5,
        max_prompt_tokens=4000
    )
    
    task = {
        "type": "document_repository",
        "repo_url": repo_url,
        "initiator": "tech_lead"
    }
    
    return await agency.handle_task(task)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py username/repository")
        sys.exit(1)
    
    repo_url = f"https://github.com/{sys.argv[1]}"
    result = asyncio.run(main(repo_url))
    print(result)
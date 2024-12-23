from typing import Dict, Any
import git
import tempfile
import os

class GitHubAgent:
    def __init__(self, agency):
        self.agency = agency

    async def handle_task(self, task: Dict[str, Any]) -> Dict:
        task_types = {
            "prepare_repository": self._prepare_repo,
            "create_pull_request": self._create_pr
        }
        
        handler = task_types.get(task["type"])
        if not handler:
            raise ValueError(f"Unknown task type: {task['type']}")
        return await handler(task)

    async def _prepare_repo(self, task: Dict) -> Dict:
        temp_dir = tempfile.mkdtemp()
        repo = git.Repo.clone_from(task["repo_url"], temp_dir)
        return {
            "repo_path": temp_dir,
            "default_branch": repo.active_branch.name,
            "repo_url": task["repo_url"]
        }

    async def _create_pr(self, task: Dict) -> Dict:
        repo_info = task["repo_info"]
        docs = task["documentation"]
        
        repo = git.Repo(repo_info["repo_path"])
        branch = f"docs/auto-generated-{os.urandom(4).hex()}"
        
        repo.git.checkout('-b', branch)
        self._write_documentation(repo_info["repo_path"], docs)
        repo.index.add('*')
        repo.index.commit("docs: Add auto-generated documentation")
        
        return {"branch": branch, "files": list(docs.keys())}

    def _write_documentation(self, repo_path: str, docs: Dict) -> None:
        for file_path, content in docs.items():
            full_path = os.path.join(repo_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
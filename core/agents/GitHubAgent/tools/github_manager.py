from github import Github
from git import Repo
import os
from typing import Dict, List, Any
from datetime import datetime

class GitHubManager:
    """Tool for managing GitHub operations."""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GitHub token not provided and GITHUB_TOKEN env var not set")
        self.github = Github(self.github_token)

    def setup_documentation_branch(self, repo_path: str, branch_name: str = None) -> str:
        """Create and checkout documentation branch."""
        self.repo = Repo(repo_path)
        
        if branch_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"{os.getenv('DOCSMITH_GITHUB_BRANCH_PREFIX', 'docs/update_')}{timestamp}"
        
        current = self.repo.active_branch
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()
        
        return branch_name

    def commit_documentation(self, files: List[Dict[str, str]], message: str = None) -> str:
        """Commit documentation changes."""
        if message is None:
            message = os.getenv('DOCSMITH_GITHUB_COMMIT_MESSAGE', 
                              'Update documentation\n\nAutomatically generated by DocSmith')
        
        docs_dir = os.path.join(self.repo.working_dir, 
                               os.getenv('DOCSMITH_DOCS_PATH', 'docs/'))
        os.makedirs(docs_dir, exist_ok=True)
        
        for file_info in files:
            original_path = file_info['file']
            relative_path = os.path.relpath(original_path, self.repo.working_dir)
            doc_path = os.path.join(docs_dir, f"{relative_path}.md")
            
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)
            
            with open(doc_path, 'w') as f:
                f.write(file_info['documentation'])
            
            self.repo.index.add([doc_path])
        
        if self.repo.is_dirty():
            commit = self.repo.index.commit(message)
            return commit.hexsha
        
        return None

    def create_pull_request(self, title: str = None, body: str = None) -> Dict[str, Any]:
        """Create pull request with documentation changes."""
        if title is None:
            title = os.getenv('DOCSMITH_GITHUB_PR_TITLE', 'Documentation Update')
        
        if body is None:
            body = os.getenv('DOCSMITH_GITHUB_PR_BODY', '''
## Documentation Update

This PR contains automatically generated documentation updates from DocSmith.

### Changes
- Updated documentation files
- Generated API references
- Added usage examples
- Updated setup instructions

Please review the changes and ensure they meet the project's documentation standards.
''')
        
        remote_url = self.repo.remotes.origin.url
        repo_name = self._get_repo_name(remote_url)
        github_repo = self.github.get_repo(repo_name)
        
        base_branch = os.getenv('DOCSMITH_GITHUB_BASE_BRANCH', 'main')
        draft = os.getenv('DOCSMITH_GITHUB_PR_DRAFT', 'false').lower() == 'true'
        labels = os.getenv('DOCSMITH_GITHUB_PR_LABELS', 'documentation,automated').split(',')
        reviewers = os.getenv('DOCSMITH_GITHUB_REVIEWERS', '').split(',')
        
        pr = github_repo.create_pull(
            title=title,
            body=body,
            head=self.repo.active_branch.name,
            base=base_branch,
            draft=draft
        )
        
        if labels:
            pr.add_to_labels(*labels)
        
        if reviewers and reviewers[0]:  # Only add reviewers if the list is not empty
            pr.create_review_request(reviewers=reviewers)
        
        return {
            "pr_number": pr.number,
            "pr_url": pr.html_url,
            "branch": self.repo.active_branch.name
        }

    def _get_repo_name(self, remote_url: str) -> str:
        """Extract repository name from remote URL."""
        if remote_url.startswith('https'):
            parts = remote_url.split('/')
            return f"{parts[-2]}/{parts[-1].replace('.git', '')}"
        else:
            parts = remote_url.split(':')[1]
            return parts.replace('.git', '')
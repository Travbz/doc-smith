from github import Github
from typing import Dict, List, Any
import os
from fnmatch import fnmatch
from pathlib import Path

class RepoAnalyzer:
    """Tool for analyzing repository structure and content using GitHub API."""
    
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GitHub token not provided and GITHUB_TOKEN env var not set")
        self.github = Github(self.github_token)

    def analyze_repository(self, repo_path_or_url: str) -> Dict[str, Any]:
        """
        Analyze repository and generate documentation tasks.
        
        Args:
            repo_path_or_url: Local path or GitHub URL of the repository
            
        Returns:
            Dict containing repository structure and tasks
        """
        if repo_path_or_url.startswith(('http://', 'https://', 'git@')):
            return self._analyze_remote_repo(repo_path_or_url)
        else:
            return self._analyze_local_repo(repo_path_or_url)

    def _analyze_remote_repo(self, repo_url: str) -> Dict[str, Any]:
        """Analyze a remote GitHub repository."""
        # Extract owner/repo from URL
        if repo_url.startswith('git@'):
            parts = repo_url.split(':')[1].replace('.git', '').split('/')
        else:
            parts = repo_url.split('/')[-2:]
        owner, repo_name = parts

        repo = self.github.get_repo(f"{owner}/{repo_name}")
        contents = repo.get_contents("")
        structure = {}
        tasks = []

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                if self._should_document(file_content.path):
                    relative_path = file_content.path
                    self._add_to_structure(structure, relative_path)
                    tasks.append({
                        "type": "documentation",
                        "file_path": relative_path,
                        "priority": self._calculate_priority(relative_path),
                        "url": file_content.html_url,
                        "sha": file_content.sha
                    })

        return {
            "structure": structure,
            "tasks": sorted(tasks, key=lambda x: x['priority'], reverse=True)
        }

    def _analyze_local_repo(self, repo_path: str) -> Dict[str, Any]:
        """Analyze a local repository."""
        structure = {}
        tasks = []
        repo_path = Path(repo_path)

        for filepath in repo_path.rglob('*'):
            if filepath.is_file() and self._should_document(filepath.name):
                relative_path = str(filepath.relative_to(repo_path))
                self._add_to_structure(structure, relative_path)
                tasks.append({
                    "type": "documentation",
                    "file_path": relative_path,
                    "priority": self._calculate_priority(relative_path)
                })

        return {
            "structure": structure,
            "tasks": sorted(tasks, key=lambda x: x['priority'], reverse=True)
        }

    def _should_document(self, filename: str) -> bool:
        """Check if file should be documented."""
        include_patterns = os.getenv('DOCSMITH_INCLUDE_PATTERNS', '*.py,*.js,*.ts,*.jsx,*.tsx').split(',')
        exclude_patterns = os.getenv('DOCSMITH_EXCLUDE_PATTERNS', '*_test.*,*.test.*,*/__pycache__/*').split(',')
        
        return (any(fnmatch(filename, pattern) for pattern in include_patterns) and
                not any(fnmatch(filename, pattern) for pattern in exclude_patterns))

    def _add_to_structure(self, structure: Dict, path: str) -> None:
        """Add file to structure dictionary."""
        parts = path.split('/')
        current = structure
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = 'file'

    def _calculate_priority(self, file_path: str) -> int:
        """Calculate documentation priority for a file."""
        priority = 1
        path_lower = file_path.lower()
        
        # Core/source files
        if any(p in path_lower for p in ['src/', 'lib/', 'core/']):
            priority += 3
        
        # Public APIs
        if any(p in path_lower for p in ['api/', 'public/', 'interface']):
            priority += 3
        
        # Main/index files
        if any(p in path_lower for p in ['main', 'index', 'app']):
            priority += 2
        
        # Tests (lower priority)
        if 'test' in path_lower:
            priority -= 1
        
        return max(priority, 0)
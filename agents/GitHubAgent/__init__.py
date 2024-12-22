from git import Repo
from github import Github
import tempfile
import os
import shutil
from datetime import datetime

class GitHubAgent:
    def __init__(self):
        print("🔧 Initializing GitHub agent...")
        self.temp_dir = None
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        self.gh = Github(self.github_token)
        
    def _format_auth_url(self, repo_url: str) -> str:
        """Format GitHub URL with token authentication"""
        if repo_url.startswith("https://"):
            clean_url = repo_url.replace("https://", "").split("@")[-1]
            return f"https://x-access-token:{self.github_token}@{clean_url}"
            
        if "/" in repo_url and len(repo_url.split("/")) == 2:
            return f"https://x-access-token:{self.github_token}@github.com/{repo_url}.git"
            
        return repo_url
        
    def _clone_repository(self, repo_url: str, branch: str) -> str:
        """Clone repository to temporary directory"""
        auth_url = self._format_auth_url(repo_url)
        safe_url = repo_url if repo_url.startswith("https://") else f"https://github.com/{repo_url}"
        print(f"📥 Cloning repository from {safe_url} (branch: {branch})")
        self.temp_dir = tempfile.mkdtemp()
        print(f"📁 Using temporary directory: {self.temp_dir}")
        
        repo = Repo.clone_from(auth_url, self.temp_dir, branch=branch)
        with repo.config_writer() as git_config:
            git_config.set_value('credential', 'helper', '')
            
        print("✅ Repository cloned successfully")
        return self.temp_dir
        
    def _create_documentation_branch(self, base_branch: str) -> str:
        """Create a new branch for documentation updates"""
        print(f"🌿 Creating new documentation branch from {base_branch}")
        repo = Repo(self.temp_dir)
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
        new_branch = f"docsmith-update-{timestamp}"
        current = repo.create_head(new_branch)
        current.checkout()
        print(f"✅ Created and checked out branch: {new_branch}")
        return new_branch
        
    def _commit_and_push_changes(self, message: str):
        """Commit and push documentation changes"""
        print("📝 Staging documentation changes...")
        repo = Repo(self.temp_dir)
        
        repo.git.add(A=True)
        
        print(f"💾 Committing changes: {message}")
        repo.index.commit(message)
        
        print("📤 Pushing changes to remote...")
        origin = repo.remote(name='origin')
        current = repo.active_branch
        print(f"🔄 Setting upstream branch for {current.name}")
        
        try:
            auth_url = self._format_auth_url(origin.url)
            origin.set_url(auth_url)
            
            repo.git.push('--set-upstream', 'origin', current.name)
            print("✅ Changes pushed successfully")
        except Exception as e:
            print(f"❌ Push failed: {str(e)}")
            raise

    def _create_pull_request(self, repo_url: str, branch: str, title: str, body: str) -> dict:
        """Create pull request with documentation changes"""
        print("🔄 Creating pull request...")
        
        # Extract owner and repo from URL
        parts = repo_url.split('/')
        if repo_url.startswith("https://"):
            owner, repo_name = parts[-2], parts[-1].replace(".git", "")
        else:
            owner, repo_name = parts[0], parts[1].replace(".git", "")
            
        try:
            gh_repo = self.gh.get_repo(f"{owner}/{repo_name}")
            default_branch = gh_repo.default_branch
            
            pr = gh_repo.create_pull(
                title=title,
                body=body,
                head=branch,
                base=default_branch
            )
            print(f"✨ Pull request created successfully: {pr.html_url}")
            
            return {
                "pr_url": pr.html_url,
                "pr_number": pr.number
            }
        except Exception as e:
            print(f"❌ Failed to create PR: {str(e)}")
            raise
            
    def cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            print(f"🧹 Cleaning up temporary directory: {self.temp_dir}")
            shutil.rmtree(self.temp_dir)
            print("✅ Cleanup complete")

    async def handle_task(self, task: str, context: dict) -> dict:
        """Handle GitHub-related tasks"""
        print(f"\n📋 GitHub Agent handling task: {task}")
        
        if task == "Prepare repository for documentation updates":
            print("🚀 Starting repository preparation...")
            repo_url = context["repo_url"]
            branch = context.get("base_branch", "main")
            repo_path = self._clone_repository(repo_url, branch)
            doc_branch = self._create_documentation_branch(branch)
            return {
                "repo_path": repo_path,
                "branch": doc_branch,
                "url": repo_url
            }
            
        elif task == "Create pull request with documentation":
            print("🚀 Starting documentation process...")
            documentation = context["documentation"]
            repo_context = context["repo"]
            config = context["config"]
            
            print(f"📝 Writing {len(documentation)} documentation files...")
            for filename, content in documentation.items():
                file_path = os.path.join(repo_context["repo_path"], filename)
                print(f"  ↪ Writing: {filename}")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                # Write content with proper newlines and encoding
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
            
            # Commit and push changes
            self._commit_and_push_changes("Add comprehensive documentation via DocSmith")
            
            # Create PR
            pr_info = self._create_pull_request(
                repo_context["url"],
                repo_context["branch"],
                config.get("pr_title", "Add Comprehensive Documentation"),
                config.get("pr_body", "Adding comprehensive documentation via DocSmith")
            )
            
            self.cleanup()
            return pr_info
        
        else:
            print(f"❌ Error: Unknown task: {task}")
            raise ValueError(f"Unknown task: {task}")
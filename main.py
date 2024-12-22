#!/usr/bin/env python3
import asyncio
import argparse
from agents.agency import DocSmithAgency
import sys
import os
from typing import Optional

def normalize_repo_url(repo: str) -> str:
    """Convert various GitHub repo formats to full HTTPS URL"""
    # If it's already a full URL, return it
    if repo.startswith(('http://', 'https://', 'git@')):
        return repo
    
    # If it's in format owner/repo
    if '/' in repo and len(repo.split('/')) == 2:
        return f"https://github.com/{repo}"
    
    raise ValueError("Repository must be a full URL or in format 'owner/repo'")

async def main(repo: str, branch: Optional[str] = None) -> None:
    try:
        repo_url = normalize_repo_url(repo)
        agency = DocSmithAgency()
        
        result = await agency.document_repository({
            "repo_url": repo_url,
            "base_branch": branch or "main",
            "pr_title": "Add Comprehensive Documentation",
            "pr_body": """
## Documentation Update via DocSmith

This PR adds comprehensive documentation based on actual codebase analysis.
Each documented feature has been verified against the implementation.
            """
        })
        
        if result["status"] == "success":
            print("\n✅ Documentation generation completed!")
            print(f"📝 PR URL: {result['pr_info']}")
        else:
            print("\n❌ Documentation generation failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate documentation for a GitHub repository')
    parser.add_argument('repository', help='GitHub repository URL or owner/repo format')
    parser.add_argument('--branch', '-b', help='Base branch (defaults to main)', default=None)
    
    args = parser.parse_args()
    
    # Ensure required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        sys.exit(1)
        
    if not os.getenv("GITHUB_TOKEN"):
        print("❌ Error: GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    asyncio.run(main(args.repository, args.branch))
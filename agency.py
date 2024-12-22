from openai import AsyncOpenAI
from typing import Dict, List
import json
import os
from agents.GitHubAgent import GitHubAgent
import re
import tiktoken
import asyncio
import sys
sys.setrecursionlimit(10000)  # Increase if needed

def get_repository_structure(repo_path: str) -> Dict:
    """Get the complete repository structure including directories"""
    structure = {
        "directories": set(),
        "files": {},
        "tree": {}
    }
    
    def add_to_tree(path_parts: List[str], current_dict: Dict) -> None:
        if not path_parts:
            return
        current = path_parts[0]
        if current not in current_dict:
            current_dict[current] = {}
        if len(path_parts) > 1:
            add_to_tree(path_parts[1:], current_dict[current])

    for root, dirs, files in os.walk(repo_path):
        # Add directories
        for dir_name in dirs:
            dir_path = os.path.relpath(os.path.join(root, dir_name), repo_path)
            structure["directories"].add(dir_path)
            add_to_tree(dir_path.split(os.sep), structure["tree"])
            
        # Add and read files
        for file_name in files:
            if file_name.endswith(('.py', '.js', '.ts', '.go', '.rs', '.java', '.md', '.yml', '.yaml', '.json')):
                try:
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, repo_path)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        structure["files"][relative_path] = content
                        add_to_tree(relative_path.split(os.sep), structure["tree"])
                except Exception as e:
                    print(f"⚠️ Failed to read {file_name}: {str(e)}")
    
    # Convert sets to lists for JSON serialization
    structure["directories"] = sorted(list(structure["directories"]))
    
    return structure

def extract_json_from_response(text: str) -> dict:
    """Extract JSON from response, handling various formats"""
    # Try parsing as raw JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from code block
        if "```json" in text:
            try:
                json_str = text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            except (IndexError, json.JSONDecodeError):
                pass
        
        # Try to extract anything that looks like JSON
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
            
        raise ValueError(f"Could not parse JSON from response: {text[:200]}...")

class Agent:
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions
        print(f"🤖 Initializing {name} agent...")
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
        
    async def execute(self, task: str, context: Dict = None, max_tokens: int = 15000) -> str:
        print(f"\n📋 {self.name} executing task: {task}")
        
        if context and 'files' in context:
            chunks = self.chunk_files(context['files'], max_tokens)
            results = []
            
            for i, chunk in enumerate(chunks, 1):
                print(f"\n📦 Processing chunk {i}/{len(chunks)} ({len(chunk)} files)")
                chunk_context = context.copy()
                chunk_context['files'] = chunk
                chunk_context['chunk_info'] = {
                    'current': i,
                    'total': len(chunks),
                    'files_in_chunk': list(chunk.keys())
                }
                
                response = await self._execute_single(task, chunk_context)
                results.append(response)
                
            return self.combine_results(results)
            
        return await self._execute_single(task, context)
            
    def chunk_files(self, files: Dict[str, str], max_tokens: int) -> List[Dict[str, str]]:
        """Split files into chunks that fit within token limit"""
        chunks = []
        current_chunk = {}
        current_tokens = self.count_tokens(self.instructions + "Context: {}")
        
        sorted_files = sorted(files.items(), key=lambda x: len(x[1]), reverse=True)
        
        for filepath, content in sorted_files:
            file_tokens = self.count_tokens(content)
            if current_tokens + file_tokens > max_tokens and current_chunk:
                chunks.append(current_chunk)
                current_chunk = {}
                current_tokens = self.count_tokens(self.instructions + "Context: {}")
            
            current_chunk[filepath] = content
            current_tokens += file_tokens
            
        if current_chunk:
            chunks.append(current_chunk)
            
        print(f"📦 Split into {len(chunks)} chunks")
        return chunks
        
    async def _execute_single(self, task: str, context: Dict = None) -> str:
        """Execute a single API call"""
        message_content = task
        if context:
            context_str = json.dumps(context, default=str)
            message_content += f"\nContext: {context_str}"
        
        print(f"🔄 {self.name} thinking...")    
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            max_tokens=4096,
            messages=[
                {
                    "role": "system",
                    "content": self.instructions
                },
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        )
        
        return response.choices[0].message.content
        
    def combine_results(self, results: List[str]) -> str:
        """Combine results from multiple chunks"""
        combined = {}
        
        for result in results:
            try:
                chunk_data = extract_json_from_response(result)
                if isinstance(chunk_data, dict):
                    combined.update(chunk_data)
            except (json.JSONDecodeError, ValueError):
                print(f"⚠️ Failed to parse chunk result as JSON")
                return "\n\n".join(results)
                
        return json.dumps(combined)

class DocSmithAgency:
    def __init__(self):
        print("\n🏢 Initializing DocSmith Agency...")
        print("🔄 Loading agent instructions...")
        
        self.tech_lead = Agent(
            name="TechLead",
            instructions=open("agents/TechLeadAgent/instructions.md").read()
        )
        self.code_analyst = Agent(
            name="CodeAnalyst",
            instructions=open("agents/CodeAnalystAgent/instructions.md").read()
        )
        self.tech_writer = Agent(
            name="TechWriter",
            instructions=open("agents/TechWriterAgent/instructions.md").read()
        )
        self.github_agent = GitHubAgent()
        print("✅ All agents initialized successfully")
        
    async def document_repository(self, config: dict) -> Dict:
        """Main entry point for repository documentation"""
        print(f"\n🚀 Starting documentation generation for: {config['repo_url']}")
        
        try:
            # Step 1: TechLead analyzes repository structure and creates documentation plan
            print("\n📊 Step 1: Technical Analysis")
            analysis = await self.tech_lead.execute(
                f"Analyze repository and create documentation plan",
                context=config
            )
            print("✅ Repository analysis complete")

            # Step 2: GitHub agent prepares repository
            print("\n📦 Step 2: Repository Preparation")
            repo_context = await self.github_agent.handle_task(
                "Prepare repository for documentation updates",
                config
            )
            print("✅ Repository preparation complete")
            
            # Read repository contents and structure
            print("\n📖 Reading repository contents...")
            repo_structure = get_repository_structure(repo_context["repo_path"])
            print(f"✅ Found {len(repo_structure['directories'])} directories and {len(repo_structure['files'])} files")
            print("\n📂 Repository structure:")
            print("\n".join(f"  {'DIR' if path in repo_structure['directories'] else 'FILE'}: {path}" 
                          for path in sorted(list(repo_structure['directories']) + list(repo_structure['files'].keys()))))

            # Step 3: CodeAnalyst performs detailed code analysis
            print("\n🔍 Step 3: Code Analysis")
            code_analysis = await self.code_analyst.execute(
                "Perform detailed code analysis based on repository contents",
                context={
                    "analysis": analysis,
                    "repo": repo_context,
                    "files": repo_structure["files"],
                    "structure": {
                        "directories": repo_structure["directories"],
                        "tree": repo_structure["tree"]
                    }
                }
            )
            print("✅ Code analysis complete")

            # Step 4: TechWriter transforms analyses into comprehensive documentation
            print("\n📝 Step 4: Documentation Generation")
            documentation_str = await self.tech_writer.execute(
                "Transform code analysis into comprehensive documentation",
                context={
                    "analysis": analysis,
                    "code_analysis": code_analysis,
                    "repo": repo_context
                }
            )
            
            # Parse the documentation JSON
            try:
                print("🔄 Parsing documentation output...")
                documentation = extract_json_from_response(documentation_str)
                print(f"✅ Successfully parsed {len(documentation)} documentation files")
                
                # Validate documentation structure
                if not isinstance(documentation, dict):
                    raise ValueError("Documentation must be a dictionary")
                
                # Check each file path and content
                for path, content in documentation.items():
                    if not isinstance(path, str) or not path.endswith('.md'):
                        raise ValueError(f"Invalid documentation file path: {path}")
                    if not isinstance(content, str):
                        raise ValueError(f"Invalid content type for {path}")
                    
            except Exception as e:
                print(f"❌ Error processing documentation output: {str(e)}")
                print("📝 Documentation format error. Raw output preview:", str(documentation_str)[:200] + "...")
                raise
                
            print("✅ Documentation generation and validation complete")

            # Step 5: GitHub agent creates PR with documentation
            print("\n🔄 Step 5: Creating Pull Request")
            pr_info = await self.github_agent.handle_task(
                "Create pull request with documentation",
                {
                    "documentation": documentation,
                    "repo": repo_context,
                    "config": config
                }
            )
            print("✅ Pull request creation complete")

            result = {
                "status": "success",
                "analysis": analysis,
                "code_analysis": code_analysis,
                "documentation": documentation,
                "pr_info": pr_info
            }
            
            print("\n🎉 Documentation process completed successfully!")
            return result
            
        except Exception as e:
            print(f"\n❌ Error during documentation generation:")
            print(f"  ↪ {str(e)}")
            raise
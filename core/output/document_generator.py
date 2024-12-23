from typing import Dict, Any, List
from pathlib import Path
import os
from ..utils.logging_config import setup_logger

logger = setup_logger(__name__)

class DocumentGenerator:
    """Handles the generation and organization of documentation files."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_documentation(
        self,
        content: Dict[str, Any],
        repo_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate all documentation files."""
        docs = {}
        
        # Generate README
        readme = self._generate_readme(content, repo_info)
        docs["README.md"] = readme
        
        # Generate API documentation if present
        if content.get("has_api"):
            api_docs = self._generate_api_docs(content["api_spec"])
            docs["docs/api.md"] = api_docs
            
        # Generate architecture documentation
        arch_docs = self._generate_architecture_docs(content)
        docs["docs/architecture.md"] = arch_docs
        
        # Generate setup documentation
        setup_docs = self._generate_setup_docs(content)
        docs["docs/setup.md"] = setup_docs
        
        # Write files to disk
        self._write_documentation(docs)
        
        return docs
        
    def _generate_readme(
        self,
        content: Dict[str, Any],
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate README.md content."""
        template = """# {title}

{description}

## Features
{features}

## Installation
{installation}

## Usage
{usage}

## Documentation
For more detailed documentation, see:
{doc_links}

## Contributing
{contributing}

## License
{license}
"""
        features = "\n".join([f"- {feature}" for feature in content.get("features", [])])
        doc_links = "\n".join([f"- [{name}]({path})" for name, path in content.get("doc_links", {}).items()])
        
        return template.format(
            title=repo_info["name"],
            description=content.get("description", ""),
            features=features,
            installation=content.get("installation", ""),
            usage=content.get("usage", ""),
            doc_links=doc_links,
            contributing=content.get("contributing", ""),
            license=content.get("license", "")
        )
        
    def _generate_api_docs(self, api_spec: Dict[str, Any]) -> str:
        """Generate API documentation."""
        template = """# API Documentation

{description}

## Endpoints

{endpoints}

## Authentication
{auth}

## Error Handling
{errors}
"""
        endpoints = []
        for endpoint in api_spec.get("endpoints", []):
            endpoints.append(f"""### {endpoint['method']} {endpoint['path']}
{endpoint.get('description', '')}

**Parameters:**
{self._format_parameters(endpoint.get('parameters', []))}

**Response:**
```json
{endpoint.get('response_example', '{}')}
```
""")
            
        return template.format(
            description=api_spec.get("description", ""),
            endpoints="\n".join(endpoints),
            auth=api_spec.get("authentication", ""),
            errors=api_spec.get("error_handling", "")
        )
        
    def _generate_architecture_docs(self, content: Dict[str, Any]) -> str:
        """Generate architecture documentation."""
        template = """# Architecture Documentation

{overview}

## System Components
{components}

## Data Flow
{data_flow}

## Dependencies
{dependencies}

## Deployment
{deployment}
"""
        components = "\n".join([
            f"### {comp['name']}\n{comp['description']}"
            for comp in content.get("components", [])
        ])
        
        return template.format(
            overview=content.get("architecture_overview", ""),
            components=components,
            data_flow=content.get("data_flow", ""),
            dependencies=content.get("dependencies", ""),
            deployment=content.get("deployment", "")
        )
        
    def _generate_setup_docs(self, content: Dict[str, Any]) -> str:
        """Generate setup documentation."""
        template = """# Setup Guide

{overview}

## Prerequisites
{prerequisites}

## Installation Steps
{installation}

## Configuration
{configuration}

## Development Setup
{development}

## Testing
{testing}
"""
        return template.format(
            overview=content.get("setup_overview", ""),
            prerequisites=content.get("prerequisites", ""),
            installation=content.get("installation_steps", ""),
            configuration=content.get("configuration_guide", ""),
            development=content.get("development_setup", ""),
            testing=content.get("testing_guide", "")
        )
        
    def _write_documentation(self, docs: Dict[str, str]) -> None:
        """Write documentation files to disk."""
        for path, content in docs.items():
            file_path = self.output_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """Format API parameters into markdown table."""
        if not parameters:
            return "No parameters required."
            
        rows = ["| Name | Type | Required | Description |",
                "|------|------|----------|-------------|"]
                
        for param in parameters:
            rows.append(
                f"| {param['name']} | {param['type']} | "
                f"{param['required']} | {param['description']} |"
            )
            
        return "\n".join(rows)
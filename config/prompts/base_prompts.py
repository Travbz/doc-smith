from typing import Dict, Any
from pathlib import Path
import json

class PromptTemplate:
    def __init__(self, template: str, **default_params: Any):
        self.template = template
        self.default_params = default_params
    
    def format(self, **kwargs: Any) -> str:
        """Format the prompt template with given parameters."""
        params = {**self.default_params, **kwargs}
        return self.template.format(**params)

# Code Analysis Prompts
CODE_ANALYSIS_PROMPTS = {
    "analyze_file": PromptTemplate(
        """Analyze the following code file and provide:
1. Main purpose and functionality
2. Key components and their relationships
3. Important patterns or practices used
4. Potential documentation points

Code:
{code}
"""),
    
    "detect_patterns": PromptTemplate(
        """Identify architectural and design patterns in the following code:
1. Common design patterns (e.g., Singleton, Factory, etc.)
2. Architectural patterns (e.g., MVC, MVVM, etc.)
3. coding patterns and practices

Code:
{code}
""")
}

# Architecture Analysis Prompts
ARCHITECTURE_PROMPTS = {
    "system_overview": PromptTemplate(
        """Analyze the system architecture based on the following components:
1. Component relationships and dependencies
2. Data flow and communication patterns
3. Key architectural decisions
4. System boundaries and interfaces

Components:
{components}
"""),
    
    "component_analysis": PromptTemplate(
        """Provide a detailed analysis of the following component:
1. Purpose and responsibilities
2. Integration points
3. Dependencies
4. Key implementation details

Component:
{component}
""")
}

# Documentation Prompts
DOCUMENTATION_PROMPTS = {
    "generate_readme": PromptTemplate(
        """Create a comprehensive README.md for the project:
1. Project overview and purpose
2. Key features and capabilities
3. Installation and setup instructions
4. Usage examples and guidelines

Project Details:
{project_details}
"""),
    
    "api_documentation": PromptTemplate(
        """Generate API documentation for the following endpoints:
1. Endpoint descriptions
2. Request/response formats
3. Authentication requirements
4. Example usage

API Details:
{api_details}
""")
}

# Review Prompts
REVIEW_PROMPTS = {
    "review_documentation": PromptTemplate(
        """Review the following documentation for:
1. Technical accuracy
2. Completeness
3. Clarity and understandability
4. Consistency with best practices

Documentation:
{documentation}
"""),
    
    "suggest_improvements": PromptTemplate(
        """Suggest improvements for the following documentation:
1. Content organization
2. Missing information
3. Clarity enhancements
4. Additional examples needed

Current Documentation:
{documentation}
""")
}

def load_prompt_template(prompt_type: str, prompt_name: str) -> PromptTemplate:
    """Load a prompt template by type and name."""
    prompts_map = {
        "code_analysis": CODE_ANALYSIS_PROMPTS,
        "architecture": ARCHITECTURE_PROMPTS,
        "documentation": DOCUMENTATION_PROMPTS,
        "review": REVIEW_PROMPTS
    }
    
    if prompt_type not in prompts_map:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    prompts = prompts_map[prompt_type]
    if prompt_name not in prompts:
        raise ValueError(f"Unknown prompt name: {prompt_name} for type: {prompt_type}")
    
    return prompts[prompt_name]
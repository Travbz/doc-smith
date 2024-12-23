from typing import Dict
from .settings import ModelConfig, validate_temperature, validate_token_limit

# Agent-specific models
AGENT_MODELS: Dict[str, ModelConfig] = {
    'code_analysis': ModelConfig(
        model="gpt-4-turbo-preview",
        temperature=validate_temperature(0.2),
        max_tokens=validate_token_limit(4000),
        frequency_penalty=0.0,
        presence_penalty=0.0
    ),
    'architecture': ModelConfig(
        model="gpt-4-turbo-preview",
        temperature=validate_temperature(0.3),
        max_tokens=validate_token_limit(4000),
        frequency_penalty=0.1,
        presence_penalty=0.1
    ),
    'documentation': ModelConfig(
        model="gpt-3.5-turbo-1106",
        temperature=validate_temperature(0.7),
        max_tokens=validate_token_limit(4000),
        frequency_penalty=0.2,
        presence_penalty=0.2
    ),
    'review': ModelConfig(
        model="gpt-4-turbo-preview",
        temperature=validate_temperature(0.2),
        max_tokens=validate_token_limit(4000),
        frequency_penalty=0.1,
        presence_penalty=0.1
    )
}

# Workflow-specific models
WORKFLOW_MODELS: Dict[str, ModelConfig] = {
    'api_docs': ModelConfig(
        model="gpt-3.5-turbo-1106",
        temperature=validate_temperature(0.3),
        max_tokens=validate_token_limit(4000),
        frequency_penalty=0.0,
        presence_penalty=0.0
    ),
    'dependency_analysis': ModelConfig(
        model="gpt-3.5-turbo-1106",
        temperature=validate_temperature(0.2),
        max_tokens=validate_token_limit(4000),
        frequency_penalty=0.0,
        presence_penalty=0.0
    ),
    'schema_generation': ModelConfig(
        model="gpt-3.5-turbo-1106",
        temperature=validate_temperature(0.2),
        max_tokens=validate_token_limit(4000),
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
}

def get_agent_model(agent_type: str) -> ModelConfig:
    """Get model configuration for a specific agent type."""
    if agent_type not in AGENT_MODELS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return AGENT_MODELS[agent_type]

def get_workflow_model(workflow_type: str) -> ModelConfig:
    """Get model configuration for a specific workflow type."""
    if workflow_type not in WORKFLOW_MODELS:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    return WORKFLOW_MODELS[workflow_type]
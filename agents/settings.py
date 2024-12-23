import os

# OpenAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-4-turbo-preview"
MAX_TOKENS = 4000
TOKEN_BUFFER = 500

# GitHub Settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DEFAULT_BRANCH = "main"

# Documentation Settings
MAX_REVIEW_ITERATIONS = 3
SUPPORTED_FILE_TYPES = ('.py', '.js', '.ts', '.go', '.rs', '.java', '.md', '.yml', '.yaml', '.json')

# Output Settings
DEFAULT_DOCS_PATH = "docs/"
DEFAULT_README = "README.md"
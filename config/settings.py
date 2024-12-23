from pathlib import Path
import os
from typing import Dict, Any
from dataclasses import dataclass

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"

# Create necessary directories
DOCS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Required environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

# Optional environment variables
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")  # Optional

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is not set")
if not GITHUB_USERNAME:
    raise ValueError("GITHUB_USERNAME environment variable is not set")

# Default settings (can be overridden by environment variables if needed)
MAX_TOKENS_PER_REQUEST = 4000
MAX_CONCURRENT_TASKS = 5
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "docsmith.log"

# Repository settings
REPO_CLONE_PATH = BASE_DIR / "repositories"
REPO_CLONE_PATH.mkdir(exist_ok=True)

# Cache settings
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL = 3600  # 1 hour default

# Rate limiting settings
RATE_LIMIT_REQUESTS = 60  # requests per minute
RATE_LIMIT_TOKENS = 90000  # tokens per minute

# Error handling settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
"""
Configuration settings for the Knowledge Graph Builder application.
"""
import os
from pathlib import Path
from typing import Optional

# Project paths
BASE_DIR = Path(__file__).parent.parent
SCHEMAS_DIR = BASE_DIR / "schemas"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
SCHEMAS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# FastAPI settings
API_TITLE = "Knowledge Graph Builder"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Build knowledge graphs from JSON schema files using FalkorDB and Graphiti"

# FalkorDB settings
FALKORDB_HOST = os.getenv("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", 6379))
FALKORDB_DB = int(os.getenv("FALKORDB_DB", 0))
FALKORDB_PASSWORD: Optional[str] = os.getenv("FALKORDB_PASSWORD", None)

# Graphiti settings
GRAPHITI_STORAGE_PATH = DATA_DIR / "graphiti_storage"
GRAPHITI_STORAGE_PATH.mkdir(exist_ok=True)

# Schema processing settings
MAX_SCHEMA_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_SCHEMA_FORMATS = [".json"]

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API settings
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# LLM Feature flags
ENABLE_LLM_EXTRACTION = os.getenv("ENABLE_LLM_EXTRACTION", "true").lower() == "true"
ENABLE_LLM_ANALYSIS = os.getenv("ENABLE_LLM_ANALYSIS", "true").lower() == "true"


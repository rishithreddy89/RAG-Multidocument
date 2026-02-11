"""
Configuration settings for the Multi-Document Reasoning Engine backend.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Document storage
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# LLM API settings
LLM_API_URL = os.getenv("LLM_API_URL", "https://umbellar-mechelle-supernationally.ngrok-free.dev/chat")

# Supported file formats
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

# API settings
API_TITLE = "Multi-Document Reasoning Engine API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Phase 1: Chat + Document Upload"

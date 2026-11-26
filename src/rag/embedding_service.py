"""4.3.1 Embedding Service
Provider: Google Gemini.
Secrets come from .env; non-secret settings from embedding_config.json."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

CONFIG_PATH = Path("embedding_config.json")
REQUIRED_ENV = ["AI_API_KEY", "EMBEDDING_MODEL"]
REQUIRED_CONFIG = ["embedding_model", "dimensions", "batch_size", "normalise"]

def load_settings():
    
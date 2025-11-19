"""
Configuration Settings for Harry Potter RAG Chatbot

This module centralizes all configuration parameters including:
- OpenAI API settings (models, API key)
- Vector database configuration (ChromaDB)
- Document processing parameters (chunking)
- System prompt defining chatbot personality
"""

import os
from pathlib import Path

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.7

# ChromaDB Configuration
CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "harry_potter_knowledge"

# Document Processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
KNOWLEDGE_BASE_FILE = Path(__file__).parent / "harry_potter_knowledge_base.txt"

# Retrieval Configuration
TOP_K_RESULTS = 5

# System Prompt
SYSTEM_PROMPT = """You are an enthusiastic Harry Potter expert with deep knowledge of "The Philosopher's Stone".
Answer questions using the provided context, showing passion for details and making connections between plot points.
Be detailed, engaging, and use wizarding terminology naturally. Base answers on the retrieved context."""

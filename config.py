"""Configuration for RAG service."""

import os

from dotenv import load_dotenv

load_dotenv()

# API Keys
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")

# Model Configuration
LLM_MODEL = "glm-4-plus"
EMBEDDING_MODEL = "embedding-2"

# Vector Database Configuration
VECTOR_DB_TYPE = "chroma"  # 可选: chroma, qdrant, milvus
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "documents"

# Data Configuration
DATA_DIR = "./data"

# Retrieval Configuration
SIMILARITY_TOP_K = 3
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Service Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

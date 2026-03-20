"""Configuration settings and API key management"""
import os
from langchain_nomic.embeddings import NomicEmbeddings
from llama_index.core import Settings

# API Keys
LLAMA_CLOUD_API_KEY = "v"  # LlamaParse document processing
NOMIC_API_KEY = ""  # Nomic Atlas vector database

# LLM settings
DEFAULT_LLM = "llama3.2"  # Ollama model
DEFAULT_TEMPERATURE = 0.7  # Response randomness (0-1)

# Nomic Atlas settings
DEFAULT_ATLAS_DATASET_ID = "mujahidquidwai/careless-bishop"
ATLAS_MAP_ID = "https://atlas.nomic.ai/data/mujahidquidwai/careless-bishop/map"

# Document chunking settings
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
DEFAULT_MAX_TOKENS = 2048

# Initialize embedding model for semantic search
Settings.embed_model = NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local")
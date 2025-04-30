"""
Configuration settings and API key management
"""
import os
from langchain_nomic.embeddings import NomicEmbeddings
from llama_index.core import Settings

# API Keys (loaded from environment variables)
LLAMA_CLOUD_API_KEY = ""
NOMIC_API_KEY = ""

# LLM settings
DEFAULT_LLM = "llama3.2"
DEFAULT_TEMPERATURE = 0.7

# Nomic Atlas settings
DEFAULT_ATLAS_DATASET_ID = "mujahidquidwai/careless-bishop"
ATLAS_MAP_ID = "https://atlas.nomic.ai/data/mujahidquidwai/careless-bishop/map"

# Document processing settings
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 450
DEFAULT_MAX_TOKENS = 2048

# Configure embedding model
Settings.embed_model = NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local")

"""
Functions for retrieving documents from Nomic Atlas
"""
import os
import nomic
from nomic import atlas
from nomic import AtlasDataset
import requests
from typing import List, Dict, Any

from src.config import NOMIC_API_KEY, DEFAULT_ATLAS_DATASET_ID

class NomicAtlasStore:
    def __init__(self, dataset_id=DEFAULT_ATLAS_DATASET_ID):
        self.dataset_id = dataset_id
        # Ensure we're logged in to Nomic
        nomic.login(NOMIC_API_KEY)
        try:
            # Load the dataset and access the associated map
            self.dataset = AtlasDataset(self.dataset_id)
            self.map = self.dataset.maps[0]
            print(f"Connected to Atlas dataset: {self.dataset_id}")
        except Exception as e:
            print(f"Error connecting to Atlas dataset: {e}")
            print("Please ensure the dataset ID is correct and accessible.")

    def search(self, query: str, k: int = 5, fields: list = ["text"]) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant documents for the given query using the Nomic REST API."""
        try:
            url = 'https://api-atlas.nomic.ai/v1/query/topk'
            headers = {
                'Authorization': f'Bearer {NOMIC_API_KEY}',
                'Content-Type': 'application/json'
            }
            payload = {
                'query': query,
                'k': k,
                'fields': fields,
                'projection_id': self.map.projection_id,
            }

            # Send the POST request
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

# Initialize the Atlas store
atlas_store = NomicAtlasStore()

def retrieve_context(query: str, k: int = 10) -> List[Dict[str, Any]]:
    """Retrieve context from Nomic Atlas"""
    try:
        results = atlas_store.search(query, k)
        print(f"Retrieved {len(results)} documents from Atlas")
        return results
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return []
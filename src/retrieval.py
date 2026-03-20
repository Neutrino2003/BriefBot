"""Document retrieval from Nomic Atlas vector database"""
import os
import nomic
from nomic import atlas
from nomic import AtlasDataset
import requests
from typing import List, Dict, Any

from src.config import NOMIC_API_KEY, DEFAULT_ATLAS_DATASET_ID

class NomicAtlasStore:
    """Interface for Nomic Atlas vector database"""

    def __init__(self, dataset_id=DEFAULT_ATLAS_DATASET_ID):
        """Connect to Nomic Atlas dataset"""
        self.dataset_id = dataset_id
        nomic.login("nk-p4RbLXYiBQInfAQyrlCssat_n9w-697uXrq4dlCmq0o")
        try:
            self.dataset = AtlasDataset(self.dataset_id)
            self.map = self.dataset.maps[0]
            print(f"Connected to Atlas dataset: {self.dataset_id}")
        except Exception as e:
            print(f"Error connecting to Atlas dataset: {e}")
            print("Please ensure the dataset ID is correct and accessible.")

    def search(self, query: str, k: int = 5, fields: list = ["text"]) -> List[Dict[str, Any]]:
        """Search for top-k semantically similar documents"""
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

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

# Global Atlas store instance
atlas_store = NomicAtlasStore()

def retrieve_context(query: str, k: int = 10) -> List[Dict[str, Any]]:
    """Retrieve k most relevant documents for query"""
    try:
        results = atlas_store.search(query, k)
        print(f"Retrieved {len(results)} documents from Atlas")
        return results
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return []

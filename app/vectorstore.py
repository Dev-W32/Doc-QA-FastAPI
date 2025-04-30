# app/vectorstore.py

import os
from qdrant_client import QdrantClient
from fastapi import Depends

# Load from environment
QDRANT_URL = os.getenv("QDRANT_URL")         # e.g. https://xxxx.a1.qdrant.cloud
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") # from Access Tokens
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")

# Initialize once
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    prefer_grpc=True
)

def get_vector_store():
    # Ensure the collection exists
    if COLLECTION_NAME not in qdrant_client.get_collections().collections:
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vector_size=768,
            distance="Cosine"
        )
    return qdrant_client

# app/vectorstore.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST")
COLLECTION_NAME = "document-qa"

client = QdrantClient(url=f"https://{QDRANT_HOST}", api_key=QDRANT_API_KEY)

def init_qdrant(vector_size: int):
    # 1. Check if the collection exists
    cols = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in cols:
        # 2. Fetch its config to see the existing vector size
        info = client.get_collection(collection_name=COLLECTION_NAME)
        
        existing_size = info.config.params.vectors.size
        # 3. If it doesn't match, delete it so we'll recreate below
        if existing_size != vector_size:
            client.delete_collection(collection_name=COLLECTION_NAME)

    # 4. Create it if now missing
    cols = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in cols:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

def get_vector_store(vector_size: int):
    init_qdrant(vector_size)
    return client

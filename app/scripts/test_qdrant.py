from core.vectorstore import get_vector_store, COLLECTION_NAME
import os


vs = get_vector_store()
print(vs.get_collections())
VECTOR_SIZE=int(os.getenv("VECTOR_SIZE"))
# 1) Upsert a dummy vector
# vs.upsert(
#     collection_name=COLLECTION_NAME,
#     points=[{"id": 5, "vector": [0.1]*VECTOR_SIZE, "payload": {"text": "test"}}]
# )
# print("Upsert done")

# 2) Search for it back
results = vs.query_points(
    collection_name=COLLECTION_NAME,
    query=[0.1]*VECTOR_SIZE,
    limit=5
)
print("Search results:", results)

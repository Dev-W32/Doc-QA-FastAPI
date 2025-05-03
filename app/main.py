# app/main.py

from fastapi import FastAPI, Depends, UploadFile, File
from app.database import get_db_connection
from app.vectorstore import get_vector_store, COLLECTION_NAME
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid
from langchain_huggingface import HuggingFaceEmbeddings

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health(
    db=Depends(get_db_connection),
):
    try:
        with db.cursor() as cur:
            cur.execute("SELECT 1;")
            db_ok = cur.fetchone() == (1,)
    except Exception:
        db_ok = False

    # Embedder
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L6-v2")
    dim = len(embedder.embed_query("test"))

    # Vector store
    try:
        vs = get_vector_store(dim)
        collections = vs.get_collections()
        vs_ok = collections is not None
    except Exception as e:
        vs_ok = False
        print(e)

    return {"database_ok": db_ok, "vector_store_ok": vs_ok}


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([text])

    # Embedder
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L6-v2")
    vectors = embedder.embed_documents([doc.page_content for doc in docs])

    # Vector store (initialize after embedding)
    dim = len(vectors[0])
    vs = get_vector_store(dim)

    points = [
        {
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {
                "text": doc.page_content,
                "source": file.filename,
            }
        }
        for doc, vector in zip(docs, vectors)
    ]

    print(points)

    vs.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": "success", "chunks_ingested": len(points)}
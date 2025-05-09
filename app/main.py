# app/main.py

import logging

from fastapi import FastAPI, Depends, UploadFile, File, BackgroundTasks, HTTPException
from app.core.database import get_db_connection, pool
from app.core.vectorstore import get_vector_store
from app.core.embedder import dim
from app.services.ingest_service import handle_ingest

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health(db=Depends(get_db_connection)):
    """
    Return health status of the database and vector store.

    - `database_ok`: True if the DB responds to `SELECT 1;`
    - `vector_store_ok`: True if Qdrant collections can be listed
    """
    # 1. Database health check
    try:
        with db.cursor() as cur:
            cur.execute("SELECT 1;")
            database_ok = cur.fetchone() == (1,)
    except Exception:
        database_ok = False

    # 2. Vector store health check
    try:
        vs = get_vector_store(dim)
        vector_store_ok = vs.get_collections() is not None
    except Exception:
        vector_store_ok = False

    return {"database_ok": database_ok, "vector_store_ok": vector_store_ok}


@app.post("/ingest", status_code=202)
async def ingest(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db_connection),
):
    """
    Kick off document ingestion:
    1. Validates and records the document.
    2. Uploads to GCS.
    3. Schedules text extraction, chunking, embedding, and Qdrant upsert in background.
    """
    try:
        return handle_ingest(file, background_tasks, db)
    except HTTPException as e:
        # Re-raise HTTPExceptions to preserve status_code & detail
        raise e
    except Exception as e:
        logger.exception("Unexpected error in /ingest")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/documents/{document_id}")
def get_document_status(document_id: str):
    conn = pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, filename, status, gcs_uri, error, uploaded_at FROM documents WHERE id = %s",
            (document_id,)
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "id": row[0],
            "filename": row[1],
            "status": row[2],
            "gcs_uri": row[3],
            "error": row[4],
            "uploaded_at": row[5]
        }
    finally:
        pool.putconn(conn)
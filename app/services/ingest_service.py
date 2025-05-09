# app/services/ingest_service.py

import io                             # ← add this!
import uuid
import hashlib
from pathlib import Path

from fastapi import HTTPException
from app.core.vectorstore import get_vector_store, COLLECTION_NAME
from app.core.embedder import dim
from app.core.database import pool
from app.core.gcp_utils import upload_to_gcs
from app.core.document_processor import extract_text, chunk_text, embed_chunks

def compute_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def insert_or_get_doc(conn, filename, checksum):
    cur = conn.cursor()
    cur.execute("SELECT id FROM documents WHERE checksum = %s", (checksum,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO documents (filename, checksum, status) VALUES (%s, %s, %s) RETURNING id",
        (filename, checksum, "processing")
    )
    doc_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return str(doc_id)

def update_gcs_uri(conn, doc_id, gcs_uri):
    cur = conn.cursor()
    cur.execute("UPDATE documents SET gcs_uri = %s WHERE id = %s", (gcs_uri, doc_id))
    conn.commit()
    cur.close()

def mark_failed(conn, doc_id, error):
    cur = conn.cursor()
    cur.execute("UPDATE documents SET status = %s, error = %s WHERE id = %s", ("failed", error, doc_id))
    conn.commit()
    cur.close()

def mark_complete(conn, doc_id):
    cur = conn.cursor()
    cur.execute("UPDATE documents SET status = %s WHERE id = %s", ("completed", doc_id))
    conn.commit()
    cur.close()

def process_in_background(doc_id, filename, content, gcs_uri):
    conn = pool.getconn()
    try:
        text = extract_text(content, filename)
        docs = chunk_text(text)
        vectors = embed_chunks(docs)
        vs = get_vector_store(dim)
        points = [
            {
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "text": doc.page_content,
                    "source": filename,
                    "gcs_uri": gcs_uri,
                    "document_id": doc_id,
                }
            }
            for doc, vector in zip(docs, vectors)
        ]
        vs.upsert(collection_name=COLLECTION_NAME, points=points)
        mark_complete(conn, doc_id)
    except Exception as e:
        mark_failed(conn, doc_id, str(e))
    finally:
        pool.putconn(conn)

def handle_ingest(file, background_tasks, db):
    filename = file.filename
    ext = Path(filename).suffix.lower()

    # 1. Validate file extension
    allowed = {".pdf", ".docx", ".txt"}
    if ext not in allowed:
        # 415 Unsupported Media Type
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {ext}. Allowed types: {', '.join(allowed)}"
        )    
    # Read the bytes (you could also do: content = await file.read() in an async function)
    content = file.file.read()
    checksum = compute_checksum(content)
    doc_id = insert_or_get_doc(db, filename, checksum)

    try:
        # Now this io.BytesIO will work
        gcs_uri = upload_to_gcs(io.BytesIO(content), filename)
        update_gcs_uri(db, doc_id, gcs_uri)
    except Exception as e:
        mark_failed(db, doc_id, str(e))
        raise HTTPException(500, detail=f"GCS upload failed: {e}")

    background_tasks.add_task(process_in_background, doc_id, filename, content, gcs_uri)
    return {"status": "processing", "document_id": doc_id}

from fastapi import FastAPI, Depends
from app.database import get_db_connection
from app.vectorstore import get_vector_store

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}



@app.get("/health")
async def health(
    db=Depends(get_db_connection),
    vs=Depends(get_vector_store),
):
    # DB check
    with db.cursor() as cur:
        cur.execute("SELECT 1;")
        db_ok = cur.fetchone() == (1,)
    # Vector store check
    stats = vs.describe_index_stats()
    vs_ok = "total_vector_count" in stats
    return {"database_ok": db_ok, "vector_store_ok": vs_ok}
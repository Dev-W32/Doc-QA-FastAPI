# app/core/document_processor.py

import io
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.embedder import embedder

def extract_text(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        return "\n".join([p.extract_text() or "" for p in reader.pages])
    elif ext == ".docx":
        doc = Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return content.decode("utf-8")

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.create_documents([text])

def embed_chunks(docs):
    return embedder.embed_documents([doc.page_content for doc in docs])

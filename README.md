# 🧠 Doc-QA-FastAPI

This repository documents the step-by-step journey of building an AI-powered Document Question Answering system using FastAPI, PostgreSQL, Qdrant, and GCS.

---

## ✅ What’s Done (Phase 0: Foundation)

- **FastAPI set up** with:
  - Basic routing and health checks.
- **Integrated core services**:
  - ✅ PostgreSQL for storing document metadata.
  - ✅ Qdrant for vector similarity search.
  - ✅ Google Cloud Storage (GCS) for storing uploaded documents.
- **Created `/ingest` endpoint**:
  - ✅ Uploads files to GCS.
  - ✅ Chunks content using LangChain’s `RecursiveCharacterTextSplitter`.
  - ✅ Embeds the chunks and stores them in Qdrant with metadata.
- **Basic health checks** for all services.

---

### 🔨 Current Work (Phase 1: Robust Ingestion & Document Tracking)

#### 1.1 Robust Text Extraction for Various File Types

**Goal:** Extract plain text from PDFs, DOCX, and TXT files.

- [✅] Support for:
  - PDF (using `pypdf`)
  - DOCX (using `python-docx`)
  - TXT (direct read)
- [✅] Detect file type by extension and apply the appropriate parser.
- [✅] Handle unsupported formats with clear 415 error.
- [✅] Gracefully handle corrupted file parsing (400 error with reason).
- [✅] Store status as `failed` in DB on extraction or upload error.

### 1.2 Store and Deduplicate Using PostgreSQL

**Goal:** Track documents and prevent re-ingestion.

- [ ] Compute SHA256 checksum of file content.
- [ ] Store document metadata (filename, checksum, status, GCS URI).
- [ ] Check DB for existing documents before ingesting.
- [ ] Update ingestion status (`pending`, `ingested`, `failed`) based on processing outcome.

### 1.3 Improve Qdrant Payloads

**Goal:** Link vectors to DB records.

- [ ] Include DB document `id` in each Qdrant payload.
- [ ] Add chunk number and GCS URI to the payload for traceability.

### 1.4 Asynchronous Background Ingestion (Optional)

**Goal:** Offload heavy lifting to background tasks.

- [ ] Use FastAPI’s `BackgroundTasks` to handle:
  - Chunking
  - Embedding
  - Qdrant upserts
- [ ] Return a `202 Accepted` immediately after file upload.
- [ ] Update document status upon task completion.

---

## 🔮 Next Steps (Phase 2: Enabling Question Answering)

### 2.1 Create the `/ask` API Endpoint

**Goal:** Allow users to ask questions about ingested documents.

- [ ] Accept a JSON body with a `question` field.
- [ ] Define a Pydantic request model.

### 2.2 Embed the Question

**Goal:** Vectorize the user's question for similarity search.

- [ ] Use the same embedding model as ingestion (`sentence-transformers/paraphrase-MiniLM-L6-v2`).

### 2.3 Perform Qdrant Similarity Search

**Goal:** Retrieve top-N most relevant chunks.

- [ ] Use `qdrant-client` to query with the embedded question.
- [ ] Return top 3–5 chunks for context construction.

### 2.4 Generate Context from Retrieved Chunks

**Goal:** Prepare the LLM prompt using relevant document snippets.

- [ ] Concatenate text content of retrieved chunks.
- [ ] Optionally include source info (filename, document ID).

### 2.5 Integrate with an LLM (GPT, Claude, Gemini, etc.)

**Goal:** Generate answers using context + question.

- [ ] Choose an LLM provider.
- [ ] Format a prompt like:
  ```
  Use the following context to answer the question:

  [Document Chunks]

  Question: [User’s question]
  Answer:
  ```
- [ ] Call LLM API and get a response.

### 2.6 Return Answer and Source Info

**Goal:** Let users see where the answer came from.

- [ ] Return:
  - The answer
  - A list of sources (chunk text, document ID, filename, GCS URI)

---

## 🚀 Production Readiness (Phase 3: Hardening and Scaling)

### 3.1 Error Handling and Input Validation

- [ ] Use Pydantic models for all endpoints.
- [ ] Add `try/except` blocks for each external service call.

### 3.2 Configuration Management

- [ ] Use Pydantic Settings to load `.env` variables with validation.

### 3.3 Authentication & Authorization

- [ ] Implement API key or OAuth2 authentication.
- [ ] Protect `/ingest` and `/ask` endpoints.

### 3.4 Logging & Monitoring

- [ ] Use Python’s `logging` module.
- [ ] Log request flow, exceptions, Qdrant queries, and LLM calls.

### 3.5 Testing

- [ ] Add unit tests (e.g., for text extraction, checksum).
- [ ] Add integration tests for `/ingest` and `/ask` using `pytest`.

### 3.6 Dockerize the Application

- [ ] Write a `Dockerfile` for FastAPI app.
- [ ] Ensure it includes dependencies and starts with `uvicorn`.

---

## 📅 Timeline (Suggested Order)

1. ✅ Foundation (setup + basic ingestion)
2. 🔨 Robust ingestion (file types + DB tracking)
3. 🔮 Q&A system (embedding + similarity search + LLM)
4. 🚀 Productionization (auth, logging, testing, Docker)

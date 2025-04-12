from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from pathlib import Path
import asyncio

from .document_processor import DocumentProcessor
from .embedding_service import EmbeddingService
from .vector_store import VectorStore

app = FastAPI(title="RAG Service API", version="1.0.0")

# Initialize services
VECTOR_STORE_PATH = "/app/data/vector_store"
doc_processor = DocumentProcessor()
embedding_service = EmbeddingService()
vector_store = VectorStore()

# Create necessary directories
Path("/app/data").mkdir(parents=True, exist_ok=True)
Path("/app/models").mkdir(parents=True, exist_ok=True)

# Load existing vector store if available
if os.path.exists(f"{VECTOR_STORE_PATH}.index"):
    vector_store = VectorStore.load(VECTOR_STORE_PATH)


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    results: List[Dict]
    query: str


@app.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    """Ingest a document into the RAG system"""
    try:
        # Save uploaded file temporarily
        temp_path = f"/app/data/temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process document
        chunks = await doc_processor.process_file(temp_path)

        # Generate embeddings for chunks
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.get_embeddings(texts)

        # Add to vector store
        vector_store.add_embeddings(embeddings, chunks)

        # Schedule vector store save for background
        background_tasks.add_task(vector_store.save, VECTOR_STORE_PATH)

        # Cleanup temp file
        os.remove(temp_path)

        return {
            "status": "success",
            "message": f"Document {file.filename} ingested successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system"""
    try:
        # Generate query embedding
        query_embedding = embedding_service.get_query_embedding(request.query)

        # Search vector store
        results = vector_store.search(query_embedding, k=request.top_k)

        return QueryResponse(results=results, query=request.query)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "rag",
        "cuda_available": str(embedding_service.device),
        "documents_indexed": vector_store.current_id,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

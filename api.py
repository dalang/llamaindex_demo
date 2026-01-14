"""REST API for RAG service using FastAPI."""

from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import config
from query_service import QueryService

app = FastAPI(
    title="RAG Query API",
    description="Retrieval-Augmented Generation Query Service",
    version="1.0.0",
)

# 全局查询服务实例
query_service = None


class QueryRequest(BaseModel):
    """Query request model."""

    question: str
    return_sources: bool = True
    top_k: Optional[int] = None


class Source(BaseModel):
    """Source document model."""

    chunk_id: int
    score: float
    text: str
    metadata: Dict


class QueryResponse(BaseModel):
    """Query response model."""

    question: str
    answer: str
    sources: List[Source]


@app.on_event("startup")
async def startup_event():
    """Initialize query service on startup."""
    global query_service
    try:
        query_service = QueryService()
        print("✅ API 服务启动成功")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        raise


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query endpoint."""
    try:
        result = query_service.query(
            question=request.question, return_sources=request.return_sources
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rag-query-api"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "RAG Query API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/query (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)",
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
    )

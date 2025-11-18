"""
Crawl4AI + ChromaDB MCP Server
Scrapes documentation and stores in vector database
"""
import os
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from crawl4ai import AsyncWebCrawler

# Environment variables
CHROMA_URL = os.getenv("CHROMA_URL", "http://chroma.railway.internal:8000")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "maicol_docs")

# Initialize FastAPI
app = FastAPI(
    title="Crawl4AI + ChromaDB MCP",
    description="Documentation scraper with vector storage",
    version="1.0.0"
)

# Initialize sentence transformer for embeddings (free, local)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(
    host=CHROMA_URL.replace("http://", "").replace("https://", "").split(":")[0],
    port=int(CHROMA_URL.split(":")[-1]) if ":" in CHROMA_URL else 8000,
    settings=Settings(
        chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
        chroma_client_auth_credentials=CHROMA_API_KEY
    ) if CHROMA_API_KEY else Settings()
)

# Request/Response models
class CrawlRequest(BaseModel):
    url: HttpUrl
    max_depth: int = 1
    chunk_size: int = 1000

class CrawlResponse(BaseModel):
    success: bool
    url: str
    chunks_added: int
    message: str

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5

class SearchResult(BaseModel):
    content: str
    metadata: dict
    distance: float

class SearchResponse(BaseModel):
    results: List[SearchResult]


def get_or_create_collection():
    """Get or create ChromaDB collection with custom embedding function"""
    try:
        return chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Documentation and knowledge base"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChromaDB connection failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test ChromaDB connection
        collection = get_or_create_collection()
        return {
            "status": "healthy",
            "chroma_url": CHROMA_URL,
            "collection": COLLECTION_NAME,
            "collection_count": collection.count()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/crawl", response_model=CrawlResponse)
async def crawl_and_index(request: CrawlRequest):
    """
    Crawl a URL and index content in ChromaDB

    Example:
    ```
    POST /crawl
    {
        "url": "https://docs.example.com",
        "max_depth": 1,
        "chunk_size": 1000
    }
    ```
    """
    try:
        url_str = str(request.url)
        collection = get_or_create_collection()

        # Initialize crawler
        async with AsyncWebCrawler(verbose=True) as crawler:
            # Crawl the page
            result = await crawler.arun(url=url_str)

            if not result.success:
                raise HTTPException(status_code=500, detail="Crawl failed")

            # Extract text content
            text_content = result.markdown or result.cleaned_html or ""

            if not text_content:
                return CrawlResponse(
                    success=False,
                    url=url_str,
                    chunks_added=0,
                    message="No content extracted from page"
                )

            # Split into chunks
            chunks = []
            chunk_size = request.chunk_size

            for i in range(0, len(text_content), chunk_size):
                chunk = text_content[i:i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk)

            if not chunks:
                return CrawlResponse(
                    success=False,
                    url=url_str,
                    chunks_added=0,
                    message="No chunks created from content"
                )

            # Generate embeddings
            embeddings = embedding_model.encode(chunks).tolist()

            # Prepare for ChromaDB
            ids = [f"{url_str}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "source_url": url_str,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "title": result.metadata.get("title", ""),
                }
                for i in range(len(chunks))
            ]

            # Add to ChromaDB
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )

            return CrawlResponse(
                success=True,
                url=url_str,
                chunks_added=len(chunks),
                message=f"Successfully indexed {len(chunks)} chunks from {url_str}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search indexed documents using semantic search

    Example:
    ```
    POST /search
    {
        "query": "How to deploy to Railway?",
        "n_results": 5
    }
    ```
    """
    try:
        collection = get_or_create_collection()

        # Generate query embedding
        query_embedding = embedding_model.encode([request.query]).tolist()[0]

        # Search ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=request.n_results
        )

        if not results['documents'] or not results['documents'][0]:
            return SearchResponse(results=[])

        # Format results
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append(
                SearchResult(
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    distance=results['distances'][0][i]
                )
            )

        return SearchResponse(results=search_results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get collection statistics"""
    try:
        collection = get_or_create_collection()
        return {
            "collection_name": COLLECTION_NAME,
            "total_documents": collection.count(),
            "chroma_url": CHROMA_URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/collection")
async def delete_collection():
    """Delete entire collection (use with caution!)"""
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        return {"message": f"Collection {COLLECTION_NAME} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

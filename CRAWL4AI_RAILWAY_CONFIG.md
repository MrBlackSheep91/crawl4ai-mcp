# Crawl4AI + ChromaDB Railway Configuration

**Project:** awake-benevolence
**Railway Project ID:** 017ca44d-838e-4374-aae7-264ccd95ab7c
**Environment:** production (f86979bf-5b65-4be2-9f81-ac8ed6ed265c)

---

## Services

### Crawl4AI Service
- **Service ID:** 155e1ce0-7dee-41df-83bc-4eac91397d66
- **URL:** https://crawl4ai-production-7ab7.up.railway.app
- **Port:** 8000
- **Repository:** https://github.com/MrBlackSheep91/crawl4ai-mcp

### ChromaDB Service
- **Service ID:** 2b898841-755c-40e7-81b9-db7202fdb843
- **Internal URL:** http://chroma.railway.internal:8000
- **Volume:** chroma-volume (394f308c-da76-4197-8362-d05c881f79bb)
- **Mount Path:** /data

### Auth Proxy (ChromaDB)
- **Service ID:** 147db8be-989f-48e9-a8b0-5676d333c951
- **URL:** https://auth-proxy-production-7c7b.up.railway.app
- **API Key:** 6fpt4o4nhwr6kp69
- **Target:** http://chroma.railway.internal:8000

---

## Environment Variables

### Crawl4AI Service
```env
CHROMA_URL=http://chroma.railway.internal:8000
CHROMA_API_KEY=6fpt4o4nhwr6kp69
COLLECTION_NAME=maicol_docs
```

### ChromaDB Service
```env
PORT=8000
CHROMA_HOST_ADDR=::
CHROMA_HOST_PORT=8000
IS_PERSISTENT=True
CHROMA_WORKERS=1
```

---

## Stack Components

### Web Scraping
- **Crawl4AI:** 0.3.74 (async web crawler with headless Chrome)
- **Playwright:** 1.47.0 (browser automation)
- **BeautifulSoup4:** 4.12.2 (HTML parsing)
- **lxml:** 5.4.0 (XML/HTML processing)

### Vector Storage
- **ChromaDB:** 0.4.22 (embedding database)
- **chroma-hnswlib:** 0.7.3 (HNSW indexing)

### ML/Embeddings
- **Sentence Transformers:** 2.2.2 (semantic embeddings)
- **Model:** all-MiniLM-L6-v2 (free, local embeddings)
- **PyTorch:** 2.9.1 (ML framework)
- **Transformers:** 4.57.1 (Hugging Face models)

### API Framework
- **FastAPI:** 0.104.1 (REST API)
- **Uvicorn:** 0.24.0 (ASGI server)
- **Pydantic:** 2.5.0 (data validation)

---

## API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "chroma_url": "http://chroma.railway.internal:8000",
  "collection": "maicol_docs",
  "collection_count": 0
}
```

### POST /crawl
Crawl and index a URL

**Request:**
```json
{
  "url": "https://docs.example.com",
  "max_depth": 1,
  "chunk_size": 1000
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://docs.example.com",
  "chunks_added": 42,
  "message": "Successfully indexed 42 chunks from https://docs.example.com"
}
```

### POST /search
Semantic search over indexed documents

**Request:**
```json
{
  "query": "How to deploy to Railway?",
  "n_results": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "To deploy to Railway, you need to...",
      "metadata": {
        "source_url": "https://docs.railway.app/deploy",
        "chunk_index": 0,
        "total_chunks": 10,
        "title": "Deployment Guide"
      },
      "distance": 0.23
    }
  ]
}
```

### GET /stats
Get collection statistics

**Response:**
```json
{
  "collection_name": "maicol_docs",
  "total_documents": 150,
  "chroma_url": "http://chroma.railway.internal:8000"
}
```

### DELETE /collection
Delete entire collection (⚠️ destructive)

**Response:**
```json
{
  "message": "Collection maicol_docs deleted successfully"
}
```

---

## Cost Optimization

### Embeddings
- **Sentence Transformers (all-MiniLM-L6-v2):** FREE
- **No OpenAI API calls:** $0/month
- **Model size:** ~90MB (cached after first run)

### Railway Costs
- **ChromaDB:** ~$1-2/month (lightweight)
- **Crawl4AI:** ~$2-3/month (Chrome + ML libraries)
- **Total:** ~$3-5/month

**Total estimated:** $3-5/month for 24/7 doc scraping + vector search 🎉

---

## Build Notes

### Docker Image Size
~3-4GB compressed due to:
- PyTorch: ~2GB
- Chrome + dependencies: ~500MB
- ML models: ~200MB
- Python libraries: ~1GB

### Build Time
- **First build:** 5-8 minutes (all dependencies)
- **Subsequent builds:** 2-4 minutes (layer caching)

### Known Issues Fixed
1. ❌ FalkorDB port conflict → ✅ Used ChromaDB instead
2. ❌ `apt-key` deprecated → ✅ Direct .deb install for Chrome
3. ❌ lxml version conflict → ✅ Updated to lxml>=5.3.0

---

## Testing

### Test 1: Health Check
```bash
curl https://crawl4ai-production-7ab7.up.railway.app/health
```

### Test 2: Crawl Railway Docs
```bash
curl -X POST https://crawl4ai-production-7ab7.up.railway.app/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.railway.app/guides/deployments",
    "max_depth": 1,
    "chunk_size": 1000
  }'
```

### Test 3: Search Indexed Docs
```bash
curl -X POST https://crawl4ai-production-7ab7.up.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to configure environment variables?",
    "n_results": 3
  }'
```

### Test 4: Get Stats
```bash
curl https://crawl4ai-production-7ab7.up.railway.app/stats
```

---

## Integration Examples

### With Graphiti Knowledge Graph
```python
import httpx

# 1. Search docs in ChromaDB
docs_response = httpx.post(
    "https://crawl4ai-production-7ab7.up.railway.app/search",
    json={"query": "Railway deployment", "n_results": 5}
)
docs = docs_response.json()["results"]

# 2. Add to Graphiti knowledge graph
for doc in docs:
    httpx.post(
        "https://graphiti-oozt-production.up.railway.app/messages",
        json={
            "group_id": "maicol_second_brain",
            "messages": [{
                "content": doc["content"],
                "role_type": "system",
                "role": "documentation",
                "timestamp": "2025-11-18T17:00:00Z"
            }]
        }
    )
```

### Batch Crawl Multiple URLs
```python
urls_to_crawl = [
    "https://docs.railway.app",
    "https://docs.anthropic.com/claude/docs",
    "https://fastapi.tiangolo.com"
]

for url in urls_to_crawl:
    response = httpx.post(
        "https://crawl4ai-production-7ab7.up.railway.app/crawl",
        json={"url": url, "chunk_size": 1000}
    )
    print(f"Indexed {response.json()['chunks_added']} chunks from {url}")
```

---

## Troubleshooting

### ChromaDB Connection Failed
**Error:** `ChromaDB connection failed: Connection refused`

**Fix:**
- Verify `CHROMA_URL=http://chroma.railway.internal:8000`
- Check ChromaDB service is running
- Ensure both services in same Railway project

### Crawl Failed
**Error:** `Crawl failed: Page not accessible`

**Fix:**
- Verify URL is publicly accessible
- Check for anti-bot protection (Cloudflare, etc.)
- Increase timeout in crawler configuration

### No Chunks Created
**Error:** `No chunks created from content`

**Fix:**
- URL may have JavaScript-rendered content
- Try increasing `max_depth` parameter
- Check if page requires authentication

### Memory Limit Exceeded
**Error:** Build fails with OOM error

**Fix:**
- Railway automatically allocates memory
- If persistent, contact Railway support
- Consider lighter embedding model

---

## Next Steps

1. ✅ Deploy Crawl4AI + ChromaDB to Railway
2. ⏳ Test crawling and indexing
3. ⏳ Integrate with Graphiti (FASE 4)
4. ⏳ Create scheduled crawls for documentation updates
5. ⏳ Add MCP protocol endpoints

**Deployed:** 2025-11-18
**Status:** 🔄 Building (in progress)

---

**Repository:** https://github.com/MrBlackSheep91/crawl4ai-mcp
**Stack:** Crawl4AI + ChromaDB + Sentence Transformers + FastAPI
**Embeddings:** FREE (all-MiniLM-L6-v2 local model)

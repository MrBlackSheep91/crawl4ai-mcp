# Crawl4AI + ChromaDB MCP Server

Documentation scraper with vector storage for Maicol's Second Brain.

## Features

- 🕷️ **Web Scraping** with Crawl4AI (async, headless Chrome)
- 📊 **Vector Storage** with ChromaDB
- 🔍 **Semantic Search** using sentence-transformers (free embeddings)
- 🚀 **FastAPI** endpoints for easy integration
- 🐳 **Docker** ready for Railway deployment

## Stack

- **Crawl4AI**: Web scraping framework
- **ChromaDB**: Vector database
- **Sentence Transformers**: all-MiniLM-L6-v2 (free embeddings)
- **FastAPI**: REST API framework
- **Railway**: Cloud hosting

## API Endpoints

### Health Check
```bash
GET /health
```

Returns service status and ChromaDB connection info.

### Crawl & Index
```bash
POST /crawl
Content-Type: application/json

{
  "url": "https://docs.example.com",
  "max_depth": 1,
  "chunk_size": 1000
}
```

Crawls a URL and indexes content in ChromaDB.

### Search
```bash
POST /search
Content-Type: application/json

{
  "query": "How to deploy to Railway?",
  "n_results": 5
}
```

Semantic search over indexed documents.

### Stats
```bash
GET /stats
```

Get collection statistics (document count, etc.).

### Delete Collection
```bash
DELETE /collection
```

⚠️ Deletes entire collection. Use with caution!

## Environment Variables

```env
CHROMA_URL=http://chroma.railway.internal:8000
CHROMA_API_KEY=your-api-key-here
COLLECTION_NAME=maicol_docs
```

## Railway Deployment

### 1. Deploy ChromaDB Template
Use Railway's official ChromaDB template (includes Auth Proxy).

### 2. Deploy Crawl4AI Service
```bash
# Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/MrBlackSheep91/crawl4ai-mcp.git
git push -u origin main

# In Railway:
# - Create new service from GitHub repo
# - Set environment variables
# - Deploy
```

### 3. Configure Environment Variables
```env
CHROMA_URL=http://chroma.railway.internal:8000
CHROMA_API_KEY=6fpt4o4nhwr6kp69
COLLECTION_NAME=maicol_docs
```

## Usage Examples

### Index Railway Documentation
```bash
curl -X POST https://your-crawl4ai.up.railway.app/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.railway.app",
    "max_depth": 1,
    "chunk_size": 1000
  }'
```

### Search Indexed Docs
```bash
curl -X POST https://your-crawl4ai.up.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to deploy Docker containers?",
    "n_results": 5
  }'
```

## Cost Optimization

- **Embeddings**: FREE (sentence-transformers locally)
- **ChromaDB**: ~$1-2/month on Railway
- **Crawl4AI**: ~$1-2/month on Railway
- **Total**: ~$2-4/month

No OpenAI costs for embeddings! 🎉

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run locally
uvicorn main:app --reload --port 8000
```

## Integration with Graphiti

After indexing docs, you can sync with Graphiti knowledge graph:

```python
# Search docs
docs = await search_documents({"query": "Railway deployment"})

# Add to Graphiti
await graphiti.add_messages({
    "group_id": "maicol_second_brain",
    "messages": [{
        "content": doc.content,
        "role_type": "system",
        "role": "documentation",
        "timestamp": datetime.now().isoformat()
    } for doc in docs.results]
})
```

## Troubleshooting

### ChromaDB Connection Failed
- Check `CHROMA_URL` is correct (should be `http://chroma.railway.internal:8000`)
- Verify `CHROMA_API_KEY` matches Auth Proxy configuration
- Ensure both services are in the same Railway project

### Crawl Failed
- Check URL is accessible
- Verify Chrome is installed in Docker container
- Increase timeout if needed

### No Embeddings Generated
- Sentence transformers model downloads on first run (~100MB)
- Ensure container has enough memory (min 512MB)

## Next Steps

- [ ] Add batch crawling for multiple URLs
- [ ] Implement crawl scheduling (cron jobs)
- [ ] Add support for authenticated pages
- [ ] Create MCP protocol endpoints

**Deployed:** 2025-11-18
**Status:** In Development

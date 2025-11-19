# Integration Tests

Comprehensive end-to-end testing suite for the Crawl4AI + ChromaDB + Graphiti infrastructure.

## Test Coverage

**5 Tests - 100% Pass Rate**

1. **Health Endpoints** - Verify all services are operational
2. **Crawl and Index** - Scrape documentation and store in ChromaDB
3. **Semantic Search** - Query vector database with semantic similarity
4. **Graphiti Integration** - Send data to knowledge graph
5. **Stats Verification** - Confirm data persistence

## Quick Start

### Install Dependencies

```bash
pip install -r test_requirements.txt
```

### Run Tests

```bash
python test_integration.py
```

## Test Results

Last execution: **2025-11-18 20:13:08**

```
✅ Test 1: Health Endpoints - PASSED
✅ Test 2: Crawl and Index - PASSED (11 chunks)
✅ Test 3: Semantic Search - PASSED (3 results)
✅ Test 4: Graphiti Integration - PASSED (202 async)
✅ Test 5: Stats Verification - PASSED (11 docs)

📊 Success Rate: 100.0% (5/5)
```

Results are saved to `test_results.json` after each run.

## Services Tested

### Crawl4AI Service
- **URL:** https://crawl4ai-production-7ab7.up.railway.app
- **Endpoints:** /health, /crawl, /search, /stats

### Graphiti Service
- **URL:** https://graphiti-oozt-production.up.railway.app
- **Endpoints:** /healthcheck, /messages, /search

## Test Configuration

```python
# Modify these in test_integration.py
TEST_URL = "https://docs.railway.app/guides/deployments"
TEST_QUERY = "How to deploy applications"
GROUP_ID = "maicol_second_brain"
```

## Windows UTF-8 Support

The test suite includes automatic UTF-8 encoding setup for Windows to support emoji output:

```python
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

## Architecture Flow

```
URL Input
   ↓
Crawl4AI (Playwright + Chromium)
   ↓
Extract & Chunk Content
   ↓
Generate Embeddings (sentence-transformers)
   ↓
Store in ChromaDB (vector database)
   ↓
Semantic Search
   ↓
Send to Graphiti (knowledge graph)
   ↓
Neo4j (graph storage)
```

## Troubleshooting

### Connection Errors
- Verify services are running on Railway
- Check environment variables in Railway dashboard
- Confirm internal DNS: `chroma.railway.internal:8000`

### Test Failures
- Check service health: `GET /health`
- Verify ChromaDB collection exists: `GET /stats`
- Review deployment logs in Railway

### Slow First Build
Railway uses Docker layer caching:
- **First build:** ~12 minutes (downloads Playwright browsers ~500MB)
- **Subsequent builds:** ~2-3 minutes (only if dependencies change)
- **Code-only changes:** ~30-60 seconds

## Cost Estimate

```
Crawl4AI + ChromaDB:  ~$2-3/month
Graphiti + Neo4j:     ~$5-7/month
────────────────────────────────
Total:                ~$7-10/month
```

**Embeddings:** FREE (sentence-transformers local model)

## More Info

See `INTEGRATION_STATUS.md` in the root directory for complete deployment status and issue history.

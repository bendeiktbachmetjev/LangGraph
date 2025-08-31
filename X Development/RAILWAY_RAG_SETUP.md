# Railway RAG Setup Instructions

## Current Status
- ✅ LangGraph API is running on Railway: `https://spotted-mom-production.up.railway.app`
- ❌ RAG system is currently disabled (`REG_ENABLED=false`)

## To Enable RAG on Railway

### Option 1: Via Railway Dashboard
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Find your project `spotted-mom-production`
3. Go to Variables tab
4. Add/update the following environment variable:
   ```
   REG_ENABLED=true
   ```
5. Deploy the changes

### Option 2: Via Railway CLI
```bash
# Login to Railway
railway login

# Link to your project
railway link

# Set the environment variable
railway variables set REG_ENABLED=true

# Deploy
railway up
```

## Required Environment Variables for RAG
Make sure these are set in Railway:
```
REG_ENABLED=true
EMBEDDINGS_PROVIDER=openai
EMBEDDINGS_MODEL=text-embedding-3-small
OPENAI_API_KEY=your_openai_api_key
RAG_INDEX_PATH=LangGraph/RAG/index
RAG_CORPUS_PATH=LangGraph/RAG/corpus
```

## Testing
After enabling RAG, test with:
```bash
# Test RAG status
curl "https://spotted-mom-production.up.railway.app/api/rag/status"

# Test RAG search
curl -X POST "https://spotted-mom-production.up.railway.app/api/rag/test/dev" \
  -H "Content-Type: application/json" \
  -d '{"query": "coaching techniques", "top_k": 3}'
```

## iOS App Integration
The iOS app is now configured to automatically use:
- **Development**: `http://192.168.1.83:8000` (local development)
- **Production**: `https://spotted-mom-production.up.railway.app` (Railway)

No manual URL configuration needed!

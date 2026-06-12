# Production AI Agent - Part 6 Final Project

Complete production-ready AI agent with all best practices implemented.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env from example
cp .env.example .env

# Run app
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build image
docker build -t my-agent:latest .

# Run container
docker run -p 8000:8000 \
  -e AGENT_API_KEY=dev-secret-key-123 \
  my-agent:latest
```

### Docker Compose

```bash
# Start all services
docker compose up

# Stop
docker compose down
```

## 📋 Features

✅ **Production-Ready:**
- Config from environment variables
- Health check (`/health`) + Readiness check (`/ready`)
- API key authentication
- Rate limiting (20 req/min per key)
- Budget tracking ($5/day per user)
- Graceful shutdown (SIGTERM handling)
- Structured logging
- In-flight request tracking

✅ **DevOps:**
- Multi-stage Docker build (optimized image size)
- Health checks in Dockerfile
- Proper signal handling
- Docker Compose orchestration
- `.dockerignore` for efficient builds

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Readiness Check
```bash
curl http://localhost:8000/ready
```

### Ask Question (requires API key)
```bash
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
```

### Rate Limit Test
```bash
# Send 25 requests — should fail after 20
for i in {1..25}; do
  curl -X POST http://localhost:8000/ask \
    -H "X-API-Key: dev-secret-key-123" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"Test $i\"}"
  echo ""
done
```

### Budget Test
```bash
# Send 501 requests (501 × $0.01 = $5.01 > $5.00 budget)
# Should fail around request 500
```

## 📁 Project Structure

```
my-production-agent/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── main.py             # FastAPI application
│   ├── auth.py             # API key authentication
│   ├── rate_limiter.py     # Rate limiting logic
│   └── cost_guard.py       # Budget tracking
├── utils/
│   ├── __init__.py
│   └── mock_llm.py         # Mock LLM for testing
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Compose configuration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .dockerignore          # Docker build exclusions
└── README.md              # This file
```

## 🔒 Security

- API keys required for `/ask` endpoint
- Rate limiting prevents abuse
- Budget tracking prevents overspending
- Sensitive logs are rate-limited

## 📈 Scaling

Current implementation uses in-memory tracking. For production with multiple instances:

1. **Replace in-memory with Redis:**
   ```python
   # rate_limiter.py
   r = redis.from_url(settings.redis_url)
   _rate_limits = r  # Use Redis instead
   ```

2. **Add load balancer (Nginx):**
   ```yaml
   # docker-compose.yml
   services:
     nginx:
       image: nginx:latest
       ports:
         - "80:80"
     agent:
       scale: 3
   ```

## 🚢 Deployment

### Railway

```bash
railway init
railway variables set AGENT_API_KEY=your-secret-key
railway up
```

### Render

```bash
# Push to GitHub
git push origin main

# Connect in Render dashboard
# Deploy from GitHub repo
```

## 📊 Monitoring

Check logs:
```bash
docker compose logs -f agent
```

Health endpoint returns:
- `uptime_seconds`: How long container has been running
- `timestamp`: Current time

## 🛑 Graceful Shutdown

When receiving SIGTERM:
1. Stop accepting new requests
2. Wait for in-flight requests to complete (max 30s)
3. Close connections
4. Exit cleanly

## 📝 License

AICB-P1 · VinUniversity 2026

# Deployment Information

**Student:** Vũ Quang Vinh — 2A202600935

## Public URL
https://lab12-production-f2a2.up.railway.app

## Platform
Railway

---

## Test Commands

### Health Check
```bash
curl https://lab12-production-f2a2.up.railway.app/health
# Expected: {"status":"ok","uptime_seconds":...,"timestamp":"..."}
```

### Root
```bash
curl https://lab12-production-f2a2.up.railway.app/
# Expected: {"message":"Production AI Agent is running","version":"1.0.0","environment":"production","docs":"/docs"}
```

### Readiness Check
```bash
curl https://lab12-production-f2a2.up.railway.app/ready
# Expected: {"ready":true,"in_flight_requests":0}
```

### Authentication Required (no key → 401)
```bash
curl -X POST https://lab12-production-f2a2.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
# Expected: 401 Unauthorized
```

### API Test (with authentication)
```bash
curl -X POST https://lab12-production-f2a2.up.railway.app/ask \
  -H "X-API-Key: vinh-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
# Expected: {"question":"Hello","answer":"...","timestamp":"..."}
```

### Rate Limiting Test (→ 429 after 20 requests)
```bash
for i in {1..25}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://lab12-production-f2a2.up.railway.app/ask \
    -H "X-API-Key: vinh-secret-key-2026" \
    -H "Content-Type: application/json" \
    -d '{"question":"test"}'
done
# First 20: 200, after that: 429
```

---

## Environment Variables Set on Railway

| Variable | Value |
|----------|-------|
| ENVIRONMENT | production |
| AGENT_API_KEY | (secret) |
| JWT_SECRET | (secret) |
| LOG_LEVEL | INFO |
| RATE_LIMIT_PER_MINUTE | 20 |
| DAILY_BUDGET_USD | 5.0 |

---

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Health check](screenshots/health.png)

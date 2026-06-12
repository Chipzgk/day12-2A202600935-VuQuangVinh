# Day 12 Lab - Mission Answers

**Student Name:** Vũ Quang Vinh  
**Student ID:** 2A202600935  
**Date:** 12/06/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. Hardcoded `PORT=8000` trong Dockerfile — Railway inject port động, bị override
2. `ENV PORT=8000` trong Dockerfile ghi đè biến Railway cấp phát
3. Default secrets (`dev-key-change-me`, `dev-jwt-secret`) không được thay thế khi lên production
4. `CMD` dùng port cứng thay vì đọc `${PORT}` từ environment
5. `ENVIRONMENT` không được set trên Railway Variables → app chạy ở `development` mode dù đã deploy

### Exercise 1.3: Comparison table

| Feature | Development | Production | Why Important? |
|---------|-------------|------------|----------------|
| Config | Hardcoded defaults, `.env` file | Environment variables từ Railway | Bảo mật, linh hoạt |
| Secrets | `dev-key-change-me` | Key mạnh, set qua Railway Variables | Tránh bị tấn công |
| Port | Hardcode 8000 | Dynamic `${PORT}` từ Railway | Railway assign port khác nhau |
| Logging | DEBUG | INFO | Tránh lộ thông tin nhạy cảm |
| CORS | `*` | Restricted origins | Bảo vệ API khỏi abuse |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image:** `python:3.11-slim` — nhẹ hơn `python:3.11` đầy đủ, đủ dùng cho production
2. **Working directory:** `/app`
3. **Multi-stage build:** Stage 1 (`builder`) cài dependencies, Stage 2 (`runtime`) chỉ copy kết quả → image nhỏ hơn
4. **PYTHONUNBUFFERED=1:** Đảm bảo log được in ra ngay lập tức, không bị buffer
5. **HEALTHCHECK:** Container tự kiểm tra `/health` mỗi 30s, restart nếu fail

### Exercise 2.3: Image size comparison

- Development (full): ~900 MB
- Production (multi-stage slim): ~200 MB
- Difference: ~78% nhỏ hơn

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- **URL:** https://lab12-production-f2a2.up.railway.app
- **Platform:** Railway
- **Status:** Running — `{"message":"Production AI Agent is running","version":"1.0.0","environment":"production"}`

---

## Part 4: API Security

### Exercise 4.1-4.3: Test results

```bash
# Health check — không cần auth
curl https://lab12-production-f2a2.up.railway.app/health
# {"status":"ok","uptime_seconds":...,"timestamp":"..."}

# Gọi /ask không có API key → 401
curl -X POST https://lab12-production-f2a2.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
# {"detail":"Invalid API key"}  → 401 Unauthorized

# Gọi /ask với API key hợp lệ → 200
curl -X POST https://lab12-production-f2a2.up.railway.app/ask \
  -H "X-API-Key: vinh-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
# {"question":"Hello","answer":"Agent đang hoạt động tốt!...","timestamp":"..."}
```

### Exercise 4.4: Cost guard implementation

`cost_guard.py` dùng in-memory dictionary theo dõi chi phí mỗi user mỗi ngày. Mỗi request tính $0.01. Khi tổng vượt `DAILY_BUDGET_USD` (mặc định $5.0) → trả về HTTP 402. Key format: `budget:{user_id}:{YYYY-MM-DD}` để tự reset mỗi ngày. Trong production thực tế nên dùng Redis để persist qua restart.

---

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

**Rate Limiting (`rate_limiter.py`):**  
Dùng sliding window theo phút. Key format `rate_limit:{user_id}:{YYYY-MM-DD-HH-MM}`, giới hạn 20 req/min (config `RATE_LIMIT_PER_MINUTE`). Vượt giới hạn → HTTP 429.

**Graceful Shutdown (`main.py`):**  
Dùng `lifespan` context manager của FastAPI. Khi nhận SIGTERM, set `_is_ready = False`, chờ tối đa 30s cho in-flight requests hoàn thành trước khi tắt.

**Health & Readiness Probes:**  
- `/health` — liveness probe, luôn trả 200 nếu container còn sống  
- `/ready` — readiness probe, trả 503 nếu app chưa sẵn sàng nhận traffic

**Stateless Design:**  
State (rate limit, budget) hiện dùng in-memory dict. Đã chuẩn bị `REDIS_URL` trong config để migrate sang Redis khi scale nhiều instance.

**In-flight Request Tracking:**  
Middleware `track_requests` đếm số request đang xử lý, dùng cho graceful shutdown tránh drop request giữa chừng.

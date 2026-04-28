# Design Decisions & Tradeoffs

## Architecture Overview

### Monolithic vs. Microservices

**Decision:** Monolithic architecture with clear separation

**Reasoning:**

- ✅ Simpler to develop, deploy, and maintain initially
- ✅ Easier debugging with single codebase
- ✅ Lower operational overhead
- ⚠️ Can be scaled to microservices later if needed

### Why FastAPI for Backend?

**Decision:** FastAPI (Python)

**Advantages:**

- ⚡ Auto-generated API documentation (Swagger UI)
- 🔄 Built-in async/await support for concurrent requests
- 🛡️ Built-in data validation with Pydantic
- 📚 Great for AI/ML integrations (Anthropic, etc.)
- 🚀 One of the fastest Python frameworks

### Why Next.js for Frontend?

**Decision:** Next.js 14 with TypeScript

**Advantages:**

- ⚡ Server-side rendering + Static generation
- 🎨 Built-in CSS support (Tailwind)
- 🔒 API routes (optional backend layer)
- 📱 Mobile-responsive by default
- 🌐 Great for SEO
- 🚀 Fast development experience

### Why MySQL?

**Decision:** MySQL (RDBMS)

**Reasoning:**

- 📊 Structured data with clear relationships
- 🔐 ACID compliance for financial data (funding amounts)
- 🏗️ Easy to reason about schema
- 📈 Scales well for this use case
- 🛠️ Great DBever support for management

---

## Data Flow Architecture

```
┌─────────────────┐
│   Next.js App   │ (Frontend)
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI        │ (Backend)
├─────────────────┤
│ • Routes        │
│ • Services      │
│ • Middlewares   │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │          │         │          │
    ▼          ▼         ▼          ▼
  MySQL    Tavily    Anthropic   Resend
(Database) (Search)  (AI)         (Email)
```

---

## Key Design Decisions

### 1. Authentication Strategy

**Decision:** JWT tokens + HTTP-only considerations (frontend)

**Implementation:**

```python
# Backend: Issue JWT on login
access_token = create_access_token(email=user.email)

# Frontend: Store in localStorage (sent via query param)
# Query param approach because:
# - Next.js doesn't have native HTTP-only cookie API
# - Works across domains
# - Still secure with HTTPS
```

**Tradeoffs:**

- ✅ Stateless (no session storage needed)
- ✅ Scales horizontally
- ⚠️ Token can be stolen via XSS (mitigated with CSP, sanitization)
- 🔄 Plan to upgrade to HTTP-only cookies in production

### 2. Database Deduplication

**Decision:** Use unique constraint on company name

```python
# Check before creating
existing = db.query(Company).filter(
    Company.name.ilike(company_name)
).first()

if existing:
    # Update with new data
else:
    # Create new record
```

**Reasoning:**

- ✅ Prevents duplicate companies
- ✅ Updates data if newer info appears
- ⚠️ Case-insensitive to handle variations

### 3. Hiring Status Classification

**Decision:** Three-tier system (0, 1, 2)

| Status | Label              | Confidence |
| ------ | ------------------ | ---------- |
| 0      | Not Hiring         | Low        |
| 1      | Potentially Hiring | Medium     |
| 2      | Actively Hiring    | High       |

**Why:**

- Simple for filtering/display
- AI can classify with confidence scores
- Can be extended later

### 4. External API Integration

**Decision:** Separate service modules

```python
# services/tavily.py
# services/anthropic.py
# services/resend.py
```

**Benefits:**

- ✅ Decoupled from routes
- ✅ Easy to mock for testing
- ✅ Can swap providers easily
- ✅ Centralized error handling

### 5. Email Template Generation

**Decision:** AI-powered with fallback template

```python
async def generate_outreach_email(
    company_name: str,
    funding_info: dict,
    hiring_status: int
) -> str:
    # Uses Anthropic to generate personalized email
    # Falls back to default template if API fails
```

**Reasoning:**

- ✅ Personalized for each company
- ✅ Better open/response rates
- ⚠️ Requires valid API key
- 🔄 Can batch-generate for performance

### 6. Data Enrichment Pipeline

**Decision:** Sequential enrichment (extract → analyze → store)

```
Raw Search Results
       ↓
Anthropic Extract (company info)
       ↓
Anthropic Analyze (hiring status)
       ↓
Store in MySQL
       ↓
Generate Email Template
```

**Tradeoffs:**

- ✅ Structured approach
- ✅ Easy to debug
- ⚠️ Multiple API calls (cost/latency)
- 🚀 Future: Could parallelize some calls

### 7. Frontend State Management

**Decision:** React hooks + localStorage (no Redux/Zustand)

**Reasoning:**

- ✅ Simple for this app size
- ✅ Less boilerplate
- ✅ Easy to understand
- ⚠️ Would need Zustand if complexity grows

### 8. Styling Approach

**Decision:** Tailwind CSS + custom CSS

```css
/* Gradient utilities */
.gradient-text {
  /* gradient effect */
}
.glass-effect {
  /* glass morphism */
}
.fade-in {
  /* animation */
}
```

**Benefits:**

- ✅ Rapid UI development
- ✅ Consistent design system
- ✅ Dark mode ready
- 🎨 Beautiful, modern look

---

## API Design Decisions

### Pagination

**Decision:** Skip/Limit pattern (not cursor)

```python
@app.get("/companies")
async def get_companies(
    skip: int = 0,
    limit: int = 20
):
```

**Reasoning:**

- ✅ Simple implementation
- ✅ Works well for <10k records
- 🚀 Can upgrade to cursor if data grows

### Response Format

**Decision:** Consistent JSON responses with metadata

```json
{
  "companies": [...],
  "total_found": 42,
  "processed_at": "2024-01-15T10:30:00Z",
  "message": "Success"
}
```

**Benefits:**

- ✅ Predictable format
- ✅ Timestamp for cache invalidation
- ✅ User-friendly message

### Error Handling

**Decision:** HTTP status codes + descriptive messages

```python
# 400 - Bad Request (validation error)
# 401 - Unauthorized (auth failed)
# 404 - Not Found (resource missing)
# 500 - Server Error (with logged details)
```

---

## Performance Optimizations

### 1. Database Indexing

```sql
CREATE INDEX idx_companies_funding_date ON companies(funding_date);
CREATE INDEX idx_outreach_user_id ON outreach(user_id);
```

**Impact:** O(log n) lookups instead of O(n) scans

### 2. API Batching

Instead of N+1 queries:

```python
# ✅ Good: Single query with joins
companies = db.query(Company).options(
    joinedload(Company.outreaches)
).all()

# ❌ Bad: Query in loop
for company in companies:
    outreaches = db.query(Outreach).filter(...).all()
```

### 3. Frontend Image Optimization

```typescript
import Image from 'next/image';
// Automatic optimization, lazy loading
<Image src="..." width={100} height={100} />
```

### 4. Caching Strategy

**Frontend:**

- Next.js automatic caching
- localStorage for auth tokens

**Backend:**

- No explicit caching (data fresh)
- Could add Redis if needed

---

## Security Decisions

### 1. Password Hashing

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Bcrypt: industry standard, slow by design
```

### 2. CORS Configuration

```python
# Only allow frontend origin
CORS_ORIGINS = ["http://localhost:3000"]
```

### 3. SQL Injection Prevention

```python
# ✅ Safe: Parameterized queries via SQLAlchemy
user = db.query(User).filter(User.email == email).first()

# ❌ Unsafe: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### 4. XSS Prevention

- React auto-escapes content
- Sanitize user inputs on backend
- CSP headers in production

---

## Scalability Considerations

### Horizontal Scaling

Current design supports:

- ✅ Running multiple backend instances
- ✅ Load balancing with nginx
- ✅ Shared database layer

### Vertical Scaling

Can optimize:

- Add Redis for caching
- Upgrade database to RDS
- CDN for static assets
- API rate limiting

### Future Improvements

1. **Async Task Queue** (Celery/RQ)
   - Long-running discovery jobs
   - Scheduled scans (daily, weekly)

2. **Caching Layer** (Redis)
   - Cache company data
   - Cache API responses

3. **Search Index** (Elasticsearch)
   - Full-text search on companies
   - Better filtering

4. **Webhooks**
   - Real-time notifications
   - Third-party integrations

---

## Known Limitations & Tradeoffs

| Feature       | Current            | Limitation      | Future              |
| ------------- | ------------------ | --------------- | ------------------- |
| Discovery     | Manual trigger     | No scheduling   | Cron jobs           |
| Email         | Single             | No bulk sending | Batch API           |
| Notifications | None               | Manual checking | Webhooks/Email      |
| Search        | Tavily + Anthropic | API costs       | Cached index        |
| Auth          | JWT                | Token on URL    | OAuth 2.0           |
| Deployment    | Local              | Manual setup    | Docker + CI/CD      |
| Database      | MySQL              | Single instance | Replica set         |
| Analytics     | None               | No insights     | Logging + Dashboard |

---

## Conclusion

These design decisions prioritize:

1. **Development Speed** - Get MVP working quickly
2. **Maintainability** - Clear, understandable code
3. **Scalability** - Can grow without major rewrites
4. **Security** - Standard best practices
5. **User Experience** - Beautiful, responsive UI

The architecture is flexible enough to accommodate changes as requirements evolve.

# API Rate Limits & Legal Constraints

## API Rate Limits

### Tavily API

**Free Plan:**

- 100 queries/month
- Response time: ~1-3 seconds
- Rate limit: Not specified (recommended: 1 req/sec)

**Pricing:**

- Free: 100 queries/month
- Pro: $10/month (10,000 queries)
- Enterprise: Custom pricing

**Rate Limiting Strategy:**

```python
# Implement backoff for 429 responses
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def search_with_retry():
    # Tavily search call
```

**Documentation:** https://tavily.com/docs/api-reference

---

### Groq API

**Free Tier:**

- Rate limit: 30 requests per minute (RPM)
- No credit limit for free tier
- Good for development and testing

**Paid Plan:**

- Pay-as-you-go pricing
- Scales with usage
- Groq Mixtral 8x7B: ~$0.27/1M tokens (input), ~$0.81/1M tokens (output)

**Optimization Tips:**

```python
# Groq is very fast, minimal optimization needed
# Use for quick email generation
# Batch requests for better throughput
```

**Cost Estimation:**

- Per company email: ~200 tokens input, 150 tokens output
- At $0.27/$0.81 per 1M tokens:
  - Input cost: ~$0.000054 per company
  - Output cost: ~$0.000122 per company
  - Total: ~$0.00018 per company (much cheaper than Anthropic)

**Documentation:** https://groq.com/openrouter-docs/

---

### Resend Email API

**Free Plan:**

- 100 emails/month (development)
- All features enabled

**Paid Plan:**

- Pay-as-you-go
- $0.0005 per email (up to 100/month free)
- For 1000 emails/month: ~$0.50

**Rate Limits:**

- 100 requests/day (free)
- 1000 requests/day (pro)

**Requirements & Configuration:**

For **development**, use Resend's test email (no verification needed):

```python
FROM_EMAIL = "onboarding@resend.dev"  # Testing - works out-of-the-box
```

For **production**, verify your custom domain:

```python
FROM_EMAIL = "noreply@yourdomain.com"  # Production - requires domain verification
```

# Production (with verification)

FROM_EMAIL = "noreply@yourdomain.com"

````

**Email Deliverability:**

- Free tier: May have lower deliverability
- Pro tier: Higher success rate
- Monitor bounce rates in dashboard

**Documentation:** https://resend.com/docs

---

## Usage Estimates

### Scenario: 100 Startups Per Month

| API    | Calls   | Cost             |
| ------ | ------- | ---------------- |
| Tavily | 2-3     | $0 (free tier)   |
| Groq   | ~100    | ~$0.02           |
| Resend | ~50-100 | $0 (free tier)   |
| **Total** | -       | **~$0.02/month** |

### Scenario: 1000 Startups Per Month

| API    | Calls     | Cost              |
| ------ | --------- | ----------------- |
| Tavily | 2-3       | $10 (pro tier)    |
| Groq   | ~1000     | ~$0.18            |
| Resend | ~500-1000 | ~$0.25            |
| **Total** | -         | **~$10.43/month** |

---

## Rate Limiting Implementation

### Backend Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/companies/discover")
@limiter.limit("5/hour")
async def discover_startups():
    # Only 5 discovery requests per hour per IP
````

### Recommended Limits

```python
# Per endpoint (per user)
Discovery: 5 per day
Email Generation: 20 per day
Email Send: 50 per day
Outreach Query: 100 per hour

# Global (total)
API Requests: 1000 per hour
Database Writes: 500 per minute
```

---

## Legal & Compliance

### Data Privacy

**GDPR Compliance:**

- ✅ User can request data export
- ✅ User can request deletion
- ✅ Privacy policy required
- ✅ Terms of service required

**CCPA Compliance:**

- ✅ Users control their data
- ✅ Can opt-out of tracking
- ✅ Must disclose data usage

**Implementation:**

```python
# Add endpoints for data export/deletion
@app.get("/users/me/export")
async def export_user_data():
    # Return all user data as JSON

@app.delete("/users/me")
async def delete_user_data():
    # Delete user and associated data
```

### Email Compliance

**CAN-SPAM Act (USA):**

- ✅ Include company name and address in emails
- ✅ Include unsubscribe mechanism
- ✅ Honor unsubscribe requests

**GDPR Email Requirements:**

- ✅ Only send to consented contacts
- ✅ Clear unsubscribe option
- ✅ Don't use purchased contact lists

**Implementation:**

```html
<!-- Add to every email -->
<footer>
  <p>CodeRound AI | 123 Company St, City, State</p>
  <p><a href="https://coderound.ai/unsubscribe">Unsubscribe</a></p>
</footer>
```

### Web Scraping Laws

**Important Notes:**

- ✅ Using Tavily API is compliant (legitimate service)
- ⚠️ Don't scrape competitor sites directly
- ✅ Public LinkedIn data OK via API
- ❌ Bypass rate limits or TOS

**Best Practice:**

```python
# Use official APIs, not scraping
# - LinkedIn official API
# - Crunchbase API
# - Company website public data
# - News APIs (Tavily, NewsAPI)
```

### Third-Party API Terms

**Tavily:**

- ✅ Commercial use allowed
- ✅ Reselling permitted (check terms)
- ⚠️ Attribution recommended

**Anthropic:**

- ✅ Commercial use allowed
- ⚠️ Can't use for competing services
- ✅ Can train on non-Anthropic data

**Resend:**

- ✅ Commercial use allowed
- ✅ Transactional emails OK
- ⚠️ Can't send unsolicited bulk emails

---

## Cost Optimization Strategies

### 1. Batch Processing

```python
# Instead of individual requests
# Process in batches of 10-50
companies_to_enrich = [...]

# Batch enrichment
enriched_data = await enrich_batch(companies_to_enrich)
```

### 2. Caching Results

```python
# Cache company data for 7 days
@cache(ttl=604800)
async def get_company_enrichment(company_id):
    return await anthropic.analyze_company(company_id)
```

### 3. Smart API Selection

```python
# Use cheaper API when appropriate
if confidence_level > 0.8:
    # Don't need expensive AI analysis
    return simple_result
else:
    # Use Anthropic for complex cases
    return await anthropic.analyze(data)
```

### 4. Monitor Usage

```python
# Log all API calls
logging.info(f"Tavily: {tavily_calls} calls")
logging.info(f"Anthropic: {anthropic_tokens} tokens")
logging.info(f"Resend: {resend_emails} emails")

# Set budgets and alerts
if monthly_cost > BUDGET_LIMIT:
    send_alert("API costs exceeded!")
```

---

## Monitoring & Alerts

### Key Metrics to Track

```python
# In backend logging
- API call count (daily)
- API latency (average response time)
- Error rates (429, 500, etc.)
- Cost spend (daily, monthly)
- Email bounce rate
- Email delivery rate
```

### Alert Thresholds

```python
if api_error_rate > 5%:
    alert("High error rate detected")

if avg_latency > 5_seconds:
    alert("API responses slow")

if estimated_daily_cost > DAILY_BUDGET:
    alert("Cost exceeding budget")
```

---

## Production Considerations

### Before Going Live

- [ ] Set up monitoring/logging
- [ ] Configure rate limiting
- [ ] Set up alerting system
- [ ] Document API limits
- [ ] Create privacy policy
- [ ] Create terms of service
- [ ] Implement unsubscribe mechanism
- [ ] Set up email compliance tracking
- [ ] Budget for API costs
- [ ] Get API key backup/rotation plan

### Cost Estimates (Annual)

| Scenario             | Tavily | Anthropic | Resend | Total |
| -------------------- | ------ | --------- | ------ | ----- |
| 100 startups/month   | $100   | $72       | $12    | $184  |
| 1000 startups/month  | $120   | $720      | $30    | $870  |
| 10000 startups/month | $500   | $7200     | $60    | $7760 |

---

## Useful Resources

- Tavily: https://tavily.com/docs
- Anthropic: https://docs.anthropic.com/
- Resend: https://resend.com/docs
- GDPR: https://gdpr-info.eu/
- CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

---

## Questions?

Document any specific compliance questions or requirements your jurisdiction may have.

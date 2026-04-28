# API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

All requests (except signup/login) require a token passed as query parameter:

```
?token=your_jwt_token_here
```

The token is obtained from the login/signup endpoint and should be stored securely.

---

## Authentication Endpoints

### 1. Sign Up

Create a new user account.

**Endpoint:** `POST /auth/signup`

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "last_login": null
  }
}
```

**Error Responses:**

- `400 Bad Request` - Email already registered or validation error
- `500 Internal Server Error` - Server error

---

### 2. Login

Authenticate and get access token.

**Endpoint:** `POST /auth/login`

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "last_login": "2024-01-15T11:30:00"
  }
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid email or password
- `403 Forbidden` - Account is inactive
- `500 Internal Server Error` - Server error

---

### 3. Get Current User

Get authenticated user's profile.

**Endpoint:** `GET /auth/me?token=YOUR_TOKEN`

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "last_login": "2024-01-15T11:30:00"
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User not found
- `500 Internal Server Error` - Server error

---

### 4. Logout

Logout user (client-side token removal).

**Endpoint:** `POST /auth/logout`

**Response (200 OK):**

```json
{
  "message": "Logged out successfully"
}
```

---

## Company Endpoints

### 1. Discover Startups

Trigger automatic discovery of recently funded startups.

**Endpoint:** `POST /companies/discover?token=YOUR_TOKEN`

**Query Parameters:**

- `token` (required) - JWT token

**Response (200 OK):**

```json
{
  "companies": [
    {
      "id": 1,
      "name": "TechStartup Inc",
      "website": "https://techstartup.com",
      "linkedin_url": "https://linkedin.com/company/techstartup",
      "funding_amount": 5000000,
      "funding_date": "2024-01-10T00:00:00",
      "funding_round": "Seed",
      "investors": "[\"Investor A\", \"Investor B\"]",
      "country": "USA",
      "description": "Building AI tools for startups",
      "hiring_status": 2,
      "hiring_positions": "[\"Backend Engineer\", \"Frontend Engineer\"]",
      "enriched_data": {...},
      "decision_makers": {...},
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "last_enriched": "2024-01-15T10:35:00"
    }
  ],
  "total_found": 5,
  "processed_at": "2024-01-15T10:35:00",
  "message": "Found and enriched 5 startup(s)"
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid token
- `500 Internal Server Error` - Discovery failed

---

### 2. Get All Companies

Retrieve paginated list of discovered companies with optional filters.

**Endpoint:** `GET /companies?token=YOUR_TOKEN&hiring_status=2&skip=0&limit=20`

**Query Parameters:**

- `token` (required) - JWT token
- `hiring_status` (optional) - Filter: 0=not hiring, 1=potentially, 2=actively
- `skip` (optional) - Pagination offset (default: 0)
- `limit` (optional) - Pagination limit (default: 20, max: 100)

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "name": "TechStartup Inc",
    "website": "https://techstartup.com",
    "linkedin_url": "https://linkedin.com/company/techstartup",
    "funding_amount": 5000000,
    "funding_date": "2024-01-10T00:00:00",
    "funding_round": "Seed",
    "investors": "[\"Investor A\", \"Investor B\"]",
    "country": "USA",
    "description": "Building AI tools for startups",
    "hiring_status": 2,
    "hiring_positions": "[\"Backend Engineer\", \"Frontend Engineer\"]",
    "enriched_data": null,
    "decision_makers": null,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "last_enriched": null
  }
]
```

**Error Responses:**

- `401 Unauthorized` - Invalid token
- `500 Internal Server Error` - Server error

---

### 3. Get Single Company

Retrieve detailed information about a specific company.

**Endpoint:** `GET /companies/{id}?token=YOUR_TOKEN`

**Path Parameters:**

- `id` (required) - Company ID

**Query Parameters:**

- `token` (required) - JWT token

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "TechStartup Inc",
  "website": "https://techstartup.com",
  "linkedin_url": "https://linkedin.com/company/techstartup",
  "funding_amount": 5000000,
  "funding_date": "2024-01-10T00:00:00",
  "funding_round": "Seed",
  "investors": "[\"Investor A\", \"Investor B\"]",
  "country": "USA",
  "description": "Building AI tools for startups",
  "hiring_status": 2,
  "hiring_positions": "[\"Backend Engineer\", \"Frontend Engineer\"]",
  "enriched_data": {...},
  "decision_makers": {...},
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "last_enriched": "2024-01-15T10:35:00"
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid token
- `404 Not Found` - Company not found
- `500 Internal Server Error` - Server error

---

## Outreach Endpoints

### 1. Generate Outreach Email

Generate an AI-powered personalized outreach email.

**Endpoint:** `POST /outreach/generate-email?token=YOUR_TOKEN`

**Query Parameters:**

- `token` (required) - JWT token

**Request Body:**

```json
{
  "company_id": 1
}
```

**Response (200 OK):**

```json
{
  "subject": "CodeRound - Streamline Hiring at TechStartup Inc",
  "body": "Hi there,\n\nI came across TechStartup Inc and was impressed by your recent Seed funding of $5M. We've been working with fast-growing startups like yours to streamline their hiring process...",
  "company_id": 1,
  "company_name": "TechStartup Inc"
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid token
- `404 Not Found` - Company not found
- `500 Internal Server Error` - Email generation failed

---

### 2. Send Outreach Email

Send the outreach email to a company contact.

**Endpoint:** `POST /outreach/send?token=YOUR_TOKEN`

**Query Parameters:**

- `token` (required) - JWT token

**Request Body:**

```json
{
  "company_id": 1,
  "email_sent_to": "founder@techstartup.com",
  "email_subject": "CodeRound - Streamline Hiring at TechStartup Inc",
  "email_content": "Hi there,\n\nI came across TechStartup Inc..."
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": 1,
  "company_id": 1,
  "email_sent_to": "founder@techstartup.com",
  "email_subject": "CodeRound - Streamline Hiring at TechStartup Inc",
  "email_content": "Hi there,\n\nI came across TechStartup Inc...",
  "response_status": 0,
  "response_received_at": null,
  "response_notes": null,
  "sent_at": "2024-01-15T10:35:00",
  "created_at": "2024-01-15T10:35:00"
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid token
- `404 Not Found` - Company not found
- `500 Internal Server Error` - Email send failed

---

### 3. Get Outreach History

Retrieve user's outreach history with optional filters.

**Endpoint:** `GET /outreach?token=YOUR_TOKEN&response_status=0&skip=0&limit=20`

**Query Parameters:**

- `token` (required) - JWT token
- `response_status` (optional) - Filter: 0=pending, 1=positive, 2=negative, 3=no response
- `skip` (optional) - Pagination offset (default: 0)
- `limit` (optional) - Pagination limit (default: 20)

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "company_id": 1,
    "email_sent_to": "founder@techstartup.com",
    "email_subject": "CodeRound - Streamline Hiring at TechStartup Inc",
    "email_content": "...",
    "response_status": 0,
    "response_received_at": null,
    "response_notes": null,
    "sent_at": "2024-01-15T10:35:00",
    "created_at": "2024-01-15T10:35:00"
  }
]
```

**Error Responses:**

- `401 Unauthorized` - Invalid token
- `500 Internal Server Error` - Server error

---

### 4. Update Outreach Status

Update response status for an outreach email.

**Endpoint:** `PATCH /outreach/{id}?token=YOUR_TOKEN`

**Path Parameters:**

- `id` (required) - Outreach record ID

**Query Parameters:**

- `token` (required) - JWT token

**Request Body:**

```json
{
  "response_status": 1,
  "response_notes": "Founder replied interested in demo"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": 1,
  "company_id": 1,
  "email_sent_to": "founder@techstartup.com",
  "email_subject": "CodeRound - Streamline Hiring at TechStartup Inc",
  "email_content": "...",
  "response_status": 1,
  "response_received_at": "2024-01-16T09:00:00",
  "response_notes": "Founder replied interested in demo",
  "sent_at": "2024-01-15T10:35:00",
  "created_at": "2024-01-15T10:35:00"
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid token
- `404 Not Found` - Outreach not found
- `500 Internal Server Error` - Update failed

---

## Status Codes

| Code | Meaning                        |
| ---- | ------------------------------ |
| 200  | Success                        |
| 201  | Created                        |
| 400  | Bad Request (validation error) |
| 401  | Unauthorized (auth failed)     |
| 403  | Forbidden (account inactive)   |
| 404  | Not Found                      |
| 500  | Internal Server Error          |

---

## Enums

### Hiring Status

```
0 = Not Hiring
1 = Potentially Hiring
2 = Actively Hiring
```

### Response Status

```
0 = Pending
1 = Positive Response
2 = Negative Response
3 = No Response
```

### Funding Rounds

```
Seed
Series A
Series B
Series C
Series D
Series E+
Pre-Seed
Venture Round
```

---

## Example Workflow

### 1. User Signup

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123",
    "name": "John Doe"
  }'
```

### 2. Start Discovery

```bash
curl -X POST http://localhost:8000/api/companies/discover \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN"}'
```

### 3. Get Companies

```bash
curl "http://localhost:8000/api/companies?token=YOUR_TOKEN&hiring_status=2"
```

### 4. Generate Email

```bash
curl -X POST http://localhost:8000/api/outreach/generate-email \
  -H "Content-Type: application/json" \
  -d '{"company_id": 1, "token": "YOUR_TOKEN"}'
```

### 5. Send Email

```bash
curl -X POST http://localhost:8000/api/outreach/send \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "email_sent_to": "founder@company.com",
    "email_subject": "CodeRound Demo",
    "email_content": "Hi there...",
    "token": "YOUR_TOKEN"
  }'
```

---

## Interactive API Documentation

When running the backend locally, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API exploration with real-time testing.

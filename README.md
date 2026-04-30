# CodeRound Startup Discovery Radar

**An automated system that discovers startups that raised funding in the last 30 days and are actively hiring.**

A production-ready full-stack application for finding recently-funded startups and automating outreach with intelligent data extraction and email generation.

## 🎯 Overview

CodeRound Startup Discovery Radar automates the process of:

- **Discovering** startups with recent seed funding (Tavily web search)
- **Parsing** company data using regex and pattern matching
- **Identifying** companies actively hiring in tech roles
- **Generating** personalized outreach emails (with fallback templates)
- **Tracking** engagement and responses in real-time

## 🏗️ Architecture

```
┌─────────────────────┐
│   Next.js Frontend  │
│  • TypeScript       │
│  • TailwindCSS      │
│  • Safe JSON parsing│
└──────────┬──────────┘
           │ REST API (JSON)
┌──────────▼──────────┐
│  FastAPI Backend    │
│  • Python async     │
│  • Pydantic models  │
│  • SQLAlchemy ORM   │
└──────────┬──────────┘
           │ SQL
┌──────────▼──────────┐
│   MySQL Database    │
│  • Users table      │
│  • Companies table  │
│  • Outreach logs    │
└─────────────────────┘

External APIs:
├─ Tavily (Web Search)
└─ Resend (Email Service)

Note: Anthropic bypassed (credit issues)
Use direct parsing + fallback templates
```

## 📋 Tech Stack

| Layer    | Technology                                    |
| -------- | --------------------------------------------- |
| Frontend | Next.js 14, React 18, TypeScript, TailwindCSS |
| Backend  | FastAPI, Python 3.9+, SQLAlchemy              |
| Database | MySQL 8.0+, JSON fields                       |
| Auth     | JWT tokens, bcrypt password hashing           |
| APIs     | Tavily (search)                               |
| Email    | Resend service                                |

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- MySQL 8.0+
- API Keys: [Tavily](https://tavily.com), [Resend](https://resend.com)

### 5-Minute Setup

See [QUICKSTART.md](QUICKSTART.md) for step-by-step guide.

**Or manual setup:**

```bash
# Backend
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add API keys
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:3000` 🎉

## � Project Structure

```
coderound-startup-discovery/
├── frontend/               # Next.js React app (7 pages, 4 components)
│   ├── pages/
│   │   ├── _app.tsx       # App wrapper
│   │   ├── index.tsx      # Landing page
│   │   ├── login.tsx      # Login page
│   │   ├── signup.tsx     # Signup page
│   │   ├── dashboard/     # Dashboard
│   │   └── results/       # Results + outreach
│   ├── components/        # 4 reusable components
│   ├── lib/              # API, auth, storage utilities
│   ├── types/            # TypeScript type definitions
│   ├── styles/           # Tailwind CSS
│   └── package.json
│
├── backend/              # FastAPI Python app
│   ├── main.py           # Entry point
│   ├── config.py         # Settings
│   ├── models.py         # Database models (3 tables)
│   ├── schemas.py        # Pydantic validation
│   ├── database.py       # DB connection
│   ├── routes/           # 3 route modules
│   ├── services/         # 4 service integrations
│   ├── utils/            # Utilities
│   └── requirements.txt   # 20+ dependencies
│
├── database/             # MySQL setup
│   └── schema.sql        # Complete schema with indexes
│
├── docs/                 # Comprehensive documentation
│   ├── SETUP.md          # Installation guide
│   ├── API.md            # API reference
│   ├── DESIGN.md         # Architecture decisions
│   └── RATE_LIMITS.md    # Compliance + costs
│
├── QUICKSTART.md         # 5-minute setup guide
├── DEPLOYMENT_CHECKLIST.md
├── PROJECT_SUMMARY.md    # What's been built
├── README.md             # This file
└── .gitignore
```

**Total: 60+ files, 10,000+ lines of code**

## 🔐 Authentication Flow

1. User signs up with email/password
2. Backend validates and hashes password
3. JWT token issued on successful login
4. Token stored in HTTP-only cookie (frontend)
5. All requests include token for validation

## 🔍 Discovery & Outreach Flow

### Startup Discovery

1. User clicks "Discover Startups" button
2. Backend queries Tavily for recent funding news
3. Anthropic AI enriches data (extracting key details)
4. Results deduplicated and stored in MySQL
5. Hiring status identified via LinkedIn/web searches
6. Results sent to frontend

### Outreach

1. User selects companies to reach out
2. Modal opens with AI-generated email template
3. User edits email (optional)
4. Email sent via Resend API
5. Outreach logged in database with timestamp
6. User can track responses (positive/negative/no response)

## 🗄️ Database Schema

### Users

- id (PK)
- email (unique)
- password_hash
- name
- created_at
- last_login

### Companies

- id (PK)
- name (unique indexed)
- website
- linkedin_url
- funding_amount
- funding_date
- funding_round
- investors
- country
- description
- hiring_status (not_hiring, potentially_hiring, actively_hiring)
- enriched_data (JSON)
- created_at
- updated_at

### Outreach

- id (PK)
- user_id (FK)
- company_id (FK)
- email_sent_to
- email_content
- sent_at
- response_status (pending, positive, negative)
- response_received_at
- notes
- created_at

## 🔑 Environment Variables

### Backend (.env)

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/coderound
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

TAVILY_API_KEY=your-tavily-key
ANTHROPIC_API_KEY=your-anthropic-key
RESEND_API_KEY=your-resend-key

FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=CodeRound Startup Discovery
```

## 📊 API Endpoints

### Authentication

- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

### Companies

- `GET /companies` - List discovered companies (with filters)
- `POST /companies/discover` - Trigger discovery process
- `GET /companies/{id}` - Get company details
- `GET /companies/{id}/enrichment` - Get enriched data

### Outreach

- `GET /outreach` - List outreach history
- `POST /outreach/send` - Send email
- `PATCH /outreach/{id}` - Update outreach status

## 🔄 Automation Features

- **Auto-Refresh**: Discover new startups daily (cron job)
- **Auto-Dedup**: Check for duplicate companies before adding
- **Auto-Update**: Update company data if newer info appears
- **Auto-Email**: Generate and send personalized emails
- **Auto-Track**: Monitor responses and engagement

## 📈 Workflow

1. **Sign Up/Login** → Create account
2. **Dashboard** → See welcome message, click "Discover Startups"
3. **Discovery** → System fetches data, displays results
4. **Review** → View companies with hiring status labels
5. **Outreach** → Select companies, generate/edit emails, send
6. **Track** → Monitor responses in "Reached Out" section

## ⚙️ Configuration

### Rate Limits

- **Tavily**: 100 queries/month (check plan)
- **Anthropic**: Based on API key tier
- **Resend**: Based on email plan

### Search Parameters

- Time window: Last 30 days
- Keywords: "seed funding", "Series A", "hiring"
- Focus countries: USA, India, UK (configurable)

## 🚨 Error Handling

- Invalid credentials → 401 Unauthorized
- Database errors → 500 Internal Server Error
- API failures → Graceful degradation with retry logic
- Rate limit exceeded → Queue for later retry

## 📝 Logging

All requests, API calls, and database operations are logged to:

- `backend/logs/app.log` - Application logs
- `backend/logs/api.log` - API call logs
- `backend/logs/db.log` - Database query logs

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔄 CI/CD

GitHub Actions workflows:

- Test on push
- Deploy on merge to main
- Build Docker image (future)

## 📚 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation instructions
- [API Reference](docs/API.md) - Complete API documentation
- [Design Decisions](docs/DESIGN.md) - Architecture & tradeoff explanations
- [Rate Limits & Legal](docs/RATE_LIMITS.md) - API limits and compliance

# CodeRound Startup Discovery Radar

**An automated system that discovers startups that raised funding in the last 30 days and are actively hiring.**

A production-ready full-stack application for finding recently-funded startups and automating outreach with intelligent data extraction and email generation.

## Overview

CodeRound Startup Discovery Radar automates the process of:

- **Discovering** startups with recent seed funding (Tavily web search)
- **Parsing** company data using regex and pattern matching
- **Identifying** companies actively hiring in tech roles
- **Generating** personalized outreach emails (with fallback templates)
- **Tracking** engagement and responses in real-time

## Architecture

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

## Tech Stack

| Layer    | Technology                                    |
| -------- | --------------------------------------------- |
| Frontend | Next.js 14, React 18, TypeScript, TailwindCSS |
| Backend  | FastAPI, Python 3.9+, SQLAlchemy              |
| Database | MySQL 8.0+, JSON fields                       |
| Auth     | JWT tokens, bcrypt password hashing           |
| APIs     | Tavily (search)                               |
| Email    | Resend service                                |

## Quick Start

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

Visit `http://localhost:3000`

## Project Structure

```
coderound-startup-discovery/
│
├── frontend/                    # Next.js React App
│   ├── pages/
│   │   ├── _app.tsx            # App wrapper
│   │   ├── index.tsx           # Landing page
│   │   ├── login.tsx           # Login page
│   │   ├── signup.tsx          # Signup page
│   │   ├── dashboard/
│   │   │   └── index.tsx       # Dashboard (discovery trigger)
│   │   └── results/
│   │       └── index.tsx       # Results + outreach tabs
│   │
│   ├── components/              # 4 React components
│   │   ├── Layout.tsx          # Page wrapper
│   │   ├── Navbar.tsx          # Navigation bar
│   │   ├── ResultsCard.tsx     # Company card component
│   │   └── OutreachModal.tsx   # Email generation modal
│   │
│   ├── lib/                     # Utilities
│   │   ├── api.ts              # Axios HTTP client
│   │   ├── auth.ts             # JWT token management
│   │   ├── storage.ts          # localStorage wrapper
│   │   └── parsing.ts          # Safe JSON parsing
│   │
│   ├── types/
│   │   └── index.ts            # TypeScript interfaces
│   │
│   ├── styles/
│   │   └── globals.css         # TailwindCSS styling
│   │
│   ├── public/                 # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── backend/                     # FastAPI Python App
│   ├── main.py                 # Entry point + middleware
│   ├── config.py               # Settings (Pydantic)
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response models
│   ├── database.py             # SQLAlchemy setup
│   │
│   ├── routes/                 # API endpoints
│   │   ├── auth.py             # Signup, login, logout, profile
│   │   ├── companies.py        # Discovery, listing, filtering
│   │   └── outreach.py         # Email generation, sending, tracking
│   │
│   ├── services/               # External service integrations
│   │   ├── tavily.py           # Web search (funded startups)
│   │   ├── resend.py           # Email delivery
│   │   └── __init__.py
│   │
│   ├── utils/                  # Helper functions
│   │   ├── auth.py             # JWT creation/verification
│   │   └── helpers.py          # General utilities
│   │
│   ├── requirements.txt        # Python dependencies
│   └── .env.example
│
├── database/
│   └── schema.sql              # MySQL schema (users, companies, outreach)
│
├── docs/                        # Documentation
│   ├── SETUP.md                # Detailed setup guide
│   ├── API.md                  # API reference + examples
│   ├── DESIGN.md               # Architecture decisions
│   └── RATE_LIMITS.md          # Compliance + cost analysis
│
├── .git/                        # Git repository
├── .gitignore
├── README.md                    # This file
├── QUICKSTART.md               # 5-minute setup
├── DEPLOYMENT_CHECKLIST.md     # Pre-launch checklist
└── PROJECT_SUMMARY.md          # Feature overview
```

## Security Features

- Password Security: bcrypt hashing with 72-byte truncation
- Authentication: JWT tokens with 24-hour expiration
- Data Validation: Pydantic model validation on all inputs
- Database: SQL injection prevention via SQLAlchemy ORM
- Frontend: Safe JSON parsing (handles mixed types)

## Data Flow

### Discovery Process

1. User clicks "Discover Startups"
2. Backend calls Tavily API (web search)
3. Parse results with regex (company name, funding, round)
4. Detect hiring status from keywords
5. Store in MySQL (deduplicate by name)
6. Return to frontend as JSON
7. Frontend renders with TailwindCSS

### Outreach Process

1. User clicks "Reach Out" on company
2. OutreachModal opens
3. Generate fallback email (Anthropic bypassed)
4. User fills recipient email and edits content
5. Click Send → Resend API delivers
6. Log in database with timestamp
7. Show in "Reached Out" tab

## Database Schema

**Users**

- id, email (unique), password_hash, name, is_active
- created_at, last_login

**Companies**

- id, name (unique), website, linkedin_url
- funding_amount (float), funding_date, funding_round
- investors (array), country, description
- hiring_status (0/1/2), hiring_positions
- enriched_data (JSON dict), decision_makers (JSON dict)
- created_at, updated_at, last_enriched

**Outreach**

- id, user_id (FK), company_id (FK)
- email_sent_to, email_subject, email_content
- response_status (0/1/2/3), response_notes
- sent_at, response_received_at, created_at

## Environment Variables

### Backend (.env)

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/coderound_db
JWT_SECRET_KEY=your-32-character-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

TAVILY_API_KEY=your-tavily-key
RESEND_API_KEY=your-resend-key

CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=CodeRound
```

## API Endpoints

### Authentication

- `POST /signup` - Register user
- `POST /login` - Authenticate user
- `POST /logout` - Logout
- `GET /auth/me` - Get profile

### Companies

- `POST /companies/discover` - Trigger discovery
- `GET /companies` - List companies (with filters)
- `GET /companies/{id}` - Get details

### Outreach

- `POST /outreach/generate-email` - Email generation
- `POST /outreach/send` - Send email
- `GET /outreach` - Outreach history
- `PATCH /outreach/{id}` - Update status

## Key Features

- User Authentication (signup/login with JWT)
- Startup Discovery (Tavily web search + parsing)
- Company Deduplication (case-insensitive checking)
- Hiring Status Detection (keyword-based classification)
- Email Generation (template-based)
- Email Sending (Resend integration)
- Response Tracking (status + notes)
- Responsive UI (mobile + desktop)
- Safe JSON Parsing (frontend edge case handling)
- Error Handling (comprehensive logging)

## Recent Improvements

1. **Safe JSON Parsing** - Frontend utility handles objects, strings, edge cases
2. **Password Security** - Bcrypt 72-byte truncation for long passwords
3. **Request Models** - Proper Pydantic validation for all POST endpoints
4. **Dict-Only Data** - No JSON strings in backend, proper serialization
5. **Anthropic Bypass** - Direct Tavily parsing (API credit limits)
6. **Fallback Templates** - Email generation without external AI

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [docs/SETUP.md](docs/SETUP.md) - Detailed installation
- [docs/API.md](docs/API.md) - API reference
- [docs/DESIGN.md](docs/DESIGN.md) - Architecture decisions
- [docs/RATE_LIMITS.md](docs/RATE_LIMITS.md) - Compliance & costs
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre-launch tasks

## Workflow

1. **Sign Up** - Create account with email/password
2. **Dashboard** - See welcome message
3. **Discover** - Click button, system finds startups
4. **Review** - Filter by hiring status
5. **Outreach** - Send emails to prospects
6. **Track** - Monitor responses

## Production Ready

- Type-safe (TypeScript + Pydantic)
- Error handling & logging
- Input validation
- Database optimization
- Security best practices
- Responsive design
- API documentation
- Deployment guide

## Support

All questions answered in documentation or check the respective markdown files for detailed guidance.

---

Built with care for CodeRound AI  
_Fullstack AI Recruiter for Fast Growing Startups_

[Get Started →](QUICKSTART.md)

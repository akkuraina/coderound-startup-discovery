# Quick Start Guide - 5 Minutes to Running

## Prerequisites

Have these installed:

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Git

## Step 1: Clone & Setup (1 min)

```bash
cd d:\DJSCE\CODING\coderound-startup-discovery
```

## Step 2: Database (1 min)

### Option A: DBever (GUI)

1. Open DBever
2. Right-click MySQL connection → SQL Editor → New SQL
3. Copy-paste `database/schema.sql`
4. Execute

### Option B: MySQL CLI

```bash
mysql -u root -p < database/schema.sql
```

## Step 3: Backend Setup (2 mins)

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
# Add your API keys for Tavily, Anthropic, Resend

# Run backend
uvicorn main:app --reload

# Should see: "Uvicorn running on http://127.0.0.1:8000"
```

## Step 4: Frontend Setup (1 min)

In a NEW terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (copy from .env.example)

# Run frontend
npm run dev

# Should see: "Local: http://localhost:3000"
```

## Step 5: Test It! (✨)

1. Open http://localhost:3000
2. Click "Sign Up"
3. Create an account
4. You're in the dashboard!
5. Click "Discover Startups" button
6. Results will appear (powered by Tavily + Anthropic)
7. Click "Reach Out" on any company
8. Generate email with AI + send via Resend

## That's It! 🎉

You now have a fully functional startup discovery system running locally.

---

## Common Issues

**"Can't connect to database"**

- Check MySQL is running
- Verify credentials in backend/.env
- Run: `mysql -u root -p -e "USE coderound_db; SHOW TABLES;"`

**"ModuleNotFoundError"**

- Make sure venv is activated: `venv\Scripts\activate`

**"CORS error"**

- Restart backend server
- Check `CORS_ORIGINS` in backend/.env includes `http://localhost:3000`

**"API key error"**

- Add your Tavily, Anthropic, Resend keys to backend/.env
- Get them from: tavily.com, anthropic.com, resend.com

---

See `docs/SETUP.md` for detailed instructions.

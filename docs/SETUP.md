# Setup Guide - CodeRound Startup Discovery Radar

## Prerequisites

Before you begin, ensure you have:

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **MySQL** 8.0+ (database)
- **Git** (version control)
- API Keys:
  - Tavily API key ([sign up](https://tavily.com))
  - Groq API key 
  - Resend API key ([sign up](https://resend.com))

---

## Step 1: Clone & Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd coderound-startup-discovery

# Create .env files from examples
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

---

## Step 2: Database Setup

### Option A: Using DBever (GUI)

1. Open DBever
2. Create a new MySQL connection (if not already configured)
3. Right-click on your MySQL connection → SQL Editor → New SQL Script
4. Copy contents of `database/schema.sql`
5. Execute the script

### Option B: Using MySQL CLI

```bash
# Login to MySQL
mysql -u root -p

# Run the schema file
SOURCE database/schema.sql;

# Verify database creation
SHOW DATABASES;
USE coderound_db;
SHOW TABLES;
```

---

## Step 3: Backend Setup

### 3.1 Create Virtual Environment

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.3 Configure Environment Variables

Edit `backend/.env` with your credentials:

```env
# Database
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/coderound_db

# JWT
JWT_SECRET_KEY=your-very-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# APIs
TAVILY_API_KEY=your_tavily_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
RESEND_API_KEY=your_resend_api_key

# Application
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development

# Email
FROM_EMAIL=noreply@coderound.ai
ADMIN_EMAIL=admin@coderound.ai
```

### 3.4 Verify Database Connection

```bash
# Test the connection
python -c "from database import engine; engine.connect(); print('Connected!')"
```

### 3.5 Run Backend Server

```bash
# From backend directory
uvicorn main:app --reload

# Server will start at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

---

## Step 4: Frontend Setup

### 4.1 Install Dependencies

```bash
cd frontend
npm install

# Or with yarn
yarn install
```

### 4.2 Configure Environment Variables

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=CodeRound Startup Discovery
```

### 4.3 Run Development Server

```bash
npm run dev

# Application available at http://localhost:3000
```

---

## Step 5: Verify Everything Works

### Backend Health Check

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", "service": "CodeRound Startup API", "version": "1.0.0"}
```

### Frontend Access

1. Open browser: http://localhost:3000
2. You should see the landing page with:
   - Navigation bar
   - Hero section
   - Features section
   - Sign up / Login buttons

### Test Authentication

1. Click "Sign Up"
2. Create an account:
   - Email: `test@coderound.ai`
   - Password: `testPassword123`
   - Name: `Test User`
3. You should be redirected to the dashboard
4. Click "Discover Startups" (will test API integration)

---

## Step 6: Configure API Keys

### Getting Tavily API Key

1. Go to [tavily.com](https://tavily.com)
2. Sign up for a free account
3. Navigate to API settings
4. Copy your API key
5. Paste into `backend/.env`: `TAVILY_API_KEY=...`

### Getting Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Create a new API key
4. Paste into `backend/.env`: `ANTHROPIC_API_KEY=...`

### Getting Resend API Key

1. Go to [resend.com](https://resend.com)
2. Sign up for a free account
3. Verify your domain (for production)
4. Get your API key from settings
5. Paste into `backend/.env`: `RESEND_API_KEY=...`

---

## Troubleshooting

### Issue: Database Connection Error

```
Error: Can't connect to MySQL server on 'localhost'
```

**Solution:**

- Ensure MySQL is running
- Check credentials in `DATABASE_URL`
- Verify database `coderound_db` exists
- Run: `mysql -u root -p -e "SHOW DATABASES;"`

### Issue: ModuleNotFoundError (Backend)

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**

- Activate virtual environment
- Run: `pip install -r requirements.txt`

### Issue: CORS Errors (Frontend-Backend)

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**

- Ensure `backend/.env` has correct `CORS_ORIGINS`
- Default: `CORS_ORIGINS=["http://localhost:3000"]`
- Restart backend server

### Issue: "Invalid token" Error

**Solution:**

- Clear browser localStorage: `localStorage.clear()`
- Sign out and log back in
- Check `JWT_SECRET_KEY` is set correctly

### Issue: Email Not Sending

```
Failed to send email: Unauthorized
```

**Solution:**

- Verify Resend API key is correct
- Check `FROM_EMAIL` is configured
- For development, emails might fail if domain not verified

---

## Database Schema Overview

### Users Table

Stores user account information:

```
- id (Primary Key)
- email (unique)
- password_hash
- name
- is_active
- created_at
- last_login
```

### Companies Table

Stores discovered startup information:

```
- id (Primary Key)
- name (unique, indexed)
- website, linkedin_url
- funding_amount, funding_date, funding_round
- investors (JSON array)
- country, description
- hiring_status (0=not hiring, 1=potentially, 2=actively)
- enriched_data (JSON)
- created_at, updated_at
```

### Outreach Table

Tracks email campaigns:

```
- id (Primary Key)
- user_id (Foreign Key)
- company_id (Foreign Key)
- email_sent_to, email_subject, email_content
- response_status (0=pending, 1=positive, 2=negative, 3=no response)
- sent_at, response_received_at
```

---

## API Endpoints Summary

### Authentication

- `POST /auth/signup` - Create new account
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Companies

- `POST /companies/discover` - Start discovery process
- `GET /companies` - Get all companies (with filters)
- `GET /companies/{id}` - Get single company

### Outreach

- `POST /outreach/generate-email` - Generate email
- `POST /outreach/send` - Send email
- `GET /outreach` - Get outreach history
- `PATCH /outreach/{id}` - Update response status

---

## Next Steps

1. ✅ Database setup
2. ✅ Backend running
3. ✅ Frontend running
4. 🔄 **Test full workflow:**
   - Sign up
   - Click "Discover Startups"
   - View results
   - Send outreach emails
   - Track responses

5. 📝 Customize email templates (backend/services/**init**.py)
6. 🎨 Customize UI/colors (frontend/tailwind.config.js)
7. 🚀 Deploy (Docker setup coming soon)

---

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review API documentation at http://localhost:8000/docs
3. Check backend logs in terminal
4. Check browser console (F12) for frontend errors

---

## Security Notes

⚠️ **Important for Production:**

1. Change `JWT_SECRET_KEY` to a long random string
2. Set `ENVIRONMENT=production`
3. Configure proper CORS origins (not localhost)
4. Use environment-specific `.env` files
5. Enable HTTPS
6. Set up rate limiting
7. Use password hashing (already configured with bcrypt)
8. Store API keys securely (use secrets manager)

---

Good luck! 🚀

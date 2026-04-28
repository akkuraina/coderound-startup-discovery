# Deployment Checklist - CodeRound Startup Discovery

## Pre-Launch Checklist

### ✅ Code Quality

- [ ] All files have proper comments
- [ ] No hardcoded secrets (use .env)
- [ ] All imports are correct
- [ ] No syntax errors
- [ ] Consistent naming conventions
- [ ] Type hints for functions
- [ ] Error handling in place

### ✅ Database

- [ ] Schema created (schema.sql executed)
- [ ] All tables created
- [ ] Indexes present
- [ ] Foreign keys configured
- [ ] Test data inserted (optional)
- [ ] Backup strategy planned

### ✅ Backend Configuration

- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] requirements.txt installed
- [ ] .env file created with all keys:
  - [ ] DATABASE_URL (MySQL connection)
  - [ ] JWT_SECRET_KEY (32+ chars)
  - [ ] TAVILY_API_KEY
  - [ ] ANTHROPIC_API_KEY
  - [ ] RESEND_API_KEY
  - [ ] CORS_ORIGINS (set correctly)
- [ ] Database migrations run
- [ ] Environment set to 'development' or 'production'
- [ ] Server starts without errors

### ✅ Frontend Configuration

- [ ] Node.js 18+ installed
- [ ] node_modules installed (npm install)
- [ ] .env.local file created:
  - [ ] NEXT_PUBLIC_API_URL (backend URL)
  - [ ] NEXT_PUBLIC_APP_NAME (app name)
- [ ] Development server runs (npm run dev)
- [ ] No console errors
- [ ] All pages load

### ✅ API Integration Testing

- [ ] Health check endpoint works
  ```bash
  curl http://localhost:8000/health
  ```
- [ ] Signup endpoint works
- [ ] Login endpoint works
- [ ] Discovery endpoint works
  - [ ] Tavily search succeeds
  - [ ] Anthropic extraction succeeds
  - [ ] Data stored in database
- [ ] Company listing works
- [ ] Email generation works
  - [ ] Anthropic generates good emails
- [ ] Email sending works
  - [ ] Resend API responds
- [ ] Outreach tracking works

### ✅ Frontend Functionality

- [ ] Landing page loads
- [ ] Signup page works
- [ ] Login page works
- [ ] Dashboard loads
- [ ] Discovery button works
- [ ] Results page shows companies
- [ ] Filters work (hiring status)
- [ ] Outreach modal opens
- [ ] Email generation works
- [ ] Email sending works
- [ ] Outreach history shows
- [ ] Response status updates

### ✅ Security

- [ ] Passwords are hashed (bcrypt)
- [ ] JWT secrets are strong
- [ ] CORS is restricted
- [ ] No credentials in code
- [ ] SQL injection prevention (SQLAlchemy)
- [ ] XSS prevention (React escaping)
- [ ] HTTPS enabled (production)
- [ ] Rate limiting implemented (if needed)

### ✅ Performance

- [ ] Database queries optimized
- [ ] Indexes created
- [ ] API response times < 3s
- [ ] Frontend loads in < 2s
- [ ] No N+1 queries
- [ ] Images optimized
- [ ] Minification enabled (production)

### ✅ Error Handling

- [ ] 404 errors handled
- [ ] 401/403 auth errors handled
- [ ] 500 server errors logged
- [ ] Network errors handled
- [ ] Validation errors shown to user
- [ ] User sees helpful error messages

### ✅ Documentation

- [ ] README.md complete
- [ ] QUICKSTART.md written
- [ ] SETUP.md detailed
- [ ] API.md documented
- [ ] DESIGN.md explains decisions
- [ ] RATE_LIMITS.md covers costs
- [ ] Code commented

### ✅ Testing

- [ ] Manual testing complete
- [ ] Happy path tested (signup → discovery → email)
- [ ] Error cases tested
- [ ] Edge cases handled
- [ ] All pages responsive
- [ ] Works on mobile
- [ ] Works on desktop

### ✅ Third-Party Services

- [ ] Tavily API key valid
- [ ] Anthropic API key valid
- [ ] Resend API key valid
- [ ] API quotas checked
- [ ] Cost estimates reviewed
- [ ] Rate limits understood

### ✅ Deployment Readiness

- [ ] Code committed to git
- [ ] .env files NOT in git
- [ ] .gitignore includes .env
- [ ] README explains setup
- [ ] No localhost URLs (production)
- [ ] Database backups configured
- [ ] Logging configured

---

## Launch Preparation

### Before Going Live

1. [ ] Set ENVIRONMENT=production in backend/.env
2. [ ] Update CORS_ORIGINS to production domain
3. [ ] Change JWT_SECRET_KEY to random 32+ char string
4. [ ] Update email FROM_EMAIL to verified domain
5. [ ] Set up monitoring/logging
6. [ ] Configure database backups
7. [ ] Set up error alerts
8. [ ] Create privacy policy
9. [ ] Create terms of service
10. [ ] Set up contact form/support

### Day-of-Launch

1. [ ] Final code review
2. [ ] Run full test suite
3. [ ] Verify all API keys are correct
4. [ ] Database is backed up
5. [ ] Server is running
6. [ ] Frontend loads
7. [ ] Test signup → discovery → email flow
8. [ ] Monitor logs for errors
9. [ ] Be ready to rollback if needed

### Post-Launch

1. [ ] Monitor error logs
2. [ ] Check API usage/costs
3. [ ] Gather user feedback
4. [ ] Plan improvements
5. [ ] Schedule maintenance window
6. [ ] Plan scaling strategy

---

## Common Issues & Solutions

### Database Connection Failed

```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1"

# Check DATABASE_URL in .env
# Format: mysql+pymysql://user:password@host:port/dbname
```

### Port Already in Use

```bash
# Backend (change port)
uvicorn main:app --reload --port 8001

# Frontend (automatic)
npm run dev -- -p 3001
```

### API Keys Not Working

- Verify key format (no extra spaces)
- Check API quota/plan
- Try creating new key
- Test with curl:

```bash
curl -X POST https://api.tavily.com/search \
  -H "Authorization: Bearer YOUR_KEY"
```

### Email Not Sending

- Verify Resend API key
- Check FROM_EMAIL is correct
- For production: verify domain
- Check spam folder
- Review Resend logs

---

## Success Metrics

Track these after launch:

1. **User Engagement**
   - Signups per day
   - Active users per day
   - Discovery runs per user
   - Emails sent per user

2. **System Performance**
   - API response times
   - Database query times
   - Email delivery time
   - Error rate

3. **Business Metrics**
   - Cost per discovery
   - Cost per email sent
   - Conversion rate (email → response)
   - User retention

---

## Maintenance Tasks

### Weekly

- [ ] Check error logs
- [ ] Monitor API usage
- [ ] Review user feedback

### Monthly

- [ ] Database backup verification
- [ ] Security audit
- [ ] Performance review
- [ ] Cost analysis

### Quarterly

- [ ] Plan new features
- [ ] Update dependencies
- [ ] Review design
- [ ] Scalability assessment

---

## Useful Commands

```bash
# Backend
python -m pip list  # Check installed packages
python -m uvicorn main:app --reload  # Run server
python -c "from database import engine; engine.connect()"  # Test DB

# Frontend
npm ls  # Check installed packages
npm run build  # Production build
npm run lint  # Lint code

# Database
mysql -u root -p -e "USE coderound_db; SHOW TABLES;"  # List tables
mysql -u root -p < database/schema.sql  # Initialize DB

# Git
git log --oneline  # See commits
git status  # See changes
git diff  # See detailed changes
```

---

## Emergency Procedures

### If Service is Down

1. [ ] Check if server is running
2. [ ] Check if database is accessible
3. [ ] Check if API keys are valid
4. [ ] Review error logs
5. [ ] Restart services if needed
6. [ ] Notify users if necessary

### If Database is Corrupted

1. [ ] Stop backend server
2. [ ] Restore from latest backup
3. [ ] Run schema.sql to ensure tables exist
4. [ ] Restart backend server
5. [ ] Test critical flows

### If API Key is Leaked

1. [ ] Rotate immediately
2. [ ] Check usage for suspicious activity
3. [ ] Update .env
4. [ ] Restart backend
5. [ ] Monitor for abuse

---

## Going Production - Final Checklist

- [ ] All credentials rotated
- [ ] All IPs whitelisted/firewalled
- [ ] SSL certificate configured
- [ ] Monitoring set up
- [ ] Backups automated
- [ ] Alert system ready
- [ ] Logging to file
- [ ] Rate limiting active
- [ ] HTTPS enforced
- [ ] Admin notified

---

Ready to launch! 🚀

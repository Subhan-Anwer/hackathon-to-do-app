# Quickstart: Production Authentication Setup

**Feature**: 003-production-auth-migration
**Last Updated**: 2026-02-06

## Overview

This guide walks you through setting up production-ready authentication with Better Auth and PostgreSQL database storage. After following these steps, user accounts will persist across server restarts and passwords will be securely hashed with bcrypt.

---

## Prerequisites

- Node.js 18+ installed
- PostgreSQL database (local or Neon cloud)
- Git configured
- Basic command line familiarity

---

## Quick Setup (5 Minutes)

###  1️⃣ Generate Authentication Secret

```bash
# Generate a secure 32-character secret
openssl rand -base64 32
```

**Example output**: `vv8JDixBRkIhCRhIBBjgqxoZmsXj5kvz`

💾 **Save this value** - you'll use it in both frontend and backend configurations.

---

### 2️⃣ Configure Frontend Environment

```bash
cd frontend

# Create .env.local file
cat > .env.local <<'EOF'
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
# CRITICAL: Must match backend's BETTER_AUTH_SECRET
BETTER_AUTH_SECRET=vv8JDixBRkIhCRhIBBjgqxoZmsXj5kvz

# Better Auth Base URL
BETTER_AUTH_URL=http://localhost:3000

# Database URL (PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_app
EOF

# Update with your actual values
nano .env.local
```

**Required Values**:
- `BETTER_AUTH_SECRET`: Paste the secret you generated in step 1
- `DATABASE_URL`: Your PostgreSQL connection string

---

### 3️⃣ Configure Backend Environment

```bash
cd ../backend

# Create .env file
cat > .env <<'EOF'
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todo_app

# JWT Secret (MUST MATCH FRONTEND)
BETTER_AUTH_SECRET=vv8JDixBRkIhCRhIBBjgqxoZmsXj5kvz

# Frontend CORS Origin
FRONTEND_ORIGIN=http://localhost:3000
EOF

# Update with your actual values
nano .env
```

**Critical**: `BETTER_AUTH_SECRET` must be identical in both frontend and backend.

---

### 4️⃣ Start Services

```bash
# Terminal 1: Start backend
cd backend
uv run uvicorn main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

**Expected Output**:
- Backend: `Uvicorn running on http://localhost:8000`
- Frontend: `✓ Ready in X ms`

---

### 5️⃣ Verify Setup

1. **Open browser**: http://localhost:3000
2. **Navigate to signup**: http://localhost:3000/signup
3. **Create test account**:
   - Email: `test@example.com`
   - Password: `password123`
4. **Check redirect**: Should redirect to `/tasks` after signup
5. **Verify database**: User should be in PostgreSQL `user` table

```sql
-- Connect to PostgreSQL
psql $DATABASE_URL

-- Check if user table exists
\dt

-- Verify user was created
SELECT id, email, "createdAt" FROM "user";
```

**Expected**:
- Table `user` exists
- Row for `test@example.com` exists
- Password field contains bcrypt hash (starts with `$2b$`)

---

## Database Setup Options

### Option A: Local PostgreSQL (Development)

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb todo_app

# Connection string
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_app
```

### Option B: Neon Serverless PostgreSQL (Recommended)

1. **Sign up**: https://neon.tech
2. **Create project**: "Todo App Production"
3. **Copy connection string**: Dashboard → Connection Details
4. **Example**:
   ```
   postgresql://user:pass@ep-cool-wave-12345.us-east-2.aws.neon.tech/todo_app?sslmode=require
   ```
5. **Update both `.env` and `.env.local`** with this URL

---

## Verification Tests

### Test 1: User Persistence

```bash
# 1. Create account via UI (http://localhost:3000/signup)
# 2. Stop Next.js server (Ctrl+C in Terminal 2)
# 3. Restart Next.js server
cd frontend && npm run dev

# 4. Login with same credentials
# ✅ PASS: Login succeeds (user persisted in database)
```

### Test 2: Password Hashing

```sql
-- Connect to database
psql $DATABASE_URL

-- Check password hash
SELECT
  email,
  LEFT(password, 10) AS password_prefix
FROM "user"
WHERE email = 'test@example.com';

-- ✅ PASS: password_prefix starts with '$2b$10$' (bcrypt)
```

### Test 3: JWT Token Format

```javascript
// 1. Login via UI
// 2. Open DevTools → Application → Cookies
// 3. Find 'session' cookie
// 4. Copy value (JWT token)
// 5. Decode at https://jwt.io

// ✅ PASS: Claims include:
// - "sub": "user-uuid"
// - "exp": timestamp (7 days later)
// - "iat": timestamp
```

### Test 4: Backend Compatibility

```bash
# 1. Login via frontend
# 2. Make API request (browser automatically includes cookie)
curl http://localhost:3000/tasks

# 3. Check backend logs
# ✅ PASS: No 401 errors
# ✅ PASS: Tasks filtered by user_id
```

---

## Troubleshooting

### Error: "BETTER_AUTH_SECRET is required"

**Cause**: Environment variable not set

**Solution**:
```bash
# Check if variable is set
echo $BETTER_AUTH_SECRET

# If empty, add to .env.local (frontend) and .env (backend)
nano frontend/.env.local
nano backend/.env
```

---

### Error: "DATABASE_URL is required"

**Cause**: Database connection string not configured

**Solution**:
1. Verify PostgreSQL is running: `psql -l`
2. Update DATABASE_URL in both `.env` files
3. Test connection: `psql $DATABASE_URL`

---

### Error: "Invalid token" from backend

**Cause**: Secret mismatch between frontend and backend

**Solution**:
```bash
# Compare secrets
grep BETTER_AUTH_SECRET frontend/.env.local
grep BETTER_AUTH_SECRET backend/.env

# Ensure both show identical values
# If different, update backend to match frontend
```

---

### Error: "Failed to connect to database"

**Cause**: Incorrect DATABASE_URL or PostgreSQL not running

**Solution**:
```bash
# Test connection
psql $DATABASE_URL

# If fails, check:
# 1. PostgreSQL service is running
# 2. Database exists (createdb todo_app)
# 3. URL format is correct (no typos)
```

---

### Session cookie not sent to backend

**Cause**: CORS misconfiguration or `credentials: "include"` missing

**Solution**:
1. **Check backend CORS** (`backend/main.py`):
   ```python
   allow_origins=[FRONTEND_ORIGIN],  # http://localhost:3000
   allow_credentials=True,  # CRITICAL
   ```

2. **Check frontend API client** (`frontend/lib/api.ts`):
   ```typescript
   credentials: "include",  // CRITICAL
   ```

3. **Restart both servers** after changes

---

## Production Deployment

### Environment Variables (Vercel/Production)

**Frontend (.env.production)**:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
BETTER_AUTH_SECRET=<generate-new-secret-for-production>
BETTER_AUTH_URL=https://yourdomain.com
DATABASE_URL=<neon-postgresql-production-url>
```

**Backend (Railway/Fly.io)**:
```bash
DATABASE_URL=<neon-postgresql-production-url>
BETTER_AUTH_SECRET=<same-as-frontend>
FRONTEND_ORIGIN=https://yourdomain.com
```

**Security Checklist**:
- [ ] Use HTTPS in production (secure cookies)
- [ ] Rotate DATABASE_URL credentials if previously committed to git
- [ ] Generate new BETTER_AUTH_SECRET for production (don't reuse dev secret)
- [ ] Enable SSL for database connection (`?sslmode=require`)
- [ ] Verify `.env.local` is in `.gitignore`

---

## Next Steps

After setup is complete:

1. **Create tasks**: Test the "Add Task" button
2. **Multi-user testing**: Create 2+ accounts, verify isolation
3. **Session expiry**: Wait 7 days or manually delete cookie to test re-login
4. **Integration tests**: Run `npm test` (frontend) and `pytest` (backend)

---

## Useful Commands

```bash
# Check environment variables
env | grep BETTER_AUTH
env | grep DATABASE_URL

# Reset database (CAUTION: Deletes all data)
psql $DATABASE_URL -c "DROP TABLE IF EXISTS user, session, account, verification CASCADE;"

# View Better Auth tables
psql $DATABASE_URL -c "\dt"

# Count users
psql $DATABASE_URL -c "SELECT COUNT(*) FROM user;"

# View recent sessions
psql $DATABASE_URL -c "SELECT \"userId\", \"expiresAt\", \"createdAt\" FROM session ORDER BY \"createdAt\" DESC LIMIT 5;"

# Check logs
# Backend: Terminal 1 output
# Frontend: Terminal 2 output + Browser DevTools console
```

---

## Support

**Documentation**:
- Better Auth: https://www.better-auth.com/docs
- Next.js App Router: https://nextjs.org/docs/app
- Neon PostgreSQL: https://neon.tech/docs

**Common Issues**:
- See `research.md` section 11 for detailed troubleshooting
- Check `plan.md` for implementation details
- Review `data-model.md` for database schema

---

## Summary

You now have production-ready authentication with:
- ✅ User accounts stored in PostgreSQL database
- ✅ Passwords hashed with bcrypt (10 rounds)
- ✅ JWT tokens in httpOnly cookies (XSS protection)
- ✅ 7-day session expiry
- ✅ Backend user isolation (users only see their own tasks)

**Time to complete**: 5-10 minutes for initial setup + testing

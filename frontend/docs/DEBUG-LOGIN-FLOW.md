# Debug Login Flow - Step by Step

## 🔍 What to Check Right Now

### 1. Is Frontend Server Running with NEW Changes?

**ACTION**: Restart frontend server
```bash
cd frontend
npm run dev
```

Wait for it to say: `✓ Ready in Xms`

---

### 2. Open Browser DevTools BEFORE Logging In

**ACTION**:
1. Open Chrome/Edge
2. Press F12 (DevTools)
3. Go to **Console** tab
4. Clear any old messages
5. Navigate to: http://localhost:3000/login

**CHECK FOR ERRORS** in Console:
- ❌ If you see `ETIMEDOUT` → Database connection still failing
- ❌ If you see `Cannot find module 'pg'` → Server not restarted
- ✅ No errors → Good to proceed

---

### 3. Try to Login

**ACTION**:
1. Enter credentials: `test@example.com` / `password123`
2. Click "Sign In"
3. Watch the Console tab for errors
4. Watch the Network tab for requests

**WHAT SHOULD HAPPEN**:
```
1. POST request to /api/auth/sign-in
2. Response with Set-Cookie header
3. Toast: "Login successful!"
4. Wait 500ms
5. Redirect to /tasks
```

**WHAT MIGHT GO WRONG**:

#### Error A: Database Timeout During Login
```
Console: "ETIMEDOUT" or "AggregateError"
```
**Cause**: Better Auth can't connect to Neon database
**Fix**: See "Database Connection Fix" below

#### Error B: Session Cookie Not Set
```
Network tab → /sign-in response → No Set-Cookie header
```
**Cause**: Login succeeded but cookie wasn't set
**Fix**: Check Better Auth configuration

#### Error C: 307 Redirect Loop
```
Navigate to /tasks → Immediately redirect to /login
```
**Cause**: getSession() returns null (can't read session)
**Fix**: Database connection issue

---

### 4. Check Network Tab After Login

**ACTION**:
1. After clicking "Sign In"
2. Go to DevTools → **Network** tab
3. Find the request to `/api/auth/sign-in` or similar

**CHECK RESPONSE HEADERS**:
```
✅ Should see:
Set-Cookie: session=eyJhbGci...; Path=/; HttpOnly; SameSite=Lax
```

**CHECK REQUEST TO /tasks** (after redirect):
```
✅ Should see in Request Headers:
Cookie: session=eyJhbGci...
```

---

### 5. Check Application Storage

**ACTION**:
1. DevTools → **Application** tab (Chrome) or **Storage** tab (Firefox)
2. Click **Cookies** → http://localhost:3000

**CHECK FOR**:
```
Name: session
Value: eyJhbGci... (long JWT token)
HttpOnly: ✓
Secure: (empty for localhost HTTP)
SameSite: Lax
```

**If NO session cookie**:
- Login didn't work
- Database connection failed
- Better Auth couldn't create session

---

## 🔧 Common Issues & Fixes

### Issue 1: "ETIMEDOUT" Error Still Appearing

**Symptoms**:
- Console shows: `ETIMEDOUT` or `AggregateError`
- Login takes 20+ seconds then fails
- Can't access /tasks page

**Root Cause**: Neon database is sleeping or unreachable

**Fix Options**:

#### Option A: Wait for Neon to Wake Up (First Login Only)
1. Try logging in
2. Wait patiently for 20-30 seconds
3. Database should wake up
4. Subsequent logins will be fast

#### Option B: Use Local PostgreSQL (Recommended for Dev)

```bash
# Install and start PostgreSQL with Docker
docker run --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres

# Create database
docker exec -it postgres createdb -U postgres todo_app

# Update frontend/.env.local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_app

# Update backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todo_app

# Restart both servers
```

---

### Issue 2: "Cannot find module 'pg'" Error

**Symptoms**:
- Console error: `Cannot find module 'pg'`
- Server won't start

**Fix**:
```bash
cd frontend
npm install pg
npm run dev
```

---

### Issue 3: Session Cookie Exists But Still Redirects

**Symptoms**:
- Cookie is set (visible in DevTools → Application → Cookies)
- Still redirects from /tasks to /login

**Root Cause**: `getSession()` failing to read the session

**Debug**:
1. Check if cookie value is a valid JWT
   - Copy cookie value
   - Go to https://jwt.io
   - Paste and verify it has `sub`, `exp`, `iat` claims

2. Check backend logs when accessing /tasks:
   ```bash
   # In backend terminal, you should see:
   INFO: User authenticated: <user_id>
   ```

3. If you see "Authentication failed: No token provided":
   - Frontend isn't sending the cookie
   - Check Network tab → /tasks request → Cookie header

---

### Issue 4: Better Auth Tables Don't Exist

**Symptoms**:
- Login fails with "relation does not exist"
- Database errors in console

**Check**:
```bash
cd frontend
node test-db-connection.js
```

Should show:
```
✅ Better Auth tables found:
   - user
   - session
   - account
   - verification
```

**If tables missing**:
- Better Auth will create them on first signup
- Try signing up a new user instead of logging in

---

## 🧪 Test Checklist

Run through this checklist:

1. **Backend Running**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","service":"task-api"}
   ```
   - [ ] Backend is running
   - [ ] Health check passes

2. **Frontend Running**
   ```bash
   # Check terminal for:
   # ✓ Ready in Xms
   # ○ Local: http://localhost:3000
   ```
   - [ ] Frontend is running
   - [ ] Server restarted after installing `pg`

3. **Database Connection**
   ```bash
   cd frontend
   node test-db-connection.js
   ```
   - [ ] Connection successful
   - [ ] Better Auth tables exist

4. **Environment Variables**
   ```bash
   # Check frontend/.env.local has:
   # - DATABASE_URL
   # - BETTER_AUTH_SECRET
   # - BETTER_AUTH_URL
   # - NEXT_PUBLIC_API_URL
   ```
   - [ ] All variables present
   - [ ] Secrets match backend

5. **Login Flow**
   - [ ] Can access /login page
   - [ ] No console errors
   - [ ] Can submit login form
   - [ ] Toast appears: "Login successful!"
   - [ ] Cookie is set (DevTools → Application → Cookies)
   - [ ] Redirects to /tasks
   - [ ] Stays on /tasks (no redirect loop)

---

## 📋 What to Report

If still not working, provide:

1. **Console Errors**:
   - Screenshot or copy/paste from Console tab

2. **Network Tab**:
   - Screenshot of the /sign-in request/response
   - Screenshot of the /tasks request (if it happens)

3. **Cookie Status**:
   - Screenshot of DevTools → Application → Cookies
   - Is `session` cookie present? What's its value (first 20 chars)?

4. **Backend Logs**:
   - Copy the last 20 lines from backend terminal

5. **Frontend Logs**:
   - Copy any errors from frontend terminal

---

## 🎯 Most Likely Issues

Based on symptoms, the issue is probably one of these:

### 1. Frontend Server Not Restarted (90% likelihood)
**Symptom**: Database timeout errors
**Fix**: Restart frontend: `npm run dev`

### 2. Neon Database Sleeping (5% likelihood)
**Symptom**: First login takes 20-30 seconds
**Fix**: Wait or use local PostgreSQL

### 3. Better Auth Tables Don't Exist (3% likelihood)
**Symptom**: Database errors during login
**Fix**: Try signup instead of login (creates tables)

### 4. Something Else (2% likelihood)
**Fix**: Share the console errors and we'll debug

---

## 🚀 Quick Recovery Steps

**If completely stuck, do this**:

```bash
# 1. Stop everything (Ctrl+C on both terminals)

# 2. Restart backend
cd backend
uv run uvicorn main:app --reload

# 3. Restart frontend (in new terminal)
cd frontend
npm run dev

# 4. Clear browser data
# Chrome: DevTools → Application → Clear site data

# 5. Try fresh signup
# Go to: http://localhost:3000/signup
# Create: newuser@example.com / password123

# 6. Check if signup works and redirects to /tasks
```

---

**Start here**: Restart the frontend server, then try logging in with DevTools open and report what you see!

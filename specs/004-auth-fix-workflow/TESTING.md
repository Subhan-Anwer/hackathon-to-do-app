# Testing Guide: Authentication Fix & Workflow Improvements

**Feature**: `004-auth-fix-workflow`
**Purpose**: Comprehensive manual testing checklist for authentication fixes and UX improvements

## Prerequisites

- [ ] Backend running: `cd backend && uv run uvicorn main:app --reload` (port 8000)
- [ ] Frontend running: `cd frontend && npm run dev` (port 3000)
- [ ] Browser DevTools open (Network + Application/Storage tabs)
- [ ] Two test user accounts created (for multi-user isolation testing)

## Phase 1: JWT Plugin Verification

**Goal**: Verify Better Auth generates JWT tokens with `sub` claim

### Test Steps

1. **Create new user account**
   - Navigate to http://localhost:3000/signup
   - Sign up with: `test1@example.com` / `password123`
   - Should auto-redirect to /tasks after signup

2. **Inspect JWT token structure**
   - Open DevTools → Application/Storage → Cookies → http://localhost:3000
   - Find cookie named `session`
   - Copy cookie value (the JWT token)
   - Decode at https://jwt.io
   - **Verify payload contains**:
     - `sub`: user_id (UUID format)
     - `exp`: expiration timestamp (7 days from now)
     - `iat`: issued at timestamp

### Expected Results

- ✅ Cookie named `session` exists
- ✅ JWT payload has `sub` claim with user_id
- ✅ JWT payload has `exp` and `iat` claims
- ✅ Token is signed with HS256 algorithm

### Troubleshooting

- ❌ No `sub` claim → JWT plugin not enabled in `frontend/lib/auth.ts`
- ❌ Cookie not found → Check Better Auth configuration

---

## Phase 2: Cookie Attributes Verification (Development)

**Goal**: Verify environment-aware cookie attributes work on localhost HTTP

### Test Steps

1. **Sign in as test user**
   - Navigate to http://localhost:3000/login
   - Sign in with: `test1@example.com` / `password123`

2. **Inspect cookie attributes**
   - Open DevTools → Application/Storage → Cookies → http://localhost:3000
   - Find `session` cookie
   - **Verify attributes**:
     - `SameSite`: `Lax` (NOT `None`)
     - `Secure`: `false` (unchecked)
     - `HttpOnly`: `true` (checked)
     - `Path`: `/`

3. **Test cookie transmission**
   - Navigate to http://localhost:3000/tasks
   - Open DevTools → Network tab
   - Create a new task
   - Inspect the POST request to `http://localhost:8000/api/{user_id}/tasks`
   - **Verify headers include**:
     - `Cookie: session=<jwt_token>`

### Expected Results

- ✅ Cookie has `SameSite=Lax` (allows localhost cross-origin)
- ✅ Cookie has `Secure=false` (allows HTTP)
- ✅ Cookie is sent in API requests to backend

### Troubleshooting

- ❌ Cookie blocked → Check if `secure: true` is hardcoded (should be conditional on `NODE_ENV`)
- ❌ `SameSite=None` → Check environment-aware logic in `frontend/lib/auth.ts`

---

## Phase 3: Authorization Bearer Header Verification

**Goal**: Verify dual authentication (both Authorization header + cookie sent)

### Test Steps

1. **Create a task while monitoring network traffic**
   - Navigate to http://localhost:3000/tasks
   - Open DevTools → Network tab
   - Click "Add Task" button
   - Fill title: "Test task for Bearer header"
   - Click "Create Task"

2. **Inspect request headers**
   - Find POST request to `http://localhost:8000/api/{user_id}/tasks`
   - Click request → Headers tab
   - **Verify Request Headers section shows**:
     - `Authorization: Bearer <jwt_token>`
     - `Cookie: session=<jwt_token>`
     - `Content-Type: application/json`

3. **Verify backend accepts both authentication methods**
   - Check backend logs (terminal running uvicorn)
   - Should see: `INFO: User authenticated: <user_id>`
   - No errors or 401 responses

### Expected Results

- ✅ Request includes `Authorization: Bearer <token>` header
- ✅ Request includes `Cookie: session=<token>` header
- ✅ Backend logs show successful authentication
- ✅ Task created successfully (no 401 error)

### Troubleshooting

- ❌ No Authorization header → Check `authClient.getSession()` in `frontend/lib/api.ts`
- ❌ 401 error → Check `BETTER_AUTH_SECRET` matches in frontend and backend .env files

---

## Phase 4: 401 Error Handling & User Feedback

**Goal**: Verify toast notification appears before redirect on session expiry

### Test Steps

1. **Simulate expired session**
   - Sign in as `test1@example.com`
   - Open DevTools → Application/Storage → Cookies
   - Delete the `session` cookie manually
   - Stay on the page (do NOT refresh)

2. **Trigger API call to force 401**
   - Click "Add Task" button
   - Fill title: "This should trigger 401"
   - Click "Create Task"

3. **Observe user feedback**
   - **Verify toast notification appears**:
     - Message: "Your session has expired. Please log in again."
     - Type: Error (red/orange toast)
     - Duration: 1.5 seconds visible
   - **Verify redirect happens after toast**:
     - After ~1.5 seconds, browser redirects to `/login`

### Expected Results

- ✅ Toast error message appears immediately
- ✅ Toast stays visible for 1.5 seconds
- ✅ Redirect to `/login` happens after toast disappears
- ✅ User has time to read the error message

### Troubleshooting

- ❌ Instant redirect, no toast → Check `setTimeout` delay in `frontend/lib/api.ts`
- ❌ No toast → Check `toast.error()` import and call in `fetchWithAuth`

---

## Phase 5: Loading States Verification

**Goal**: Verify all task operations show loading states with disabled buttons

### Test 5.1: Create Task Loading State

1. **Open create task dialog**
   - Navigate to http://localhost:3000/tasks
   - Click "Add Task" button

2. **Submit and observe loading state**
   - Fill title: "Loading state test"
   - Click "Create Task" button
   - **Observe during API call**:
     - Button text changes to "Creating..."
     - Button is disabled (grayed out)
     - Spinner icon appears
     - Cannot click button again

### Test 5.2: Edit Task Loading State

1. **Open edit dialog for existing task**
   - Click "Edit" button on any task
   - Change title to "Updated with loading"
   - Click "Update Task" button
   - **Observe**:
     - Button text: "Updating..."
     - Button disabled
     - Spinner icon visible

### Test 5.3: Delete Task Loading State

1. **Open delete confirmation**
   - Click "Delete" button on any task
   - Confirm deletion in dialog
   - **Observe**:
     - Button text: "Deleting..."
     - Button disabled
     - Cannot cancel during deletion

### Test 5.4: Toggle Complete Loading State

1. **Toggle task completion**
   - Click checkbox on any task
   - **Observe**:
     - Checkbox disabled during toggle
     - Cannot click checkbox again until operation completes

### Expected Results

- ✅ All buttons show loading text ("Creating...", "Updating...", "Deleting...")
- ✅ All buttons disabled during operations
- ✅ Spinner icons visible (where applicable)
- ✅ Operations cannot be double-clicked

### Troubleshooting

- ❌ No loading state → Check `useState(false)` for loading/isDeleting/isToggling
- ❌ Button still clickable → Check `disabled={loading}` prop

---

## Phase 6: Toast Notifications Verification

**Goal**: Verify success/error toasts for all CRUD operations with auto-refresh

### Test 6.1: Create Task Success Toast

1. **Create a new task**
   - Click "Add Task"
   - Title: "Toast notification test"
   - Click "Create Task"
   - **Verify**:
     - Green success toast appears: "Task created successfully!"
     - Toast auto-dismisses after ~3 seconds
     - New task appears in list immediately (no page refresh needed)

### Test 6.2: Update Task Success Toast

1. **Edit an existing task**
   - Click "Edit" on any task
   - Change title to "Updated title"
   - Click "Update Task"
   - **Verify**:
     - Success toast: "Task updated successfully!"
     - Task title updates in list immediately

### Test 6.3: Delete Task Success Toast

1. **Delete a task**
   - Click "Delete" on any task
   - Confirm deletion
   - **Verify**:
     - Success toast: "Task deleted successfully"
     - Task removed from list immediately

### Test 6.4: Toggle Complete Success Toast

1. **Mark task as complete**
   - Click checkbox on incomplete task
   - **Verify**:
     - Success toast: "Task marked as complete"
     - Task shows strikethrough immediately

2. **Mark task as incomplete**
   - Click checkbox on completed task
   - **Verify**:
     - Success toast: "Task marked as incomplete"
     - Strikethrough removed immediately

### Test 6.5: Error Toast (Simulated)

1. **Trigger network error** (optional)
   - Stop backend server
   - Try creating a task
   - **Verify**:
     - Red error toast appears
     - Descriptive error message shown

### Expected Results

- ✅ Success toasts appear for all CRUD operations
- ✅ Toasts auto-dismiss after 3-5 seconds
- ✅ Task list refreshes immediately after operations (no manual refresh needed)
- ✅ Error toasts show descriptive messages

### Troubleshooting

- ❌ No toasts → Check `import { toast } from "sonner"` in components
- ❌ List doesn't refresh → Check `onTaskCreated`, `onUpdate`, `onDelete` callbacks

---

## Phase 7: Multi-User Isolation Testing

**Goal**: Verify users can ONLY see their own tasks (Constitution Principle II)

### Test Steps

1. **Create two user accounts**
   - User 1: `user1@example.com` / `password123`
   - User 2: `user2@example.com` / `password123`

2. **Create tasks as User 1**
   - Sign in as `user1@example.com`
   - Create 3 tasks:
     - "User 1 - Task A"
     - "User 1 - Task B"
     - "User 1 - Task C"
   - **Note user_id** from URL: `/tasks` page, check DevTools → Network → user_id in API calls

3. **Sign out and sign in as User 2**
   - Click "Logout" button
   - Sign in as `user2@example.com`
   - Create 2 tasks:
     - "User 2 - Task X"
     - "User 2 - Task Y"

4. **Verify User 2 sees ONLY their tasks**
   - **Count tasks visible**: Should be exactly 2 tasks
   - **Verify task titles**: Only "User 2 - Task X" and "User 2 - Task Y"
   - **No User 1 tasks visible**: "User 1 - Task A/B/C" should NOT appear

5. **Sign out and sign back in as User 1**
   - Sign out
   - Sign in as `user1@example.com`
   - **Verify User 1 sees ONLY their 3 tasks**
   - **No User 2 tasks visible**

6. **Check backend logs for user_id filtering**
   - Backend logs should show:
     - `INFO: User authenticated: <user1_id>` when user1 is signed in
     - `INFO: User authenticated: <user2_id>` when user2 is signed in
   - API calls should filter by authenticated user_id

### Expected Results

- ✅ User 1 sees only their 3 tasks
- ✅ User 2 sees only their 2 tasks
- ✅ No cross-user data leakage
- ✅ Backend logs show different user_id values for each user
- ✅ API requests include correct user_id in path: `/api/{user_id}/tasks`

### Troubleshooting

- ❌ User 2 sees User 1's tasks → Backend query NOT filtering by user_id (critical security issue!)
- ❌ 404 errors → Check user_id extraction from JWT `sub` claim in backend

---

## Phase 8: Production Environment Verification

**Goal**: Verify cookie attributes work correctly in production HTTPS

### Prerequisites for Production Testing

- [ ] Deploy frontend to HTTPS domain (e.g., Vercel, Netlify)
- [ ] Deploy backend to HTTPS domain (e.g., Railway, Render)
- [ ] Set `NODE_ENV=production` in frontend environment variables
- [ ] Update `BETTER_AUTH_URL` to HTTPS frontend URL
- [ ] Update `NEXT_PUBLIC_API_URL` to HTTPS backend URL
- [ ] Ensure `BETTER_AUTH_SECRET` matches in both environments

### Test Steps (Production Only)

1. **Sign in on production HTTPS site**
   - Navigate to `https://your-app.com/login`
   - Sign in with test account

2. **Inspect cookie attributes in production**
   - Open DevTools → Application/Storage → Cookies → https://your-app.com
   - Find `session` cookie
   - **Verify production attributes**:
     - `SameSite`: `None` (NOT `Lax`)
     - `Secure`: `true` (checked)
     - `HttpOnly`: `true` (checked)

3. **Test cross-origin requests work**
   - Create a task on production
   - Verify API call succeeds (no cookie blocking)
   - Check Network tab shows cookie sent to backend

### Expected Results (Production)

- ✅ Cookie has `SameSite=None` (allows HTTPS cross-origin)
- ✅ Cookie has `Secure=true` (required for HTTPS)
- ✅ Cookie transmitted to backend successfully
- ✅ No CORS errors in console
- ✅ All functionality works same as development

### Troubleshooting

- ❌ Cookie not sent → Check `NODE_ENV=production` is set
- ❌ CORS errors → Check backend `FRONTEND_ORIGIN` matches frontend domain

---

## Test Results Summary

**Date**: _______________
**Tester**: _______________

| Phase | Test | Status | Notes |
|-------|------|--------|-------|
| 1 | JWT Plugin | ☐ Pass ☐ Fail | |
| 2 | Cookie Attributes (Dev) | ☐ Pass ☐ Fail | |
| 3 | Bearer Header | ☐ Pass ☐ Fail | |
| 4 | 401 Error Handling | ☐ Pass ☐ Fail | |
| 5 | Loading States | ☐ Pass ☐ Fail | |
| 6 | Toast Notifications | ☐ Pass ☐ Fail | |
| 7 | Multi-User Isolation | ☐ Pass ☐ Fail | |
| 8 | Production (if applicable) | ☐ Pass ☐ Fail ☐ N/A | |

**Overall Status**: ☐ All tests passed ☐ Issues found (see notes)

---

## Common Issues & Solutions

### Issue: 401 errors on all API calls

**Symptoms**: Every API call returns 401 Unauthorized

**Solutions**:
1. Check `BETTER_AUTH_SECRET` matches in frontend/.env.local and backend/.env
2. Verify JWT token is being sent (check Network tab for Authorization header + Cookie)
3. Check backend logs for JWT verification errors

### Issue: Cookie not sent to backend

**Symptoms**: Network tab shows no Cookie header in requests

**Solutions**:
1. Verify `credentials: "include"` in `frontend/lib/api.ts`
2. Check cookie attributes match environment (dev vs prod)
3. Clear browser cookies and sign in again

### Issue: Cross-user data visible

**Symptoms**: User sees tasks from other users

**Solutions**:
1. **CRITICAL SECURITY ISSUE** - Backend queries MUST filter by user_id
2. Check backend endpoint: `session.exec(select(Task).where(Task.user_id == user_id))`
3. Verify JWT `sub` claim is being extracted correctly

### Issue: Toast notifications not appearing

**Symptoms**: No feedback after operations

**Solutions**:
1. Check `<Toaster />` component in root layout (`app/layout.tsx`)
2. Verify `import { toast } from "sonner"` in all components
3. Check browser console for errors

### Issue: Loading states not showing

**Symptoms**: Buttons don't show "Creating..." text or disable

**Solutions**:
1. Verify `useState(false)` for loading state exists
2. Check `disabled={loading}` prop on buttons
3. Ensure `setLoading(false)` in finally blocks

---

## References

- **Spec**: `specs/004-auth-fix-workflow/spec.md`
- **Plan**: `specs/004-auth-fix-workflow/plan.md`
- **Tasks**: `specs/004-auth-fix-workflow/tasks.md`
- **Auth Flow Contract**: `specs/004-auth-fix-workflow/contracts/auth-flow.md`
- **Better Auth JWT Docs**: https://www.better-auth.com/docs/plugins/jwt
- **MDN Cookie Attributes**: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies

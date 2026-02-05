# Common Pitfalls and Solutions

## Critical Security Issues

### 1. Missing User Isolation

❌ **WRONG - No user verification:**
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    session: Session = Depends(get_session),
):
    return session.exec(select(Task).where(Task.user_id == user_id)).all()
```

✅ **CORRECT - Verify authenticated user:**
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return session.exec(select(Task).where(Task.user_id == user_id)).all()
```

### 2. Forgetting to Filter by User

❌ **WRONG - Returns ALL tasks:**
```python
@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(task_id: int, session: Session = Depends(get_session)):
    return session.get(Task, task_id)  # Returns ANY user's task!
```

✅ **CORRECT - Filter by both ID and user:**
```python
@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### 3. Incorrect CORS Configuration

❌ **WRONG - Missing credentials:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

✅ **CORRECT - Allow credentials for JWT cookies:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # CRITICAL for JWT cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Hardcoded Secrets

❌ **WRONG - Secret in code:**
```python
SECRET_KEY = "my-super-secret-key-12345"
```

✅ **CORRECT - Use environment variables:**
```python
import os
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")
```

## Database Issues

### 5. Not Using Dependency Injection

❌ **WRONG - Manual session management:**
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str):
    session = Session(engine)
    try:
        tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        return tasks
    finally:
        session.close()
```

✅ **CORRECT - Use FastAPI dependency:**
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return session.exec(select(Task).where(Task.user_id == user_id)).all()
```

### 6. Missing Index on user_id

❌ **WRONG - No index:**
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str  # Will be slow for queries!
```

✅ **CORRECT - Add index:**
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Fast lookups
```

### 7. Not Committing Changes

❌ **WRONG - Missing commit:**
```python
@router.post("/api/{user_id}/tasks")
async def create_task(task_data: TaskCreate, session: Session = Depends(get_session)):
    task = Task(**task_data.model_dump())
    session.add(task)
    # Missing session.commit()!
    return task
```

✅ **CORRECT - Commit and refresh:**
```python
@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = Task(**task_data.model_dump(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)  # Get generated ID
    return task
```

## JWT Authentication Issues

### 8. Incorrect Token Format

❌ **WRONG - Missing "Bearer" prefix:**
```python
async def verify_jwt(authorization: str = Header(None)):
    payload = jwt.decode(authorization, SECRET_KEY, algorithms=[ALGORITHM])
```

✅ **CORRECT - Parse "Bearer <token>":**
```python
async def verify_jwt(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

### 9. Not Handling JWT Errors

❌ **WRONG - No error handling:**
```python
async def verify_jwt(authorization: str = Header(None)):
    scheme, token = authorization.split()
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

✅ **CORRECT - Handle all error cases:**
```python
async def verify_jwt(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {"user_id": user_id}

    except (ValueError, JWTError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

## Request/Response Issues

### 10. Not Using Response Models

❌ **WRONG - Raw model returns internal fields:**
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()  # Returns raw SQLModel
```

✅ **CORRECT - Use Pydantic response model:**
```python
@router.get("/api/{user_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return session.exec(select(Task).where(Task.user_id == user_id)).all()
```

### 11. Missing HTTP Status Codes

❌ **WRONG - Wrong status code for creation:**
```python
@router.post("/api/{user_id}/tasks")
async def create_task(task_data: TaskCreate, session: Session = Depends(get_session)):
    # Returns 200 instead of 201
    return task
```

✅ **CORRECT - Use 201 for creation:**
```python
@router.post("/api/{user_id}/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = Task(**task_data.model_dump(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### 12. Not Validating Update Data

❌ **WRONG - Overwrites all fields with None:**
```python
@router.put("/api/{user_id}/tasks/{task_id}")
async def update_task(task_id: int, task_data: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    for key, value in task_data.model_dump().items():
        setattr(task, key, value)  # Sets unset fields to None!
```

✅ **CORRECT - Only update provided fields:**
```python
@router.put("/api/{user_id}/tasks/{task_id}")
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update fields that were explicitly set
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## Configuration Issues

### 13. SQLite Check Same Thread

❌ **WRONG - SQLite errors in FastAPI:**
```python
engine = create_engine("sqlite:///./database.db")
```

✅ **CORRECT - Disable check for SQLite:**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
```

### 14. Not Creating Tables

❌ **WRONG - Tables don't exist:**
```python
# app/main.py
app = FastAPI()
# Missing table creation!
```

✅ **CORRECT - Create tables on startup:**
```python
from app.db import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
```

## Error Handling Issues

### 15. Generic Error Messages

❌ **WRONG - Unhelpful error:**
```python
if not task:
    raise HTTPException(status_code=404)
```

✅ **CORRECT - Descriptive error:**
```python
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

### 16. Exposing Internal Errors

❌ **WRONG - Leaks implementation details:**
```python
try:
    task = session.get(Task, task_id)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # Exposes SQL!
```

✅ **CORRECT - Generic error message:**
```python
try:
    task = session.get(Task, task_id)
except Exception as e:
    # Log the real error
    logger.error(f"Database error: {str(e)}")
    # Return generic message to client
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Quick Checklist

Before deploying, verify:

- [ ] All endpoints verify `user_id` matches authenticated user
- [ ] All database queries filter by `user_id`
- [ ] CORS middleware includes `allow_credentials=True`
- [ ] Secrets loaded from environment variables
- [ ] Response models defined for all endpoints
- [ ] Proper HTTP status codes (201 for creation, 204 for deletion)
- [ ] Error handling with descriptive messages
- [ ] Database sessions use dependency injection
- [ ] Indexes on frequently queried columns
- [ ] JWT errors handled gracefully
- [ ] Update operations use `exclude_unset=True`
- [ ] Tables created on startup
- [ ] SQLite includes `check_same_thread=False`

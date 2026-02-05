# FastAPI Code Patterns Reference

## Core Patterns

### 1. Main Application Setup

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import create_db_and_tables
from app.routes import tasks, auth
import os

app = FastAPI(title="API", version="1.0.0")

# CORS Configuration - CRITICAL for JWT cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,  # Required for JWT cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router registration
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 2. Database Connection with SQLModel

```python
# app/db.py
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

### 3. SQLModel Table Definition

```python
# app/models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)  # CRITICAL: Always index user_id
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False
            }
        }
```

### 4. Pydantic Schemas

```python
# app/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(max_length=200)
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 5. JWT Middleware

```python
# app/middleware/jwt.py
from fastapi import HTTPException, Header
from jose import JWTError, jwt
from typing import Optional
import os

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

async def verify_jwt(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify JWT token from Authorization header.
    Returns decoded token payload with user_id.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {"user_id": user_id}

    except (ValueError, JWTError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

### 6. Protected CRUD Endpoints with User Isolation

```python
# app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_session
from app.middleware.jwt import verify_jwt
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from typing import List

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """List all tasks for authenticated user."""
    # CRITICAL: Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # CRITICAL: Filter by user_id
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks

@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Create a new task for authenticated user."""
    # CRITICAL: Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # CRITICAL: Set user_id from authenticated user
    task = Task(**task_data.model_dump(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Get a specific task."""
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # CRITICAL: Filter by BOTH task_id AND user_id
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Update a task."""
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    from datetime import datetime
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Delete a task."""
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()

@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Toggle task completion status."""
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed

    from datetime import datetime
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### 7. Error Handling Pattern

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
```

## Critical Security Patterns

### User Isolation Checklist

Every protected endpoint MUST:
1. ✅ Accept `user_id` in path parameter
2. ✅ Require JWT authentication via `Depends(verify_jwt)`
3. ✅ Compare `current_user["user_id"]` with path `user_id`
4. ✅ Return 403 if mismatch
5. ✅ Filter ALL database queries by `user_id`

### CORS for JWT Cookies

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # CRITICAL - enables cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variable Management

```python
# .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
API_HOST=0.0.0.0
API_PORT=8000
```

## Common Query Patterns

### Filtering
```python
statement = select(Task).where(
    Task.user_id == user_id,
    Task.completed == False
)
```

### Pagination
```python
statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
```

### Sorting
```python
statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
```

### Search
```python
statement = select(Task).where(
    Task.user_id == user_id,
    Task.title.contains(search_term)
)
```

# FastAPI Project Structure Reference

## Standard Directory Layout

```
backend/                      # uv-managed project root
├── .venv/                    # Virtual environment (uv managed)
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── db.py                # Database connection and session
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py         # Example CRUD endpoints
│   │   └── auth.py          # Authentication endpoints
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── jwt.py           # JWT verification middleware
│   └── utils/
│       ├── __init__.py
│       └── auth.py          # Auth helper functions
├── .python-version          # Python version for uv
├── pyproject.toml           # Project dependencies
├── requirements.txt         # Exported dependencies
├── .env.example             # Environment variable template
├── README.md                # Project documentation
└── CLAUDE.md                # Backend-specific AI instructions
```

## File Responsibilities

### `app/main.py`
- FastAPI application initialization
- CORS middleware configuration
- Router registration
- Database initialization
- Startup/shutdown event handlers
- Health check endpoint
- Global error handlers

### `app/models.py`
- SQLModel table definitions
- Relationships and foreign keys
- Indexes for performance
- Timestamps (created_at, updated_at)
- Validation constraints

### `app/schemas.py`
- Request validation models
- Response serialization models
- Separates API contract from database models
- Optional fields for PATCH operations

### `app/db.py`
- Database engine creation
- Session management
- Dependency injection function
- Table creation utility
- Connection pooling configuration

### `app/routes/*.py`
- API endpoint implementations
- CRUD operations
- JWT authentication dependencies
- User isolation logic
- Error handling

### `app/middleware/jwt.py`
- JWT token verification
- User extraction from token
- Dependency for protected routes
- Token validation errors

### `app/utils/auth.py`
- Password hashing
- Token generation
- User verification helpers

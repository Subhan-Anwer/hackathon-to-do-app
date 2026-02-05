# FastAPI Backend

Production-ready FastAPI backend with SQLModel ORM and JWT authentication.

## Features

- FastAPI web framework
- SQLModel ORM (SQLAlchemy + Pydantic)
- JWT authentication middleware
- User isolation and security
- CORS configuration
- RESTful API design
- Error handling
- Interactive API docs

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- PostgreSQL (or SQLite for development)

### Installation

```bash
# Install dependencies
uv sync

# Or using uv add
uv add fastapi uvicorn sqlmodel python-jose[cryptography]
```

### Configuration

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
```

### Run Development Server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── db.py                # Database connection
│   ├── routes/              # API endpoints
│   ├── middleware/          # JWT verification
│   └── utils/               # Helper functions
├── pyproject.toml           # Project dependencies
├── .env                     # Environment variables (not in git)
└── .env.example             # Environment template
```

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Tasks (Example)
- `GET /api/{user_id}/tasks` - List all tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{id}` - Get task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

All endpoints except health check require JWT authentication.

## Development

### Run Tests

```bash
uv run pytest
```

### Add Dependencies

```bash
uv add package-name
```

### Database Migrations

```bash
# Tables are auto-created on startup
# For production, consider using Alembic
uv add alembic
alembic init migrations
```

## Security

### User Isolation

Every endpoint:
1. Verifies JWT token
2. Extracts user_id from token
3. Compares with user_id in URL
4. Returns 403 if mismatch
5. Filters queries by authenticated user_id

### CORS Configuration

Configured to allow credentials for JWT cookies from frontend origin.

### Environment Variables

Never commit `.env` file. Use `.env.example` as template.

## Troubleshooting

### CORS Errors
- Verify `CORS_ORIGINS` includes frontend URL
- Ensure `allow_credentials=True` in middleware

### JWT Authentication Fails
- Check `BETTER_AUTH_SECRET` matches frontend
- Verify token format: "Bearer <token>"
- Ensure user_id exists in token payload

### Database Connection Errors
- Verify `DATABASE_URL` format
- Check database server is running
- Test connection with database client

## Production Deployment

1. Use PostgreSQL (not SQLite)
2. Set secure `BETTER_AUTH_SECRET`
3. Configure proper CORS origins
4. Enable HTTPS
5. Set up logging and monitoring
6. Use database migrations (Alembic)
7. Configure connection pooling
8. Add rate limiting

## License

[Your License]

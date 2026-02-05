# Security Testing Guide

Comprehensive guide to testing security in FastAPI applications with JWT authentication and user isolation.

## Table of Contents

- [Testing Strategy](#testing-strategy)
- [Manual Testing](#manual-testing)
- [Automated Testing](#automated-testing)
- [Penetration Testing](#penetration-testing)
- [CI/CD Integration](#cicd-integration)
- [Security Tools](#security-tools)

## Testing Strategy

### Test Pyramid for Security

```
        ┌─────────────────┐
        │  Penetration    │  ← Annual/quarterly
        │    Testing      │
        ├─────────────────┤
        │  Integration    │  ← CI/CD (every commit)
        │  Security Tests │
        ├─────────────────┤
        │   Unit Tests    │  ← Development (continuous)
        │  (Auth/Authz)   │
        └─────────────────┘
```

### Test Categories

1. **Authentication Tests** - Token validation, expiration, signature
2. **Authorization Tests** - User isolation, resource ownership
3. **Input Validation** - Injection, XSS, path traversal
4. **IDOR Tests** - Cross-user access attempts
5. **Rate Limiting** - Brute force protection
6. **Error Handling** - Information disclosure

## Manual Testing

### 1. Authentication Testing

#### Test Valid Token
```bash
# 1. Login and get token
curl -X POST http://localhost:3000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c cookies.txt

# 2. Make authenticated request through proxy
curl http://localhost:3000/api/proxy/api/user_id/tasks \
  -b cookies.txt

# Should return 200 with user's tasks
```

#### Test Missing Token
```bash
curl http://localhost:8000/api/user_id/tasks

# Expected: 401 Unauthorized
# Response: {"detail": "Missing Authorization header"}
```

#### Test Invalid Token
```bash
curl http://localhost:8000/api/user_id/tasks \
  -H "Authorization: Bearer invalid_token"

# Expected: 401 Unauthorized
# Response: {"detail": "Invalid token: ..."}
```

#### Test Expired Token
```bash
# Create token that expires in 1 second
python3 << EOF
import jwt
from datetime import datetime, timedelta

payload = {
    "sub": "user123",
    "exp": datetime.utcnow() + timedelta(seconds=1)
}
token = jwt.encode(payload, "your-secret", algorithm="HS256")
print(token)
EOF

# Wait 2 seconds, then use token
sleep 2
curl http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer $TOKEN"

# Expected: 401 Unauthorized
# Response: {"detail": "Token has expired"}
```

#### Test Wrong Secret
```bash
# Generate token with wrong secret
python3 << EOF
import jwt
payload = {"sub": "user123", "exp": 9999999999}
token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
print(token)
EOF

curl http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer $TOKEN"

# Expected: 401 Unauthorized
# Response: {"detail": "Invalid token: Signature verification failed"}
```

### 2. Authorization Testing (IDOR)

#### Test Cross-User Access (List)
```bash
# Get token for User A
USER_A_TOKEN="<token_for_user_a>"

# Try to access User B's tasks
curl http://localhost:8000/api/user_b_id/tasks \
  -H "Authorization: Bearer $USER_A_TOKEN"

# Expected: 403 Forbidden
# Response: {"detail": "Access forbidden: You can only access your own tasks"}
```

#### Test Cross-User Access (Single Resource)
```bash
# User A tries to read User B's task
curl http://localhost:8000/api/user_a_id/tasks/999 \
  -H "Authorization: Bearer $USER_A_TOKEN"

# If task 999 belongs to User B:
# Expected: 403 Forbidden
```

#### Test Cross-User Create
```bash
# User A tries to create task for User B
curl -X POST http://localhost:8000/api/user_b_id/tasks \
  -H "Authorization: Bearer $USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hacking attempt", "completed": false}'

# Expected: 403 Forbidden
```

#### Test Cross-User Update
```bash
# User A tries to update User B's task
curl -X PUT http://localhost:8000/api/user_a_id/tasks/999 \
  -H "Authorization: Bearer $USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hacked!", "completed": true}'

# If task 999 belongs to User B:
# Expected: 403 Forbidden
```

#### Test Cross-User Delete
```bash
# User A tries to delete User B's task
curl -X DELETE http://localhost:8000/api/user_a_id/tasks/999 \
  -H "Authorization: Bearer $USER_A_TOKEN"

# If task 999 belongs to User B:
# Expected: 403 Forbidden
```

### 3. Input Validation Testing

#### Test SQL Injection
```bash
# Try SQL injection in search parameter
curl "http://localhost:8000/api/user_id/tasks/search?q=' OR '1'='1" \
  -H "Authorization: Bearer $TOKEN"

# Should NOT return all tasks (SQLModel prevents this)
# Should return tasks matching the literal string
```

#### Test XSS in Task Title
```bash
curl -X POST http://localhost:8000/api/user_id/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "<script>alert(\"XSS\")</script>", "completed": false}'

# Should accept (backend stores as-is)
# Frontend must escape when rendering
```

#### Test Oversized Input
```bash
# Try to create task with very long title
curl -X POST http://localhost:8000/api/user_id/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"$(python3 -c 'print(\"A\" * 10000)')\"}"

# Expected: 422 Validation Error (if max_length set)
```

### 4. Rate Limiting Testing

```bash
# Send 100 requests quickly
for i in {1..100}; do
  curl http://localhost:8000/api/user_id/tasks \
    -H "Authorization: Bearer $TOKEN" &
done
wait

# Expected: Some requests return 429 Too Many Requests
```

### 5. Error Message Testing

```bash
# Test that errors don't leak information
curl http://localhost:8000/api/user_id/nonexistent \
  -H "Authorization: Bearer $TOKEN"

# Should NOT reveal:
# - Stack traces
# - File paths
# - Database errors
# - Internal implementation details
```

## Automated Testing

### Setup Test Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
import jwt
from datetime import datetime, timedelta

from main import app
from database import get_session

# Test database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture
def session():
    """Create test database session"""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def client(session):
    """Create test client with test database"""
    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session
    return TestClient(app)

@pytest.fixture
def test_secret():
    return "test-secret-key-32-characters-long!"

@pytest.fixture
def user_a_token(test_secret):
    """Generate token for User A"""
    payload = {
        "sub": "user_a_id",
        "email": "usera@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, test_secret, algorithm="HS256")

@pytest.fixture
def user_b_token(test_secret):
    """Generate token for User B"""
    payload = {
        "sub": "user_b_id",
        "email": "userb@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, test_secret, algorithm="HS256")
```

### Authentication Tests

```python
# tests/test_authentication.py
import pytest
from datetime import datetime, timedelta
import jwt

class TestAuthentication:
    """Test JWT authentication requirements"""

    def test_missing_token_returns_401(self, client):
        response = client.get("/api/user_id/tasks")
        assert response.status_code == 401
        assert "authorization" in response.json()["detail"].lower()

    def test_invalid_token_format_returns_401(self, client):
        response = client.get(
            "/api/user_id/tasks",
            headers={"Authorization": "Invalid token123"}
        )
        assert response.status_code == 401

    def test_malformed_bearer_token_returns_401(self, client):
        response = client.get(
            "/api/user_id/tasks",
            headers={"Authorization": "Bearer"}  # Missing token
        )
        assert response.status_code == 401

    def test_expired_token_returns_401(self, client, test_secret):
        payload = {
            "sub": "user_id",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
        }
        expired_token = jwt.encode(payload, test_secret, algorithm="HS256")

        response = client.get(
            "/api/user_id/tasks",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_wrong_secret_returns_401(self, client):
        payload = {"sub": "user_id", "exp": 9999999999}
        wrong_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

        response = client.get(
            "/api/user_id/tasks",
            headers={"Authorization": f"Bearer {wrong_token}"}
        )

        assert response.status_code == 401

    def test_valid_token_allows_access(self, client, user_a_token):
        response = client.get(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        assert response.status_code == 200
```

### Authorization Tests

```python
# tests/test_authorization.py
import pytest

class TestAuthorization:
    """Test user isolation and IDOR protection"""

    def test_user_cannot_list_other_user_tasks(
        self, client, user_a_token
    ):
        """User A cannot list User B's tasks"""
        response = client.get(
            "/api/user_b_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        assert response.status_code == 403

    def test_user_can_list_own_tasks(
        self, client, user_a_token, seed_user_a_tasks
    ):
        """User A can list their own tasks"""
        response = client.get(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        assert response.status_code == 200
        tasks = response.json()

        # All tasks belong to user_a
        for task in tasks:
            assert task["user_id"] == "user_a_id"

    def test_user_cannot_read_other_user_task(
        self, client, user_a_token, user_b_task
    ):
        """User A cannot read User B's specific task"""
        response = client.get(
            f"/api/user_a_id/tasks/{user_b_task.id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        assert response.status_code == 403

    def test_user_cannot_create_for_other_user(
        self, client, user_a_token
    ):
        """User A cannot create tasks for User B"""
        response = client.post(
            "/api/user_b_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "Test", "completed": False}
        )

        assert response.status_code == 403

    def test_user_cannot_update_other_user_task(
        self, client, user_a_token, user_b_task
    ):
        """User A cannot update User B's task"""
        response = client.put(
            f"/api/user_a_id/tasks/{user_b_task.id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "Hacked", "completed": True}
        )

        assert response.status_code == 403

    def test_user_cannot_delete_other_user_task(
        self, client, user_a_token, user_b_task
    ):
        """User A cannot delete User B's task"""
        response = client.delete(
            f"/api/user_a_id/tasks/{user_b_task.id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        assert response.status_code == 403

    def test_created_task_has_correct_user_id(
        self, client, user_a_token
    ):
        """Created task uses user_id from token, not request"""
        response = client.post(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={
                "title": "Test",
                "user_id": "user_b_id"  # Try to set different user
            }
        )

        assert response.status_code == 201
        task = response.json()

        # Should use token's user_id, not provided one
        assert task["user_id"] == "user_a_id"
```

### Input Validation Tests

```python
# tests/test_input_validation.py
import pytest

class TestInputValidation:
    """Test input validation and injection protection"""

    def test_sql_injection_in_search(self, client, user_a_token):
        """SQL injection attempts should not work"""
        response = client.get(
            "/api/user_a_id/tasks/search?q=' OR '1'='1",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # Should return 200 but not all tasks
        assert response.status_code == 200
        # SQLModel prevents injection

    def test_xss_in_title_accepted(self, client, user_a_token):
        """XSS in title should be accepted (frontend must escape)"""
        xss_payload = '<script>alert("XSS")</script>'

        response = client.post(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": xss_payload, "completed": False}
        )

        assert response.status_code == 201
        task = response.json()
        assert task["title"] == xss_payload

    def test_empty_title_rejected(self, client, user_a_token):
        """Empty title should be rejected"""
        response = client.post(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "", "completed": False}
        )

        assert response.status_code == 422

    def test_oversized_input_rejected(self, client, user_a_token):
        """Very long input should be rejected"""
        response = client.post(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "A" * 10000, "completed": False}
        )

        # Depends on validation rules
        assert response.status_code in [422, 400]
```

### Performance and Rate Limiting Tests

```python
# tests/test_rate_limiting.py
import pytest
import asyncio

class TestRateLimiting:
    """Test rate limiting protection"""

    @pytest.mark.asyncio
    async def test_rate_limit_enforced(self, client, user_a_token):
        """Rapid requests should trigger rate limit"""
        # Send 100 requests quickly
        tasks = []
        for _ in range(100):
            tasks.append(
                client.get(
                    "/api/user_a_id/tasks",
                    headers={"Authorization": f"Bearer {user_a_token}"}
                )
            )

        responses = await asyncio.gather(*tasks)

        # Some should be rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes  # Too Many Requests
```

## Penetration Testing

### Tools

1. **OWASP ZAP** - Automated security scanner
2. **Burp Suite** - Manual testing and scanning
3. **sqlmap** - SQL injection testing
4. **Postman** - API testing with collections

### OWASP ZAP Example

```bash
# Install OWASP ZAP
# https://www.zaproxy.org/download/

# Run automated scan
zap-cli quick-scan http://localhost:8000

# Generate report
zap-cli report -o security-report.html
```

### Burp Suite Workflow

1. Configure browser to use Burp proxy (localhost:8080)
2. Navigate through application
3. Review captured requests in Burp
4. Send interesting requests to Repeater
5. Modify and resend to test authorization

**Common Tests:**
- Change user_id in URL
- Modify resource IDs
- Remove Authorization header
- Modify JWT payload (detect tampering)
- Test IDOR by incrementing IDs

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on: [push, pull_request]

jobs:
  security-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio safety bandit

      - name: Run security tests
        run: |
          pytest tests/test_authentication.py -v
          pytest tests/test_authorization.py -v

      - name: Check dependencies for vulnerabilities
        run: safety check

      - name: Run static security analysis
        run: bandit -r . -f json -o bandit-report.json

      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            test-results/
```

## Security Tools

### 1. Safety - Dependency Scanner

```bash
# Install
pip install safety

# Check for known vulnerabilities
safety check

# Generate report
safety check --json > safety-report.json
```

### 2. Bandit - Static Analysis

```bash
# Install
pip install bandit

# Scan for security issues
bandit -r . -f json -o bandit-report.json

# Common issues detected:
# - Hardcoded passwords
# - SQL injection risks
# - Shell injection risks
# - Insecure random number generation
```

### 3. Trivy - Container Scanning

```bash
# Install
# https://github.com/aquasecurity/trivy

# Scan Docker image
trivy image your-app:latest

# Scan filesystem
trivy fs .
```

### 4. pytest-security

```bash
# Install
pip install pytest-security

# Run security-focused tests
pytest --security
```

## Testing Checklist

Use this checklist for comprehensive security testing:

### Authentication
- [ ] Missing token returns 401
- [ ] Invalid token returns 401
- [ ] Expired token returns 401
- [ ] Wrong secret returns 401
- [ ] Valid token allows access
- [ ] Token in httpOnly cookie works
- [ ] WWW-Authenticate header present in 401

### Authorization (IDOR)
- [ ] User cannot list other user's resources
- [ ] User cannot read other user's resource
- [ ] User cannot create for other user
- [ ] User cannot update other user's resource
- [ ] User cannot delete other user's resource
- [ ] List returns only user's resources
- [ ] Search filters by user
- [ ] Created resources have correct user_id

### Input Validation
- [ ] SQL injection prevented
- [ ] XSS handled appropriately
- [ ] Empty input rejected
- [ ] Oversized input rejected
- [ ] Invalid data types rejected
- [ ] Path traversal prevented

### Rate Limiting
- [ ] Rapid requests trigger rate limit
- [ ] Rate limit resets after timeout
- [ ] Different endpoints have appropriate limits
- [ ] Login endpoint has strict limit

### Error Handling
- [ ] No stack traces in responses
- [ ] No file paths in errors
- [ ] No database errors exposed
- [ ] Generic error messages
- [ ] Proper logging of errors

### CORS
- [ ] Specific origins configured
- [ ] Credentials allowed
- [ ] Preflight requests handled
- [ ] Headers properly configured

### Security Headers
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] Strict-Transport-Security (HTTPS)
- [ ] Content-Security-Policy configured

---

## Summary

Security testing should be:
- **Continuous** - Run on every commit
- **Comprehensive** - Cover all attack vectors
- **Automated** - Integrated in CI/CD
- **Realistic** - Test actual attack scenarios
- **Documented** - Track findings and fixes

Remember: **Security is not a one-time check, it's an ongoing process.**

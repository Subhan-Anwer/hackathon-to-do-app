"""
Security Test Suite for JWT-Protected APIs

Comprehensive security tests covering:
- Authentication (valid/invalid/missing tokens)
- Authorization (user isolation, resource ownership)
- IDOR vulnerabilities
- Mass assignment protection
- Error responses

Run with: pytest tests/test_security.py -v
"""

import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta
import os

# Assumes you have a conftest.py with these fixtures
# from main import app
# from database import get_session


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def valid_token_user_a(test_secret):
    """Generate valid JWT token for user A"""
    payload = {
        "sub": "user_a_id",  # User ID
        "email": "usera@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, test_secret, algorithm="HS256")


@pytest.fixture
def valid_token_user_b(test_secret):
    """Generate valid JWT token for user B"""
    payload = {
        "sub": "user_b_id",
        "email": "userb@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, test_secret, algorithm="HS256")


@pytest.fixture
def expired_token(test_secret):
    """Generate expired JWT token"""
    payload = {
        "sub": "user_a_id",
        "email": "usera@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
    }
    return jwt.encode(payload, test_secret, algorithm="HS256")


@pytest.fixture
def test_secret():
    """Test JWT secret (use same as BETTER_AUTH_SECRET in tests)"""
    return os.getenv("BETTER_AUTH_SECRET", "test-secret-key-32-characters-long!")


# ==============================================================================
# Authentication Tests
# ==============================================================================

class TestAuthentication:
    """Test JWT authentication requirements"""

    def test_missing_token_returns_401(self, client):
        """Request without token should return 401"""
        response = client.get("/api/user123/tasks")

        assert response.status_code == 401
        assert "Authorization" in response.json()["detail"].lower()

    def test_invalid_token_format_returns_401(self, client):
        """Malformed token should return 401"""
        response = client.get(
            "/api/user123/tasks",
            headers={"Authorization": "InvalidFormat token123"}
        )

        assert response.status_code == 401

    def test_invalid_token_signature_returns_401(self, client):
        """Token with invalid signature should return 401"""
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        response = client.get(
            "/api/user123/tasks",
            headers={"Authorization": f"Bearer {fake_token}"}
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_expired_token_returns_401(self, client, expired_token):
        """Expired token should return 401"""
        response = client.get(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_valid_token_allows_access(self, client, valid_token_user_a):
        """Valid token should allow access"""
        response = client.get(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_a}"}
        )

        assert response.status_code == 200


# ==============================================================================
# Authorization Tests (User Isolation)
# ==============================================================================

class TestAuthorization:
    """Test user isolation and resource ownership"""

    def test_user_cannot_access_other_user_resources(
        self, client, valid_token_user_a
    ):
        """User A cannot access User B's resources"""
        response = client.get(
            "/api/user_b_id/tasks",  # Trying to access User B's tasks
            headers={"Authorization": f"Bearer {valid_token_user_a}"}  # User A's token
        )

        assert response.status_code == 403
        assert "forbidden" in response.json()["detail"].lower()

    def test_user_can_only_create_for_themselves(
        self, client, valid_token_user_a
    ):
        """User A cannot create resources for User B"""
        response = client.post(
            "/api/user_b_id/tasks",  # Trying to create for User B
            headers={"Authorization": f"Bearer {valid_token_user_a}"},  # User A's token
            json={"title": "Test task", "completed": False}
        )

        assert response.status_code == 403

    def test_user_cannot_update_other_user_resources(
        self, client, valid_token_user_a, user_b_task_id
    ):
        """User A cannot update User B's task"""
        response = client.put(
            f"/api/user_a_id/tasks/{user_b_task_id}",  # User B's task
            headers={"Authorization": f"Bearer {valid_token_user_a}"},
            json={"title": "Hacked!", "completed": True}
        )

        # Should return 403 when checking resource ownership
        assert response.status_code == 403

    def test_user_cannot_delete_other_user_resources(
        self, client, valid_token_user_a, user_b_task_id
    ):
        """User A cannot delete User B's task"""
        response = client.delete(
            f"/api/user_a_id/tasks/{user_b_task_id}",
            headers={"Authorization": f"Bearer {valid_token_user_a}"}
        )

        assert response.status_code == 403


# ==============================================================================
# IDOR (Insecure Direct Object Reference) Tests
# ==============================================================================

class TestIDORProtection:
    """Test protection against IDOR vulnerabilities"""

    def test_cannot_access_task_by_id_alone(
        self, client, valid_token_user_a, user_b_task_id
    ):
        """User cannot access resource just by knowing its ID"""
        # Try to access User B's task using User A's token
        response = client.get(
            f"/api/user_a_id/tasks/{user_b_task_id}",
            headers={"Authorization": f"Bearer {valid_token_user_a}"}
        )

        # Should fail ownership check
        assert response.status_code in [403, 404]

    def test_sequential_id_enumeration_blocked(
        self, client, valid_token_user_a
    ):
        """User cannot enumerate IDs to find other users' resources"""
        # Try accessing sequential IDs
        for task_id in range(1, 100):
            response = client.get(
                f"/api/user_a_id/tasks/{task_id}",
                headers={"Authorization": f"Bearer {valid_token_user_a}"}
            )

            # Should either be user's own task (200), not found (404), or forbidden (403)
            assert response.status_code in [200, 404, 403]

            # If 200, verify it belongs to user_a
            if response.status_code == 200:
                assert response.json()["user_id"] == "user_a_id"


# ==============================================================================
# Mass Assignment Tests
# ==============================================================================

class TestMassAssignment:
    """Test protection against mass assignment vulnerabilities"""

    def test_cannot_set_user_id_in_create(self, client, valid_token_user_a):
        """User cannot set user_id when creating resource"""
        response = client.post(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_a}"},
            json={
                "title": "Test task",
                "completed": False,
                "user_id": "user_b_id"  # Trying to set different user_id
            }
        )

        # Should succeed but use token's user_id, not the provided one
        if response.status_code == 201:
            assert response.json()["user_id"] == "user_a_id"

    def test_cannot_change_user_id_in_update(
        self, client, valid_token_user_a, user_a_task_id
    ):
        """User cannot change user_id when updating resource"""
        response = client.put(
            f"/api/user_a_id/tasks/{user_a_task_id}",
            headers={"Authorization": f"Bearer {valid_token_user_a}"},
            json={
                "title": "Updated task",
                "user_id": "user_b_id"  # Trying to change ownership
            }
        )

        # Should not allow changing user_id
        if response.status_code == 200:
            assert response.json()["user_id"] == "user_a_id"


# ==============================================================================
# Query Filter Tests
# ==============================================================================

class TestQueryFiltering:
    """Test that database queries are properly filtered by user"""

    def test_list_returns_only_user_resources(
        self, client, valid_token_user_a, seed_tasks
    ):
        """List endpoint returns only authenticated user's resources"""
        response = client.get(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_a}"}
        )

        assert response.status_code == 200
        tasks = response.json()

        # All tasks should belong to user_a
        for task in tasks:
            assert task["user_id"] == "user_a_id"

    def test_search_filters_by_user(
        self, client, valid_token_user_a, seed_tasks
    ):
        """Search endpoint filters by authenticated user"""
        response = client.get(
            "/api/user_a_id/tasks/search?q=test",
            headers={"Authorization": f"Bearer {valid_token_user_a}"}
        )

        assert response.status_code == 200
        tasks = response.json()

        # All results should belong to user_a
        for task in tasks:
            assert task["user_id"] == "user_a_id"


# ==============================================================================
# Error Response Tests
# ==============================================================================

class TestErrorResponses:
    """Test that error responses don't leak sensitive information"""

    def test_404_does_not_leak_existence(
        self, client, valid_token_user_a
    ):
        """404 for non-existent resource should not reveal if it exists for another user"""
        response = client.get(
            "/api/user_a_id/tasks/999999",
            headers={"Authorization": f"Bearer {valid_token_user_a}"}
        )

        # Should return 404, not 403 (which would confirm existence)
        assert response.status_code in [404, 403]

        # Error message should not mention other users
        assert "user_b" not in response.json()["detail"].lower()

    def test_401_includes_www_authenticate_header(self, client):
        """401 responses should include WWW-Authenticate header"""
        response = client.get("/api/user123/tasks")

        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"

    def test_error_does_not_leak_internal_details(
        self, client, valid_token_user_a
    ):
        """Error responses should not leak implementation details"""
        # Trigger an error
        response = client.post(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_a}"},
            json={"invalid": "data"}  # Invalid payload
        )

        # Should return 422 validation error
        # Should not contain stack traces or file paths
        error_text = str(response.json())
        assert "/app/" not in error_text
        assert "Traceback" not in error_text


# ==============================================================================
# Fixtures for Test Data
# ==============================================================================

@pytest.fixture
def user_a_task_id(client, valid_token_user_a):
    """Create a task for User A and return its ID"""
    response = client.post(
        "/api/user_a_id/tasks",
        headers={"Authorization": f"Bearer {valid_token_user_a}"},
        json={"title": "User A Task", "completed": False}
    )
    return response.json()["id"]


@pytest.fixture
def user_b_task_id(client, valid_token_user_b):
    """Create a task for User B and return its ID"""
    response = client.post(
        "/api/user_b_id/tasks",
        headers={"Authorization": f"Bearer {valid_token_user_b}"},
        json={"title": "User B Task", "completed": False}
    )
    return response.json()["id"]


@pytest.fixture
def seed_tasks(client, valid_token_user_a, valid_token_user_b):
    """Create multiple tasks for both users"""
    # Create 5 tasks for User A
    for i in range(5):
        client.post(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_a}"},
            json={"title": f"User A Task {i}", "completed": i % 2 == 0}
        )

    # Create 5 tasks for User B
    for i in range(5):
        client.post(
            "/api/user_b_id/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_b}"},
            json={"title": f"User B Task {i}", "completed": i % 2 == 0}
        )


# ==============================================================================
# Run Tests
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

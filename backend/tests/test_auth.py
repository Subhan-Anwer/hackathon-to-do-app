"""Authentication tests (401 Unauthorized).

Tests JWT validation for all endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tasks_returns_401_when_no_token(client: AsyncClient, user_a_id):
    """T018: GET /api/{user_id}/tasks returns 401 when no token provided."""
    response = await client.get(f"/api/{user_a_id}/tasks")
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_tasks_returns_401_with_invalid_token(client: AsyncClient, user_a_id, invalid_token):
    """GET /api/{user_id}/tasks returns 401 when token is invalid."""
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = await client.get(f"/api/{user_a_id}/tasks", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_task_returns_401_when_no_token(client: AsyncClient, user_a_id):
    """T030: POST /api/{user_id}/tasks returns 401 when no token provided."""
    response = await client.post(
        f"/api/{user_a_id}/tasks",
        json={"title": "Test Task"}
    )
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_toggle_completion_returns_401_when_no_token(client: AsyncClient, user_a_id):
    """T044: PATCH /complete returns 401 when no token provided."""
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.patch(f"/api/{user_a_id}/tasks/{fake_task_id}/complete")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_task_returns_401_when_no_token(client: AsyncClient, user_a_id):
    """T076: GET /tasks/{task_id} returns 401 when no token."""
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.get(f"/api/{user_a_id}/tasks/{fake_task_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_task_returns_401_when_no_token(client: AsyncClient, user_a_id):
    """T059: PUT /tasks/{task_id} returns 401 when no token."""
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.put(
        f"/api/{user_a_id}/tasks/{fake_task_id}",
        json={"title": "Updated"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_task_returns_401_when_no_token(client: AsyncClient, user_a_id):
    """T088: DELETE /tasks/{task_id} returns 401 when no token."""
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.delete(f"/api/{user_a_id}/tasks/{fake_task_id}")
    assert response.status_code == 401

"""User isolation tests (403 Forbidden, cross-user access prevention).

Critical security tests ensuring users cannot access each other's data.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tasks_returns_403_when_user_id_mismatch(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token
):
    """T019: GET /api/{user_id}/tasks returns 403 when path user_id doesn't match token user_id."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    # User A token trying to access User B's endpoint
    response = await client.get(f"/api/{user_b_id}/tasks", headers=headers)
    assert response.status_code == 403
    assert "cannot access other users" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_a_cannot_see_user_b_tasks(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token,
    user_b_token
):
    """T020: User A cannot see User B's tasks via GET endpoint."""
    # User B creates a task
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    create_response = await client.post(
        f"/api/{user_b_id}/tasks",
        headers=headers_b,
        json={"title": "User B's Private Task"}
    )
    assert create_response.status_code == 201

    # User A lists their tasks (should be empty)
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    list_response = await client.get(f"/api/{user_a_id}/tasks", headers=headers_a)
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 0  # User A should not see User B's task


@pytest.mark.asyncio
async def test_create_task_returns_403_when_user_id_mismatch(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token
):
    """T031: POST /api/{user_id}/tasks returns 403 when user_id mismatch."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    # User A token trying to create task for User B
    response = await client.post(
        f"/api/{user_b_id}/tasks",
        headers=headers,
        json={"title": "Test Task"}
    )
    assert response.status_code == 403
    assert "cannot" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_toggle_completion_returns_403_when_user_id_mismatch(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token
):
    """T045: PATCH /complete returns 403 when user_id mismatch."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.patch(
        f"/api/{user_b_id}/tasks/{fake_task_id}/complete",
        headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_toggle_completion_returns_404_when_other_user_task(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token,
    user_b_token
):
    """T046: PATCH /complete returns 404 when trying to complete other user's task."""
    # User B creates a task
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    create_response = await client.post(
        f"/api/{user_b_id}/tasks",
        headers=headers_b,
        json={"title": "User B's Task"}
    )
    assert create_response.status_code == 201
    task_b = create_response.json()

    # User A tries to toggle User B's task (using correct user_a_id in path)
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.patch(
        f"/api/{user_a_id}/tasks/{task_b['id']}/complete",
        headers=headers_a
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_returns_403_when_user_id_mismatch(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token
):
    """T060: PUT /tasks/{task_id} returns 403 when user_id mismatch."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.put(
        f"/api/{user_b_id}/tasks/{fake_task_id}",
        headers=headers,
        json={"title": "Updated"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_task_returns_404_when_other_user_task(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token,
    user_b_token
):
    """T061: PUT /tasks/{task_id} returns 404 when trying to update other user's task."""
    # User B creates a task
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    create_response = await client.post(
        f"/api/{user_b_id}/tasks",
        headers=headers_b,
        json={"title": "User B's Task"}
    )
    assert create_response.status_code == 201
    task_b = create_response.json()

    # User A tries to update User B's task
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.put(
        f"/api/{user_a_id}/tasks/{task_b['id']}",
        headers=headers_a,
        json={"title": "Hacked"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_returns_403_when_user_id_mismatch(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token
):
    """T077: GET /tasks/{task_id} returns 403 when user_id mismatch."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.get(
        f"/api/{user_b_id}/tasks/{fake_task_id}",
        headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_task_returns_404_when_other_user_task(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token,
    user_b_token
):
    """T078: GET /tasks/{task_id} returns 404 when requesting other user's task."""
    # User B creates a task
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    create_response = await client.post(
        f"/api/{user_b_id}/tasks",
        headers=headers_b,
        json={"title": "User B's Private Task"}
    )
    assert create_response.status_code == 201
    task_b = create_response.json()

    # User A tries to get User B's task
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.get(
        f"/api/{user_a_id}/tasks/{task_b['id']}",
        headers=headers_a
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_returns_403_when_user_id_mismatch(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token
):
    """T089: DELETE /tasks/{task_id} returns 403 when user_id mismatch."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.delete(
        f"/api/{user_b_id}/tasks/{fake_task_id}",
        headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_task_returns_404_when_other_user_task(
    client: AsyncClient,
    user_a_id,
    user_b_id,
    user_a_token,
    user_b_token
):
    """T090: DELETE /tasks/{task_id} returns 404 when trying to delete other user's task."""
    # User B creates a task
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    create_response = await client.post(
        f"/api/{user_b_id}/tasks",
        headers=headers_b,
        json={"title": "User B's Task"}
    )
    assert create_response.status_code == 201
    task_b = create_response.json()

    # User A tries to delete User B's task
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.delete(
        f"/api/{user_a_id}/tasks/{task_b['id']}",
        headers=headers_a
    )
    assert response.status_code == 404

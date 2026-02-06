"""Task CRUD functional tests.

Tests task creation, retrieval, and validation logic.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tasks_returns_empty_for_new_user(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T021: GET /api/{user_id}/tasks returns empty list for new user."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.get(f"/api/{user_a_id}/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) == 0


@pytest.mark.asyncio
async def test_list_tasks_returns_correct_count(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T022: GET /api/{user_id}/tasks returns correct task count for authenticated user."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create 3 tasks
    for i in range(3):
        create_response = await client.post(
            f"/api/{user_a_id}/tasks",
            headers=headers,
            json={"title": f"Task {i+1}"}
        )
        assert create_response.status_code == 201

    # List tasks
    list_response = await client.get(f"/api/{user_a_id}/tasks", headers=headers)
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 3


@pytest.mark.asyncio
async def test_create_task_returns_422_when_title_empty(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T032: POST /api/{user_id}/tasks returns 422 when title empty."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": ""}  # Empty title
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_returns_422_when_title_too_long(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T033: POST /api/{user_id}/tasks returns 422 when title exceeds 200 chars."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "x" * 201}  # 201 characters
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_with_defaults(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T034: POST creates task with correct defaults (completed=false, timestamps)."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Test Task"}
    )
    assert response.status_code == 201
    task = response.json()
    assert task["completed"] is False
    assert task["description"] is None
    assert "created_at" in task
    assert "updated_at" in task
    assert "id" in task


@pytest.mark.asyncio
async def test_create_task_with_title_and_description(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T035: POST creates task with title and description."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }
    )
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Buy groceries"
    assert task["description"] == "Milk, eggs, bread"
    assert task["completed"] is False


# User Story 3: Toggle Completion


@pytest.mark.asyncio
async def test_toggle_completion_incomplete_to_complete(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T047: PATCH /complete toggles incomplete to complete."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task (defaults to completed=false)
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Task to complete"}
    )
    assert create_response.status_code == 201
    task = create_response.json()
    assert task["completed"] is False

    # Toggle completion
    toggle_response = await client.patch(
        f"/api/{user_a_id}/tasks/{task['id']}/complete",
        headers=headers
    )
    assert toggle_response.status_code == 200
    updated_task = toggle_response.json()
    assert updated_task["completed"] is True


@pytest.mark.asyncio
async def test_toggle_completion_complete_back_to_incomplete(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T048: PATCH /complete toggles complete back to incomplete."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create and toggle to completed
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Task to toggle twice"}
    )
    task = create_response.json()

    # Toggle to complete
    await client.patch(
        f"/api/{user_a_id}/tasks/{task['id']}/complete",
        headers=headers
    )

    # Toggle back to incomplete
    toggle_response = await client.patch(
        f"/api/{user_a_id}/tasks/{task['id']}/complete",
        headers=headers
    )
    assert toggle_response.status_code == 200
    updated_task = toggle_response.json()
    assert updated_task["completed"] is False


# User Story 4: Update Task


@pytest.mark.asyncio
async def test_update_task_title_only(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T062: PUT updates title only (partial update)."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Original Title", "description": "Keep this"}
    )
    task = create_response.json()

    # Update only title
    update_response = await client.put(
        f"/api/{user_a_id}/tasks/{task['id']}",
        headers=headers,
        json={"title": "Updated Title"}
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Keep this"


@pytest.mark.asyncio
async def test_update_task_description_only(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T063: PUT updates description only (partial update)."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Keep Title", "description": "Original"}
    )
    task = create_response.json()

    # Update only description
    update_response = await client.put(
        f"/api/{user_a_id}/tasks/{task['id']}",
        headers=headers,
        json={"description": "Updated Description"}
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Keep Title"
    assert updated_task["description"] == "Updated Description"


@pytest.mark.asyncio
async def test_update_task_completed_status(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T064: PUT updates completed status."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Task"}
    )
    task = create_response.json()
    assert task["completed"] is False

    # Update completed status
    update_response = await client.put(
        f"/api/{user_a_id}/tasks/{task['id']}",
        headers=headers,
        json={"completed": True}
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["completed"] is True


@pytest.mark.asyncio
async def test_update_task_returns_422_when_title_too_long(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T065: PUT returns 422 when title exceeds 200 chars."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Task"}
    )
    task = create_response.json()

    # Try to update with too-long title
    update_response = await client.put(
        f"/api/{user_a_id}/tasks/{task['id']}",
        headers=headers,
        json={"title": "x" * 201}
    )
    assert update_response.status_code == 422


# User Story 5: Get Single Task


@pytest.mark.asyncio
async def test_get_task_returns_404_when_not_exists(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T079: GET /tasks/{task_id} returns 404 when task doesn't exist."""
    headers = {"Authorization": f"Bearer {user_a_token}"}
    fake_task_id = "550e8400-e29b-41d4-a716-446655440000"

    response = await client.get(
        f"/api/{user_a_id}/tasks/{fake_task_id}",
        headers=headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_returns_full_details(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T080: GET /tasks/{task_id} returns full task details."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Detailed Task", "description": "Full details here"}
    )
    task = create_response.json()

    # Get task by ID
    get_response = await client.get(
        f"/api/{user_a_id}/tasks/{task['id']}",
        headers=headers
    )
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["id"] == task["id"]
    assert retrieved_task["title"] == "Detailed Task"
    assert retrieved_task["description"] == "Full details here"
    assert retrieved_task["completed"] is False


# User Story 6: Delete Task


@pytest.mark.asyncio
async def test_delete_task_permanently_removes(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T091: DELETE permanently removes task (verify not in list)."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Task to delete"}
    )
    task = create_response.json()

    # Delete task
    delete_response = await client.delete(
        f"/api/{user_a_id}/tasks/{task['id']}",
        headers=headers
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True

    # Verify not in list
    list_response = await client.get(
        f"/api/{user_a_id}/tasks",
        headers=headers
    )
    tasks = list_response.json()
    assert len(tasks) == 0


@pytest.mark.asyncio
async def test_delete_task_returns_success_response(
    client: AsyncClient,
    user_a_id,
    user_a_token
):
    """T092: DELETE returns success response."""
    headers = {"Authorization": f"Bearer {user_a_token}"}

    # Create task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        headers=headers,
        json={"title": "Task to delete"}
    )
    task = create_response.json()

    # Delete task
    delete_response = await client.delete(
        f"/api/{user_a_id}/tasks/{task['id']}",
        headers=headers
    )
    assert delete_response.status_code == 200
    result = delete_response.json()
    assert "success" in result
    assert result["success"] is True

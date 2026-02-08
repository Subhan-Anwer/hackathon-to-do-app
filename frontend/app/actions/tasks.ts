/**
 * Task Server Actions
 *
 * Server-side functions for task CRUD operations with JWT Bearer token authentication.
 *
 * Key Features:
 * - Single database call per Server Action (optimized for Neon serverless)
 * - Generates JWT tokens manually using jose library (matches backend format)
 * - Adds Authorization: Bearer <token> header to all backend API requests
 * - Enforces user isolation by verifying userId matches authenticated user
 * - Handles 401 errors with clear error messages
 *
 * Authentication Flow (via authenticateAndGetToken helper):
 * 1. Call auth.api.getSession() to validate session (single database call)
 * 2. Verify userId parameter matches session.user.id (security check)
 * 3. Generate JWT token manually with HS256, sub=user_id, 7-day expiry
 * 4. Include Authorization: Bearer <token> header in backend request
 * 5. Return task data or throw user-friendly error
 *
 * JWT Token Generation:
 * - Uses jose library (same as backend for validation)
 * - Algorithm: HS256 (matches backend dependencies.py)
 * - Secret: BETTER_AUTH_SECRET (must match backend exactly)
 * - Claims: sub=user_id, iat, exp (7 days)
 * - Format: header.payload.signature (200+ characters)
 *
 * Performance Optimization:
 * - Combined authentication + JWT generation in single DB call
 * - Critical for Neon serverless databases with cold-start wake-up latency
 *
 * Reference: specs/004-auth-fix-workflow/research.md
 */

"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { SignJWT } from "jose";
import type { Task, TaskCreateInput, TaskUpdateInput } from "@/types/task";

// Validate environment configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Production environment validation
if (process.env.NODE_ENV === "production") {
  if (!process.env.NEXT_PUBLIC_API_URL) {
    console.error(
      "[Server Actions] NEXT_PUBLIC_API_URL not set in production - using fallback"
    );
  }

  if (!process.env.BETTER_AUTH_SECRET) {
    throw new Error(
      "BETTER_AUTH_SECRET environment variable is required in production"
    );
  }
}

/**
 * Helper: Authenticate and generate JWT token
 *
 * Combined authentication flow that:
 * 1. Validates session exists (single database call)
 * 2. Verifies userId matches authenticated user (security check)
 * 3. Generates JWT token manually for backend authentication
 *
 * JWT Token Generation:
 * - Uses same BETTER_AUTH_SECRET as backend (must match exactly)
 * - Uses HS256 algorithm (matches backend dependencies.py)
 * - Includes "sub" claim with user_id for backend validation
 * - 7-day expiry (matches Better Auth session duration)
 *
 * Why Manual Generation:
 * - Better Auth JWT plugin doesn't expose JWT tokens server-side via auth.api.getSession()
 * - session.session.token is the session ID (32 chars), not a JWT token (200+ chars)
 * - Manual generation ensures token format matches backend expectations exactly
 *
 * This single helper reduces database calls from 2 to 1 per Server Action,
 * which is critical for Neon serverless databases with wake-up latency.
 *
 * @param userId - User ID from function parameter
 * @returns JWT token string (HS256, sub=user_id, 7-day expiry)
 * @throws Error if not authenticated, user ID mismatch, or secret missing
 */
async function authenticateAndGetToken(userId: string): Promise<string> {
  // Step 1: Get session (single database call)
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    throw new Error("Unauthorized - please log in");
  }

  // Step 2: Verify userId matches authenticated user (security check)
  if (userId !== session.user.id) {
    throw new Error("User ID mismatch - security violation");
  }

  // Step 3: Generate JWT token manually (matches backend expectations)
  // Backend expects: HS256 algorithm, sub claim with user_id, BETTER_AUTH_SECRET
  const secret = process.env.BETTER_AUTH_SECRET;
  if (!secret) {
    throw new Error("Server configuration error - missing auth secret");
  }

  try {
    // Create JWT token with jose library (same library backend uses for validation)
    const jwtToken = await new SignJWT({ sub: session.user.id })
      .setProtectedHeader({ alg: "HS256" }) // Algorithm matches backend
      .setIssuedAt() // Current timestamp
      .setExpirationTime("7d") // 7-day expiry (matches Better Auth session)
      .sign(new TextEncoder().encode(secret)); // Sign with shared secret

    return jwtToken;
  } catch (error) {
    throw new Error("Failed to generate authentication token");
  }
}

/**
 * Helper: Handle fetch errors with user-friendly messages
 *
 * Transforms HTTP error responses into clear error messages for users.
 *
 * @param response - Fetch response object
 * @param operation - Operation name for error message (e.g., "create task")
 * @throws Error with user-friendly message
 */
async function handleFetchError(
  response: Response,
  operation: string
): Promise<never> {
  if (response.status === 401) {
    throw new Error("Unauthorized - please log in again");
  }

  try {
    const error = await response.json();
    throw new Error(error.detail || `Failed to ${operation}`);
  } catch {
    throw new Error(`Failed to ${operation} - ${response.statusText}`);
  }
}

/**
 * Create a new task
 *
 * @param userId - User ID (must match authenticated user)
 * @param data - Task data (title, description)
 * @returns Created task object
 * @throws Error if authentication fails or task creation fails
 *
 * @example
 * const task = await createTask(session.user.id, {
 *   title: "Buy groceries",
 *   description: "Milk, eggs, bread"
 * });
 */
export async function createTask(
  userId: string,
  data: TaskCreateInput
): Promise<Task> {
  // Authenticate and get JWT token (single database call)
  const jwtToken = await authenticateAndGetToken(userId);

  // Call backend API with Authorization Bearer header
  const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${jwtToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    await handleFetchError(response, "create task");
  }

  return await response.json();
}

/**
 * List all tasks for a user
 *
 * @param userId - User ID (must match authenticated user)
 * @returns Array of user's tasks
 * @throws Error if authentication fails or task listing fails
 *
 * @example
 * const tasks = await listTasks(session.user.id);
 * console.log(`User has ${tasks.length} tasks`);
 */
export async function listTasks(userId: string): Promise<Task[]> {
  // Authenticate and get JWT token (single database call)
  const jwtToken = await authenticateAndGetToken(userId);

  // Call backend API with Authorization Bearer header
  const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${jwtToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    await handleFetchError(response, "list tasks");
  }

  return await response.json();
}

/**
 * Get a single task by ID
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID to retrieve
 * @returns Task object
 * @throws Error if authentication fails, task not found, or user doesn't own task
 *
 * @example
 * const task = await getTask(session.user.id, "task_123");
 */
export async function getTask(userId: string, taskId: string): Promise<Task> {
  // Authenticate and get JWT token (single database call)
  const jwtToken = await authenticateAndGetToken(userId);

  // Call backend API with Authorization Bearer header
  const response = await fetch(
    `${API_BASE_URL}/api/${userId}/tasks/${taskId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    await handleFetchError(response, "get task");
  }

  return await response.json();
}

/**
 * Update an existing task
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID to update
 * @param data - Updated task data (title, description)
 * @returns Updated task object
 * @throws Error if authentication fails, task not found, or user doesn't own task
 *
 * @example
 * const updatedTask = await updateTask(session.user.id, "task_123", {
 *   title: "Updated title",
 *   description: "Updated description"
 * });
 */
export async function updateTask(
  userId: string,
  taskId: string,
  data: TaskUpdateInput
): Promise<Task> {
  // Authenticate and get JWT token (single database call)
  const jwtToken = await authenticateAndGetToken(userId);

  // Call backend API with Authorization Bearer header
  const response = await fetch(
    `${API_BASE_URL}/api/${userId}/tasks/${taskId}`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    await handleFetchError(response, "update task");
  }

  return await response.json();
}

/**
 * Delete a task
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID to delete
 * @throws Error if authentication fails, task not found, or user doesn't own task
 *
 * @example
 * await deleteTask(session.user.id, "task_123");
 * console.log("Task deleted successfully");
 */
export async function deleteTask(
  userId: string,
  taskId: string
): Promise<void> {
  // Authenticate and get JWT token (single database call)
  const jwtToken = await authenticateAndGetToken(userId);

  // Call backend API with Authorization Bearer header
  const response = await fetch(
    `${API_BASE_URL}/api/${userId}/tasks/${taskId}`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    await handleFetchError(response, "delete task");
  }
}

/**
 * Toggle task completion status
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID to toggle
 * @returns Updated task object with new is_completed status
 * @throws Error if authentication fails, task not found, or user doesn't own task
 *
 * @example
 * const toggledTask = await toggleComplete(session.user.id, "task_123");
 * console.log(`Task is now ${toggledTask.is_completed ? "completed" : "incomplete"}`);
 */
export async function toggleComplete(
  userId: string,
  taskId: string
): Promise<Task> {
  // Authenticate and get JWT token (single database call)
  const jwtToken = await authenticateAndGetToken(userId);

  // Call backend API with Authorization Bearer header
  const response = await fetch(
    `${API_BASE_URL}/api/${userId}/tasks/${taskId}/complete`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    await handleFetchError(response, "toggle task completion");
  }

  return await response.json();
}

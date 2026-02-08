/**
 * DEPRECATED: API Client for FastAPI Backend
 *
 * ⚠️ DEPRECATION NOTICE (2026-02-08):
 * This file is DEPRECATED and should not be used for new code.
 * All components have been migrated to use Server Actions (app/actions/tasks.ts).
 *
 * Why deprecated:
 * - Cookie-based authentication fails on cross-origin requests (localhost:3000 → localhost:8000)
 * - Server Actions provide better security with JWT Bearer token authentication
 * - Server Actions work in both development and production without code changes
 *
 * Migration guide:
 * - Replace taskApi.create() with createTask() Server Action
 * - Replace taskApi.list() with listTasks() Server Action
 * - Replace taskApi.update() with updateTask() Server Action
 * - Replace taskApi.delete() with deleteTask() Server Action
 * - Replace taskApi.toggleComplete() with toggleComplete() Server Action
 *
 * See: app/actions/tasks.ts for new implementation
 * See: specs/004-auth-fix-workflow/ for migration details
 *
 * ---
 *
 * Original Documentation (for reference only):
 *
 * Centralized API client that:
 * - Automatically includes JWT cookie in requests (credentials: "include")
 * - Handles 401 redirects to login
 * - Provides typed methods for all CRUD operations
 * - Manages error handling and user-friendly messages
 *
 * The JWT token is stored in an httpOnly cookie by the frontend auth system.
 * The browser automatically includes it in requests via credentials: "include".
 * The FastAPI backend reads the JWT from the "session" cookie and validates it.
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-005, FR-008, FR-024)
 */

"use client";

import type { Task, TaskCreateInput, TaskUpdateInput } from "@/types/task";
import { toast } from "sonner";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Parse API errors into user-friendly messages
 * Reference: spec.md (FR-027 - meaningful error messages)
 */
function parseError(error: unknown): string {
  if (error instanceof Error) {
    if (error.message.includes("Failed to fetch")) {
      return "Unable to connect to server. Please check your internet connection.";
    }
    if (error.message.includes("401") || error.message.includes("Unauthorized")) {
      return "Your session has expired. Please log in again.";
    }
    if (error.message.includes("403") || error.message.includes("Forbidden")) {
      return "You don't have permission to perform this action.";
    }
    if (error.message.includes("404")) {
      return "Resource not found.";
    }
    if (error.message.includes("500")) {
      return "Server error. Please try again later.";
    }
    return error.message;
  }
  return "An unexpected error occurred. Please try again.";
}

/**
 * Fetch wrapper that includes JWT via httpOnly cookie
 *
 * Better Auth stores JWT tokens in httpOnly cookies which are automatically
 * sent by the browser. This is more secure than manual token management as:
 * - JavaScript cannot access httpOnly cookies (XSS protection)
 * - Browser handles cookie lifecycle automatically
 * - No need to extract/manage tokens in client code
 *
 * The backend accepts JWT from the "session" cookie and validates it.
 */
async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  // Build headers
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  // JWT token is in httpOnly cookie, automatically sent via credentials: "include"
  // No manual Authorization header needed - simpler and more secure
  const response = await fetch(url, {
    ...options,
    credentials: "include", // Automatically includes httpOnly session cookie
    headers,
  });

  // Handle 401 Unauthorized - show toast and redirect to login
  if (response.status === 401) {
    if (typeof window !== "undefined") {
      // Show user-friendly error toast before redirect
      toast.error("Your session has expired. Please log in again.", {
        duration: 1500,
      });

      // Delay redirect to allow user to read the toast message
      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);
    }
    throw new Error("Unauthorized");
  }

  return response;
}

/**
 * Task API methods for CRUD operations
 * All methods automatically include JWT cookie
 */
export const taskApi = {
  /**
   * List all tasks for authenticated user
   * GET /api/{user_id}/tasks
   */
  async list(userId: string): Promise<Task[]> {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/${userId}/tasks`);

      if (!response.ok) {
        throw new Error("Failed to fetch tasks");
      }

      return await response.json();
    } catch (error) {
      throw new Error(parseError(error));
    }
  },

  /**
   * Create a new task
   * POST /api/{user_id}/tasks
   */
  async create(userId: string, data: TaskCreateInput): Promise<Task> {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/${userId}/tasks`, {
        method: "POST",
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create task");
      }

      return await response.json();
    } catch (error) {
      throw new Error(parseError(error));
    }
  },

  /**
   * Get a single task by ID
   * GET /api/{user_id}/tasks/{task_id}
   */
  async get(userId: string, taskId: string): Promise<Task> {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`);

      if (!response.ok) {
        throw new Error("Task not found");
      }

      return await response.json();
    } catch (error) {
      throw new Error(parseError(error));
    }
  },

  /**
   * Update an existing task
   * PUT /api/{user_id}/tasks/{task_id}
   */
  async update(userId: string, taskId: string, data: TaskUpdateInput): Promise<Task> {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to update task");
      }

      return await response.json();
    } catch (error) {
      throw new Error(parseError(error));
    }
  },

  /**
   * Delete a task
   * DELETE /api/{user_id}/tasks/{task_id}
   */
  async delete(userId: string, taskId: string): Promise<void> {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete task");
      }
    } catch (error) {
      throw new Error(parseError(error));
    }
  },

  /**
   * Toggle task completion status
   * PATCH /api/{user_id}/tasks/{task_id}/complete
   */
  async toggleComplete(userId: string, taskId: string): Promise<Task> {
    try {
      const response = await fetchWithAuth(
        `${API_BASE_URL}/api/${userId}/tasks/${taskId}/complete`,
        {
          method: "PATCH",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to toggle task completion");
      }

      return await response.json();
    } catch (error) {
      throw new Error(parseError(error));
    }
  },
};

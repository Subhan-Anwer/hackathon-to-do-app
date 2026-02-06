/**
 * TypeScript types for Task entity matching backend schemas
 * Backend reference: backend/schemas.py (TaskRead, TaskCreate, TaskUpdate)
 */

/**
 * Task entity (matches TaskRead from backend schemas.py)
 * Represents a complete task with all metadata
 */
export interface Task {
  id: string;                 // UUID from backend
  title: string;              // Required, max 200 chars
  description: string | null; // Optional, max 1000 chars
  completed: boolean;         // Completion status
  created_at: string;         // ISO datetime string
  updated_at: string;         // ISO datetime string
}

/**
 * Task creation payload (matches TaskCreate from backend)
 * Used when creating a new task
 */
export interface TaskCreateInput {
  title: string;              // Required, 1-200 chars
  description?: string;       // Optional, max 1000 chars
}

/**
 * Task update payload (matches TaskUpdate from backend)
 * All fields optional - only include fields to be updated
 */
export interface TaskUpdateInput {
  title?: string;             // Optional, 1-200 chars if provided
  description?: string;       // Optional, max 1000 chars if provided
  completed?: boolean;        // Optional, toggle completion status
}

/**
 * API response wrapper for error handling
 */
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  code?: string;
}

/**
 * User entity from Better Auth session
 */
export interface User {
  id: string;                 // UUID from backend
  email: string;              // User email
  name?: string;              // Optional display name
}

/**
 * Session state from Better Auth
 */
export interface Session {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

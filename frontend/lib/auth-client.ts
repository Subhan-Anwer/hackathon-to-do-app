/**
 * Better Auth Client Configuration
 *
 * Client-side Better Auth instance for React components.
 * Provides authentication hooks and methods for:
 * - Sign in / Sign up
 * - Session management
 * - JWT token retrieval for API calls
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-003, FR-004)
 */

"use client";

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  // Better Auth client must connect to the frontend (where /api/auth/* routes are)
  // NOT the backend API. Uses environment variable for production compatibility.
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});

/**
 * Export auth session hook for client components
 * Usage: const { data: session, isPending } = useSession()
 */
export const { useSession } = authClient;

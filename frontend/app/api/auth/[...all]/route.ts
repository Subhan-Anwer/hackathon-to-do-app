/**
 * Better Auth API Route Handler
 *
 * Handles all Better Auth API requests at /api/auth/*
 * Supports both GET and POST methods for authentication flows.
 *
 * Routes handled:
 * - POST /api/auth/signup - User registration
 * - POST /api/auth/login - User authentication
 * - POST /api/auth/logout - Session termination
 * - GET /api/auth/session - Get current session
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-003)
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);

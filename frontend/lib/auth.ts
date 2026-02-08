/**
 * Better Auth Server Configuration
 *
 * Server-side Better Auth instance with PostgreSQL database for user management.
 * This configuration handles:
 * - User registration and authentication
 * - JWT token generation with 7-day expiry
 * - Session management with httpOnly cookies
 * - Server Actions cookie handling via nextCookies plugin
 *
 * Better Auth will:
 * 1. Store users in PostgreSQL database (same as backend, different tables)
 * 2. Issue JWT tokens with user_id in "sub" claim
 * 3. Store JWT in httpOnly cookie named "session"
 * 4. Backend validates JWT and extracts user_id from "sub" claim
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-003, FR-004, FR-025)
 */

import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Validate required environment variables
if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error(
    "BETTER_AUTH_SECRET environment variable is required. " +
    "Generate one with: openssl rand -base64 32"
  );
}

if (!process.env.DATABASE_URL) {
  throw new Error(
    "DATABASE_URL environment variable is required. " +
    "Configure PostgreSQL connection string."
  );
}

export const auth = betterAuth({
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  secret: process.env.BETTER_AUTH_SECRET,

  // Database configuration - PostgreSQL connection pool
  // Better Auth requires a pg Pool instance, not a config object
  // Optimized for Neon serverless with extended timeouts
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
    connectionTimeoutMillis: 20000, // 20 seconds (Neon wake-up time)
    idleTimeoutMillis: 30000, // 30 seconds idle before closing
    max: 3, // Small pool size for serverless
    min: 0, // Scale to zero when idle
    keepAlive: true, // Keep connections alive
    keepAliveInitialDelayMillis: 10000,
  }),

  // Enable email/password authentication
  emailAndPassword: {
    enabled: true,
    autoSignIn: true, // Auto sign in after successful signup
  },

  // Session configuration (JWT stored in httpOnly cookie)
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days (spec requirement)
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    // Disable cookie cache to avoid extra session_data cookie
    cookieCache: {
      enabled: false,
    },
  },

  // Advanced configuration - custom cookie names and attributes
  advanced: {
    cookies: {
      // CRITICAL: Rename session_token cookie to "session" to match backend expectations
      session_token: {
        name: "session",
        attributes: {
          // Environment-aware cookie attributes:
          // - Development (HTTP): sameSite="lax" allows localhost cross-origin, secure=false for HTTP
          // - Production (HTTPS): sameSite="none" allows HTTPS cross-origin, secure=true required
          sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
          secure: process.env.NODE_ENV === "production",
        },
      },
    },
  },

  // Social providers disabled (out of scope per spec)
  socialProviders: {},

  // Plugins
  plugins: [
    jwt(), // Generate JWT tokens with sub claim (user_id)
    nextCookies(), // Enable cookie handling in Server Actions (MUST be last)
  ],
});

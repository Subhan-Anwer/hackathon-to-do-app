/**
 * Next.js Middleware for Protected Routes
 *
 * Handles authentication checks and redirects based on session state.
 * Runs on all routes except static files and API routes.
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-006, FR-007)
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";

const JWT_SECRET = new TextEncoder().encode(
  process.env.BETTER_AUTH_SECRET || "fallback-secret"
);
const COOKIE_NAME = "session";

/**
 * Check if user has valid session
 */
async function hasValidSession(request: NextRequest): Promise<boolean> {
  const token = request.cookies.get(COOKIE_NAME)?.value;

  if (!token) {
    return false;
  }

  try {
    await jwtVerify(token, JWT_SECRET);
    return true;
  } catch {
    return false;
  }
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isAuthenticated = await hasValidSession(request);

  // Public routes (accessible without auth)
  const publicRoutes = ["/login", "/signup"];
  const isPublicRoute = publicRoutes.includes(pathname);

  // Protected routes (require auth)
  const protectedRoutes = ["/tasks"];
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );

  // Redirect unauthenticated users from protected routes to login
  if (isProtectedRoute && !isAuthenticated) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirect authenticated users from auth pages to tasks
  if (isPublicRoute && isAuthenticated) {
    return NextResponse.redirect(new URL("/tasks", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)",
  ],
};

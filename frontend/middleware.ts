/**
 * Next.js Middleware - DISABLED
 *
 * Authentication is handled by server components (app/page.tsx, app/tasks/page.tsx)
 * using Better Auth's getSession(). Middleware is not needed and was causing
 * redirect loops due to cookie name mismatches.
 *
 * Better Auth uses its own cookie management with the nextCookies() plugin.
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function middleware(_request: NextRequest) {
  // Let all requests through - auth is handled by server components
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
     * - api routes (Better Auth uses /api/auth/*)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)",
  ],
};

/**
 * Root Page - Redirect Logic
 *
 * Server component that redirects based on authentication status:
 * - Authenticated users → /tasks (dashboard)
 * - Unauthenticated users → /login
 *
 * This ensures users always land on the appropriate page.
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 1, Scenarios 1 & 7)
 */

import { redirect } from "next/navigation";
import { getSession } from "@/lib/simple-auth";

export default async function HomePage() {
  const session = await getSession();

  if (session) {
    // User is authenticated, redirect to tasks dashboard
    redirect("/tasks");
  } else {
    // User is not authenticated, redirect to login
    redirect("/login");
  }
}

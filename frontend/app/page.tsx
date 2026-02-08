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



import Link from "next/link";

export default async function HomePage() {
  <main style={{ padding: "2rem", textAlign: "center" }}>
    <h1>Hackathon II Todo App</h1>
    <p>Welcome! Go to the tasks page:</p>
    <Link href="/tasks">
      <button style={{ padding: "1rem 2rem", fontSize: "1.2rem" }}>
        View Tasks →
      </button>
    </Link>
  </main>;
}

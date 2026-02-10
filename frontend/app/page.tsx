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

// import { redirect } from "next/navigation";
// import { getSession } from "@/lib/auth-actions";

// export default async function HomePage() {
//   const session = await getSession();

//   if (session) {
//     // User is authenticated, redirect to tasks dashboard
//     redirect("/tasks");
//   } else {
//     // User is not authenticated, redirect to login
//     redirect("/login");
//   }
// }

// frontend/app/page.tsx
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-50 dark:bg-gray-900">
      <h1 className="text-4xl md:text-5xl font-bold mb-6 text-center">
        Hackathon Todo App
      </h1>
      <p className="text-lg mb-8 text-center max-w-md">
        Multi-user Todo application — built with Next.js, FastAPI, Neon, and
        Better Auth
      </p>

      <div className="flex gap-4 flex-wrap justify-center">
        <Link href="/tasks">
          <button className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Go to Tasks
          </button>
        </Link>
        <Link href="/login">
          <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Login
          </button>
        </Link>
      </div>
    </div>
  );
}
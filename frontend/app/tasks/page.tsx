/**
 * Tasks Dashboard Page
 *
 * Protected route for authenticated users to manage their tasks.
 * Server component that verifies session and fetches tasks from backend.
 *
 * Features:
 * - Session verification (redirect to /login if not authenticated)
 * - Header with logout button
 * - Task list display with data from backend API
 * - Empty state for users with no tasks
 * - Loading states with Suspense
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 2)
 */

import { Suspense } from "react";
import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth-actions";
import { taskApi } from "@/lib/api";
import { Header } from "@/components/layout/header";
import { TaskListSkeleton } from "@/components/tasks/task-list-skeleton";
import { TasksPageClient } from "@/components/tasks/tasks-page-client";

async function TasksContent({ userId }: { userId: string }) {
  // Fetch tasks from backend API
  let tasks: Awaited<ReturnType<typeof taskApi.list>> = [];
  try {
    tasks = await taskApi.list(userId);
  } catch {
    // Failed to fetch tasks - return empty array to show empty state
    tasks = [];
  }

  // Use client wrapper that handles both empty and populated states
  return <TasksPageClient initialTasks={tasks} userId={userId} />;
}

export default async function TasksPage() {
  // Verify user is authenticated
  const session = await getSession();

  if (!session) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header with logout button */}
      <Header />

      {/* Main content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <Suspense fallback={<TaskListSkeleton />}>
          <TasksContent userId={session.userId} />
        </Suspense>
      </main>
    </div>
  );
}

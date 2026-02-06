/**
 * Empty State Component
 *
 * Displays a friendly message when the user has no tasks.
 * Server component that encourages users to create their first task.
 *
 * Features:
 * - Centered layout
 * - Clear call-to-action message
 * - Icon illustration
 * - Helpful text
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-029, User Story 2 Scenario 4)
 */

import { Card, CardContent } from "@/components/ui/card";

export function EmptyState() {
  return (
    <Card className="border-dashed border-2">
      <CardContent className="flex flex-col items-center justify-center py-16 px-4">
        <div className="w-16 h-16 mb-6 rounded-full bg-slate-100 flex items-center justify-center">
          <svg
            className="w-8 h-8 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
            />
          </svg>
        </div>

        <h3 className="text-xl font-semibold text-slate-900 mb-2">
          No tasks yet
        </h3>

        <p className="text-slate-600 text-center max-w-sm mb-6">
          Get started by creating your first task. Stay organized and track your progress!
        </p>

        <p className="text-sm text-slate-500">
          Click &quot;Add Task&quot; to begin
        </p>
      </CardContent>
    </Card>
  );
}

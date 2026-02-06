/**
 * Task Skeleton Component
 *
 * Loading placeholder for task items using shadcn/ui Skeleton.
 * Displays while tasks are being fetched from the API.
 *
 * Features:
 * - Mimics task card layout
 * - Animated shimmer effect
 * - Proper spacing and sizing
 * - Multiple skeletons for list view
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-014, SC-003)
 */

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function TaskSkeleton() {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Checkbox skeleton */}
          <Skeleton className="h-5 w-5 rounded mt-1" />

          {/* Content skeleton */}
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-full" />
          </div>

          {/* Action buttons skeleton */}
          <div className="flex gap-2">
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-16" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Task List Skeleton
 *
 * Displays multiple task skeletons for the initial loading state.
 */
export function TaskListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <TaskSkeleton key={i} />
      ))}
    </div>
  );
}

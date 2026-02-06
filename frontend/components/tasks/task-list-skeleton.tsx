/**
 * Task List Skeleton Component
 *
 * Loading skeleton for the task list page.
 * Displays placeholder cards while tasks are being fetched.
 *
 * Features:
 * - Shimmer animation effect
 * - Matches actual task card layout
 * - Accessible loading state
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-026)
 */

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function TaskListSkeleton() {
  return (
    <div className="space-y-4">
      {/* Header skeleton */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1">
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-4 w-48" />
        </div>
        <Skeleton className="h-10 w-32" />
      </div>

      {/* Task card skeletons */}
      <div className="space-y-3">
        {[...Array(3)].map((_, index) => (
          <Card key={index} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                {/* Checkbox skeleton */}
                <Skeleton className="h-5 w-5 rounded mt-1" />

                {/* Content skeleton */}
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-3 w-32" />
                </div>

                {/* Button skeletons */}
                <div className="flex gap-2">
                  <Skeleton className="h-9 w-20" />
                  <Skeleton className="h-9 w-20" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

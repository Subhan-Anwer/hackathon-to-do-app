/**
 * Task Item Component
 *
 * Displays a single task with completion checkbox and action buttons.
 * Client component for interactive elements (checkbox, buttons).
 *
 * Features:
 * - Checkbox for completion status with optimistic UI updates
 * - Line-through styling for completed tasks
 * - Edit dialog integration (Phase 7)
 * - Delete button (Phase 8)
 * - Responsive card layout
 * - Accessible markup
 * - Error handling with revert and toast notifications
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 2, 4)
 */

"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { EditTaskDialog } from "./edit-task-dialog";
import { DeleteTaskDialog } from "./delete-task-dialog";
import { toggleComplete } from "@/app/actions/tasks";
import { toast } from "sonner";
import type { Task } from "@/types/task";

interface TaskItemProps {
  task: Task;
  userId: string;
  onUpdate?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

export function TaskItem({ task, userId, onUpdate, onDelete }: TaskItemProps) {
  const [localTask, setLocalTask] = useState(task);
  const [isToggling, setIsToggling] = useState(false);

  /**
   * Handle task completion toggle with optimistic UI update
   * Updates UI immediately, then calls Server Action
   * Reverts on error with toast notification
   * Reference: spec.md (User Story 4 Scenario 2, FR-018)
   */
  const handleToggleComplete = async () => {
    if (isToggling) return; // Prevent double-clicks

    const previousState = localTask.completed;
    const optimisticTask = { ...localTask, completed: !previousState };

    // Optimistic update - immediate UI feedback
    setLocalTask(optimisticTask);
    setIsToggling(true);

    try {
      const updatedTask = await toggleComplete(userId, task.id);

      // Update parent state with server response
      if (onUpdate) {
        onUpdate(updatedTask);
      }

      // Update local state with server response
      setLocalTask(updatedTask);

      // Success feedback
      toast.success(
        updatedTask.completed
          ? "Task marked as complete"
          : "Task marked as incomplete"
      );
    } catch (error) {
      // Revert on error
      setLocalTask({ ...localTask, completed: previousState });

      toast.error(
        error instanceof Error
          ? error.message
          : "Failed to update task. Please try again."
      );
    } finally {
      setIsToggling(false);
    }
  };

  /**
   * Handle task update from edit dialog
   * Reference: spec.md (User Story 4 Scenario 1)
   */
  const handleTaskUpdated = (updatedTask: Task) => {
    setLocalTask(updatedTask);
    if (onUpdate) {
      onUpdate(updatedTask);
    }
  };

  /**
   * Handle task deletion from delete dialog
   * Reference: spec.md (User Story 5 Scenario 1)
   */
  const handleTaskDeleted = (taskId: string) => {
    if (onDelete) {
      onDelete(taskId);
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Completion checkbox */}
          <Checkbox
            checked={localTask.completed}
            onCheckedChange={handleToggleComplete}
            disabled={isToggling}
            className="mt-1"
            aria-label={`Mark "${localTask.title}" as ${localTask.completed ? "incomplete" : "complete"}`}
          />

          {/* Task content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`font-medium text-slate-900 break-words ${
                localTask.completed ? "line-through text-slate-500" : ""
              }`}
            >
              {localTask.title}
            </h3>

            {localTask.description && (
              <p
                className={`text-sm mt-1 break-words ${
                  localTask.completed ? "text-slate-400" : "text-slate-600"
                }`}
              >
                {localTask.description}
              </p>
            )}

            {/* Metadata */}
            <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
              <span>
                Created: {new Date(localTask.created_at).toLocaleDateString()}
              </span>
              {localTask.updated_at !== localTask.created_at && (
                <span>
                  Updated: {new Date(localTask.updated_at).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2 flex-shrink-0">
            <EditTaskDialog
              task={localTask}
              userId={userId}
              onTaskUpdated={handleTaskUpdated}
            />
            <DeleteTaskDialog
              taskId={localTask.id}
              taskTitle={localTask.title}
              userId={userId}
              onTaskDeleted={handleTaskDeleted}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

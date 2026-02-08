/**
 * Delete Task Dialog Component
 *
 * Confirmation dialog for task deletion to prevent accidental deletions.
 * Uses shadcn/ui AlertDialog for destructive action confirmation.
 *
 * Features:
 * - Delete button trigger
 * - Confirmation dialog with warning text
 * - Cancel and Confirm actions
 * - Loading state during deletion
 * - Toast notifications for success/error
 * - Callback to parent on successful deletion
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 5 Scenario 1)
 */

"use client";

import { useState } from "react";
import { Trash2 } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { deleteTask } from "@/app/actions/tasks";
import { toast } from "sonner";

interface DeleteTaskDialogProps {
  taskId: string;
  taskTitle: string;
  userId: string;
  onTaskDeleted: (taskId: string) => void;
}

export function DeleteTaskDialog({
  taskId,
  taskTitle,
  userId,
  onTaskDeleted,
}: DeleteTaskDialogProps) {
  const [open, setOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);

    try {
      await deleteTask(userId, taskId);

      // Update parent state
      onTaskDeleted(taskId);

      // Close dialog
      setOpen(false);

      // Success feedback
      toast.success("Task deleted successfully");
    } catch (error) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Failed to delete task. Please try again."
      );
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <Trash2 className="h-4 w-4 mr-1.5" />
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Task</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete &ldquo;{taskTitle}&rdquo;? This action cannot be
            undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.preventDefault();
              handleDelete();
            }}
            disabled={isDeleting}
            className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

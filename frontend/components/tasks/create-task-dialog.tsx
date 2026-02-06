/**
 * Create Task Dialog Component
 *
 * Modal dialog for creating new tasks.
 * Uses shadcn/ui Dialog component with TaskForm.
 *
 * Features:
 * - Modal overlay with backdrop
 * - "Add Task" trigger button
 * - Contains TaskForm component
 * - Auto-closes on successful creation
 * - Keyboard accessible (Escape to close)
 * - Focus management
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 3, Scenario 1)
 */

"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { TaskForm } from "./task-form";
import type { Task } from "@/types/task";

interface CreateTaskDialogProps {
  userId: string;
  onTaskCreated: (task: Task) => void;
}

export function CreateTaskDialog({ userId, onTaskCreated }: CreateTaskDialogProps) {
  const [open, setOpen] = useState(false);

  const handleSuccess = (task: Task) => {
    onTaskCreated(task);
    setOpen(false);
  };

  const handleCancel = () => {
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="lg" className="gap-2">
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add Task
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
          <DialogDescription>
            Add a new task to your list. Fill in the details below.
          </DialogDescription>
        </DialogHeader>

        <TaskForm
          userId={userId}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      </DialogContent>
    </Dialog>
  );
}

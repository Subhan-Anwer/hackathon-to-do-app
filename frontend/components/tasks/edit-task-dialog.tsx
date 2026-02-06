/**
 * Edit Task Dialog Component
 *
 * Modal dialog for editing existing tasks. Reuses TaskForm component
 * with the task prop to populate initial values.
 *
 * Features:
 * - Edit button trigger with pencil icon
 * - shadcn/ui Dialog component
 * - Reuses TaskForm in edit mode
 * - Auto-closes on successful update
 * - Callback to parent on task update
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 4 Scenario 1)
 */

"use client";

import { useState } from "react";
import { Pencil } from "lucide-react";
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

interface EditTaskDialogProps {
  task: Task;
  userId: string;
  onTaskUpdated: (task: Task) => void;
}

export function EditTaskDialog({
  task,
  userId,
  onTaskUpdated,
}: EditTaskDialogProps) {
  const [open, setOpen] = useState(false);

  const handleSuccess = (updatedTask: Task) => {
    onTaskUpdated(updatedTask);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="text-slate-700 hover:text-slate-900"
        >
          <Pencil className="h-4 w-4 mr-1.5" />
          Edit
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Edit Task</DialogTitle>
          <DialogDescription>
            Update the task title and description. Click save when you're done.
          </DialogDescription>
        </DialogHeader>

        <TaskForm task={task} userId={userId} onSuccess={handleSuccess} />
      </DialogContent>
    </Dialog>
  );
}

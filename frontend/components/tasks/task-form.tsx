/**
 * Task Form Component
 *
 * Reusable form for creating and editing tasks.
 * Uses react-hook-form with zod validation for client-side validation.
 *
 * Features:
 * - Title input (required, 1-200 characters)
 * - Description textarea (optional, max 1000 characters)
 * - Client-side validation before API call
 * - Loading state during submission
 * - Error handling with toast notifications
 * - Accessible form markup
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-010, FR-020, FR-026)
 */

"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { taskApi } from "@/lib/api";
import type { Task, TaskCreateInput, TaskUpdateInput } from "@/types/task";

// Validation schema matching backend requirements
const taskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less"),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional()
    .or(z.literal("")),
});

type TaskFormValues = z.infer<typeof taskSchema>;

interface TaskFormProps {
  userId: string;
  task?: Task;
  onSuccess: (task: Task) => void;
  onCancel?: () => void;
}

export function TaskForm({ userId, task, onSuccess, onCancel }: TaskFormProps) {
  const [loading, setLoading] = useState(false);
  const isEditing = !!task;

  const form = useForm<TaskFormValues>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: task?.title || "",
      description: task?.description || "",
    },
  });

  const onSubmit = async (data: TaskFormValues) => {
    setLoading(true);

    try {
      let result: Task;

      if (isEditing) {
        // Update existing task
        const updateData: TaskUpdateInput = {
          title: data.title,
          description: data.description || undefined,
        };
        result = await taskApi.update(userId, task.id, updateData);
        toast.success("Task updated successfully!");
      } else {
        // Create new task
        const createData: TaskCreateInput = {
          title: data.title,
          description: data.description || undefined,
        };
        result = await taskApi.create(userId, createData);
        toast.success("Task created successfully!");
      }

      onSuccess(result);
      form.reset();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to save task";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Title field */}
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Title <span className="text-red-500">*</span>
              </FormLabel>
              <FormControl>
                <Input
                  placeholder="Enter task title"
                  {...field}
                  disabled={loading}
                  autoFocus
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Description field */}
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description (Optional)</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Add more details about this task..."
                  className="resize-none"
                  rows={4}
                  {...field}
                  disabled={loading}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Form actions */}
        <div className="flex gap-3 justify-end pt-2">
          {onCancel && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </Button>
          )}
          <Button type="submit" disabled={loading}>
            {loading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                {isEditing ? "Updating..." : "Creating..."}
              </>
            ) : (
              <>{isEditing ? "Update Task" : "Create Task"}</>
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
}

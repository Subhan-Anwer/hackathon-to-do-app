/**
 * Task List Component
 *
 * Client component that manages task list state and displays tasks.
 * Receives initial tasks from server component and handles client-side updates.
 *
 * Features:
 * - Displays list of tasks
 * - State management for task updates
 * - Task creation dialog (Phase 6)
 * - Callback props for CRUD operations
 * - Responsive grid layout
 * - Empty state handling
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 2 Scenario 1, User Story 3)
 */

"use client";

import { useState } from "react";
import { TaskItem } from "./task-item";
import { CreateTaskDialog } from "./create-task-dialog";
import type { Task } from "@/types/task";

interface TaskListProps {
  initialTasks: Task[];
  userId: string;
}

export function TaskList({ initialTasks, userId }: TaskListProps) {
  const [tasks, setTasks] = useState(initialTasks);

  // Handler for new task creation (Phase 6)
  const handleTaskCreate = (newTask: Task) => {
    setTasks((prevTasks) => [newTask, ...prevTasks]);
  };

  // Handler for task updates (will be used in Phase 7)
  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === updatedTask.id ? updatedTask : task
      )
    );
  };

  // Handler for task deletion (will be used in Phase 8)
  const handleTaskDelete = (taskId: string) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  };

  return (
    <div className="space-y-4">
      {/* Header with task count and create button */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-slate-900">Your Tasks</h2>
          <p className="text-sm text-slate-600 mt-1">
            {tasks.length} {tasks.length === 1 ? "task" : "tasks"} total
            {tasks.filter((t) => t.completed).length > 0 &&
              ` • ${tasks.filter((t) => t.completed).length} completed`}
          </p>
        </div>

        {/* Create task dialog */}
        <CreateTaskDialog userId={userId} onTaskCreated={handleTaskCreate} />
      </div>

      {/* Task list */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            userId={userId}
            onUpdate={handleTaskUpdate}
            onDelete={handleTaskDelete}
          />
        ))}
      </div>
    </div>
  );
}

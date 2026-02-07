/**
 * Tasks Page Client Wrapper
 *
 * Client component that wraps task content and provides persistent Add Task button.
 * Ensures users can always create tasks, even when list is empty.
 */

"use client";

import { useState } from "react";
import { CreateTaskDialog } from "./create-task-dialog";
import { TaskItem } from "./task-item";
import { EmptyState } from "./empty-state";
import type { Task } from "@/types/task";

interface TasksPageClientProps {
  initialTasks: Task[];
  userId: string;
}

export function TasksPageClient({ initialTasks, userId }: TasksPageClientProps) {
  const [tasks, setTasks] = useState(initialTasks);

  const handleTaskCreate = (newTask: Task) => {
    setTasks((prevTasks) => [newTask, ...prevTasks]);
  };

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === updatedTask.id ? updatedTask : task
      )
    );
  };

  const handleTaskDelete = (taskId: string) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  };

  return (
    <div className="space-y-6">
      {/* Header with task count and persistent Add Task button */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-slate-900">Your Tasks</h2>
          <p className="text-sm text-slate-600 mt-1">
            {tasks.length === 0 ? (
              "No tasks yet. Get started by creating one!"
            ) : (
              <>
                {tasks.length} {tasks.length === 1 ? "task" : "tasks"} total
                {tasks.filter((t) => t.completed).length > 0 &&
                  ` • ${tasks.filter((t) => t.completed).length} completed`}
              </>
            )}
          </p>
        </div>

        {/* Persistent Create Task button - always visible */}
        <CreateTaskDialog userId={userId} onTaskCreated={handleTaskCreate} />
      </div>

      {/* Content area - empty state or task list */}
      {tasks.length === 0 ? (
        <EmptyState />
      ) : (
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
      )}
    </div>
  );
}

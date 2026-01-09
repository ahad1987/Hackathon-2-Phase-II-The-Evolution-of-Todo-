'use client';

import React, { useState } from 'react';
import { taskApi } from '@/lib/api-client';

interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface TaskItemProps {
  task: Task;
  onDeleted?: (taskId: string) => void;
  onUpdated?: (task: Task) => void;
}

export default function TaskItem({ task, onDeleted, onUpdated }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(task.title);
  const [editedDescription, setEditedDescription] = useState(task.description || '');
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggleCompletion = async () => {
    try {
      setIsToggling(true);
      setError(null);
      const updatedTask = await taskApi.updateTask(task.id, {
        completed: !task.completed,
      });
      if (onUpdated) {
        onUpdated(updatedTask);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setIsToggling(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editedTitle.trim()) {
      setError('Task title cannot be empty');
      return;
    }

    try {
      setError(null);
      const updatedTask = await taskApi.updateTask(task.id, {
        title: editedTitle.trim(),
        description: editedDescription.trim() || null,
      });
      if (onUpdated) {
        onUpdated(updatedTask);
      }
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      setIsDeleting(true);
      setError(null);
      await taskApi.deleteTask(task.id);
      if (onDeleted) {
        onDeleted(task.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      setIsDeleting(false);
    }
  };

  const handleCancel = () => {
    setEditedTitle(task.title);
    setEditedDescription(task.description || '');
    setIsEditing(false);
    setError(null);
  };

  if (isEditing) {
    return (
      <div className="card p-6 border-l-4 border-l-blue-600 shadow-sm">
        <div className="space-y-5">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-red-700 text-sm font-medium">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-2">
              Title
            </label>
            <input
              type="text"
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              className="input-field"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-2">
              Description
            </label>
            <textarea
              value={editedDescription}
              onChange={(e) => setEditedDescription(e.target.value)}
              rows={3}
              className="input-field resize-none"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button
              onClick={handleSaveEdit}
              className="btn-primary font-semibold py-2.5"
            >
              Save Changes
            </button>
            <button
              onClick={handleCancel}
              className="btn-secondary font-semibold py-2.5"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`card p-6 border-l-4 transition-all shadow-sm ${
        task.completed
          ? 'border-l-green-500 bg-gradient-to-r from-green-50/50 to-white'
          : 'border-l-blue-500 hover:shadow-md'
      }`}
    >
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-red-700 text-sm font-medium mb-4">
          {error}
        </div>
      )}

      <div className="flex flex-col gap-4">
        {/* Task content */}
        <div className="flex items-start gap-4">
          {/* Checkbox */}
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggleCompletion}
            disabled={isToggling}
            className="mt-1 w-5 h-5 rounded border-slate-300 text-blue-600 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 accent-blue-600"
            title={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
          />

          {/* Task text */}
          <div className="flex-1 min-w-0">
            <h3
              className={`text-lg font-semibold ${
                task.completed
                  ? 'text-slate-500 line-through'
                  : 'text-slate-900'
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p
                className={`mt-2 text-sm ${
                  task.completed
                    ? 'text-slate-400 line-through'
                    : 'text-slate-600'
                }`}
              >
                {task.description}
              </p>
            )}
            <p className="mt-3 text-xs text-slate-500">
              Created {new Date(task.created_at).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              })} at {new Date(task.created_at).toLocaleTimeString(undefined, {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2 flex-wrap pt-2">
          <button
            onClick={handleToggleCompletion}
            disabled={isToggling}
            className={`px-3 py-2 text-sm font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed ${
              task.completed
                ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200'
            }`}
          >
            {isToggling ? 'Updating...' : task.completed ? 'Mark Incomplete' : 'Mark Complete'}
          </button>
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-2 text-sm font-semibold bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="px-3 py-2 text-sm font-semibold bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}

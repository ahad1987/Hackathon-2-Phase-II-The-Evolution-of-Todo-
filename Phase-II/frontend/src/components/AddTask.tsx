'use client';

import React, { useState } from 'react';
import { taskApi } from '@/lib/api-client';

interface AddTaskProps {
  onTaskCreated?: () => void;
}

export default function AddTask({ onTaskCreated }: AddTaskProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Task title cannot be empty');
      return;
    }

    try {
      setError(null);
      setIsLoading(true);

      await taskApi.createTask({
        title: title.trim(),
        description: description.trim() || undefined,
      });

      // Reset form
      setTitle('');
      setDescription('');
      setIsOpen(false);

      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setTitle('');
    setDescription('');
    setError(null);
    setIsOpen(false);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="btn-primary flex items-center gap-2 text-base font-semibold py-3 px-6"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Create New Task
      </button>
    );
  }

  return (
    <div className="card p-6 sm:p-8 border-l-4 border-l-blue-600 mb-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-900">Create a new task</h3>
        <button
          onClick={handleCancel}
          disabled={isLoading}
          className="text-slate-500 hover:text-slate-700 disabled:opacity-50"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {error && (
        <div className="mb-5 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-red-700 text-sm font-medium">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Task Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-semibold text-slate-900 mb-2">
            Task Title <span className="text-red-500">*</span>
          </label>
          <input
            id="title"
            type="text"
            maxLength={255}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What do you need to accomplish?"
            disabled={isLoading}
            className="input-field"
            autoFocus
          />
          <p className="mt-1 text-xs text-slate-500">
            {title.length}/255 characters
          </p>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-semibold text-slate-900 mb-2">
            Description <span className="text-slate-400 font-normal">(Optional)</span>
          </label>
          <textarea
            id="description"
            maxLength={5000}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add details about your task..."
            rows={4}
            disabled={isLoading}
            className="input-field resize-none"
          />
          <p className="mt-1 text-xs text-slate-500">
            {description.length}/5000 characters
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={isLoading || !title.trim()}
            className="btn-primary font-semibold py-2.5"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                Creating...
              </span>
            ) : (
              'Create Task'
            )}
          </button>
          <button
            type="button"
            onClick={handleCancel}
            disabled={isLoading}
            className="btn-secondary font-semibold py-2.5"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

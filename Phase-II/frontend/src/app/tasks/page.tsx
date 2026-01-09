'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import AddTask from '@/components/AddTask';
import TaskList from '@/components/TaskList';

interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export default function TasksPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [mounted, setMounted] = useState(false);
  const [taskStats, setTaskStats] = useState({ total: 0, completed: 0, pending: 0 });
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !isLoading && !isAuthenticated) {
      router.push('/login?redirect=/tasks');
    }
  }, [isAuthenticated, isLoading, mounted, router]);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const handleTasksLoaded = (loadedTasks: Task[]) => {
    updateTaskStats(loadedTasks);
  };

  const updateTaskStats = (taskList: Task[]) => {
    const completed = taskList.filter(t => t.completed).length;
    const pending = taskList.filter(t => !t.completed).length;
    setTaskStats({
      total: taskList.length,
      completed,
      pending,
    });
  };

  const handleTaskCreated = () => {
    setRefreshKey(prev => prev + 1);
  };

  if (!mounted || isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h1 className="text-2xl font-semibold text-slate-900 mb-2">Loading</h1>
          <p className="text-slate-600">Getting your tasks ready...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-slate-900 mb-2">Redirecting...</h1>
          <p className="text-slate-600">Please log in to continue.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left side - Logo and Title */}
            <div className="flex items-center gap-4">
              <Link href="/" className="flex items-center gap-2 hover:opacity-75 transition">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">✓</span>
                </div>
                <span className="text-lg font-bold text-slate-900 hidden sm:inline">TaskFlow</span>
              </Link>
              <span className="text-sm text-slate-600 hidden md:inline">Manage your productivity</span>
            </div>

            {/* Right side - User info and logout */}
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-slate-900">{user?.email}</p>
                <p className="text-xs text-slate-500">Your workspace</p>
              </div>
              <button
                onClick={handleLogout}
                className="btn-danger text-sm py-2"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">Your Tasks</h1>
          <p className="text-slate-600">Organize, prioritize, and accomplish your goals</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {/* Total Tasks */}
          <div className="card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 mb-1">Total Tasks</p>
                <div className="text-4xl font-bold text-slate-900">{taskStats.total}</div>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </div>

          {/* Completed Tasks */}
          <div className="card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 mb-1">Completed</p>
                <div className="text-4xl font-bold text-green-600">{taskStats.completed}</div>
                {taskStats.total > 0 && (
                  <p className="text-xs text-slate-500 mt-1">{Math.round((taskStats.completed / taskStats.total) * 100)}% done</p>
                )}
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Pending Tasks */}
          <div className="card p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 mb-1">Pending</p>
                <div className="text-4xl font-bold text-amber-600">{taskStats.pending}</div>
                {taskStats.total > 0 && (
                  <p className="text-xs text-slate-500 mt-1">{Math.round((taskStats.pending / taskStats.total) * 100)}% remaining</p>
                )}
              </div>
              <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Add Task Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-900">Tasks</h2>
          </div>
          <AddTask onTaskCreated={handleTaskCreated} />
        </div>

        {/* Task List */}
        <div className="card p-6 sm:p-8 shadow-sm">
          <TaskList key={refreshKey} onTasksLoaded={handleTasksLoaded} />
        </div>
      </main>
    </div>
  );
}

/**
 * Login page for user authentication.
 */

import type { Metadata, Viewport } from 'next';
import React, { Suspense } from 'react';
import Link from 'next/link';
import LoginForm from '@/components/LoginForm';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Sign In - TaskFlow',
  description: 'Sign in to your TaskFlow account to manage your tasks',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Logo/Brand */}
      <div className="mb-8">
        <Link href="/" className="flex items-center justify-center gap-2 mb-8">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">✓</span>
          </div>
          <span className="text-xl font-bold text-slate-900">TaskFlow</span>
        </Link>
      </div>

      <div className="max-w-md w-full mx-auto">
        <div className="card p-8 sm:p-10 shadow-sm">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">Welcome back</h1>
            <p className="text-slate-600">Sign in to your account to continue managing your tasks</p>
          </div>

          {/* Form */}
          <Suspense fallback={
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          }>
            <LoginForm />
          </Suspense>

          {/* Divider */}
          <div className="mt-6 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-slate-500">Don't have an account?</span>
            </div>
          </div>

          {/* Signup Link */}
          <Link
            href="/signup"
            className="mt-6 block text-center px-4 py-2.5 border-2 border-blue-600 text-blue-600 font-medium rounded-lg hover:bg-blue-50 transition-colors"
          >
            Create a new account
          </Link>
        </div>

        {/* Footer Text */}
        <p className="mt-6 text-center text-sm text-slate-600">
          By signing in, you agree to our Terms of Service
        </p>
      </div>
    </div>
  );
}

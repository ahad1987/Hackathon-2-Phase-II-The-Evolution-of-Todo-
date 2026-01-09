/**
 * SignupForm component for user registration.
 * Handles email/password input, validation, and signup submission.
 */

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-context';

interface SignupFormProps {
  onSuccess?: () => void;
}

export default function SignupForm({ onSuccess }: SignupFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { signup, error: authError, isLoading: authIsLoading } = useAuth();

  /**
   * Validate form input.
   */
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Invalid email format';
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Confirm password validation
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Confirm password is required';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission.
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Clear previous errors and submit
    setErrors({});
    await signup(email, password);

    // Auth context will handle the redirect and error display
    if (onSuccess) {
      onSuccess();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 w-full">
      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-semibold text-slate-900 mb-2">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (errors.email) {
              setErrors({ ...errors, email: '' });
            }
          }}
          placeholder="you@example.com"
          className="input-field"
          disabled={authIsLoading}
        />
        {errors.email && (
          <p className="text-red-600 text-sm mt-2 font-medium">{errors.email}</p>
        )}
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-semibold text-slate-900 mb-2">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (errors.password) {
              setErrors({ ...errors, password: '' });
            }
          }}
          placeholder="Minimum 8 characters"
          className="input-field"
          disabled={authIsLoading}
        />
        {errors.password && (
          <p className="text-red-600 text-sm mt-2 font-medium">{errors.password}</p>
        )}
      </div>

      {/* Confirm Password Field */}
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-semibold text-slate-900 mb-2">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
            if (errors.confirmPassword) {
              setErrors({ ...errors, confirmPassword: '' });
            }
          }}
          placeholder="Confirm your password"
          className="input-field"
          disabled={authIsLoading}
        />
        {errors.confirmPassword && (
          <p className="text-red-600 text-sm mt-2 font-medium">{errors.confirmPassword}</p>
        )}
      </div>

      {/* Error Message */}
      {(errors.submit || authError) && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm font-medium">
          {errors.submit || authError}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={authIsLoading}
        className="btn-primary w-full text-base font-semibold py-3"
      >
        {authIsLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
            Creating account...
          </span>
        ) : (
          'Create Account'
        )}
      </button>
    </form>
  );
}

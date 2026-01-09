/**
 * Next.js Middleware for protecting routes.
 * Redirects unauthenticated users to login page.
 */

import { NextRequest, NextResponse } from 'next/server';

// Routes that don't require authentication
const publicRoutes = ['/login', '/signup', '/'];

// Routes that require authentication
const protectedRoutes = ['/tasks', '/dashboard'];

/**
 * Middleware function to check authentication.
 */
export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Check if route is protected
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname === route || pathname.startsWith(route + '/')
  );

  // Check if route is public
  const isPublicRoute = publicRoutes.includes(pathname);

  // Get token from cookies
  const token = request.cookies.get('better-auth.token')?.value ||
                request.cookies.get('auth_token')?.value ||
                request.cookies.get('token')?.value;

  // If protected route and no token, redirect to login
  if (isProtectedRoute && !token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If public route and has token, could redirect to tasks
  // but allowing users to access login/signup even when authenticated is fine
  if (isPublicRoute && pathname === '/' && token) {
    return NextResponse.redirect(new URL('/tasks', request.url));
  }

  return NextResponse.next();
}

/**
 * Configure which routes the middleware runs on.
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

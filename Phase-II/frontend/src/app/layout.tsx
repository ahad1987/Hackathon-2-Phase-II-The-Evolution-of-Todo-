/**
 * Root layout for the Next.js application.
 * Provides AuthProvider and global styling.
 */

import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/lib/auth-context';
import '@/styles/globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'TaskFlow - Manage Your Productivity',
  description: 'A modern, secure task management app to stay organized and productive',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-slate-50">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}

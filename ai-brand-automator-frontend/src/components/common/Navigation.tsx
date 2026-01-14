'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useState, useSyncExternalStore } from 'react';

// External store for localStorage token
function subscribeToToken(callback: () => void) {
  window.addEventListener('storage', callback);
  return () => window.removeEventListener('storage', callback);
}

function getTokenSnapshot() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

function getServerSnapshot() {
  return null;
}

export function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const token = useSyncExternalStore(subscribeToToken, getTokenSnapshot, getServerSnapshot);
  const [, forceUpdate] = useState(0);
  
  // Derive login state from token
  const isLoggedIn = !!token;

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('company_id');
    forceUpdate(n => n + 1); // Trigger re-render after logout
    router.push('/auth/login');
  };

  // Don't show navigation on auth pages
  if (pathname?.startsWith('/auth/')) {
    return null;
  }

  return (
    <nav className="nav-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-heading font-bold text-brand-electric">AI Brand Automator</span>
            </Link>
            
            {isLoggedIn && (
              <div className="hidden sm:ml-10 sm:flex sm:space-x-8">
                <Link
                  href="/"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    pathname === '/'
                      ? 'border-brand-electric text-white'
                      : 'border-transparent text-brand-silver/70 hover:border-brand-ghost hover:text-white'
                  }`}
                >
                  Home
                </Link>
                <Link
                  href="/dashboard"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    pathname === '/dashboard'
                      ? 'border-brand-electric text-white'
                      : 'border-transparent text-brand-silver/70 hover:border-brand-ghost hover:text-white'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  href="/onboarding"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    pathname?.startsWith('/onboarding')
                      ? 'border-brand-electric text-white'
                      : 'border-transparent text-brand-silver/70 hover:border-brand-ghost hover:text-white'
                  }`}
                >
                  Onboarding
                </Link>
                <Link
                  href="/chat"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    pathname === '/chat'
                      ? 'border-brand-electric text-white'
                      : 'border-transparent text-brand-silver/70 hover:border-brand-ghost hover:text-white'
                  }`}
                >
                  Chat
                </Link>
                <Link
                  href="/files"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    pathname === '/files'
                      ? 'border-brand-electric text-white'
                      : 'border-transparent text-brand-silver/70 hover:border-brand-ghost hover:text-white'
                  }`}
                >
                  Files
                </Link>
                <Link
                  href="/automation"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    pathname === '/automation'
                      ? 'border-brand-electric text-white'
                      : 'border-transparent text-brand-silver/70 hover:border-brand-ghost hover:text-white'
                  }`}
                >
                  Automation
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center">
            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="btn-secondary text-sm"
              >
                Logout
              </button>
            ) : (
              <Link
                href="/auth/login"
                className="btn-primary text-sm"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

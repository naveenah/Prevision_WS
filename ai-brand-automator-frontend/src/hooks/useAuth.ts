'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Hook to protect routes that require authentication
 * Redirects to login page if no valid access token is found
 */
export function useAuth() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      // No token found, redirect to login
      router.push('/auth/login');
    }
    
    // Optional: Could add token expiration check here
    // For now, we rely on API responses (401) to handle expired tokens
  }, [router]);
}

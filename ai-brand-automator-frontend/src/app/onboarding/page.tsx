'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useEffect } from 'react';

export default function OnboardingPage() {
  useAuth(); // Protect this route
  const router = useRouter();
  
  useEffect(() => {
    // Redirect to first step
    router.push('/onboarding/step-1');
  }, [router]);
}
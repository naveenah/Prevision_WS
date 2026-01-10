import { redirect } from 'next/navigation';

export default function OnboardingPage() {
  // Redirect to first step
  redirect('/onboarding/step-1');
}
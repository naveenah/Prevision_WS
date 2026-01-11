'use client';

import { StepWizard } from '@/components/onboarding/StepWizard';
import { OnboardingReview } from '@/components/onboarding/OnboardingReview';
import { useAuth } from '@/hooks/useAuth';

export default function OnboardingStep5() {
  useAuth(); // Protect this route
  
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Review & Generate Brand Strategy
          </h1>
          <p className="text-gray-600 mb-8">
            Review your information and let AI create your brand strategy
          </p>

          <StepWizard currentStep={5} totalSteps={5} />

          <OnboardingReview />
        </div>
      </div>
    </div>
  );
}

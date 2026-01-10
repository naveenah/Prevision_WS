'use client';

import { StepWizard } from '@/components/onboarding/StepWizard';
import { BrandForm } from '@/components/onboarding/BrandForm';
import { useAuth } from '@/hooks/useAuth';

export default function OnboardingStep2() {
  useAuth(); // Protect this route
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <StepWizard currentStep={2} totalSteps={5} />
        <div className="mt-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Brand Details</h1>
          <p className="text-gray-600 mb-8">Define your brand voice and positioning.</p>
          <BrandForm />
        </div>
      </div>
    </div>
  );
}
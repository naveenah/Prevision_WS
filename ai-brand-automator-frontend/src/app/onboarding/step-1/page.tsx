'use client';

import { StepWizard } from '@/components/onboarding/StepWizard';
import { CompanyForm } from '@/components/onboarding/CompanyForm';
import { useAuth } from '@/hooks/useAuth';

export default function OnboardingStep1() {
  useAuth(); // Protect this route
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <StepWizard currentStep={1} totalSteps={5} />
        <div className="mt-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Company Information</h1>
          <p className="text-gray-600 mb-8">Tell us about your company to get started with your brand automation.</p>
          <CompanyForm />
        </div>
      </div>
    </div>
  );
}
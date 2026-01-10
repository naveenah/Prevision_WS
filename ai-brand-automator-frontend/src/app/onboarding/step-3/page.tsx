'use client';

import { StepWizard } from '@/components/onboarding/StepWizard';
import { TargetAudienceForm } from '@/components/onboarding/TargetAudienceForm';
import { useAuth } from '@/hooks/useAuth';

export default function OnboardingStep3() {
  useAuth(); // Protect this route
  
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Define Your Target Audience
          </h1>
          <p className="text-gray-600 mb-8">
            Help us understand who your brand is speaking to
          </p>

          <StepWizard currentStep={3} totalSteps={5} />

          <TargetAudienceForm />
        </div>
      </div>
    </div>
  );
}

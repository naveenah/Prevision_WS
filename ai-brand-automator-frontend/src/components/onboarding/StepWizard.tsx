'use client';

import Link from 'next/link';

interface StepWizardProps {
  currentStep: number;
  totalSteps: number;
}

const stepRoutes = [
  '/onboarding/step-1',
  '/onboarding/step-2',
  '/onboarding/step-3',
  '/onboarding/step-4',
  '/onboarding/step-5',
];

const stepLabels = [
  'Company Info',
  'Brand Details',
  'Target Audience',
  'Upload Assets',
  'Review',
];

export function StepWizard({ currentStep, totalSteps }: StepWizardProps) {
  const steps = Array.from({ length: totalSteps }, (_, i) => i + 1);

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step) => (
          <div key={step} className="flex items-center">
            <Link
              href={stepRoutes[step - 1]}
              className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium cursor-pointer transition-transform hover:scale-110 ${
                step < currentStep
                  ? 'bg-green-500 text-white hover:bg-green-600'
                  : step === currentStep
                  ? 'bg-indigo-500 text-white'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
              title={`Go to ${stepLabels[step - 1]}`}
            >
              {step < currentStep ? '✓' : step}
            </Link>
            {step < totalSteps && (
              <div
                className={`flex-1 h-1 mx-4 ${
                  step < currentStep ? 'bg-green-500' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>
      <div className="mt-4 flex justify-between text-sm">
        {stepLabels.map((label, idx) => (
          <Link
            key={label}
            href={stepRoutes[idx]}
            className={`hover:text-indigo-600 hover:underline cursor-pointer ${
              idx + 1 === currentStep ? 'text-indigo-600 font-medium' : 'text-gray-600'
            }`}
          >
            {label}
          </Link>
        ))}
      </div>
    </div>
  );
}
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
                  ? 'bg-brand-mint text-brand-midnight hover:bg-brand-mint/80'
                  : step === currentStep
                  ? 'bg-brand-electric text-brand-midnight'
                  : 'bg-white/10 text-brand-silver/70 hover:bg-white/20'
              }`}
              title={`Go to ${stepLabels[step - 1]}`}
            >
              {step < currentStep ? '✓' : step}
            </Link>
            {step < totalSteps && (
              <div
                className={`flex-1 h-1 mx-4 ${
                  step < currentStep ? 'bg-brand-mint' : 'bg-white/10'
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
            className={`hover:text-brand-electric hover:underline cursor-pointer ${
              idx + 1 === currentStep ? 'text-brand-electric font-medium' : 'text-brand-silver/70'
            }`}
          >
            {label}
          </Link>
        ))}
      </div>
    </div>
  );
}
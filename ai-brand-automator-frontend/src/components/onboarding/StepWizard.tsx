interface StepWizardProps {
  currentStep: number;
  totalSteps: number;
}

export function StepWizard({ currentStep, totalSteps }: StepWizardProps) {
  const steps = Array.from({ length: totalSteps }, (_, i) => i + 1);

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step) => (
          <div key={step} className="flex items-center">
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                step < currentStep
                  ? 'bg-green-500 text-white'
                  : step === currentStep
                  ? 'bg-indigo-500 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {step < currentStep ? '✓' : step}
            </div>
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
      <div className="mt-4 flex justify-between text-sm text-gray-600">
        <span>Company Info</span>
        <span>Brand Details</span>
        <span>Target Audience</span>
        <span>Upload Assets</span>
        <span>Review</span>
      </div>
    </div>
  );
}
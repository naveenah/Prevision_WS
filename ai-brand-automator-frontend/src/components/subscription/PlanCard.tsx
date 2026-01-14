'use client';

import { SubscriptionPlan } from '@/lib/api';

interface PlanCardProps {
  plan: SubscriptionPlan;
  isCurrentPlan?: boolean;
  onSelect: (plan: SubscriptionPlan) => void;
  isLoading?: boolean;
}

export function PlanCard({ plan, isCurrentPlan, onSelect, isLoading }: PlanCardProps) {
  const isPro = plan.name === 'pro';
  const isEnterprise = plan.name === 'enterprise';

  // Build feature list based on plan features
  const featureList = [
    plan.description,
    plan.max_brands === -1 ? 'Unlimited brands' : `${plan.max_brands} brand${plan.max_brands > 1 ? 's' : ''}`,
    plan.ai_generations_per_month === -1 ? 'Unlimited AI generations' : `${plan.ai_generations_per_month} AI generations/month`,
    plan.max_team_members === -1 ? 'Unlimited team members' : `${plan.max_team_members} team member${plan.max_team_members > 1 ? 's' : ''}`,
    plan.automation_enabled ? 'Social media automation' : null,
    plan.priority_support ? 'Priority support' : 'Email support',
  ].filter(Boolean) as string[];

  return (
    <div
      className={`relative rounded-2xl border-2 p-8 shadow-sm transition-all hover:shadow-lg ${
        isPro
          ? 'border-indigo-600 bg-white ring-2 ring-indigo-600'
          : 'border-gray-200 bg-white'
      } ${isCurrentPlan ? 'ring-2 ring-green-500' : ''}`}
    >
      {isPro && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="inline-flex items-center rounded-full bg-indigo-600 px-4 py-1 text-sm font-semibold text-white">
            Most Popular
          </span>
        </div>
      )}

      {isCurrentPlan && (
        <div className="absolute -top-4 right-4">
          <span className="inline-flex items-center rounded-full bg-green-500 px-4 py-1 text-sm font-semibold text-white">
            Current Plan
          </span>
        </div>
      )}

      <div className="text-center">
        <h3 className="text-xl font-semibold text-gray-900">{plan.display_name}</h3>
        <div className="mt-4 flex items-baseline justify-center gap-x-2">
          <span className="text-5xl font-bold tracking-tight text-gray-900">
            ${parseFloat(plan.price).toFixed(0)}
          </span>
          <span className="text-sm font-semibold leading-6 tracking-wide text-gray-600">
            /month
          </span>
        </div>
      </div>

      <ul className="mt-8 space-y-3">
        {featureList.map((feature, index) => (
          <li key={index} className="flex items-start gap-3">
            <svg
              className="h-6 w-6 flex-shrink-0 text-indigo-600"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4.5 12.75l6 6 9-13.5"
              />
            </svg>
            <span className="text-sm text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>

      <div className="mt-8 space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Brands:</span>
          <span className="font-medium">
            {plan.max_brands === -1 ? 'Unlimited' : plan.max_brands}
          </span>
        </div>
        <div className="flex justify-between text-sm text-gray-600">
          <span>AI Generations:</span>
          <span className="font-medium">
            {plan.ai_generations_per_month === -1
              ? 'Unlimited'
              : `${plan.ai_generations_per_month}/month`}
          </span>
        </div>
        <div className="flex justify-between text-sm text-gray-600">
          <span>Team Members:</span>
          <span className="font-medium">
            {plan.max_team_members === -1 ? 'Unlimited' : plan.max_team_members}
          </span>
        </div>
      </div>

      <button
        onClick={() => onSelect(plan)}
        disabled={isLoading || isCurrentPlan}
        className={`mt-8 w-full rounded-lg px-4 py-3 text-center text-sm font-semibold transition-colors ${
          isCurrentPlan
            ? 'cursor-not-allowed bg-gray-100 text-gray-500'
            : isPro
            ? 'bg-indigo-600 text-white hover:bg-indigo-700'
            : isEnterprise
            ? 'bg-gray-900 text-white hover:bg-gray-800'
            : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'
        } ${isLoading ? 'cursor-wait opacity-75' : ''}`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Processing...
          </span>
        ) : isCurrentPlan ? (
          'Current Plan'
        ) : (
          `Get ${plan.display_name}`
        )}
      </button>
    </div>
  );
}

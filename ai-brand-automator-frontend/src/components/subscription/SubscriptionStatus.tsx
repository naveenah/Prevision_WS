'use client';

import { Subscription } from '@/lib/api';

interface SubscriptionStatusProps {
  subscription: Subscription | null;
  onManageBilling: () => void;
  onCancelSubscription: () => void;
  isLoading?: boolean;
}

export function SubscriptionStatus({
  subscription,
  onManageBilling,
  onCancelSubscription,
  isLoading,
}: SubscriptionStatusProps) {
  if (!subscription) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            No Active Subscription
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Choose a plan below to get started with AI Brand Automator.
          </p>
        </div>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    active: 'bg-green-100 text-green-800',
    trialing: 'bg-blue-100 text-blue-800',
    past_due: 'bg-yellow-100 text-yellow-800',
    canceled: 'bg-red-100 text-red-800',
    incomplete: 'bg-gray-100 text-gray-800',
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {subscription.plan?.display_name || subscription.plan?.name || 'Unknown'} Plan
          </h3>
          <span
            className={`mt-2 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
              statusColors[subscription.status] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {subscription.status?.charAt(0).toUpperCase() +
              subscription.status?.slice(1).replace('_', ' ')}
          </span>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">
            ${parseFloat(subscription.plan?.price || '0').toFixed(2)}
          </p>
          <p className="text-sm text-gray-500">
            per month
          </p>
        </div>
      </div>

      <div className="mt-6 border-t border-gray-100 pt-4">
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-gray-500">Current Period Started</dt>
            <dd className="font-medium text-gray-900">
              {formatDate(subscription.current_period_start)}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Current Period Ends</dt>
            <dd className="font-medium text-gray-900">
              {formatDate(subscription.current_period_end)}
            </dd>
          </div>
        </dl>
      </div>

      {subscription.cancel_at_period_end && (
        <div className="mt-4 rounded-md bg-yellow-50 p-4">
          <div className="flex">
            <svg
              className="h-5 w-5 text-yellow-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
                clipRule="evenodd"
              />
            </svg>
            <p className="ml-3 text-sm text-yellow-700">
              Your subscription will be canceled at the end of the current
              billing period.
            </p>
          </div>
        </div>
      )}

      <div className="mt-6 flex gap-3">
        <button
          onClick={onManageBilling}
          disabled={isLoading}
          className="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-wait disabled:opacity-75"
        >
          Manage Billing
        </button>
        {!subscription.cancel_at_period_end &&
          (subscription.status === 'active' ||
            subscription.status === 'trialing') && (
            <button
              onClick={onCancelSubscription}
              disabled={isLoading}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:cursor-wait disabled:opacity-75"
            >
              Cancel
            </button>
          )}
      </div>
    </div>
  );
}

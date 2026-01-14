import { env } from './env';

let isRefreshing = false;
let failedQueue: Array<{ resolve: (value: unknown) => void; reject: (reason?: Error) => void }> = [];

const processQueue = (error: Error | null = null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(env.getApiUrl('/auth/token/refresh/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', data.access);
        // If a new refresh token is provided, update it
        if (data.refresh) {
          localStorage.setItem('refresh_token', data.refresh);
        }
      }
      return data.access;
    }

    return null;
  } catch (error) {
    console.error('Token refresh failed:', error);
    return null;
  }
};

export const apiClient = {
  async request(endpoint: string, options: RequestInit = {}) {
    const url = env.getApiUrl(endpoint);
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);

    if (response.status === 401 && typeof window !== 'undefined') {
      // Token expired or invalid
      if (isRefreshing) {
        // Wait for the token refresh to complete
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            config.headers = {
              ...config.headers,
              'Authorization': `Bearer ${token}`,
            };
            return fetch(url, config);
          })
          .catch(err => {
            return Promise.reject(err);
          });
      }

      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();

        if (newToken) {
          processQueue(null, newToken);
          // Retry original request with new token
          config.headers = {
            ...config.headers,
            'Authorization': `Bearer ${newToken}`,
          };
          return fetch(url, config);
        } else {
          // Refresh failed, redirect to login
          processQueue(new Error('Token refresh failed'), null);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/auth/login';
          return response;
        }
      } finally {
        isRefreshing = false;
      }
    }

    return response;
  },

  async get(endpoint: string) {
    return this.request(endpoint);
  },

  async post(endpoint: string, data: unknown) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async put(endpoint: string, data: unknown) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async delete(endpoint: string) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  },
};

// Subscription API types
export interface SubscriptionPlan {
  id: number;
  name: string;
  display_name: string;
  description: string;
  price: string;
  currency: string;
  max_brands: number;
  max_team_members: number;
  ai_generations_per_month: number;
  automation_enabled: boolean;
  priority_support: boolean;
  is_active: boolean;
}

export interface Subscription {
  id: number;
  plan: SubscriptionPlan;
  status: string;
  stripe_subscription_id: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

export interface PaymentHistory {
  id: number;
  stripe_payment_intent_id: string;
  amount: string;
  currency: string;
  status: string;
  description: string;
  created_at: string;
}

// Paginated response type
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Subscription API functions
export const subscriptionApi = {
  async getPlans(): Promise<SubscriptionPlan[]> {
    const response = await apiClient.get('/subscriptions/plans/');
    if (!response.ok) {
      throw new Error('Failed to fetch plans');
    }
    const data = await response.json();
    // Handle both paginated and non-paginated responses
    if (Array.isArray(data)) {
      return data;
    }
    // Paginated response
    return (data as PaginatedResponse<SubscriptionPlan>).results || [];
  },

  async getStatus(): Promise<Subscription | null> {
    const response = await apiClient.get('/subscriptions/status/');
    if (response.status === 404) {
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch subscription status');
    }
    return response.json();
  },

  async createCheckoutSession(planId: number): Promise<{ checkout_url: string }> {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
    const response = await apiClient.post('/subscriptions/create-checkout-session/', {
      plan_id: planId,
      success_url: `${baseUrl}/subscription?success=true`,
      cancel_url: `${baseUrl}/subscription?canceled=true`,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create checkout session');
    }
    return response.json();
  },

  async createPortalSession(): Promise<{ portal_url: string }> {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
    const response = await apiClient.post('/subscriptions/create-portal-session/', {
      return_url: `${baseUrl}/billing`,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create portal session');
    }
    return response.json();
  },

  async cancelSubscription(): Promise<{ message: string }> {
    const response = await apiClient.post('/subscriptions/cancel/', {});
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to cancel subscription');
    }
    return response.json();
  },

  async syncSubscription(): Promise<{ message: string; subscription: Subscription }> {
    const response = await apiClient.post('/subscriptions/sync/', {});
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to sync subscription');
    }
    return response.json();
  },

  async getPaymentHistory(): Promise<PaymentHistory[]> {
    const response = await apiClient.get('/subscriptions/payments/');
    if (!response.ok) {
      throw new Error('Failed to fetch payment history');
    }
    const data = await response.json();
    // Handle both paginated and non-paginated responses
    if (Array.isArray(data)) {
      return data;
    }
    return (data as PaginatedResponse<PaymentHistory>).results || [];
  },
};
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

export function RegisterForm() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    setIsLoading(true);
    
    try {
      const response = await apiClient.post('/auth/register/', {
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
      });

      if (response.ok) {
        alert('Registration successful! You can now login.');
        window.location.href = '/auth/login';
      } else {
        const error = await response.json();
        alert(error.errors ? JSON.stringify(error.errors) : 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    }
    
    setIsLoading(false);
  };

  return (
    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-brand-silver/70 mb-1">
              First Name
            </label>
            <input
              id="firstName"
              name="firstName"
              type="text"
              required
              className="appearance-none relative block w-full px-4 py-3 bg-white/5 border border-white/10 placeholder-brand-silver/50 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-electric/50 focus:border-brand-electric transition-colors sm:text-sm font-body"
              placeholder="John"
              value={formData.firstName}
              onChange={handleChange}
            />
          </div>
          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-brand-silver/70 mb-1">
              Last Name
            </label>
            <input
              id="lastName"
              name="lastName"
              type="text"
              required
              className="appearance-none relative block w-full px-4 py-3 bg-white/5 border border-white/10 placeholder-brand-silver/50 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-electric/50 focus:border-brand-electric transition-colors sm:text-sm font-body"
              placeholder="Doe"
              value={formData.lastName}
              onChange={handleChange}
            />
          </div>
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-brand-silver/70 mb-1">
            Email address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            className="appearance-none relative block w-full px-4 py-3 bg-white/5 border border-white/10 placeholder-brand-silver/50 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-electric/50 focus:border-brand-electric transition-colors sm:text-sm font-body"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-brand-silver/70 mb-1">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            className="appearance-none relative block w-full px-4 py-3 bg-white/5 border border-white/10 placeholder-brand-silver/50 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-electric/50 focus:border-brand-electric transition-colors sm:text-sm font-body"
            placeholder="••••••••"
            value={formData.password}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-brand-silver/70 mb-1">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            autoComplete="new-password"
            required
            className="appearance-none relative block w-full px-4 py-3 bg-white/5 border border-white/10 placeholder-brand-silver/50 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-electric/50 focus:border-brand-electric transition-colors sm:text-sm font-body"
            placeholder="••••••••"
            value={formData.confirmPassword}
            onChange={handleChange}
          />
        </div>
      </div>

      <div>
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Creating account...' : 'Sign up'}
        </button>
      </div>

      <div className="text-center">
        <Link href="/auth/login" className="font-medium text-brand-electric hover:text-brand-electric/80 transition-colors">
          Already have an account? Sign in
        </Link>
      </div>
    </form>
  );
}
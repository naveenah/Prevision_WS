'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export function BrandForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    brandVoice: '',
    visionStatement: '',
    missionStatement: '',
    values: '',
    positioningStatement: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      // Assume company ID is stored after creation, for now use 1
      const companyId = localStorage.getItem('company_id') || '1';

      const response = await apiClient.put(`/api/v1/companies/${companyId}/`, formData);

      if (response.ok) {
        const data = await response.json();
        console.log('Brand data updated:', data);
        router.push('/onboarding/step-3');
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to save brand data');
      }
    } catch (error) {
      console.error('Brand update error:', error);
      alert('Failed to save brand data. Please try again.');
    }
    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="brandVoice" className="block text-sm font-medium text-gray-700">
          Brand Voice *
        </label>
        <select
          id="brandVoice"
          name="brandVoice"
          required
          value={formData.brandVoice}
          onChange={handleChange}
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        >
          <option value="">Select brand voice</option>
          <option value="professional">Professional</option>
          <option value="friendly">Friendly</option>
          <option value="authoritative">Authoritative</option>
          <option value="innovative">Innovative</option>
          <option value="casual">Casual</option>
        </select>
      </div>

      <div>
        <label htmlFor="visionStatement" className="block text-sm font-medium text-gray-700">
          Vision Statement
        </label>
        <textarea
          id="visionStatement"
          name="visionStatement"
          rows={3}
          value={formData.visionStatement}
          onChange={handleChange}
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="What is your long-term vision?"
        />
      </div>

      <div>
        <label htmlFor="missionStatement" className="block text-sm font-medium text-gray-700">
          Mission Statement
        </label>
        <textarea
          id="missionStatement"
          name="missionStatement"
          rows={3}
          value={formData.missionStatement}
          onChange={handleChange}
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="What is your mission?"
        />
      </div>

      <div>
        <label htmlFor="values" className="block text-sm font-medium text-gray-700">
          Core Values
        </label>
        <textarea
          id="values"
          name="values"
          rows={3}
          value={formData.values}
          onChange={handleChange}
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="List your core values (comma-separated)"
        />
      </div>

      <div>
        <label htmlFor="positioningStatement" className="block text-sm font-medium text-gray-700">
          Positioning Statement
        </label>
        <textarea
          id="positioningStatement"
          name="positioningStatement"
          rows={3}
          value={formData.positioningStatement}
          onChange={handleChange}
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="How do you position your brand?"
        />
      </div>

      <div className="flex justify-between">
        <button
          type="button"
          onClick={() => router.push('/onboarding/step-1')}
          className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Previous
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : 'Next Step'}
        </button>
      </div>
    </form>
  );
}
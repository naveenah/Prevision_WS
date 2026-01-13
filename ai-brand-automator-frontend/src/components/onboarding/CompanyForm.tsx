'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export function CompanyForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    industry: '',
    targetAudience: '',
    coreProblem: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [existingCompanyId, setExistingCompanyId] = useState<number | null>(null);

  // Load existing company data if it exists
  useEffect(() => {
    const loadExistingCompany = async () => {
      try {
        const response = await apiClient.get('/companies/');
        if (response.ok) {
          const data = await response.json();
          // API returns paginated data with results array
          const companies = data.results || [];
          if (companies.length > 0) {
            const company = companies[0]; // Get first company (one per tenant)
            setExistingCompanyId(company.id);
            setFormData({
              name: company.name || '',
              description: company.description || '',
              industry: company.industry || '',
              targetAudience: company.target_audience || '',
              coreProblem: company.core_problem || '',
            });
            // Store company ID for next steps
            localStorage.setItem('company_id', company.id.toString());
          }
        }
      } catch (error) {
        console.error('Error loading company:', error);
      }
    };
    loadExistingCompany();
  }, []);

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
      // Convert camelCase to snake_case for backend
      const apiData = {
        name: formData.name,
        description: formData.description,
        industry: formData.industry,
        target_audience: formData.targetAudience,
        core_problem: formData.coreProblem,
      };
      
      let response;
      if (existingCompanyId) {
        // Update existing company
        response = await apiClient.put(`/companies/${existingCompanyId}/`, apiData);
      } else {
        // Create new company
        response = await apiClient.post('/companies/', apiData);
      }

      if (response.ok) {
        const data = await response.json();
        console.log('Company saved:', data);
        localStorage.setItem('company_id', data.id);
        router.push('/onboarding/step-2');
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to save company data');
      }
    } catch (error) {
      console.error('Company save error:', error);
      alert('Failed to save company data. Please try again.');
    }
    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Company Name *
        </label>
        <input
          type="text"
          id="name"
          name="name"
          required
          value={formData.name}
          onChange={handleChange}
          className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        />
      </div>

      <div>
        <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
          Industry *
        </label>
        <select
          id="industry"
          name="industry"
          required
          value={formData.industry}
          onChange={handleChange}
          className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-gray-900 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        >
          <option value="">Select an industry</option>
          <option value="technology">Technology</option>
          <option value="healthcare">Healthcare</option>
          <option value="finance">Finance</option>
          <option value="retail">Retail</option>
          <option value="education">Education</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Company Description *
        </label>
        <textarea
          id="description"
          name="description"
          rows={4}
          required
          value={formData.description}
          onChange={handleChange}
          className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Describe your company and what it does..."
        />
      </div>

      <div>
        <label htmlFor="targetAudience" className="block text-sm font-medium text-gray-700">
          Target Audience
        </label>
        <textarea
          id="targetAudience"
          name="targetAudience"
          rows={3}
          value={formData.targetAudience}
          onChange={handleChange}
          className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Who is your ideal customer?"
        />
      </div>

      <div>
        <label htmlFor="coreProblem" className="block text-sm font-medium text-gray-700">
          Core Problem You Solve
        </label>
        <textarea
          id="coreProblem"
          name="coreProblem"
          rows={3}
          value={formData.coreProblem}
          onChange={handleChange}
          className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="What problem does your company solve for customers?"
        />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : existingCompanyId ? 'Update & Continue' : 'Next Step'}
        </button>
      </div>
    </form>
  );
}
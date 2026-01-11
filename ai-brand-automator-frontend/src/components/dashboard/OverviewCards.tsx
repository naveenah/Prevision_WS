'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

interface CardData {
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'neutral' | 'negative';
}

export function OverviewCards() {
  const [cards, setCards] = useState<CardData[]>([
    {
      title: 'Total Assets',
      value: '0',
      change: 'Loading...',
      changeType: 'neutral' as const,
    },
    {
      title: 'AI Interactions',
      value: '0',
      change: 'Loading...',
      changeType: 'neutral' as const,
    },
    {
      title: 'Companies',
      value: '0',
      change: 'Active',
      changeType: 'neutral' as const,
    },
    {
      title: 'Chat Sessions',
      value: '0',
      change: 'Total',
      changeType: 'neutral' as const,
    },
  ]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      // Fetch assets count
      const assetsResponse = await apiClient.get('/api/v1/assets/');
      const assetsData = await assetsResponse.json();
      const assetsCount = Array.isArray(assetsData) ? assetsData.length : 0;

      // Fetch AI generations count
      const aiResponse = await apiClient.get('/api/v1/ai/generations/');
      const aiData = await aiResponse.json();
      const aiCount = Array.isArray(aiData) ? aiData.length : 0;

      // Fetch companies count
      const companiesResponse = await apiClient.get('/api/v1/companies/');
      const companiesData = await companiesResponse.json();
      const companiesCount = Array.isArray(companiesData) ? companiesData.length : 0;

      // Fetch chat sessions count
      const chatResponse = await apiClient.get('/api/v1/ai/chat-sessions/');
      const chatData = await chatResponse.json();
      const chatCount = Array.isArray(chatData) ? chatData.length : 0;

      setCards([
        {
          title: 'Total Assets',
          value: assetsCount.toString(),
          change: `${assetsCount} files`,
          changeType: 'neutral',
        },
        {
          title: 'AI Interactions',
          value: aiCount.toString(),
          change: `${aiCount} total`,
          changeType: aiCount > 0 ? 'positive' : 'neutral',
        },
        {
          title: 'Companies',
          value: companiesCount.toString(),
          change: 'Active',
          changeType: 'neutral',
        },
        {
          title: 'Chat Sessions',
          value: chatCount.toString(),
          change: `${chatCount} sessions`,
          changeType: chatCount > 0 ? 'positive' : 'neutral',
        },
      ]);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500">{card.title}</h3>
          <div className="mt-2 flex items-baseline">
            <p className="text-2xl font-semibold text-gray-900">{card.value}</p>
            <p
              className={`ml-2 text-sm ${
                card.changeType === 'positive'
                  ? 'text-green-600'
                  : 'text-gray-600'
              }`}
            >
              {card.change}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
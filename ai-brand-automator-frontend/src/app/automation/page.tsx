'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { apiClient } from '@/lib/api';
import Link from 'next/link';

interface SocialPlatformStatus {
  connected: boolean;
  profile_name: string | null;
  profile_url: string | null;
  profile_image_url: string | null;
  status: string;
  is_token_valid: boolean;
}

interface SocialProfilesStatus {
  linkedin: SocialPlatformStatus;
  twitter: SocialPlatformStatus;
  instagram: SocialPlatformStatus;
  facebook: SocialPlatformStatus;
}

const PLATFORM_CONFIG = {
  linkedin: {
    name: 'LinkedIn',
    icon: (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
      </svg>
    ),
    color: 'bg-[#0A66C2]',
    hoverColor: 'hover:bg-[#004182]',
    available: true,
  },
  twitter: {
    name: 'Twitter/X',
    icon: (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    ),
    color: 'bg-black',
    hoverColor: 'hover:bg-gray-800',
    available: false, // Coming soon
  },
  instagram: {
    name: 'Instagram',
    icon: (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
      </svg>
    ),
    color: 'bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500',
    hoverColor: 'hover:opacity-90',
    available: false, // Coming soon
  },
  facebook: {
    name: 'Facebook',
    icon: (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    ),
    color: 'bg-[#1877F2]',
    hoverColor: 'hover:bg-[#0d5fc7]',
    available: false, // Coming soon
  },
};

export default function AutomationPage() {
  useAuth();
  const searchParams = useSearchParams();
  
  const [profiles, setProfiles] = useState<SocialProfilesStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Check for OAuth callback results
  useEffect(() => {
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    const name = searchParams.get('name');
    const errorMessage = searchParams.get('message');

    if (success) {
      setMessage({
        type: 'success',
        text: `Successfully connected ${success}${name ? ` as ${name}` : ''}!`,
      });
      // Clear the URL params
      window.history.replaceState({}, '', '/automation');
    } else if (error) {
      setMessage({
        type: 'error',
        text: `Failed to connect: ${errorMessage || error}`,
      });
      window.history.replaceState({}, '', '/automation');
    }
  }, [searchParams]);

  // Fetch social profiles status
  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const response = await apiClient.get('/automation/social-profiles/status/');
        if (response.ok) {
          const data = await response.json();
          setProfiles(data);
        }
      } catch (error) {
        console.error('Failed to fetch social profiles:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfiles();
  }, []);

  const handleConnect = async (platform: string) => {
    if (platform !== 'linkedin') {
      setMessage({
        type: 'error',
        text: `${PLATFORM_CONFIG[platform as keyof typeof PLATFORM_CONFIG].name} integration coming soon!`,
      });
      return;
    }

    setConnecting(platform);
    try {
      const response = await apiClient.get('/automation/linkedin/connect/');
      if (response.ok) {
        const data = await response.json();
        // Redirect to LinkedIn authorization
        window.location.href = data.authorization_url;
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to initiate connection',
        });
      }
    } catch (error) {
      console.error('Failed to connect:', error);
      setMessage({
        type: 'error',
        text: 'Failed to initiate connection',
      });
    } finally {
      setConnecting(null);
    }
  };

  // Test connection (dev mode only - no real LinkedIn data)
  const handleTestConnect = async (platform: string) => {
    if (platform !== 'linkedin') return;

    setConnecting(platform);
    try {
      const response = await apiClient.post('/automation/linkedin/test-connect/', {});
      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: `${data.message} (Test Mode - No real LinkedIn data)`,
        });
        // Refresh profiles
        const profilesResponse = await apiClient.get('/automation/social-profiles/status/');
        if (profilesResponse.ok) {
          const profileData = await profilesResponse.json();
          setProfiles(profileData);
        }
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to create test connection',
        });
      }
    } catch (error) {
      console.error('Failed to test connect:', error);
      setMessage({
        type: 'error',
        text: 'Failed to create test connection',
      });
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async (platform: string) => {
    if (platform !== 'linkedin') return;

    setConnecting(platform);
    try {
      const response = await apiClient.post('/automation/linkedin/disconnect/', {});
      if (response.ok) {
        setMessage({
          type: 'success',
          text: 'LinkedIn disconnected successfully',
        });
        // Refresh profiles
        const profilesResponse = await apiClient.get('/automation/social-profiles/status/');
        if (profilesResponse.ok) {
          const data = await profilesResponse.json();
          setProfiles(data);
        }
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to disconnect',
        });
      }
    } catch (error) {
      console.error('Failed to disconnect:', error);
      setMessage({
        type: 'error',
        text: 'Failed to disconnect',
      });
    } finally {
      setConnecting(null);
    }
  };

  return (
    <div className="min-h-screen bg-brand-midnight">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/dashboard" 
            className="inline-flex items-center gap-2 text-brand-silver hover:text-brand-electric transition-colors mb-4"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>Back to Dashboard</span>
          </Link>
          
          <h1 className="text-3xl font-heading font-bold text-white">Social Media Automation</h1>
          <p className="mt-2 text-brand-silver/70">
            Connect your social media accounts to automate posting and manage your brand presence.
          </p>
        </div>

        {/* Message Banner */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg border ${
            message.type === 'success' 
              ? 'bg-brand-mint/10 border-brand-mint/30 text-brand-mint' 
              : 'bg-red-900/30 border-red-500/30 text-red-300'
          }`}>
            <div className="flex items-center justify-between">
              <p>{message.text}</p>
              <button 
                onClick={() => setMessage(null)}
                className="text-current hover:opacity-70"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Social Platforms Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(PLATFORM_CONFIG).map(([platform, config]) => {
            const platformStatus = profiles?.[platform as keyof SocialProfilesStatus];
            const isConnected = platformStatus?.connected;
            const isLoading = connecting === platform;

            return (
              <div 
                key={platform}
                className="glass-card p-6 hover:border-brand-electric/30 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${config.color} text-white`}>
                      {config.icon}
                    </div>
                    <div>
                      <h3 className="text-lg font-heading font-semibold text-white">
                        {config.name}
                      </h3>
                      {isConnected && platformStatus?.profile_name ? (
                        <p className="text-sm text-brand-silver/70">
                          Connected as {platformStatus.profile_name}
                        </p>
                      ) : (
                        <p className="text-sm text-brand-silver/70">
                          {config.available ? 'Not connected' : 'Coming soon'}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Status Indicator */}
                  {isConnected && (
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-brand-mint rounded-full animate-pulse"></span>
                      <span className="text-xs text-brand-mint">Connected</span>
                    </div>
                  )}
                </div>

                {/* Profile Info */}
                {isConnected && platformStatus?.profile_url && (
                  <div className="mt-4 p-3 bg-white/5 rounded-lg">
                    <a 
                      href={platformStatus.profile_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-brand-electric hover:underline"
                    >
                      View Profile →
                    </a>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="mt-6 space-y-2">
                  {isConnected ? (
                    <button
                      onClick={() => handleDisconnect(platform)}
                      disabled={isLoading}
                      className="w-full py-2.5 px-4 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-900/20 transition-colors disabled:opacity-50"
                    >
                      {isLoading ? 'Disconnecting...' : 'Disconnect'}
                    </button>
                  ) : config.available ? (
                    <>
                      <button
                        onClick={() => handleConnect(platform)}
                        disabled={isLoading || loading}
                        className={`w-full py-2.5 px-4 rounded-lg text-white transition-colors disabled:opacity-50 ${config.color} ${config.hoverColor}`}
                      >
                        {isLoading ? 'Connecting...' : `Connect ${config.name}`}
                      </button>
                      {/* Test Connect Button - Dev Mode Only */}
                      {platform === 'linkedin' && (
                        <button
                          onClick={() => handleTestConnect(platform)}
                          disabled={isLoading || loading}
                          className="w-full py-2 px-4 rounded-lg border border-brand-electric/30 text-brand-electric text-sm hover:bg-brand-electric/10 transition-colors disabled:opacity-50"
                        >
                          {isLoading ? 'Creating...' : '🧪 Test Connect (No Real Data)'}
                        </button>
                      )}
                    </>
                  ) : (
                    <button
                      disabled
                      className="w-full py-2.5 px-4 rounded-lg bg-white/10 text-brand-silver/50 cursor-not-allowed"
                    >
                      Coming Soon
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Content Calendar Section */}
        <div className="mt-12">
          <h2 className="text-2xl font-heading font-bold text-white mb-4">Content Calendar</h2>
          <div className="glass-card p-8 text-center">
            <div className="w-16 h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-brand-electric" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Schedule Your Content</h3>
            <p className="text-brand-silver/70 mb-6 max-w-md mx-auto">
              Connect your social accounts first, then start scheduling posts to be published automatically.
            </p>
            <button 
              disabled={!profiles?.linkedin?.connected}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Scheduled Post
            </button>
          </div>
        </div>

        {/* Automation Tasks Section */}
        <div className="mt-12">
          <h2 className="text-2xl font-heading font-bold text-white mb-4">Automation Tasks</h2>
          <div className="glass-card p-8 text-center">
            <div className="w-16 h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-brand-electric" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Automated Workflows</h3>
            <p className="text-brand-silver/70 max-w-md mx-auto">
              No automation tasks yet. Once you connect your social accounts, you&apos;ll be able to set up automated workflows.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

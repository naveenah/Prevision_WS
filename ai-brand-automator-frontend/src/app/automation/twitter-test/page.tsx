'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { apiClient } from '@/lib/api';
import Link from 'next/link';

interface TwitterProfile {
  connected: boolean;
  profile_name: string | null;
  profile_url: string | null;
  profile_image_url: string | null;
  status: string;
  is_token_valid: boolean;
  username?: string;
}

interface TweetValidation {
  is_valid: boolean;
  length: number;
  max_length: number;
  remaining: number;
  is_premium: boolean;
  errors: string[];
}

const TWITTER_MAX_LENGTH = 280;
const TWITTER_PREMIUM_MAX_LENGTH = 25000;

export default function TwitterTestPage() {
  useAuth();
  
  const [profile, setProfile] = useState<TwitterProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  
  // Tweet composition state
  const [tweetText, setTweetText] = useState('');
  const [posting, setPosting] = useState(false);
  const [validation, setValidation] = useState<TweetValidation | null>(null);
  const [isPremium, setIsPremium] = useState(false);
  const [testMode, setTestMode] = useState(true); // Default to test mode for safety
  
  // Recent tweets (test mode only)
  const [testTweets, setTestTweets] = useState<Array<{ id: string; text: string; created_at: string }>>([]);

  // Fetch Twitter profile status
  const fetchProfile = useCallback(async () => {
    try {
      const response = await apiClient.get('/automation/social-profiles/status/');
      if (response.ok) {
        const data = await response.json();
        setProfile(data.twitter || null);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  // Validate tweet text in real-time
  useEffect(() => {
    const validateTweet = async () => {
      if (!tweetText.trim()) {
        setValidation(null);
        return;
      }
      
      try {
        const response = await apiClient.post('/automation/twitter/validate/', {
          text: tweetText,
          is_premium: isPremium,
        });
        if (response.ok) {
          const data = await response.json();
          setValidation(data);
        }
      } catch (error) {
        console.error('Validation error:', error);
      }
    };

    // Debounce validation
    const timer = setTimeout(validateTweet, 300);
    return () => clearTimeout(timer);
  }, [tweetText, isPremium]);

  const handleConnect = async () => {
    setConnecting(true);
    try {
      const response = await apiClient.get('/automation/twitter/connect/');
      if (response.ok) {
        const data = await response.json();
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
      setConnecting(false);
    }
  };

  const handleTestConnect = async () => {
    setConnecting(true);
    try {
      const response = await apiClient.post('/automation/twitter/test-connect/', {});
      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: `${data.message} (Test Mode - No real Twitter data)`,
        });
        await fetchProfile();
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
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect your Twitter account?')) {
      return;
    }

    setConnecting(true);
    try {
      const response = await apiClient.post('/automation/twitter/disconnect/', {});
      if (response.ok) {
        setMessage({
          type: 'success',
          text: 'Twitter account disconnected successfully',
        });
        await fetchProfile();
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
      setConnecting(false);
    }
  };

  const handlePostTweet = async () => {
    if (!tweetText.trim()) {
      setMessage({ type: 'error', text: 'Tweet text cannot be empty' });
      return;
    }

    if (validation && !validation.is_valid) {
      setMessage({ type: 'error', text: validation.errors.join(', ') });
      return;
    }

    setPosting(true);
    try {
      if (testMode) {
        // In test mode, just simulate the tweet locally
        const testTweet = {
          id: `test_${Date.now()}`,
          text: tweetText,
          created_at: new Date().toISOString(),
        };
        setTestTweets(prev => [testTweet, ...prev]);
        setMessage({
          type: 'success',
          text: 'Test tweet simulated! (Not posted to Twitter)',
        });
        setTweetText('');
      } else {
        // Real mode - actually post to Twitter
        const response = await apiClient.post('/automation/twitter/post/', {
          text: tweetText,
        });

        if (response.ok) {
          const data = await response.json();
          setMessage({
            type: 'success',
            text: `Tweet posted successfully! Tweet ID: ${data.tweet_id}`,
          });
          setTweetText('');
        } else {
          const error = await response.json();
          setMessage({
            type: 'error',
            text: error.error || 'Failed to post tweet',
          });
        }
      }
    } catch (error) {
      console.error('Failed to post tweet:', error);
      setMessage({
        type: 'error',
        text: 'Failed to post tweet',
      });
    } finally {
      setPosting(false);
    }
  };

  const getCharacterCountColor = () => {
    if (!validation) return 'text-gray-400';
    if (validation.remaining < 0) return 'text-red-500';
    if (validation.remaining < 20) return 'text-yellow-500';
    return 'text-gray-400';
  };

  const maxLength = isPremium ? TWITTER_PREMIUM_MAX_LENGTH : TWITTER_MAX_LENGTH;

  if (loading) {
    return (
      <div className="min-h-screen bg-brand-midnight flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-electric"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brand-midnight text-white p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/automation" className="text-gray-400 hover:text-white mb-2 inline-block">
              ← Back to Automation
            </Link>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
              Twitter/X Integration Test
            </h1>
            <p className="text-gray-400 mt-2">
              Test Twitter OAuth and posting without affecting your real account
            </p>
          </div>
        </div>

        {/* Message Display */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-500/10 border border-green-500/30 text-green-400'
                : message.type === 'info'
                ? 'bg-blue-500/10 border border-blue-500/30 text-blue-400'
                : 'bg-red-500/10 border border-red-500/30 text-red-400'
            }`}
          >
            {message.text}
            <button
              onClick={() => setMessage(null)}
              className="float-right text-gray-400 hover:text-white"
            >
              ×
            </button>
          </div>
        )}

        {/* Connection Status Card */}
        <div className="bg-gray-900 rounded-xl p-6 mb-8 border border-gray-800">
          <h2 className="text-xl font-semibold mb-4">Connection Status</h2>
          
          {profile?.connected ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {profile.profile_image_url && (
                  <img
                    src={profile.profile_image_url}
                    alt="Profile"
                    className="w-12 h-12 rounded-full"
                  />
                )}
                <div>
                  <p className="font-medium">{profile.profile_name}</p>
                  {profile.username && (
                    <p className="text-gray-400 text-sm">@{profile.username}</p>
                  )}
                  <p className={`text-sm ${profile.is_token_valid ? 'text-green-400' : 'text-yellow-400'}`}>
                    {profile.is_token_valid ? '✓ Token Valid' : '⚠ Token may need refresh'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleDisconnect}
                disabled={connecting}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50"
              >
                {connecting ? 'Disconnecting...' : 'Disconnect'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-400">
                Connect your Twitter account to test posting functionality.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={handleConnect}
                  disabled={connecting}
                  className="px-6 py-3 bg-black hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                  {connecting ? 'Connecting...' : 'Connect with Twitter'}
                </button>
                <button
                  onClick={handleTestConnect}
                  disabled={connecting}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50"
                >
                  {connecting ? 'Creating...' : 'Create Test Connection'}
                </button>
              </div>
              <p className="text-gray-500 text-sm">
                💡 Use &quot;Create Test Connection&quot; to simulate a connection without OAuth
              </p>
            </div>
          )}
        </div>

        {/* Tweet Composer */}
        <div className="bg-gray-900 rounded-xl p-6 mb-8 border border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Compose Tweet</h2>
            <div className="flex items-center gap-4">
              {/* Test Mode Toggle */}
              <label className="flex items-center gap-2 cursor-pointer">
                <span className={`text-sm ${testMode ? 'text-green-400' : 'text-gray-400'}`}>
                  Test Mode
                </span>
                <div
                  onClick={() => setTestMode(!testMode)}
                  className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${
                    testMode ? 'bg-green-600' : 'bg-gray-600'
                  }`}
                >
                  <div
                    className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      testMode ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </div>
              </label>
              {/* Premium Toggle */}
              <label className="flex items-center gap-2 cursor-pointer">
                <span className="text-sm text-gray-400">X Premium</span>
                <input
                  type="checkbox"
                  checked={isPremium}
                  onChange={(e) => setIsPremium(e.target.checked)}
                  className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-brand-electric focus:ring-brand-electric"
                />
              </label>
            </div>
          </div>

          {!testMode && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4">
              <p className="text-yellow-400 text-sm">
                ⚠️ <strong>Live Mode Active!</strong> Tweets will be posted to your real Twitter account.
              </p>
            </div>
          )}

          <textarea
            value={tweetText}
            onChange={(e) => setTweetText(e.target.value)}
            placeholder="What's happening?"
            className="w-full h-32 bg-gray-800 border border-gray-700 rounded-lg p-4 text-white placeholder-gray-500 resize-none focus:outline-none focus:border-brand-electric"
            disabled={!profile?.connected}
          />

          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center gap-4">
              {/* Character count */}
              <span className={`text-sm ${getCharacterCountColor()}`}>
                {tweetText.length} / {maxLength}
                {validation && (
                  <span className="ml-2">
                    ({validation.remaining} remaining)
                  </span>
                )}
              </span>
              {/* Validation errors */}
              {validation && !validation.is_valid && (
                <span className="text-red-400 text-sm">
                  {validation.errors.join(', ')}
                </span>
              )}
            </div>

            <button
              onClick={handlePostTweet}
              disabled={!profile?.connected || posting || !tweetText.trim() || (validation !== null && !validation.is_valid)}
              className={`px-6 py-2 rounded-full font-medium transition-colors disabled:opacity-50 ${
                testMode
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-brand-electric hover:bg-blue-600'
              }`}
            >
              {posting ? 'Posting...' : testMode ? '🧪 Test Tweet' : 'Post Tweet'}
            </button>
          </div>
        </div>

        {/* Test Tweets Preview */}
        {testMode && testTweets.length > 0 && (
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h2 className="text-xl font-semibold mb-4">Test Tweets (Not Posted)</h2>
            <div className="space-y-4">
              {testTweets.map((tweet) => (
                <div
                  key={tweet.id}
                  className="bg-gray-800 rounded-lg p-4 border border-gray-700"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Test User</span>
                        <span className="text-gray-500 text-sm">@testuser</span>
                        <span className="text-gray-500 text-sm">·</span>
                        <span className="text-gray-500 text-sm">
                          {new Date(tweet.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="mt-1 whitespace-pre-wrap">{tweet.text}</p>
                      <div className="mt-2 text-xs text-green-400">
                        ✓ Simulated tweet (ID: {tweet.id})
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => setTestTweets([])}
              className="mt-4 text-gray-400 hover:text-white text-sm"
            >
              Clear test tweets
            </button>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 bg-gray-900/50 rounded-xl p-6 border border-gray-800">
          <h2 className="text-xl font-semibold mb-4">How to Use</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-400">
            <li>Connect your Twitter account using OAuth or create a test connection</li>
            <li>Keep <strong className="text-green-400">Test Mode</strong> enabled to simulate tweets without posting</li>
            <li>Compose your tweet in the text area (max {TWITTER_MAX_LENGTH} characters, or {TWITTER_PREMIUM_MAX_LENGTH} with X Premium)</li>
            <li>Click &quot;Test Tweet&quot; to simulate posting - the tweet will appear below without being sent to Twitter</li>
            <li>When ready for real posting, disable Test Mode and click &quot;Post Tweet&quot;</li>
          </ol>
          <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <p className="text-blue-400 text-sm">
              <strong>💡 Tip:</strong> Test Mode is enabled by default to prevent accidental posts to your real Twitter account.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

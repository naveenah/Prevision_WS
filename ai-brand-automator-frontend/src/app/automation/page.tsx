'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
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
  access_token?: string | null;
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

interface ScheduledPost {
  id: number;
  title: string;
  content: string;
  media_urls: string[];
  platforms: string[];
  scheduled_date: string;
  status: string;
  status_display: string;
}

interface AutomationTask {
  id: number;
  task_type: string;
  task_type_display: string;
  status: string;
  status_display: string;
  payload: Record<string, unknown>;
  result: Record<string, unknown>;
  error_message: string | null;
  scheduled_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

// Loading fallback for Suspense
function AutomationLoading() {
  return (
    <div className="min-h-screen bg-brand-midnight flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-electric"></div>
    </div>
  );
}

// Main page wrapper with Suspense
export default function AutomationPage() {
  return (
    <Suspense fallback={<AutomationLoading />}>
      <AutomationPageContent />
    </Suspense>
  );
}

function AutomationPageContent() {
  useAuth();
  const searchParams = useSearchParams();
  
  const [profiles, setProfiles] = useState<SocialProfilesStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Compose post state
  const [showComposeModal, setShowComposeModal] = useState(false);
  const [postTitle, setPostTitle] = useState('');
  const [postText, setPostText] = useState('');
  const [posting, setPosting] = useState(false);
  const [postMediaUrns, setPostMediaUrns] = useState<string[]>([]);
  const [uploadingMedia, setUploadingMedia] = useState(false);
  
  // Schedule post state
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleTitle, setScheduleTitle] = useState('');
  const [scheduleContent, setScheduleContent] = useState('');
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');
  const [scheduling, setScheduling] = useState(false);
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [publishedPosts, setPublishedPosts] = useState<ScheduledPost[]>([]);
  const [publishedPostsLimit, setPublishedPostsLimit] = useState<number>(6);
  const [scheduleMediaUrns, setScheduleMediaUrns] = useState<string[]>([]);
  const [uploadingScheduleMedia, setUploadingScheduleMedia] = useState(false);

  // Edit post state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingPost, setEditingPost] = useState<ScheduledPost | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editDate, setEditDate] = useState('');
  const [editTime, setEditTime] = useState('');
  const [editing, setEditing] = useState(false);
  const [editMediaUrns, setEditMediaUrns] = useState<string[]>([]);
  const [uploadingEditMedia, setUploadingEditMedia] = useState(false);

  // Automation tasks state
  const [automationTasks, setAutomationTasks] = useState<AutomationTask[]>([]);

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

  // Fetch social profiles status and scheduled posts
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch social profiles
        const profilesResponse = await apiClient.get('/automation/social-profiles/status/');
        if (profilesResponse.ok) {
          const data = await profilesResponse.json();
          setProfiles(data);
        }
        
        // Fetch upcoming scheduled posts
        const scheduledResponse = await apiClient.get('/automation/content-calendar/upcoming/');
        if (scheduledResponse.ok) {
          const data = await scheduledResponse.json();
          setScheduledPosts(data);
        }

        // Fetch published posts (initial limit of 6)
        const publishedResponse = await apiClient.get('/automation/content-calendar/?status=published&limit=6');
        if (publishedResponse.ok) {
          const data = await publishedResponse.json();
          // Handle paginated response (DRF returns {count, results, ...})
          const posts = data.results || data;
          setPublishedPosts(Array.isArray(posts) ? posts : []);
        }

        // Fetch automation tasks (limit to recent 10)
        const tasksResponse = await apiClient.get('/automation/tasks/?limit=10');
        if (tasksResponse.ok) {
          const data = await tasksResponse.json();
          const tasks = data.results || data;
          setAutomationTasks(Array.isArray(tasks) ? tasks : []);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Fetch scheduled posts function (for refresh after actions)
  const fetchScheduledPosts = useCallback(async () => {
    try {
      const response = await apiClient.get('/automation/content-calendar/upcoming/');
      if (response.ok) {
        const data = await response.json();
        setScheduledPosts(data);
      }
    } catch (error) {
      console.error('Failed to fetch scheduled posts:', error);
    }
  }, []);

  // Fetch published posts
  const fetchPublishedPosts = useCallback(async (limit?: number) => {
    try {
      const queryLimit = limit ?? publishedPostsLimit;
      const response = await apiClient.get(`/automation/content-calendar/?status=published&limit=${queryLimit}`);
      console.log('Published posts response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Published posts data:', data);
        // Handle paginated response (DRF returns {count, results, ...})
        const posts = data.results || data;
        setPublishedPosts(Array.isArray(posts) ? posts : []);
      } else {
        console.error('Published posts error:', await response.text());
      }
    } catch (error) {
      console.error('Failed to fetch published posts:', error);
    }
  }, [publishedPostsLimit]);

  // Fetch automation tasks
  const fetchAutomationTasks = useCallback(async () => {
    try {
      const response = await apiClient.get('/automation/tasks/?limit=10');
      if (response.ok) {
        const data = await response.json();
        const tasks = data.results || data;
        setAutomationTasks(Array.isArray(tasks) ? tasks : []);
      }
    } catch (error) {
      console.error('Failed to fetch automation tasks:', error);
    }
  }, []);

  // Auto-refresh scheduled posts every 30 seconds to catch Celery updates
  useEffect(() => {
    const interval = setInterval(() => {
      fetchScheduledPosts();
      fetchPublishedPosts();
      fetchAutomationTasks();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [fetchScheduledPosts, fetchPublishedPosts, fetchAutomationTasks]);

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

  // Handle media upload for posts (images and videos)
  const handleMediaUpload = async (
    file: File,
    setMediaUrns: React.Dispatch<React.SetStateAction<string[]>>,
    setUploading: React.Dispatch<React.SetStateAction<boolean>>
  ) => {
    // Validate file type (LinkedIn standards: JPEG/PNG/GIF for images, MP4 only for video)
    const imageTypes = ['image/jpeg', 'image/png', 'image/gif'];
    const videoTypes = ['video/mp4'];  // LinkedIn officially supports MP4 only
    const isImage = imageTypes.includes(file.type);
    const isVideo = videoTypes.includes(file.type);

    if (!isImage && !isVideo) {
      setMessage({
        type: 'error',
        text: 'Invalid file type. Allowed: JPEG, PNG, GIF for images; MP4 for video',
      });
      return;
    }

    // Validate file size (LinkedIn standards: 8MB for images, 500MB for videos)
    const maxSize = isVideo ? 500 * 1024 * 1024 : 8 * 1024 * 1024;
    const sizeLabel = isVideo ? '500MB' : '8MB';
    if (file.size > maxSize) {
      setMessage({
        type: 'error',
        text: `File too large. Maximum size is ${sizeLabel}`,
      });
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('media', file);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/automation/linkedin/media/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMediaUrns((prev) => [...prev, data.asset_urn]);
        
        const mediaType = data.media_type === 'video' ? 'Video' : 'Image';
        const processingNote = data.status === 'PROCESSING' ? ' (processing...)' : '';
        
        setMessage({
          type: 'success',
          text: data.test_mode 
            ? `🧪 ${mediaType} uploaded (Test Mode)${processingNote}` 
            : `${mediaType} uploaded successfully!${processingNote}`,
        });
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to upload media',
        });
      }
    } catch (error) {
      console.error('Failed to upload media:', error);
      setMessage({
        type: 'error',
        text: 'Failed to upload media',
      });
    } finally {
      setUploading(false);
    }
  };

  // Handle posting to LinkedIn
  const handlePost = async () => {
    if (!postText.trim()) {
      setMessage({
        type: 'error',
        text: 'Please enter some text for your post',
      });
      return;
    }

    setPosting(true);
    try {
      const response = await apiClient.post('/automation/linkedin/post/', { 
        title: postTitle.trim() || undefined,
        text: postText,
        media_urns: postMediaUrns.length > 0 ? postMediaUrns : undefined,
      });
      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: data.test_mode 
            ? '🧪 Post created successfully (Test Mode - not actually posted)' 
            : `Post published to LinkedIn successfully!${data.has_media ? ' (with image)' : ''}`,
        });
        setPostTitle('');
        setPostText('');
        setPostMediaUrns([]);
        setShowComposeModal(false);
        // Refresh published posts list
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to create post',
        });
      }
    } catch (error) {
      console.error('Failed to post:', error);
      setMessage({
        type: 'error',
        text: 'Failed to create post',
      });
    } finally {
      setPosting(false);
    }
  };

  // Handle scheduling a post
  const handleSchedulePost = async () => {
    if (!scheduleTitle.trim() || !scheduleContent.trim() || !scheduleDate || !scheduleTime) {
      setMessage({
        type: 'error',
        text: 'Please fill in all fields',
      });
      return;
    }

    // Create a proper Date object from local date/time and convert to ISO string
    // This preserves the local timezone information
    const localDateTime = new Date(`${scheduleDate}T${scheduleTime}:00`);
    const scheduledDateTime = localDateTime.toISOString();
    
    setScheduling(true);
    try {
      const response = await apiClient.post('/automation/content-calendar/', {
        title: scheduleTitle,
        content: scheduleContent,
        media_urls: scheduleMediaUrns.length > 0 ? scheduleMediaUrns : [],
        platforms: ['linkedin'],
        scheduled_date: scheduledDateTime,
        status: 'scheduled',
      });
      
      if (response.ok) {
        setMessage({
          type: 'success',
          text: `Post scheduled successfully!${scheduleMediaUrns.length > 0 ? ' (with image)' : ''}`,
        });
        setScheduleTitle('');
        setScheduleContent('');
        setScheduleDate('');
        setScheduleTime('');
        setScheduleMediaUrns([]);
        setShowScheduleModal(false);
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to schedule post',
        });
      }
    } catch (error) {
      console.error('Failed to schedule:', error);
      setMessage({
        type: 'error',
        text: 'Failed to schedule post',
      });
    } finally {
      setScheduling(false);
    }
  };

  // Handle publishing a scheduled post
  const handlePublishNow = async (postId: number) => {
    try {
      const response = await apiClient.post(`/automation/content-calendar/${postId}/publish/`, {});
      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: data.message,
        });
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to publish',
        });
      }
    } catch (error) {
      console.error('Failed to publish:', error);
      setMessage({
        type: 'error',
        text: 'Failed to publish post',
      });
    }
  };

  // Handle cancelling a scheduled post
  const handleCancelScheduled = async (postId: number) => {
    try {
      const response = await apiClient.post(`/automation/content-calendar/${postId}/cancel/`, {});
      if (response.ok) {
        setMessage({
          type: 'success',
          text: 'Scheduled post cancelled',
        });
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to cancel',
        });
      }
    } catch (error) {
      console.error('Failed to cancel:', error);
    }
  };

  // Open edit modal with post data
  const openEditModal = (post: ScheduledPost) => {
    setEditingPost(post);
    setEditTitle(post.title);
    setEditContent(post.content);
    // Parse the scheduled date/time
    const date = new Date(post.scheduled_date);
    setEditDate(date.toISOString().split('T')[0]);
    setEditTime(date.toTimeString().slice(0, 5));
    // Load existing media if any
    setEditMediaUrns(post.media_urls || []);
    setShowEditModal(true);
  };

  // Handle updating a scheduled post
  const handleEditPost = async () => {
    if (!editingPost) return;
    
    setEditing(true);
    try {
      const scheduledDate = new Date(`${editDate}T${editTime}`);
      
      const response = await apiClient.put(`/automation/content-calendar/${editingPost.id}/`, {
        title: editTitle,
        content: editContent,
        media_urls: editMediaUrns,
        platforms: editingPost.platforms,
        scheduled_date: scheduledDate.toISOString(),
        status: 'scheduled',
      });

      if (response.ok) {
        setMessage({
          type: 'success',
          text: `Post updated successfully!${editMediaUrns.length > 0 ? ' (with image)' : ''}`,
        });
        setShowEditModal(false);
        setEditingPost(null);
        setEditMediaUrns([]);
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to update post',
        });
      }
    } catch (error) {
      console.error('Failed to update post:', error);
      setMessage({
        type: 'error',
        text: 'Failed to update post. Please try again.',
      });
    } finally {
      setEditing(false);
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
                  <div className="mt-4 p-3 bg-white/5 rounded-lg flex items-center justify-between">
                    <a 
                      href={platformStatus.profile_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-brand-electric hover:underline"
                    >
                      View Profile →
                    </a>
                    {platform === 'linkedin' && (
                      <button
                        onClick={() => setShowComposeModal(true)}
                        className="text-sm text-brand-mint hover:text-brand-mint/80 flex items-center gap-1"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Create Post
                      </button>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="mt-6 space-y-2">
                  {isConnected ? (
                    <>
                      {platform === 'linkedin' && (
                        <button
                          onClick={() => setShowComposeModal(true)}
                          className="w-full py-2.5 px-4 rounded-lg bg-brand-electric hover:bg-brand-electric/80 text-brand-midnight font-bold transition-colors"
                        >
                          📝 Compose Post
                        </button>
                      )}
                      <button
                        onClick={() => handleDisconnect(platform)}
                        disabled={isLoading}
                        className="w-full py-2.5 px-4 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-900/20 transition-colors disabled:opacity-50"
                      >
                        {isLoading ? 'Disconnecting...' : 'Disconnect'}
                      </button>
                    </>
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
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-heading font-bold text-white">Content Calendar</h2>
            {profiles?.linkedin?.connected && (
              <button
                onClick={() => setShowScheduleModal(true)}
                className="btn-primary flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Schedule Post
              </button>
            )}
          </div>
          
          {scheduledPosts.length > 0 ? (
            <div className="space-y-4">
              {scheduledPosts.map((post) => {
                const isOverdue = new Date(post.scheduled_date) < new Date();
                return (
                <div key={post.id} className={`glass-card p-4 ${isOverdue ? 'border border-yellow-500/30' : ''}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="text-white font-medium">{post.title}</h4>
                        {isOverdue && (
                          <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full">
                            Overdue
                          </span>
                        )}
                      </div>
                      <p className="text-brand-silver/70 text-sm mt-1 line-clamp-2">{post.content}</p>
                      <div className="flex items-center gap-4 mt-3">
                        <span className={`text-xs flex items-center gap-1 ${isOverdue ? 'text-yellow-400' : 'text-brand-electric'}`}>
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          {new Date(post.scheduled_date).toLocaleString(undefined, {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                            timeZoneName: 'short'
                          })}
                        </span>
                        <span className="text-xs text-brand-silver/50">
                          {post.platforms.join(', ')}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => openEditModal(post)}
                        className="px-3 py-1.5 text-xs rounded border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
                        title="Edit post"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handlePublishNow(post.id)}
                        className="px-3 py-1.5 text-xs rounded bg-brand-electric hover:bg-brand-electric/80 text-brand-midnight font-bold transition-colors"
                      >
                        Publish Now
                      </button>
                      <button
                        onClick={() => handleCancelScheduled(post.id)}
                        className="px-3 py-1.5 text-xs rounded border border-red-500/30 text-red-400 hover:bg-red-900/20 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              );})}
            </div>
          ) : (
            <div className="glass-card p-8 text-center">
              <div className="w-16 h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-brand-electric" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No Scheduled Posts</h3>
              <p className="text-brand-silver/70 mb-6 max-w-md mx-auto">
                {profiles?.linkedin?.connected 
                  ? "You don't have any posts scheduled. Click 'Schedule Post' to create one."
                  : "Connect your social accounts first, then start scheduling posts to be published automatically."
                }
              </p>
              {profiles?.linkedin?.connected && (
                <button 
                  onClick={() => setShowScheduleModal(true)}
                  className="btn-primary"
                >
                  Schedule Your First Post
                </button>
              )}
            </div>
          )}
        </div>

        {/* Published Posts Section */}
        <div className="mt-12">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-heading font-bold text-white">Published Posts</h2>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm text-brand-silver">Show:</label>
                <select
                  value={publishedPostsLimit}
                  onChange={(e) => {
                    const newLimit = Number(e.target.value);
                    setPublishedPostsLimit(newLimit);
                    fetchPublishedPosts(newLimit);
                  }}
                  className="bg-brand-midnight border border-brand-ghost/30 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                >
                  <option value={3}>3 posts</option>
                  <option value={6}>6 posts</option>
                  <option value={10}>10 posts</option>
                </select>
              </div>
              <button
                onClick={() => { fetchScheduledPosts(); fetchPublishedPosts(); }}
                className="text-sm text-brand-electric hover:text-brand-electric/80 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>
          </div>
          
          {publishedPosts.length > 0 ? (
            <div className="space-y-4">
              {publishedPosts.map((post) => (
                <div key={post.id} className="glass-card p-4 border border-green-500/20">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="text-white font-medium">{post.title}</h4>
                        <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                          Published
                        </span>
                        {post.status_display?.includes('test') && (
                          <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full">
                            Test Mode
                          </span>
                        )}
                      </div>
                      <p className="text-brand-silver/70 text-sm mt-1 line-clamp-2">{post.content}</p>
                      <div className="flex items-center gap-4 mt-3">
                        <span className="text-xs text-green-400 flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          {new Date(post.scheduled_date).toLocaleString(undefined, {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                        <span className="text-xs text-brand-silver/50">
                          {post.platforms.join(', ')}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card p-8 text-center">
              <div className="w-16 h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No Published Posts Yet</h3>
              <p className="text-brand-silver/70 max-w-md mx-auto">
                Once your scheduled posts are published (automatically or manually), they&apos;ll appear here.
              </p>
            </div>
          )}
        </div>

        {/* Automation Tasks Section */}
        <div className="mt-12">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-heading font-bold text-white">Automation Tasks</h2>
            <button
              onClick={fetchAutomationTasks}
              className="text-sm text-brand-electric hover:text-brand-electric/80 flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
          
          {automationTasks.length > 0 ? (
            <div className="space-y-3">
              {automationTasks.map((task) => (
                <div key={task.id} className="glass-card p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {/* Task Type Icon */}
                      <div className={`p-2 rounded-lg ${
                        task.task_type === 'social_post' ? 'bg-blue-500/20 text-blue-400' :
                        task.task_type === 'profile_sync' ? 'bg-purple-500/20 text-purple-400' :
                        task.task_type === 'content_schedule' ? 'bg-brand-electric/20 text-brand-electric' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {task.task_type === 'social_post' ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                          </svg>
                        ) : task.task_type === 'profile_sync' ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        )}
                      </div>
                      
                      <div>
                        <h4 className="text-white font-medium">{task.task_type_display}</h4>
                        <p className="text-xs text-brand-silver/70">
                          {new Date(task.created_at).toLocaleString(undefined, {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                    </div>
                    
                    {/* Status Badge */}
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                      task.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      task.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                      task.status === 'in_progress' ? 'bg-yellow-500/20 text-yellow-400' :
                      task.status === 'pending' ? 'bg-blue-500/20 text-blue-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {task.status_display}
                    </span>
                  </div>
                  
                  {/* Error message if failed */}
                  {task.status === 'failed' && task.error_message && (
                    <div className="mt-3 p-2 bg-red-900/20 border border-red-500/30 rounded text-xs text-red-300">
                      {task.error_message}
                    </div>
                  )}
                  
                  {/* Result preview for completed tasks */}
                  {task.status === 'completed' && task.result && Object.keys(task.result).length > 0 && (
                    <div className="mt-3 p-2 bg-green-900/10 border border-green-500/20 rounded text-xs text-green-300/70">
                      {task.result.test_mode ? '✓ Test mode - simulated' : '✓ Successfully completed'}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card p-8 text-center">
              <div className="w-16 h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-brand-electric" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No Automation Tasks Yet</h3>
              <p className="text-brand-silver/70 max-w-md mx-auto">
                {profiles?.linkedin?.connected 
                  ? "Your automation tasks will appear here as you post and schedule content."
                  : "Connect your social accounts to start tracking automation tasks."
                }
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Compose Post Modal */}
      {showComposeModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg p-6 relative">
            {/* Close button */}
            <button
              onClick={() => {
                setShowComposeModal(false);
                setPostTitle('');
                setPostText('');
              }}
              className="absolute top-4 right-4 text-brand-silver hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-[#0A66C2] text-white">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-white">Create LinkedIn Post</h2>
                <p className="text-sm text-brand-silver/70">
                  Share your thoughts with your network
                </p>
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Title</label>
                <input
                  type="text"
                  value={postTitle}
                  onChange={(e) => setPostTitle(e.target.value)}
                  placeholder="Give your post a title (optional)"
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Content</label>
                <textarea
                  value={postText}
                  onChange={(e) => setPostText(e.target.value)}
                  placeholder="What do you want to talk about?"
                  rows={6}
                  maxLength={3000}
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 resize-none"
                />
                <div className="flex justify-between items-center mt-1 text-xs">
                  <span className={`${postText.length > 2800 ? 'text-amber-400' : 'text-brand-silver/50'}`}>
                    {postText.length} / 3,000 characters
                  </span>
                  {profiles?.linkedin?.access_token === 'test_access_token_not_real' && (
                    <span className="text-amber-400 flex items-center gap-1">
                      <span>🧪</span> Test Mode
                    </span>
                  )}
                </div>
              </div>

              {/* Media Upload */}
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Media (optional)</label>
                <div className="flex items-center gap-3">
                  <label className={`flex items-center gap-2 px-4 py-2 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors cursor-pointer ${uploadingMedia ? 'opacity-50 cursor-not-allowed' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {uploadingMedia ? 'Uploading...' : 'Add Media'}
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/gif,video/mp4"
                      className="hidden"
                      disabled={uploadingMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          handleMediaUpload(file, setPostMediaUrns, setUploadingMedia);
                        }
                        e.target.value = '';
                      }}
                    />
                  </label>
                  {postMediaUrns.length > 0 && (
                    <div className="flex items-center gap-2 text-green-400 text-sm">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {postMediaUrns.length} file{postMediaUrns.length > 1 ? 's' : ''} attached
                      <button
                        onClick={() => setPostMediaUrns([])}
                        className="text-red-400 hover:text-red-300 ml-2"
                        title="Remove media"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
                <p className="text-xs text-brand-silver/50 mt-1">Images: JPEG, PNG, GIF (max 8MB) • Video: MP4 (max 500MB)</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowComposeModal(false);
                  setPostTitle('');
                  setPostText('');
                  setPostMediaUrns([]);
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handlePost}
                disabled={posting || uploadingMedia || !postText.trim()}
                className="px-6 py-2.5 rounded-lg bg-[#0A66C2] hover:bg-[#004182] text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {posting ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Posting...
                  </>
                ) : (
                  'Post'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Schedule Post Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg p-6 relative">
            {/* Close button */}
            <button
              onClick={() => {
                setShowScheduleModal(false);
                setScheduleTitle('');
                setScheduleContent('');
                setScheduleDate('');
                setScheduleTime('');
              }}
              className="absolute top-4 right-4 text-brand-silver hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-brand-electric text-white">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-white">Schedule Post</h2>
                <p className="text-sm text-brand-silver/70">
                  Schedule content to be posted later
                </p>
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Title</label>
                <input
                  type="text"
                  value={scheduleTitle}
                  onChange={(e) => setScheduleTitle(e.target.value)}
                  placeholder="Give your post a title"
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Content</label>
                <textarea
                  value={scheduleContent}
                  onChange={(e) => setScheduleContent(e.target.value)}
                  placeholder="What do you want to share?"
                  rows={4}
                  maxLength={3000}
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 resize-none"
                />
                <div className="text-xs text-brand-silver/50 mt-1">
                  {scheduleContent.length} / 3,000 characters
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-brand-silver mb-1">Date</label>
                  <input
                    type="date"
                    value={scheduleDate}
                    onChange={(e) => setScheduleDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-brand-silver mb-1">Time</label>
                  <input
                    type="time"
                    value={scheduleTime}
                    onChange={(e) => setScheduleTime(e.target.value)}
                    className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                  />
                </div>
              </div>
              
              <div className="p-3 bg-white/5 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded bg-[#0A66C2]">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </div>
                  <span className="text-sm text-white">LinkedIn</span>
                  <span className="text-xs text-brand-silver/50 ml-auto">Selected</span>
                </div>
              </div>

              {/* Media Upload for Schedule */}
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Media (optional)</label>
                <div className="flex items-center gap-3">
                  <label className={`flex items-center gap-2 px-4 py-2 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors cursor-pointer ${uploadingScheduleMedia ? 'opacity-50 cursor-not-allowed' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {uploadingScheduleMedia ? 'Uploading...' : 'Add Media'}
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/gif,video/mp4"
                      className="hidden"
                      disabled={uploadingScheduleMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          handleMediaUpload(file, setScheduleMediaUrns, setUploadingScheduleMedia);
                        }
                        e.target.value = '';
                      }}
                    />
                  </label>
                  {scheduleMediaUrns.length > 0 && (
                    <div className="flex items-center gap-2 text-green-400 text-sm">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {scheduleMediaUrns.length} file{scheduleMediaUrns.length > 1 ? 's' : ''} attached
                      <button
                        onClick={() => setScheduleMediaUrns([])}
                        className="text-red-400 hover:text-red-300 ml-2"
                        title="Remove media"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
                <p className="text-xs text-brand-silver/50 mt-1">Images: JPEG, PNG, GIF (max 8MB) • Video: MP4 (max 500MB)</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowScheduleModal(false);
                  setScheduleTitle('');
                  setScheduleContent('');
                  setScheduleDate('');
                  setScheduleTime('');
                  setScheduleMediaUrns([]);
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSchedulePost}
                disabled={scheduling || uploadingScheduleMedia || !scheduleTitle.trim() || !scheduleContent.trim() || !scheduleDate || !scheduleTime}
                className="px-6 py-2.5 rounded-lg bg-brand-electric hover:bg-brand-electric/80 text-brand-midnight font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {scheduling ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Scheduling...
                  </>
                ) : (
                  'Schedule Post'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Post Modal */}
      {showEditModal && editingPost && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg p-6 relative">
            {/* Close button */}
            <button
              onClick={() => {
                setShowEditModal(false);
                setEditingPost(null);
                setEditTitle('');
                setEditContent('');
                setEditDate('');
                setEditTime('');
                setEditMediaUrns([]);
              }}
              className="absolute top-4 right-4 text-brand-silver hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-brand-electric text-white">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-white">Edit Scheduled Post</h2>
                <p className="text-sm text-brand-silver/70">
                  Update your scheduled post details
                </p>
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Title</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Give your post a title"
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Content</label>
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  placeholder="What do you want to share?"
                  rows={4}
                  maxLength={3000}
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 resize-none"
                />
                <div className="text-xs text-brand-silver/50 mt-1">
                  {editContent.length} / 3,000 characters
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-brand-silver mb-1">Date</label>
                  <input
                    type="date"
                    value={editDate}
                    onChange={(e) => setEditDate(e.target.value)}
                    className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-brand-silver mb-1">Time</label>
                  <input
                    type="time"
                    value={editTime}
                    onChange={(e) => setEditTime(e.target.value)}
                    className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                  />
                </div>
              </div>
              
              <div className="p-3 bg-white/5 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded bg-[#0A66C2]">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </div>
                  <span className="text-sm text-white">LinkedIn</span>
                  <span className="text-xs text-brand-silver/50 ml-auto">
                    {editingPost.platforms.join(', ')}
                  </span>
                </div>
              </div>

              {/* Media Upload for Edit */}
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Media (optional)</label>
                <div className="flex items-center gap-3">
                  <label className={`flex items-center gap-2 px-4 py-2 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors cursor-pointer ${uploadingEditMedia ? 'opacity-50 cursor-not-allowed' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {uploadingEditMedia ? 'Uploading...' : 'Add Media'}
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/gif,video/mp4"
                      className="hidden"
                      disabled={uploadingEditMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          handleMediaUpload(file, setEditMediaUrns, setUploadingEditMedia);
                        }
                        e.target.value = '';
                      }}
                    />
                  </label>
                  {editMediaUrns.length > 0 && (
                    <div className="flex items-center gap-2 text-green-400 text-sm">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {editMediaUrns.length} file{editMediaUrns.length > 1 ? 's' : ''} attached
                      <button
                        onClick={() => setEditMediaUrns([])}
                        className="text-red-400 hover:text-red-300 ml-2"
                        title="Remove media"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
                <p className="text-xs text-brand-silver/50 mt-1">Images: JPEG, PNG, GIF (max 8MB) • Video: MP4 (max 500MB)</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingPost(null);
                  setEditTitle('');
                  setEditContent('');
                  setEditDate('');
                  setEditTime('');
                  setEditMediaUrns([]);
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleEditPost}
                disabled={editing || uploadingEditMedia || !editTitle.trim() || !editContent.trim() || !editDate || !editTime}
                className="px-6 py-2.5 rounded-lg bg-brand-electric hover:bg-brand-electric/80 text-brand-midnight font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {editing ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
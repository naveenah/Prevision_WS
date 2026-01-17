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
    available: true, // Twitter/X integration enabled
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
    available: true, // Facebook Page integration enabled
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
  post_results?: {
    id?: string;
    text?: string;
    created_at?: string;
    author_id?: string;
    [key: string]: unknown;
  };
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

// Media upload constants (LinkedIn standards)
const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif'] as const;
const VIDEO_TYPES = ['video/mp4'] as const;
const DOCUMENT_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
] as const;

// LinkedIn media size limits
const LINKEDIN_MAX_IMAGE_SIZE = 8 * 1024 * 1024;  // 8MB
const LINKEDIN_MAX_VIDEO_SIZE = 500 * 1024 * 1024;  // 500MB
const LINKEDIN_MAX_DOCUMENT_SIZE = 100 * 1024 * 1024;  // 100MB

// Twitter media size limits
const TWITTER_MAX_IMAGE_SIZE = 5 * 1024 * 1024;  // 5MB
const TWITTER_MAX_VIDEO_SIZE = 512 * 1024 * 1024;  // 512MB

// Facebook media size limits
const FACEBOOK_MAX_IMAGE_SIZE = 4 * 1024 * 1024;  // 4MB
const FACEBOOK_MAX_VIDEO_SIZE = 1024 * 1024 * 1024;  // 1GB
const FACEBOOK_MAX_POST_LENGTH = 63206;  // Facebook page post limit

// Shared image size limit (use smaller of the platforms)
const MAX_IMAGE_SIZE = LINKEDIN_MAX_IMAGE_SIZE;

// Twitter constants
const TWITTER_MAX_LENGTH = 280;

// Helper function to get media limits based on selected platforms
const getMediaLimits = (platforms: string[]) => {
  const hasTwitter = platforms.includes('twitter');
  const hasLinkedIn = platforms.includes('linkedin');
  const hasFacebook = platforms.includes('facebook');
  
  // If no platforms selected, use LinkedIn defaults (most permissive for documents)
  if (!hasTwitter && !hasLinkedIn && !hasFacebook) {
    return {
      maxImageSize: LINKEDIN_MAX_IMAGE_SIZE,
      maxVideoSize: LINKEDIN_MAX_VIDEO_SIZE,
      maxDocumentSize: LINKEDIN_MAX_DOCUMENT_SIZE,
      imageSizeLabel: '8MB',
      videoSizeLabel: '500MB',
      documentSizeLabel: '100MB',
      supportsDocuments: true,
    };
  }
  
  // Calculate the most restrictive limits across all selected platforms
  let maxImage = Infinity;
  let maxVideo = Infinity;
  let maxDocument = Infinity;
  let supportsDocuments = true;
  
  if (hasLinkedIn) {
    maxImage = Math.min(maxImage, LINKEDIN_MAX_IMAGE_SIZE);
    maxVideo = Math.min(maxVideo, LINKEDIN_MAX_VIDEO_SIZE);
    maxDocument = Math.min(maxDocument, LINKEDIN_MAX_DOCUMENT_SIZE);
  }
  
  if (hasTwitter) {
    maxImage = Math.min(maxImage, TWITTER_MAX_IMAGE_SIZE);
    maxVideo = Math.min(maxVideo, TWITTER_MAX_VIDEO_SIZE);
    supportsDocuments = false; // Twitter doesn't support documents
  }
  
  if (hasFacebook) {
    maxImage = Math.min(maxImage, FACEBOOK_MAX_IMAGE_SIZE);
    maxVideo = Math.min(maxVideo, FACEBOOK_MAX_VIDEO_SIZE);
    supportsDocuments = false; // Facebook doesn't support document uploads
  }
  
  // If Twitter or Facebook selected, documents not supported
  if (!supportsDocuments) {
    maxDocument = 0;
  }
  
  // Format size labels
  const formatSize = (bytes: number) => {
    if (bytes >= 1024 * 1024 * 1024) return `${bytes / (1024 * 1024 * 1024)}GB`;
    return `${bytes / (1024 * 1024)}MB`;
  };
  
  return {
    maxImageSize: maxImage === Infinity ? LINKEDIN_MAX_IMAGE_SIZE : maxImage,
    maxVideoSize: maxVideo === Infinity ? LINKEDIN_MAX_VIDEO_SIZE : maxVideo,
    maxDocumentSize: supportsDocuments ? maxDocument : 0,
    imageSizeLabel: formatSize(maxImage === Infinity ? LINKEDIN_MAX_IMAGE_SIZE : maxImage),
    videoSizeLabel: formatSize(maxVideo === Infinity ? LINKEDIN_MAX_VIDEO_SIZE : maxVideo),
    documentSizeLabel: supportsDocuments ? formatSize(maxDocument) : 'N/A',
    supportsDocuments,
  };
};

// Helper function to extract post ID for a specific platform from post_results
// Handles both single-platform and multi-platform post structures
// Returns 'test_mode' for test mode posts without an ID (allows calendar deletion)
const getPostIdForPlatform = (postResults: Record<string, unknown> | undefined, platform: string): string | null => {
  if (!postResults) return null;

  // Check for platform-specific nested structure (multi-platform posts)
  const platformData = postResults[platform] as Record<string, unknown> | undefined;
  if (platformData) {
    // LinkedIn: { linkedin: { post_urn: "..." } } or { linkedin: { id: "..." } }
    if (platform === 'linkedin') {
      return (platformData.post_urn as string) || (platformData.id as string) || 
        (platformData.test_mode ? 'test_mode' : null);
    }
    // Twitter: { twitter: { id: "..." } } or { twitter: { tweet: { id: "..." } } }
    if (platform === 'twitter') {
      const tweetData = platformData.tweet as Record<string, unknown> | undefined;
      return (platformData.id as string) || (tweetData?.id as string) || 
        (platformData.test_mode ? 'test_mode' : null);
    }
    // Facebook: { facebook: { id: "...", post_id: "...", video_id: "..." } }
    if (platform === 'facebook') {
      return (platformData.id as string) || (platformData.post_id as string) || (platformData.video_id as string) || 
        (platformData.test_mode ? 'test_mode' : null);
    }
  }

  // Check for direct structure (single-platform posts)
  // Twitter: { tweet: { id: "..." } } or { id: "..." }
  if (platform === 'twitter') {
    const tweetData = postResults.tweet as Record<string, unknown> | undefined;
    return (postResults.id as string) || (tweetData?.id as string) || 
      (postResults.test_mode ? 'test_mode' : null);
  }
  // LinkedIn: { post_urn: "..." } or { id: "..." }
  if (platform === 'linkedin') {
    return (postResults.post_urn as string) || (postResults.id as string) || 
      (postResults.test_mode ? 'test_mode' : null);
  }
  // Facebook: { id: "...", post_id: "...", video_id: "..." }
  if (platform === 'facebook') {
    return (postResults.id as string) || (postResults.post_id as string) || (postResults.video_id as string) || 
      (postResults.test_mode ? 'test_mode' : null);
  }

  return null;
};

// Helper function to check if any platform has a deletable post ID
// Returns true if we should show delete button (even for posts without IDs to allow calendar cleanup)
const hasAnyDeletablePostId = (postResults: Record<string, unknown> | undefined | null, platforms: string[]): boolean => {
  // Always allow deletion if there are platforms - allows cleaning up posts from calendar
  // even if they don't have post_results (failed posts, old posts, etc.)
  if (platforms && platforms.length > 0) {
    return true;
  }
  return false;
};

// Helper function to get media helper text based on selected platforms
const getMediaHelperText = (platforms: string[]) => {
  const limits = getMediaLimits(platforms);
  const hasTwitter = platforms.includes('twitter');
  const hasFacebook = platforms.includes('facebook');
  
  if ((hasTwitter || hasFacebook) && !limits.supportsDocuments) {
    return `Images: JPEG, PNG, GIF (max ${limits.imageSizeLabel}) • Video: MP4 (max ${limits.videoSizeLabel}) • Note: Documents not supported on ${hasTwitter && hasFacebook ? 'Twitter/Facebook' : hasTwitter ? 'Twitter' : 'Facebook'}`;
  }
  
  return `Images: JPEG, PNG, GIF (max ${limits.imageSizeLabel}) • Video: MP4 (max ${limits.videoSizeLabel}) • Documents: PDF, DOC, PPT (max ${limits.documentSizeLabel})`;
};

// File input accept attribute - all supported media types
const ACCEPTED_FILE_TYPES = [
  ...IMAGE_TYPES,
  ...VIDEO_TYPES,
  ...DOCUMENT_TYPES,
].join(',');

// Get accepted file types based on platforms
const getAcceptedFileTypes = (platforms: string[]) => {
  const limits = getMediaLimits(platforms);
  if (!limits.supportsDocuments) {
    return [...IMAGE_TYPES, ...VIDEO_TYPES].join(',');
  }
  return ACCEPTED_FILE_TYPES;
};

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
  const [postMediaPreview, setPostMediaPreview] = useState<{ url: string; type: 'image' | 'video' } | null>(null);
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
  const [scheduleMediaPreview, setScheduleMediaPreview] = useState<{ url: string; type: 'image' | 'video' } | null>(null);
  const [uploadingScheduleMedia, setUploadingScheduleMedia] = useState(false);
  const [schedulePlatforms, setSchedulePlatforms] = useState<string[]>(['linkedin']);

  // Edit post state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingPost, setEditingPost] = useState<ScheduledPost | null>(null);
  const [editPlatforms, setEditPlatforms] = useState<string[]>([]);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editDate, setEditDate] = useState('');
  const [editTime, setEditTime] = useState('');
  const [editing, setEditing] = useState(false);
  const [editMediaUrns, setEditMediaUrns] = useState<string[]>([]);
  const [uploadingEditMedia, setUploadingEditMedia] = useState(false);

  // Automation tasks state
  const [automationTasks, setAutomationTasks] = useState<AutomationTask[]>([]);

  // Twitter compose state
  const [showTwitterComposeModal, setShowTwitterComposeModal] = useState(false);
  const [tweetTitle, setTweetTitle] = useState('');
  const [tweetText, setTweetText] = useState('');
  const [tweetMediaUrns, setTweetMediaUrns] = useState<string[]>([]);
  const [tweetMediaPreview, setTweetMediaPreview] = useState<{ url: string; type: 'image' | 'video' } | null>(null);
  const [tweetMediaAltText, setTweetMediaAltText] = useState('');
  const [uploadingTweetMedia, setUploadingTweetMedia] = useState(false);
  const [tweetPosting, setTweetPosting] = useState(false);
  // Reply/Quote tweet
  const [tweetReplyToId, setTweetReplyToId] = useState('');
  const [tweetQuoteId, setTweetQuoteId] = useState('');
  // Thread mode
  const [isThreadMode, setIsThreadMode] = useState(false);
  const [threadTweets, setThreadTweets] = useState<string[]>(['']);
  // Twitter Carousel mode (multi-image, max 4)
  const [twitterCarouselMode, setTwitterCarouselMode] = useState(false);
  const [twitterCarouselImages, setTwitterCarouselImages] = useState<{ url: string; file?: File; mediaId?: string }[]>([]);
  const [uploadingTwitterCarouselImage, setUploadingTwitterCarouselImage] = useState(false);
  // Deleting tweet
  const [deletingTweetId, setDeletingTweetId] = useState<string | null>(null);
  // Deleting LinkedIn post
  const [deletingLinkedInPostId, setDeletingLinkedInPostId] = useState<string | null>(null);
  // LinkedIn Carousel mode (multi-image, max 9)
  const [linkedinCarouselMode, setLinkedinCarouselMode] = useState(false);
  const [linkedinCarouselImages, setLinkedinCarouselImages] = useState<{ url: string; file?: File; mediaUrn?: string }[]>([]);
  const [uploadingLinkedinCarouselImage, setUploadingLinkedinCarouselImage] = useState(false);

  // Facebook compose state
  const [showFacebookComposeModal, setShowFacebookComposeModal] = useState(false);
  const [fbPostTitle, setFbPostTitle] = useState('');
  const [fbPostText, setFbPostText] = useState('');
  const [fbMediaUrns, setFbMediaUrns] = useState<string[]>([]);
  const [fbMediaPreview, setFbMediaPreview] = useState<{ url: string; type: 'image' | 'video' } | null>(null);
  const [uploadingFbMedia, setUploadingFbMedia] = useState(false);
  const [fbPosting, setFbPosting] = useState(false);
  // Carousel mode state
  const [fbCarouselMode, setFbCarouselMode] = useState(false);
  const [fbCarouselImages, setFbCarouselImages] = useState<{ url: string; file?: File }[]>([]);
  const [uploadingCarouselImage, setUploadingCarouselImage] = useState(false);
  // Stories state
  const [showFacebookStoriesModal, setShowFacebookStoriesModal] = useState(false);
  const [fbStories, setFbStories] = useState<Array<{ id: string; media_type: string; created_at: string; expires_at?: string }>>([]);
  const [loadingFbStories, setLoadingFbStories] = useState(false);
  // Multi-file story queue
  interface StoryQueueItem {
    id: string;
    file: File;
    type: 'photo' | 'video';
    preview: string;
    status: 'pending' | 'uploading' | 'success' | 'failed';
  }
  const [fbStoryQueue, setFbStoryQueue] = useState<StoryQueueItem[]>([]);
  const [postingFbStory, setPostingFbStory] = useState(false);
  const [storyUploadProgress, setStoryUploadProgress] = useState<{ current: number; total: number }>({ current: 0, total: 0 });
  const [deletingFbStoryId, setDeletingFbStoryId] = useState<string | null>(null);
  
  // Facebook Resumable Upload state (for large videos > 1GB)
  interface ResumableUpload {
    upload_session_id: string;
    file_name: string;
    file_size: number;
    bytes_uploaded: number;
    progress_percent: number;
    status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  }
  const [fbResumableUploads, setFbResumableUploads] = useState<ResumableUpload[]>([]);
  const [showResumableUploadModal, setShowResumableUploadModal] = useState(false);
  const [resumableUploadFile, setResumableUploadFile] = useState<File | null>(null);
  const [resumableUploadProgress, setResumableUploadProgress] = useState(0);
  const [resumableUploadStatus, setResumableUploadStatus] = useState<'idle' | 'uploading' | 'paused' | 'completed' | 'failed'>('idle');
  const [resumableUploadTitle, setResumableUploadTitle] = useState('');
  const [resumableUploadDescription, setResumableUploadDescription] = useState('');
  const [currentUploadSessionId, setCurrentUploadSessionId] = useState<string | null>(null);
  
  // Deleting Facebook post
  const [deletingFbPostId, setDeletingFbPostId] = useState<string | null>(null);
  // Deleting multi-platform post
  const [deletingPostId, setDeletingPostId] = useState<number | null>(null);

  // Facebook multi-page state
  interface FacebookPage {
    id: string;
    name: string;
    category?: string;
    picture?: { data?: { url?: string } };
    access_token?: string;
  }
  const [fbPages, setFbPages] = useState<FacebookPage[]>([]);
  const [loadingFbPages, setLoadingFbPages] = useState(false);
  const [showFbPageSwitcher, setShowFbPageSwitcher] = useState(false);
  const [switchingFbPage, setSwitchingFbPage] = useState(false);
  const [currentFbPage, setCurrentFbPage] = useState<{ id: string; name: string } | null>(null);

  // Fetch Facebook pages
  const fetchFacebookPages = useCallback(async () => {
    if (!profiles?.facebook?.connected) return;
    
    setLoadingFbPages(true);
    try {
      const response = await apiClient.get('/automation/facebook/pages/');
      if (response.ok) {
        const data = await response.json();
        setFbPages(data.pages || []);
        if (data.current_page) {
          setCurrentFbPage(data.current_page);
        }
      }
    } catch (error) {
      console.error('Failed to fetch Facebook pages:', error);
    } finally {
      setLoadingFbPages(false);
    }
  }, [profiles?.facebook?.connected]);

  // Switch Facebook page
  const handleSwitchFacebookPage = async (pageId: string) => {
    setSwitchingFbPage(true);
    try {
      const response = await apiClient.post('/automation/facebook/pages/select/', {
        page_id: pageId,
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentFbPage({ id: data.page_id, name: data.page_name });
        setShowFbPageSwitcher(false);
        setMessage({
          type: 'success',
          text: `Switched to page: ${data.page_name}`,
        });
        // Refresh profiles to update status
        fetchProfiles();
      } else {
        const errorData = await response.json();
        setMessage({
          type: 'error',
          text: errorData.error || 'Failed to switch page',
        });
      }
    } catch (error) {
      console.error('Failed to switch Facebook page:', error);
      setMessage({
        type: 'error',
        text: 'Failed to switch page. Please try again.',
      });
    } finally {
      setSwitchingFbPage(false);
    }
  };

  // LinkedIn multi-organization (Company Page) state
  interface LinkedInOrganization {
    id: string;
    urn: string;
    name: string;
    vanity_name?: string;
    logo_url?: string;
  }
  const [linkedInOrgs, setLinkedInOrgs] = useState<LinkedInOrganization[]>([]);
  const [loadingLinkedInOrgs, setLoadingLinkedInOrgs] = useState(false);
  const [showLinkedInOrgSwitcher, setShowLinkedInOrgSwitcher] = useState(false);
  const [switchingLinkedInOrg, setSwitchingLinkedInOrg] = useState(false);
  const [currentLinkedInOrg, setCurrentLinkedInOrg] = useState<{ id: string; name: string } | null>(null);
  const [linkedInPostingAs, setLinkedInPostingAs] = useState<'personal' | 'organization'>('personal');

  // Twitter account panel state
  const [showTwitterAccountPanel, setShowTwitterAccountPanel] = useState(false);

  // Fetch LinkedIn organizations
  const fetchLinkedInOrganizations = useCallback(async () => {
    if (!profiles?.linkedin?.connected) return;
    
    setLoadingLinkedInOrgs(true);
    try {
      const response = await apiClient.get('/automation/linkedin/organizations/');
      if (response.ok) {
        const data = await response.json();
        setLinkedInOrgs(data.organizations || []);
        setLinkedInPostingAs(data.posting_as || 'personal');
        if (data.current_organization && data.organizations) {
          const currentOrg = data.organizations.find((org: LinkedInOrganization) => org.id === data.current_organization);
          if (currentOrg) {
            setCurrentLinkedInOrg({ id: currentOrg.id, name: currentOrg.name });
          }
        } else {
          setCurrentLinkedInOrg(null);
        }
      }
    } catch (error) {
      console.error('Failed to fetch LinkedIn organizations:', error);
    } finally {
      setLoadingLinkedInOrgs(false);
    }
  }, [profiles?.linkedin?.connected]);

  // Switch LinkedIn posting entity (personal or organization)
  const handleSwitchLinkedInOrg = async (organizationId: string | null) => {
    setSwitchingLinkedInOrg(true);
    try {
      const response = await apiClient.post('/automation/linkedin/organizations/select/', {
        organization_id: organizationId,
      });
      
      if (response.ok) {
        const data = await response.json();
        if (organizationId) {
          const selectedOrg = linkedInOrgs.find(org => org.id === organizationId);
          setCurrentLinkedInOrg(selectedOrg ? { id: selectedOrg.id, name: selectedOrg.name } : null);
        } else {
          setCurrentLinkedInOrg(null);
        }
        setLinkedInPostingAs(data.posting_as);
        setShowLinkedInOrgSwitcher(false);
        setMessage({
          type: 'success',
          text: data.posting_as === 'personal' 
            ? 'Now posting as personal profile' 
            : `Now posting as: ${linkedInOrgs.find(org => org.id === organizationId)?.name || 'Organization'}`,
        });
        fetchProfiles();
      } else {
        const errorData = await response.json();
        setMessage({
          type: 'error',
          text: errorData.error || 'Failed to switch posting entity',
        });
      }
    } catch (error) {
      console.error('Failed to switch LinkedIn organization:', error);
      setMessage({
        type: 'error',
        text: 'Failed to switch. Please try again.',
      });
    } finally {
      setSwitchingLinkedInOrg(false);
    }
  };

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

  // Fetch social profiles (for refresh after actions)
  const fetchProfiles = useCallback(async () => {
    try {
      const response = await apiClient.get('/automation/social-profiles/status/');
      if (response.ok) {
        const data = await response.json();
        setProfiles(data);
      }
    } catch (error) {
      console.error('Failed to fetch profiles:', error);
    }
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

  // Fetch Facebook pages when connected
  useEffect(() => {
    if (profiles?.facebook?.connected) {
      fetchFacebookPages();
    }
  }, [profiles?.facebook?.connected, fetchFacebookPages]);

  // Fetch LinkedIn organizations when connected
  useEffect(() => {
    if (profiles?.linkedin?.connected) {
      fetchLinkedInOrganizations();
    }
  }, [profiles?.linkedin?.connected, fetchLinkedInOrganizations]);

  const handleConnect = async (platform: string) => {
    if (platform !== 'linkedin' && platform !== 'twitter' && platform !== 'facebook') {
      setMessage({
        type: 'error',
        text: `${PLATFORM_CONFIG[platform as keyof typeof PLATFORM_CONFIG].name} integration coming soon!`,
      });
      return;
    }

    setConnecting(platform);
    try {
      const response = await apiClient.get(`/automation/${platform}/connect/`);
      if (response.ok) {
        const data = await response.json();
        // Redirect to platform authorization
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

  // Test connection (dev mode only - no real platform data)
  const handleTestConnect = async (platform: string) => {
    if (platform !== 'linkedin' && platform !== 'twitter' && platform !== 'facebook') return;

    setConnecting(platform);
    try {
      const response = await apiClient.post(`/automation/${platform}/test-connect/`, {});
      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: `${data.message} (Test Mode - No real ${PLATFORM_CONFIG[platform as keyof typeof PLATFORM_CONFIG].name} data)`,
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
    if (platform !== 'linkedin' && platform !== 'twitter' && platform !== 'facebook') return;

    setConnecting(platform);
    try {
      const response = await apiClient.post(`/automation/${platform}/disconnect/`, {});
      if (response.ok) {
        setMessage({
          type: 'success',
          text: `${PLATFORM_CONFIG[platform as keyof typeof PLATFORM_CONFIG].name} disconnected successfully`,
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

  // Handle media upload for posts (images, videos, and documents)
  const handleMediaUpload = async (
    file: File,
    setMediaUrns: React.Dispatch<React.SetStateAction<string[]>>,
    setUploading: React.Dispatch<React.SetStateAction<boolean>>,
    platforms: string[] = ['linkedin'] // Default to LinkedIn for backward compatibility
  ) => {
    const limits = getMediaLimits(platforms);
    
    // Validate file type using constants
    const isImage = (IMAGE_TYPES as readonly string[]).includes(file.type);
    const isVideo = (VIDEO_TYPES as readonly string[]).includes(file.type);
    const isDocument = (DOCUMENT_TYPES as readonly string[]).includes(file.type);

    if (!isImage && !isVideo && !isDocument) {
      setMessage({
        type: 'error',
        text: 'Invalid file type. Allowed: JPEG, PNG, GIF (images); MP4 (video); PDF, DOC, DOCX, PPT, PPTX (documents)',
      });
      return;
    }

    // Check if documents are supported for the selected platforms
    if (isDocument && !limits.supportsDocuments) {
      setMessage({
        type: 'error',
        text: 'Documents are not supported on Twitter or Facebook. Please upload an image or video instead.',
      });
      return;
    }

    // Validate file size using platform-specific limits
    let maxSize: number;
    let sizeLabel: string;
    if (isVideo) {
      maxSize = limits.maxVideoSize;
      sizeLabel = limits.videoSizeLabel;
    } else if (isDocument) {
      maxSize = limits.maxDocumentSize;
      sizeLabel = limits.documentSizeLabel;
    } else {
      maxSize = limits.maxImageSize;
      sizeLabel = limits.imageSizeLabel;
    }
    
    if (file.size > maxSize) {
      setMessage({
        type: 'error',
        text: `File too large. Maximum size for selected platforms is ${sizeLabel}`,
      });
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('media', file);

      // Determine which endpoint to use based on selected platforms
      // If Twitter only, use Twitter endpoint. Otherwise use LinkedIn (works for both or LinkedIn-only)
      const hasLinkedIn = platforms.includes('linkedin');
      const hasTwitterOnly = platforms.includes('twitter') && !hasLinkedIn;
      const uploadEndpoint = hasTwitterOnly 
        ? '/api/v1/automation/twitter/media/upload/'
        : '/api/v1/automation/linkedin/media/upload/';

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${uploadEndpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // For LinkedIn: asset_urn, For Twitter: media_id_string
        const mediaId = data.asset_urn || data.media_id_string;
        setMediaUrns((prev) => [...prev, mediaId]);
        
        let mediaType: string;
        if (data.media_type === 'video') {
          mediaType = 'Video';
        } else if (data.media_type === 'document') {
          mediaType = 'Document';
        } else if (data.media_type === 'gif') {
          mediaType = 'GIF';
        } else {
          mediaType = 'Image';
        }
        const processingNote = data.status === 'PROCESSING' ? ' (processing...)' : '';
        
        setMessage({
          type: 'success',
          text: data.test_mode 
            ? `🧪 ${mediaType} uploaded (Test Mode)${processingNote}` 
            : `${mediaType} uploaded successfully!${processingNote}`,
        });
      } else {
        const error = await response.json();
        // Check for Twitter 403 Forbidden - usually means missing permissions
        if (response.status === 403 && hasTwitterOnly) {
          setMessage({
            type: 'error',
            text: 'Twitter media upload failed: Your Twitter Developer app needs "Basic" tier or "Read and Write" permissions. Check your Twitter Developer Portal settings.',
          });
        } else {
          setMessage({
            type: 'error',
            text: error.error || 'Failed to upload media',
          });
        }
      }
    } catch (error) {
      console.error('Failed to upload media:', error);
      setMessage({
        type: 'error',
        text: 'Failed to upload media. Please try again.',
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
        if (postMediaPreview) {
          URL.revokeObjectURL(postMediaPreview.url);
          setPostMediaPreview(null);
        }
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

  // Handle LinkedIn Carousel Post (multi-image, max 9)
  const handleLinkedInCarouselPost = async () => {
    if (linkedinCarouselImages.length < 2) {
      setMessage({ type: 'error', text: 'Carousel posts require at least 2 images' });
      return;
    }
    if (linkedinCarouselImages.length > 9) {
      setMessage({ type: 'error', text: 'LinkedIn supports maximum 9 images per post' });
      return;
    }
    if (!postText.trim()) {
      setMessage({ type: 'error', text: 'Please enter some text for your post' });
      return;
    }

    setPosting(true);
    try {
      // In test mode, send placeholder media_urns (backend will simulate)
      const mediaUrns = linkedinCarouselImages.map((_, index) => `test_urn_${index + 1}`);
      
      const response = await apiClient.post('/automation/linkedin/carousel/post/', {
        text: postText,
        title: postTitle.trim() || undefined,
        media_urns: mediaUrns,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: data.test_mode 
            ? '🧪 Carousel post simulated (Test Mode)' 
            : '✅ Carousel posted to LinkedIn successfully!',
        });
        resetLinkedInComposeForm();
        setShowComposeModal(false);
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to create carousel post',
        });
      }
    } catch (error) {
      console.error('LinkedIn carousel post error:', error);
      setMessage({
        type: 'error',
        text: 'Failed to create carousel post',
      });
    } finally {
      setPosting(false);
    }
  };

  // Reset LinkedIn compose form
  const resetLinkedInComposeForm = () => {
    setPostTitle('');
    setPostText('');
    setPostMediaUrns([]);
    if (postMediaPreview) {
      URL.revokeObjectURL(postMediaPreview.url);
      setPostMediaPreview(null);
    }
    setLinkedinCarouselMode(false);
    linkedinCarouselImages.forEach(img => URL.revokeObjectURL(img.url));
    setLinkedinCarouselImages([]);
  };

  // Add images to LinkedIn carousel
  const addLinkedinCarouselImages = (files: FileList | null) => {
    if (!files) return;
    
    const currentCount = linkedinCarouselImages.length;
    const maxAllowed = 9 - currentCount;
    
    if (maxAllowed <= 0) {
      setMessage({ type: 'error', text: 'Maximum 9 images allowed' });
      return;
    }
    
    const newImages = Array.from(files).slice(0, maxAllowed).map(file => ({
      url: URL.createObjectURL(file),
      file,
    }));
    
    setLinkedinCarouselImages(prev => [...prev, ...newImages]);
  };

  // Remove image from LinkedIn carousel
  const removeLinkedinCarouselImage = (index: number) => {
    setLinkedinCarouselImages(prev => {
      const removed = prev[index];
      if (removed) URL.revokeObjectURL(removed.url);
      return prev.filter((_, i) => i !== index);
    });
  };

  // Handle posting to Twitter/X
  const handleTwitterPost = async () => {
    // Thread mode handling
    if (isThreadMode) {
      await handleThreadPost();
      return;
    }

    if (!tweetTitle.trim()) {
      setMessage({
        type: 'error',
        text: 'Please enter a title for your tweet',
      });
      return;
    }

    if (!tweetText.trim()) {
      setMessage({
        type: 'error',
        text: 'Please enter some text for your tweet',
      });
      return;
    }

    if (tweetText.length > TWITTER_MAX_LENGTH) {
      setMessage({
        type: 'error',
        text: `Tweet exceeds ${TWITTER_MAX_LENGTH} characters`,
      });
      return;
    }

    setTweetPosting(true);
    try {
      // Build request payload
      const payload: Record<string, unknown> = {
        title: tweetTitle.trim() || undefined,
        text: tweetText,
      };
      
      if (tweetMediaUrns.length > 0) {
        payload.media_ids = tweetMediaUrns;
      }
      if (tweetReplyToId.trim()) {
        payload.reply_to_id = tweetReplyToId.trim();
      }
      if (tweetQuoteId.trim()) {
        payload.quote_tweet_id = tweetQuoteId.trim();
      }
      if (tweetMediaAltText.trim() && tweetMediaUrns.length > 0) {
        payload.alt_text = tweetMediaAltText.trim();
      }
      
      const response = await apiClient.post('/automation/twitter/post/', payload);

      if (response.ok) {
        const data = await response.json();
        const isTestMode = data.test_mode === true;
        setMessage({
          type: 'success',
          text: isTestMode 
            ? '🧪 Tweet simulated (Test Mode - saved to history)' 
            : `Tweet posted successfully! Tweet ID: ${data.tweet_id}`,
        });
        resetTwitterComposeForm();
        setShowTwitterComposeModal(false);
        // Refresh published posts to show the new tweet
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to post tweet',
        });
      }
    } catch (error) {
      console.error('Failed to post tweet:', error);
      setMessage({
        type: 'error',
        text: 'Failed to post tweet',
      });
    } finally {
      setTweetPosting(false);
    }
  };

  // Reset Twitter compose form
  const resetTwitterComposeForm = () => {
    setTweetTitle('');
    setTweetText('');
    setTweetMediaUrns([]);
    setTweetMediaAltText('');
    setTweetReplyToId('');
    setTweetQuoteId('');
    setIsThreadMode(false);
    setThreadTweets(['']);
    if (tweetMediaPreview) {
      URL.revokeObjectURL(tweetMediaPreview.url);
      setTweetMediaPreview(null);
    }
    // Reset carousel state
    setTwitterCarouselMode(false);
    twitterCarouselImages.forEach(img => URL.revokeObjectURL(img.url));
    setTwitterCarouselImages([]);
  };

  // Handle Twitter Carousel Post (multi-image, max 4)
  const handleTwitterCarouselPost = async () => {
    if (twitterCarouselImages.length < 2) {
      setMessage({ type: 'error', text: 'Carousel posts require at least 2 images' });
      return;
    }
    if (twitterCarouselImages.length > 4) {
      setMessage({ type: 'error', text: 'Twitter supports maximum 4 images per tweet' });
      return;
    }
    if (!tweetText.trim()) {
      setMessage({ type: 'error', text: 'Please enter some text for your tweet' });
      return;
    }

    setTweetPosting(true);
    try {
      // In test mode, send placeholder media_ids (backend will simulate)
      const mediaIds = twitterCarouselImages.map((_, index) => `test_media_${index + 1}`);
      
      const response = await apiClient.post('/automation/twitter/carousel/post/', {
        text: tweetText,
        media_ids: mediaIds,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: data.test_mode 
            ? '🧪 Carousel tweet simulated (Test Mode)' 
            : '✅ Carousel tweet posted successfully!',
        });
        resetTwitterComposeForm();
        setShowTwitterComposeModal(false);
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to create carousel tweet',
        });
      }
    } catch (error) {
      console.error('Twitter carousel post error:', error);
      setMessage({
        type: 'error',
        text: 'Failed to create carousel tweet',
      });
    } finally {
      setTweetPosting(false);
    }
  };

  // Add images to Twitter carousel
  const addTwitterCarouselImages = (files: FileList | null) => {
    if (!files) return;
    
    const currentCount = twitterCarouselImages.length;
    const maxAllowed = 4 - currentCount;
    
    if (maxAllowed <= 0) {
      setMessage({ type: 'error', text: 'Maximum 4 images allowed' });
      return;
    }
    
    const newImages = Array.from(files).slice(0, maxAllowed).map(file => ({
      url: URL.createObjectURL(file),
      file,
    }));
    
    setTwitterCarouselImages(prev => [...prev, ...newImages]);
  };

  // Remove image from Twitter carousel
  const removeTwitterCarouselImage = (index: number) => {
    setTwitterCarouselImages(prev => {
      const removed = prev[index];
      if (removed) URL.revokeObjectURL(removed.url);
      return prev.filter((_, i) => i !== index);
    });
  };

  // Handle thread posting (multiple tweets in sequence)
  const handleThreadPost = async () => {
    const validTweets = threadTweets.filter(t => t.trim().length > 0);
    
    if (validTweets.length === 0) {
      setMessage({
        type: 'error',
        text: 'Please enter at least one tweet for your thread',
      });
      return;
    }

    // Validate all tweets are within limit
    const overLimitIndex = validTweets.findIndex(t => t.length > TWITTER_MAX_LENGTH);
    if (overLimitIndex !== -1) {
      setMessage({
        type: 'error',
        text: `Tweet ${overLimitIndex + 1} exceeds ${TWITTER_MAX_LENGTH} characters`,
      });
      return;
    }

    setTweetPosting(true);
    try {
      let previousTweetId: string | null = null;
      const postedTweets: string[] = [];

      for (let i = 0; i < validTweets.length; i++) {
        const payload: Record<string, unknown> = {
          title: i === 0 ? (tweetTitle.trim() || `Thread - ${new Date().toLocaleString()}`) : `Thread part ${i + 1}`,
          text: validTweets[i],
        };
        
        // After the first tweet, reply to the previous one
        if (previousTweetId) {
          payload.reply_to_id = previousTweetId;
        }
        
        // Add media only to the first tweet
        if (i === 0 && tweetMediaUrns.length > 0) {
          payload.media_ids = tweetMediaUrns;
          if (tweetMediaAltText.trim()) {
            payload.alt_text = tweetMediaAltText.trim();
          }
        }

        const response = await apiClient.post('/automation/twitter/post/', payload);

        if (response.ok) {
          const data = await response.json();
          previousTweetId = data.tweet_id || data.tweet?.id;
          postedTweets.push(previousTweetId || 'unknown');
        } else {
          const error = await response.json();
          throw new Error(error.error || `Failed to post tweet ${i + 1}`);
        }
      }

      setMessage({
        type: 'success',
        text: `Thread posted successfully! ${postedTweets.length} tweets created.`,
      });
      resetTwitterComposeForm();
      setShowTwitterComposeModal(false);
      fetchPublishedPosts();
    } catch (error) {
      console.error('Failed to post thread:', error);
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to post thread',
      });
    } finally {
      setTweetPosting(false);
    }
  };

  // Handle posting to Facebook Page
  const handleFacebookPost = async () => {
    if (!fbPostText.trim()) {
      setMessage({
        type: 'error',
        text: 'Please enter some text for your Facebook post',
      });
      return;
    }

    if (fbPostText.length > FACEBOOK_MAX_POST_LENGTH) {
      setMessage({
        type: 'error',
        text: `Post exceeds ${FACEBOOK_MAX_POST_LENGTH} characters`,
      });
      return;
    }

    setFbPosting(true);
    try {
      // Build request payload
      const payload: Record<string, unknown> = {
        title: fbPostTitle.trim() || undefined,
        message: fbPostText,
      };
      
      if (fbMediaUrns.length > 0) {
        payload.media_urls = fbMediaUrns;
      }
      
      const response = await apiClient.post('/automation/facebook/post/', payload);

      if (response.ok) {
        const data = await response.json();
        const isTestMode = data.test_mode === true;
        setMessage({
          type: 'success',
          text: isTestMode 
            ? '🧪 Facebook post simulated (Test Mode - saved to history)' 
            : `Posted to Facebook successfully! Post ID: ${data.post_id}`,
        });
        resetFacebookComposeForm();
        setShowFacebookComposeModal(false);
        // Refresh published posts to show the new post
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to post to Facebook',
        });
      }
    } catch (error) {
      console.error('Failed to post to Facebook:', error);
      setMessage({
        type: 'error',
        text: 'Failed to post to Facebook',
      });
    } finally {
      setFbPosting(false);
    }
  };

  // Handle Facebook Carousel Post
  const handleFacebookCarouselPost = async () => {
    if (fbCarouselImages.length < 2) {
      setMessage({ type: 'error', text: 'Carousel posts require at least 2 images' });
      return;
    }
    if (fbCarouselImages.length > 10) {
      setMessage({ type: 'error', text: 'Carousel posts can have at most 10 images' });
      return;
    }

    setFbPosting(true);
    try {
      // For test mode, send placeholder URLs (backend will simulate the carousel)
      // For production, images would need to be uploaded first
      const photoUrls = fbCarouselImages.map((_, index) => `carousel_image_${index + 1}`);
      
      const response = await apiClient.post('/automation/facebook/carousel/post/', {
        message: fbPostText || 'Check out these photos!',
        photo_urls: photoUrls,
        title: fbPostTitle || undefined,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage({
          type: 'success',
          text: data.test_mode 
            ? '🧪 Carousel post simulated (Test Mode)' 
            : '✅ Carousel post published successfully!',
        });
        resetFacebookComposeForm();
        setShowFacebookComposeModal(false);
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to create carousel post',
        });
      }
    } catch (error) {
      console.error('Carousel post error:', error);
      setMessage({
        type: 'error',
        text: 'Failed to create carousel post',
      });
    } finally {
      setFbPosting(false);
    }
  };

  // Add files to story queue
  const addToStoryQueue = (files: FileList | null) => {
    if (!files) return;
    
    const newItems: StoryQueueItem[] = [];
    
    Array.from(files).forEach((file) => {
      // Determine type based on file mime type
      const isVideo = file.type.startsWith('video/');
      const isImage = file.type.startsWith('image/');
      
      if (!isVideo && !isImage) {
        setMessage({ type: 'error', text: `${file.name} is not a valid image or video file` });
        return;
      }
      
      // Validate file sizes
      if (isImage && file.size > 4 * 1024 * 1024) {
        setMessage({ type: 'error', text: `${file.name} is too large. Max 4MB for photos.` });
        return;
      }
      if (isVideo && file.size > 4 * 1024 * 1024 * 1024) {
        setMessage({ type: 'error', text: `${file.name} is too large. Max 4GB for videos.` });
        return;
      }
      
      newItems.push({
        id: `story_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        file,
        type: isVideo ? 'video' : 'photo',
        preview: URL.createObjectURL(file),
        status: 'pending',
      });
    });
    
    setFbStoryQueue(prev => [...prev, ...newItems]);
  };

  // Remove item from story queue
  const removeFromStoryQueue = (id: string) => {
    setFbStoryQueue(prev => {
      const item = prev.find(i => i.id === id);
      if (item) {
        URL.revokeObjectURL(item.preview);
      }
      return prev.filter(i => i.id !== id);
    });
  };

  // Handle Facebook Story Post - posts all items in queue
  const handleFacebookStoryPost = async () => {
    if (fbStoryQueue.length === 0) {
      setMessage({ type: 'error', text: 'Please add at least one photo or video to your story' });
      return;
    }

    setPostingFbStory(true);
    setStoryUploadProgress({ current: 0, total: fbStoryQueue.length });
    
    let successCount = 0;
    let failCount = 0;
    
    // Update queue with uploading status
    setFbStoryQueue(prev => prev.map(item => ({ ...item, status: 'pending' as const })));

    try {
      for (let i = 0; i < fbStoryQueue.length; i++) {
        const item = fbStoryQueue[i];
        setStoryUploadProgress({ current: i + 1, total: fbStoryQueue.length });
        
        // Mark current item as uploading
        setFbStoryQueue(prev => prev.map(q => 
          q.id === item.id ? { ...q, status: 'uploading' as const } : q
        ));
        
        try {
          const formData = new FormData();
          formData.append('type', item.type);
          formData.append('file', item.file);

          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/automation/facebook/stories/`,
            {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
              },
              body: formData,
            }
          );

          if (response.ok) {
            successCount++;
            setFbStoryQueue(prev => prev.map(q => 
              q.id === item.id ? { ...q, status: 'success' as const } : q
            ));
          } else {
            failCount++;
            setFbStoryQueue(prev => prev.map(q => 
              q.id === item.id ? { ...q, status: 'failed' as const } : q
            ));
          }
        } catch {
          failCount++;
          setFbStoryQueue(prev => prev.map(q => 
            q.id === item.id ? { ...q, status: 'failed' as const } : q
          ));
        }
        
        // Small delay between uploads to avoid rate limiting
        if (i < fbStoryQueue.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }

      // Show result message
      if (failCount === 0) {
        setMessage({
          type: 'success',
          text: `✅ ${successCount} ${successCount === 1 ? 'story' : 'stories'} published successfully!`,
        });
        resetFacebookStoryForm();
        setShowFacebookStoriesModal(false);
      } else if (successCount === 0) {
        setMessage({
          type: 'error',
          text: `Failed to post ${failCount} ${failCount === 1 ? 'story' : 'stories'}`,
        });
      } else {
        setMessage({
          type: 'success',
          text: `Posted ${successCount} stories, ${failCount} failed`,
        });
      }
      
      fetchFacebookStories();
      
    } finally {
      setPostingFbStory(false);
      setStoryUploadProgress({ current: 0, total: 0 });
    }
  };

  // Fetch Facebook Stories
  const fetchFacebookStories = async () => {
    setLoadingFbStories(true);
    try {
      const response = await apiClient.get('/automation/facebook/stories/');
      if (response.ok) {
        const data = await response.json();
        setFbStories(data.stories || []);
      }
    } catch (error) {
      console.error('Failed to fetch stories:', error);
    } finally {
      setLoadingFbStories(false);
    }
  };

  // Delete Facebook Story
  const handleDeleteFacebookStory = async (storyId: string) => {
    if (!confirm('Are you sure you want to delete this story?')) {
      return;
    }

    setDeletingFbStoryId(storyId);
    try {
      const response = await apiClient.delete(`/automation/facebook/stories/${storyId}/`);
      if (response.ok) {
        setMessage({ type: 'success', text: 'Story deleted successfully' });
        fetchFacebookStories();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.error || 'Failed to delete story' });
      }
    } catch (error) {
      console.error('Failed to delete story:', error);
      setMessage({ type: 'error', text: 'Failed to delete story' });
    } finally {
      setDeletingFbStoryId(null);
    }
  };

  // Reset Facebook Story Form
  const resetFacebookStoryForm = () => {
    // Clean up all preview URLs
    fbStoryQueue.forEach(item => URL.revokeObjectURL(item.preview));
    setFbStoryQueue([]);
    setStoryUploadProgress({ current: 0, total: 0 });
  };

  // ========== RESUMABLE UPLOAD FUNCTIONS ==========
  // Chunk size: 4MB (Facebook recommends 4MB-1GB chunks)
  const CHUNK_SIZE = 4 * 1024 * 1024;
  const ONE_GB = 1 * 1024 * 1024 * 1024;

  // Check if a file should use resumable upload (> 1GB)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const shouldUseResumableUpload = (file: File) => file.size > ONE_GB;

  // Fetch active resumable uploads
  const fetchResumableUploads = async () => {
    try {
      const response = await apiClient.get('/automation/facebook/upload/resumable/');
      if (response.ok) {
        const data = await response.json();
        setFbResumableUploads(data.uploads || []);
      }
    } catch (error) {
      console.error('Failed to fetch resumable uploads:', error);
    }
  };

  // Start a resumable upload session
  const startResumableUpload = async () => {
    if (!resumableUploadFile) {
      setMessage({ type: 'error', text: 'Please select a video file' });
      return;
    }

    if (resumableUploadFile.size <= ONE_GB) {
      setMessage({ type: 'error', text: 'Use regular upload for videos under 1GB. Resumable upload is for large files > 1GB.' });
      return;
    }

    try {
      setResumableUploadStatus('uploading');
      setResumableUploadProgress(0);

      // Step 1: Start the upload session
      const startResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/automation/facebook/upload/resumable/start/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            file_size: resumableUploadFile.size,
            file_name: resumableUploadFile.name,
            title: resumableUploadTitle || resumableUploadFile.name,
            description: resumableUploadDescription,
          }),
        }
      );

      if (!startResponse.ok) {
        const errorData = await startResponse.json();
        throw new Error(errorData.error || 'Failed to start upload');
      }

      const startData = await startResponse.json();
      const uploadSessionId = startData.upload_session_id;
      setCurrentUploadSessionId(uploadSessionId);

      // Step 2: Upload chunks
      let offset = 0;
      const totalChunks = Math.ceil(resumableUploadFile.size / CHUNK_SIZE);
      let chunkIndex = 0;

      while (offset < resumableUploadFile.size) {
        // Check if paused (via ref to avoid stale closure)
        if (resumableUploadStatus === 'paused') {
          setMessage({ type: 'success', text: 'Upload paused. You can resume later.' });
          return;
        }

        const chunk = resumableUploadFile.slice(offset, offset + CHUNK_SIZE);
        const formData = new FormData();
        formData.append('upload_session_id', uploadSessionId);
        formData.append('start_offset', String(offset));
        formData.append('file', chunk);

        const chunkResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/automation/facebook/upload/resumable/chunk/`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: formData,
          }
        );

        if (!chunkResponse.ok) {
          const errorData = await chunkResponse.json();
          throw new Error(errorData.error || 'Chunk upload failed');
        }

        const chunkData = await chunkResponse.json();
        offset = chunkData.start_offset || offset + CHUNK_SIZE;
        chunkIndex++;
        setResumableUploadProgress(Math.min(100, Math.round((chunkIndex / totalChunks) * 100)));
      }

      // Step 3: Finish the upload
      const finishResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/automation/facebook/upload/resumable/finish/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            upload_session_id: uploadSessionId,
            title: resumableUploadTitle || resumableUploadFile.name,
            description: resumableUploadDescription,
          }),
        }
      );

      if (!finishResponse.ok) {
        const errorData = await finishResponse.json();
        throw new Error(errorData.error || 'Failed to finalize upload');
      }

      setResumableUploadStatus('completed');
      setResumableUploadProgress(100);
      setMessage({ type: 'success', text: 'Large video uploaded successfully!' });
      
      // Refresh uploads list
      fetchResumableUploads();
      
      // Reset form after delay
      setTimeout(() => {
        resetResumableUploadForm();
      }, 2000);

    } catch (error: unknown) {
      console.error('Resumable upload failed:', error);
      setResumableUploadStatus('failed');
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setMessage({ type: 'error', text: errorMessage });
    }
  };

  // Resume an interrupted upload
  const resumeUpload = async (uploadSessionId: string) => {
    try {
      const response = await apiClient.get(`/automation/facebook/upload/resumable/?upload_session_id=${uploadSessionId}`);
      if (!response.ok) {
        throw new Error('Failed to get upload status');
      }
      
      const data = await response.json();
      const { start_offset, file_size, file_name } = data;

      setMessage({ type: 'success', text: `Resuming upload of ${file_name} from ${Math.round((start_offset / file_size) * 100)}%` });
      
      // User needs to select the same file again to resume
      setCurrentUploadSessionId(uploadSessionId);
      setResumableUploadStatus('paused');
      setResumableUploadProgress(Math.round((start_offset / file_size) * 100));
      setShowResumableUploadModal(true);
      
    } catch (error) {
      console.error('Failed to get upload status:', error);
      setMessage({ type: 'error', text: 'Failed to resume upload. The session may have expired.' });
    }
  };

  // Reset resumable upload form
  const resetResumableUploadForm = () => {
    setResumableUploadFile(null);
    setResumableUploadProgress(0);
    setResumableUploadStatus('idle');
    setResumableUploadTitle('');
    setResumableUploadDescription('');
    setCurrentUploadSessionId(null);
    setShowResumableUploadModal(false);
  };

  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes >= ONE_GB) {
      return `${(bytes / ONE_GB).toFixed(2)} GB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  // Reset Facebook compose form
  const resetFacebookComposeForm = () => {
    setFbPostTitle('');
    setFbPostText('');
    setFbMediaUrns([]);
    if (fbMediaPreview) {
      URL.revokeObjectURL(fbMediaPreview.url);
      setFbMediaPreview(null);
    }
    // Reset carousel state
    setFbCarouselMode(false);
    fbCarouselImages.forEach(img => {
      if (img.url.startsWith('blob:')) {
        URL.revokeObjectURL(img.url);
      }
    });
    setFbCarouselImages([]);
  };

  // Handle deleting a Facebook post
  const handleDeleteFacebookPost = async (postId: string) => {
    if (!confirm('Are you sure you want to delete this Facebook post? This action cannot be undone.')) {
      return;
    }

    setDeletingFbPostId(postId);
    try {
      const response = await apiClient.delete(`/automation/facebook/post/${postId}/`);
      if (response.ok) {
        setMessage({
          type: 'success',
          text: 'Facebook post deleted successfully',
        });
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to delete Facebook post',
        });
      }
    } catch (error) {
      console.error('Failed to delete Facebook post:', error);
      setMessage({
        type: 'error',
        text: 'Failed to delete Facebook post',
      });
    } finally {
      setDeletingFbPostId(null);
    }
  };

  // Handle deleting a tweet
  const handleDeleteTweet = async (tweetId: string) => {
    if (!confirm('Are you sure you want to delete this tweet? This action cannot be undone.')) {
      return;
    }

    setDeletingTweetId(tweetId);
    try {
      const response = await apiClient.delete(`/automation/twitter/tweet/${tweetId}/`);

      if (response.ok) {
        setMessage({
          type: 'success',
          text: 'Tweet deleted successfully',
        });
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to delete tweet',
        });
      }
    } catch (error) {
      console.error('Failed to delete tweet:', error);
      setMessage({
        type: 'error',
        text: 'Failed to delete tweet',
      });
    } finally {
      setDeletingTweetId(null);
    }
  };

  // Handle deleting a LinkedIn post
  const handleDeleteLinkedInPost = async (postUrn: string) => {
    if (!confirm('Are you sure you want to delete this LinkedIn post? This action cannot be undone.')) {
      return;
    }

    setDeletingLinkedInPostId(postUrn);
    try {
      const response = await apiClient.delete(`/automation/linkedin/post/${encodeURIComponent(postUrn)}/`);

      if (response.ok) {
        setMessage({
          type: 'success',
          text: 'LinkedIn post deleted successfully',
        });
        fetchPublishedPosts();
      } else {
        const error = await response.json();
        setMessage({
          type: 'error',
          text: error.error || 'Failed to delete LinkedIn post',
        });
      }
    } catch (error) {
      console.error('Failed to delete LinkedIn post:', error);
      setMessage({
        type: 'error',
        text: 'Failed to delete LinkedIn post',
      });
    } finally {
      setDeletingLinkedInPostId(null);
    }
  };

  // Handle deleting a post from all platforms
  const handleDeletePost = async (post: ScheduledPost) => {
    const platformCount = post.platforms.length;
    const platformNames = post.platforms.join(', ');
    
    if (!confirm(`Are you sure you want to delete this post from ${platformNames}? This action cannot be undone.`)) {
      return;
    }

    setDeletingPostId(post.id);
    const errors: string[] = [];
    let successCount = 0;
    let hasAnyPostId = false;

    try {
      // Delete from each platform
      for (const platform of post.platforms) {
        try {
          let response: Response;
          
          // Extract post ID using helper that handles both single and multi-platform structures
          const postId = getPostIdForPlatform(post.post_results as Record<string, unknown>, platform);
          
          if (!postId) {
            // No post ID for this platform, skip the platform API call
            // The post will be deleted from ContentCalendar at the end
            continue;
          }
          
          hasAnyPostId = true;
          
          // For test mode posts without real IDs, the delete API will still clean up ContentCalendar
          // The backend handles test_mode detection and skips actual platform API calls
          if (platform === 'twitter') {
            response = await apiClient.delete(`/automation/twitter/tweet/${postId}/`);
          } else if (platform === 'facebook') {
            response = await apiClient.delete(`/automation/facebook/post/${postId}/`);
          } else if (platform === 'linkedin') {
            response = await apiClient.delete(`/automation/linkedin/post/${encodeURIComponent(postId)}/`);
          } else {
            // Platform not supported for deletion
            continue;
          }

          if (response.ok) {
            successCount++;
          } else {
            const error = await response.json();
            errors.push(`${platform}: ${error.error || 'Failed to delete'}`);
          }
        } catch (error) {
          console.error(`Failed to delete from ${platform}:`, error);
          errors.push(`${platform}: Network error`);
        }
      }

      // If no platform had a post ID, delete directly from ContentCalendar
      if (!hasAnyPostId) {
        try {
          const response = await apiClient.delete(`/automation/content-calendar/${post.id}/`);
          if (response.ok) {
            successCount = platformCount;
          } else {
            const error = await response.json();
            errors.push(`Calendar: ${error.error || 'Failed to delete'}`);
          }
        } catch (error) {
          console.error('Failed to delete from calendar:', error);
          errors.push('Calendar: Network error');
        }
      }

      // Show result message
      if (successCount === platformCount || (successCount > 0 && !hasAnyPostId)) {
        setMessage({
          type: 'success',
          text: `Post deleted successfully`,
        });
      } else if (successCount > 0) {
        setMessage({
          type: 'success',
          text: `Post deleted from ${successCount}/${platformCount} platforms. Errors: ${errors.join('; ')}`,
        });
      } else {
        setMessage({
          type: 'error',
          text: `Failed to delete post: ${errors.join('; ')}`,
        });
      }

      fetchPublishedPosts();
    } finally {
      setDeletingPostId(null);
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

    if (schedulePlatforms.length === 0) {
      setMessage({
        type: 'error',
        text: 'Please select at least one platform',
      });
      return;
    }

    // Check content length for Twitter
    if (schedulePlatforms.includes('twitter') && scheduleContent.length > TWITTER_MAX_LENGTH) {
      setMessage({
        type: 'error',
        text: `Content exceeds Twitter's ${TWITTER_MAX_LENGTH} character limit`,
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
        platforms: schedulePlatforms,
        scheduled_date: scheduledDateTime,
        status: 'scheduled',
      });
      
      if (response.ok) {
        const platformNames = schedulePlatforms.map(p => p === 'linkedin' ? 'LinkedIn' : 'Twitter/X').join(' & ');
        setMessage({
          type: 'success',
          text: `Post scheduled for ${platformNames}!${scheduleMediaUrns.length > 0 ? ' (with media)' : ''}`,
        });
        setScheduleTitle('');
        setScheduleContent('');
        setScheduleDate('');
        setScheduleTime('');
        setScheduleMediaUrns([]);
        if (scheduleMediaPreview) {
          URL.revokeObjectURL(scheduleMediaPreview.url);
          setScheduleMediaPreview(null);
        }
        setSchedulePlatforms(['linkedin']);
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
    // Parse the scheduled date/time using consistent local timezone handling
    const date = new Date(post.scheduled_date);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    setEditDate(`${year}-${month}-${day}`);
    setEditTime(
      date.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
      })
    );
    // Load existing media if any
    setEditMediaUrns(post.media_urls || []);
    // Load platforms
    setEditPlatforms(post.platforms || ['linkedin']);
    setShowEditModal(true);
  };

  // Handle updating a scheduled post
  const handleEditPost = async () => {
    if (!editingPost) return;

    if (editPlatforms.length === 0) {
      setMessage({
        type: 'error',
        text: 'Please select at least one platform',
      });
      return;
    }

    // Check content length for Twitter
    if (editPlatforms.includes('twitter') && editContent.length > TWITTER_MAX_LENGTH) {
      setMessage({
        type: 'error',
        text: `Content exceeds Twitter's ${TWITTER_MAX_LENGTH} character limit`,
      });
      return;
    }
    
    setEditing(true);
    try {
      const scheduledDate = new Date(`${editDate}T${editTime}`);
      
      const response = await apiClient.put(`/automation/content-calendar/${editingPost.id}/`, {
        title: editTitle,
        content: editContent,
        media_urls: editMediaUrns,
        platforms: editPlatforms,
        scheduled_date: scheduledDate.toISOString(),
        status: editingPost.status,  // Preserve original status
      });

      if (response.ok) {
        setMessage({
          type: 'success',
          text: `Post updated successfully!${editMediaUrns.length > 0 ? ' (with media)' : ''}`,
        });
        setShowEditModal(false);
        setEditingPost(null);
        setEditMediaUrns([]);
        setEditPlatforms([]);
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
                    {platform === 'twitter' && (
                      <button
                        onClick={() => setShowTwitterComposeModal(true)}
                        className="text-sm text-brand-mint hover:text-brand-mint/80 flex items-center gap-1"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Create Tweet
                      </button>
                    )}
                    {platform === 'facebook' && (
                      <button
                        onClick={() => setShowFacebookComposeModal(true)}
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

                {/* Facebook Page Switcher */}
                {platform === 'facebook' && isConnected && fbPages.length > 0 && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-brand-silver/70">
                        {currentFbPage ? `Page: ${currentFbPage.name}` : 'Select a page'}
                      </span>
                      <button
                        onClick={() => setShowFbPageSwitcher(!showFbPageSwitcher)}
                        className="text-xs text-brand-electric hover:underline flex items-center gap-1"
                      >
                        <svg className={`w-3 h-3 transition-transform ${showFbPageSwitcher ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                        {fbPages.length > 1 ? 'Switch Page' : 'View Pages'}
                      </button>
                    </div>
                    
                    {showFbPageSwitcher && (
                      <div className="bg-white/5 rounded-lg p-3 space-y-2 max-h-48 overflow-y-auto">
                        {loadingFbPages ? (
                          <div className="text-center py-2">
                            <span className="text-brand-silver/50 text-sm">Loading pages...</span>
                          </div>
                        ) : (
                          fbPages.map((page) => (
                            <button
                              key={page.id}
                              onClick={() => handleSwitchFacebookPage(page.id)}
                              disabled={switchingFbPage || currentFbPage?.id === page.id}
                              className={`w-full flex items-center gap-3 p-2 rounded-lg transition-colors ${
                                currentFbPage?.id === page.id
                                  ? 'bg-brand-electric/20 border border-brand-electric/30'
                                  : 'hover:bg-white/10'
                              } disabled:opacity-50`}
                            >
                              {page.picture?.data?.url ? (
                                <img
                                  src={page.picture.data.url}
                                  alt={page.name}
                                  className="w-8 h-8 rounded-full"
                                />
                              ) : (
                                <div className="w-8 h-8 rounded-full bg-[#1877F2] flex items-center justify-center">
                                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                                  </svg>
                                </div>
                              )}
                              <div className="flex-1 text-left">
                                <p className="text-sm text-white font-medium">{page.name}</p>
                                {page.category && (
                                  <p className="text-xs text-brand-silver/50">{page.category}</p>
                                )}
                              </div>
                              {currentFbPage?.id === page.id && (
                                <span className="text-brand-mint text-xs">Active</span>
                              )}
                            </button>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* LinkedIn Organization Switcher */}
                {platform === 'linkedin' && isConnected && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-brand-silver/70">
                        {linkedInPostingAs === 'organization' && currentLinkedInOrg 
                          ? `Posting as: ${currentLinkedInOrg.name}` 
                          : `Posting as: ${profiles?.linkedin?.profile_name || 'Personal Profile'}`}
                      </span>
                      <button
                        onClick={() => setShowLinkedInOrgSwitcher(!showLinkedInOrgSwitcher)}
                        className="text-xs text-brand-electric hover:underline flex items-center gap-1"
                      >
                        <svg className={`w-3 h-3 transition-transform ${showLinkedInOrgSwitcher ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                        {linkedInOrgs.length > 0 ? 'Switch Account' : 'View Account'}
                      </button>
                    </div>
                    
                    {showLinkedInOrgSwitcher && (
                      <div className="bg-white/5 rounded-lg p-3 space-y-2 max-h-48 overflow-y-auto">
                        {loadingLinkedInOrgs ? (
                          <div className="text-center py-2">
                            <span className="text-brand-silver/50 text-sm">Loading...</span>
                          </div>
                        ) : (
                          <>
                            {/* Personal Profile Option */}
                            <button
                              onClick={() => handleSwitchLinkedInOrg(null)}
                              disabled={switchingLinkedInOrg || linkedInPostingAs === 'personal'}
                              className={`w-full flex items-center gap-3 p-2 rounded-lg transition-colors ${
                                linkedInPostingAs === 'personal'
                                  ? 'bg-brand-electric/20 border border-brand-electric/30'
                                  : 'hover:bg-white/10'
                              } disabled:opacity-50`}
                            >
                              {profiles?.linkedin?.profile_image_url ? (
                                <img
                                  src={profiles.linkedin.profile_image_url}
                                  alt={profiles.linkedin.profile_name || 'Profile'}
                                  className="w-8 h-8 rounded-full"
                                />
                              ) : (
                                <div className="w-8 h-8 rounded-full bg-[#0A66C2] flex items-center justify-center">
                                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                                  </svg>
                                </div>
                              )}
                              <div className="flex-1 text-left">
                                <p className="text-sm text-white font-medium">{profiles?.linkedin?.profile_name || 'Personal Profile'}</p>
                                <p className="text-xs text-brand-silver/50">Personal Account</p>
                              </div>
                              {linkedInPostingAs === 'personal' && (
                                <span className="text-brand-mint text-xs">Active</span>
                              )}
                            </button>
                            
                            {/* Organization Options */}
                            {linkedInOrgs.map((org) => (
                              <button
                                key={org.id}
                                onClick={() => handleSwitchLinkedInOrg(org.id)}
                                disabled={switchingLinkedInOrg || currentLinkedInOrg?.id === org.id}
                                className={`w-full flex items-center gap-3 p-2 rounded-lg transition-colors ${
                                  currentLinkedInOrg?.id === org.id
                                    ? 'bg-brand-electric/20 border border-brand-electric/30'
                                    : 'hover:bg-white/10'
                                } disabled:opacity-50`}
                              >
                                {org.logo_url ? (
                                  <img
                                    src={org.logo_url}
                                    alt={org.name}
                                    className="w-8 h-8 rounded-full"
                                  />
                                ) : (
                                  <div className="w-8 h-8 rounded-full bg-[#0A66C2] flex items-center justify-center">
                                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                    </svg>
                                  </div>
                                )}
                                <div className="flex-1 text-left">
                                  <p className="text-sm text-white font-medium">{org.name}</p>
                                  <p className="text-xs text-brand-silver/50">Company Page</p>
                                </div>
                                {currentLinkedInOrg?.id === org.id && (
                                  <span className="text-brand-mint text-xs">Active</span>
                                )}
                              </button>
                            ))}
                            
                            {linkedInOrgs.length === 0 && (
                              <p className="text-xs text-brand-silver/50 text-center py-2">
                                No company pages available. You&apos;re posting as your personal profile.
                              </p>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Twitter Account Switcher */}
                {platform === 'twitter' && isConnected && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-brand-silver/70">
                        Posting as: @{profiles?.twitter?.profile_name || 'Twitter Account'}
                      </span>
                      <button
                        onClick={() => setShowTwitterAccountPanel(!showTwitterAccountPanel)}
                        className="text-xs text-brand-electric hover:underline flex items-center gap-1"
                      >
                        <svg className={`w-3 h-3 transition-transform ${showTwitterAccountPanel ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                        View Account
                      </button>
                    </div>
                    {showTwitterAccountPanel && (
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="flex items-center gap-3 p-2 rounded-lg bg-brand-electric/20 border border-brand-electric/30">
                        {profiles?.twitter?.profile_image_url ? (
                          <img
                            src={profiles.twitter.profile_image_url}
                            alt={profiles.twitter.profile_name || 'Profile'}
                            className="w-8 h-8 rounded-full"
                          />
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                            </svg>
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="text-sm text-white font-medium">{profiles?.twitter?.profile_name || 'Twitter Account'}</p>
                          <p className="text-xs text-brand-silver/50">Personal Account</p>
                        </div>
                        <span className="text-brand-mint text-xs">Active</span>
                      </div>
                      <p className="text-xs text-brand-silver/40 mt-2 text-center">
                        Twitter/X only supports personal account posting
                      </p>
                    </div>
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
                      {platform === 'twitter' && (
                        <button
                          onClick={() => setShowTwitterComposeModal(true)}
                          className="w-full py-2.5 px-4 rounded-lg bg-brand-electric hover:bg-brand-electric/80 text-brand-midnight font-bold transition-colors"
                        >
                          🐦 Compose Tweet
                        </button>
                      )}
                      {platform === 'facebook' && (
                        <>
                          <button
                            onClick={() => setShowFacebookComposeModal(true)}
                            className="w-full py-2.5 px-4 rounded-lg bg-brand-electric hover:bg-brand-electric/80 text-brand-midnight font-bold transition-colors"
                          >
                            📘 Compose Post
                          </button>
                          <button
                            onClick={() => {
                              setShowFacebookStoriesModal(true);
                              fetchFacebookStories();
                            }}
                            className="w-full py-2 px-4 rounded-lg border border-blue-500/30 text-blue-400 hover:bg-blue-500/10 transition-colors"
                          >
                            📸 Create Story
                          </button>
                          <button
                            onClick={() => {
                              setShowResumableUploadModal(true);
                              fetchResumableUploads();
                            }}
                            className="w-full py-2 px-4 rounded-lg border border-purple-500/30 text-purple-400 hover:bg-purple-500/10 transition-colors"
                          >
                            📹 Upload Large Video (&gt;1GB)
                          </button>
                        </>
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
                      {(platform === 'linkedin' || platform === 'twitter' || platform === 'facebook') && (
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
                        <div className="flex items-center gap-1.5">
                          {post.platforms.includes('linkedin') && (
                            <div className="p-1 rounded bg-[#0A66C2]" title="LinkedIn">
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                              </svg>
                            </div>
                          )}
                          {post.platforms.includes('twitter') && (
                            <div className="p-1 rounded bg-black" title="Twitter/X">
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                              </svg>
                            </div>
                          )}
                          {post.platforms.includes('facebook') && (
                            <div className="p-1 rounded bg-[#1877F2]" title="Facebook">
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                              </svg>
                            </div>
                          )}
                        </div>
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

        {/* Recent Activity Section - Combined LinkedIn posts and Tweets */}
        <div className="mt-12">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-heading font-bold text-white">Recent Activity</h2>
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
              <Link
                href="/automation/history"
                className="text-sm text-brand-electric hover:text-brand-electric/80 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                View All History
              </Link>
            </div>
          </div>
          
          {/* Combined list of published posts */}
          {publishedPosts.length > 0 ? (
            <div className="space-y-4">
              {/* Published Posts */}
              {publishedPosts.map((post) => (
                <div key={`post-${post.id}`} className="glass-card p-4 border border-green-500/20">
                  <div className="flex items-start gap-3">
                    {/* Platform Icons */}
                    <div className="flex flex-col gap-1 flex-shrink-0">
                      {post.platforms.includes('linkedin') && (
                        <div className="p-1.5 rounded bg-[#0A66C2]" title="LinkedIn">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                          </svg>
                        </div>
                      )}
                      {post.platforms.includes('twitter') && (
                        <div className="p-1.5 rounded bg-black" title="Twitter/X">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                          </svg>
                        </div>
                      )}
                      {post.platforms.includes('facebook') && (
                        <div className="p-1.5 rounded bg-[#1877F2]" title="Facebook">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                          </svg>
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
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
                      <div className="flex items-center justify-between mt-3">
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
                        {/* Delete Button - works for all platforms */}
                        {hasAnyDeletablePostId(post.post_results as Record<string, unknown>, post.platforms) ? (
                          <button
                            onClick={() => handleDeletePost(post)}
                            disabled={deletingPostId === post.id}
                            className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1 disabled:opacity-50"
                            title={`Delete from ${post.platforms.join(', ')}`}
                          >
                            {deletingPostId === post.id ? (
                              <svg className="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                            ) : (
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            )}
                            {post.platforms.length > 1 ? 'Delete All' : 'Delete'}
                          </button>
                        ) : null}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card p-8 text-center">
              <div className="w-16 h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-brand-silver" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-2">No Recent Activity</h3>
              <p className="text-brand-silver/70 max-w-md mx-auto">
                Once you post or schedule content, it will appear here.
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
                <h2 className="text-xl font-heading font-bold text-white">
                  {linkedinCarouselMode ? 'Create Carousel Post' : 'Create LinkedIn Post'}
                </h2>
                <p className="text-sm text-brand-silver/70">
                  {linkedinCarouselMode ? 'Share multiple images your network can swipe through' : 'Share your thoughts with your network'}
                </p>
              </div>
            </div>

            {/* Mode Toggle: Single Post / Carousel */}
            <div className="mb-4 flex gap-2">
              <button
                onClick={() => setLinkedinCarouselMode(false)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  !linkedinCarouselMode 
                    ? 'bg-[#0A66C2] text-white' 
                    : 'bg-brand-midnight border border-brand-ghost/30 text-brand-silver hover:bg-white/5'
                }`}
              >
                Single Post
              </button>
              <button
                onClick={() => setLinkedinCarouselMode(true)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  linkedinCarouselMode 
                    ? 'bg-[#0A66C2] text-white' 
                    : 'bg-brand-midnight border border-brand-ghost/30 text-brand-silver hover:bg-white/5'
                }`}
              >
                🖼️ Carousel (2-9 images)
              </button>
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
                      accept={getAcceptedFileTypes(['linkedin'])}
                      className="hidden"
                      disabled={uploadingMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          // Create a local preview URL
                          const previewUrl = URL.createObjectURL(file);
                          const isVideo = file.type.startsWith('video/');
                          setPostMediaPreview({ url: previewUrl, type: isVideo ? 'video' : 'image' });
                          handleMediaUpload(file, setPostMediaUrns, setUploadingMedia, ['linkedin']);
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
                        onClick={() => {
                          setPostMediaUrns([]);
                          if (postMediaPreview) {
                            URL.revokeObjectURL(postMediaPreview.url);
                            setPostMediaPreview(null);
                          }
                        }}
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
                {/* Media Preview */}
                {postMediaPreview && (
                  <div className="mt-3 relative inline-block">
                    {postMediaPreview.type === 'video' ? (
                      <video 
                        src={postMediaPreview.url} 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30"
                        controls
                      />
                    ) : (
                      <img 
                        src={postMediaPreview.url} 
                        alt="Media preview" 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30 object-cover"
                      />
                    )}
                    {uploadingMedia && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                        <div className="flex items-center gap-2 text-white">
                          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Uploading...
                        </div>
                      </div>
                    )}
                  </div>
                )}
                <p className="text-xs text-brand-silver/50 mt-1">{getMediaHelperText(['linkedin'])}</p>
              </div>

              {/* LinkedIn Carousel Mode */}
              {linkedinCarouselMode && (
                <div>
                  <label className="block text-sm font-medium text-brand-silver mb-2">
                    Carousel Images ({linkedinCarouselImages.length}/9)
                  </label>
                  <p className="text-xs text-brand-silver/50 mb-3">
                    Add 2-9 images. Your network can swipe through them.
                  </p>
                  
                  {/* Carousel Image Grid */}
                  <div className="grid grid-cols-3 gap-2 mb-3">
                    {linkedinCarouselImages.map((img, index) => (
                      <div key={index} className="relative aspect-square group">
                        <img
                          src={img.url}
                          alt={`Carousel image ${index + 1}`}
                          className="w-full h-full object-cover rounded-lg border border-brand-ghost/30"
                        />
                        <div className="absolute top-1 left-1 w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">
                          {index + 1}
                        </div>
                        <button
                          onClick={() => removeLinkedinCarouselImage(index)}
                          className="absolute top-1 right-1 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    
                    {/* Add Image Button - Inside Grid */}
                    {linkedinCarouselImages.length < 9 && (
                      <label className="aspect-square flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-brand-ghost/30 hover:border-blue-500 hover:bg-blue-500/10 transition-colors cursor-pointer">
                        <svg className="w-6 h-6 text-brand-silver" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span className="text-xs text-brand-silver mt-1">Add</span>
                        <input
                          type="file"
                          accept="image/*"
                          multiple
                          className="hidden"
                          onChange={(e) => {
                            addLinkedinCarouselImages(e.target.files);
                            e.target.value = '';
                          }}
                        />
                      </label>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowComposeModal(false);
                  setPostTitle('');
                  setPostText('');
                  setPostMediaUrns([]);
                  if (postMediaPreview) {
                    URL.revokeObjectURL(postMediaPreview.url);
                    setPostMediaPreview(null);
                  }
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={linkedinCarouselMode ? handleLinkedInCarouselPost : handlePost}
                disabled={
                  posting || 
                  uploadingMedia || 
                  !postText.trim() ||
                  (linkedinCarouselMode && linkedinCarouselImages.length < 2)
                }
                className="px-6 py-2.5 rounded-lg bg-[#0A66C2] hover:bg-[#004182] text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {posting ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {linkedinCarouselMode ? 'Posting Carousel...' : 'Posting...'}
                  </>
                ) : (
                  linkedinCarouselMode 
                    ? `Post Carousel (${linkedinCarouselImages.length} images)` 
                    : 'Post'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Twitter Compose Tweet Modal */}
      {showTwitterComposeModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 relative">
            {/* Close button */}
            <button
              onClick={() => {
                setShowTwitterComposeModal(false);
                resetTwitterComposeForm();
              }}
              className="absolute top-4 right-4 text-brand-silver hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-black text-white">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-white">
                  {isThreadMode ? 'Create Thread' : 'Create Tweet'}
                </h2>
                <p className="text-sm text-brand-silver/70">
                  {isThreadMode ? 'Post multiple tweets as a thread' : 'Share your thoughts on Twitter/X'}
                </p>
              </div>
            </div>

            {/* Mode Toggle: Single Tweet / Thread / Carousel */}
            <div className="mb-4 flex gap-2 flex-wrap">
              <button
                onClick={() => { setIsThreadMode(false); setTwitterCarouselMode(false); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  !isThreadMode && !twitterCarouselMode
                    ? 'bg-brand-electric text-brand-midnight' 
                    : 'bg-brand-midnight border border-brand-ghost/30 text-brand-silver hover:bg-white/5'
                }`}
              >
                Single Tweet
              </button>
              <button
                onClick={() => { setIsThreadMode(true); setTwitterCarouselMode(false); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isThreadMode 
                    ? 'bg-brand-electric text-brand-midnight' 
                    : 'bg-brand-midnight border border-brand-ghost/30 text-brand-silver hover:bg-white/5'
                }`}
              >
                🧵 Thread
              </button>
              <button
                onClick={() => { setTwitterCarouselMode(true); setIsThreadMode(false); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  twitterCarouselMode 
                    ? 'bg-brand-electric text-brand-midnight' 
                    : 'bg-brand-midnight border border-brand-ghost/30 text-brand-silver hover:bg-white/5'
                }`}
              >
                🖼️ Carousel (2-4 images)
              </button>
            </div>

            {/* Info about test mode */}
            <div className="mb-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <p className="text-blue-400 text-sm">
                ℹ️ Test mode is automatically enabled when using test credentials. Connect real Twitter API credentials to post live tweets.
              </p>
            </div>

            {/* Form Fields */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Title</label>
                <input
                  type="text"
                  value={tweetTitle}
                  onChange={(e) => setTweetTitle(e.target.value)}
                  placeholder="Give your tweet a title"
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                />
              </div>
              
              {/* Thread Mode: Multiple Tweets */}
              {isThreadMode ? (
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-brand-silver">Thread Tweets</label>
                  {threadTweets.map((tweet, index) => (
                    <div key={index} className="relative">
                      <div className="flex items-start gap-2">
                        <span className="text-brand-silver/50 text-sm mt-3 w-6">{index + 1}.</span>
                        <div className="flex-1">
                          <textarea
                            value={tweet}
                            onChange={(e) => {
                              const newTweets = [...threadTweets];
                              newTweets[index] = e.target.value;
                              setThreadTweets(newTweets);
                            }}
                            placeholder={index === 0 ? "Start your thread..." : "Continue your thread..."}
                            rows={3}
                            maxLength={TWITTER_MAX_LENGTH}
                            className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 resize-none"
                          />
                          <div className="flex justify-between items-center mt-1 text-xs">
                            <span className={`${
                              tweet.length > TWITTER_MAX_LENGTH - 20 
                                ? tweet.length > TWITTER_MAX_LENGTH 
                                  ? 'text-red-400' 
                                  : 'text-amber-400' 
                                : 'text-brand-silver/50'
                            }`}>
                              {tweet.length} / {TWITTER_MAX_LENGTH}
                            </span>
                            {threadTweets.length > 1 && (
                              <button
                                onClick={() => setThreadTweets(threadTweets.filter((_, i) => i !== index))}
                                className="text-red-400 hover:text-red-300 text-xs"
                              >
                                Remove
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  <button
                    onClick={() => setThreadTweets([...threadTweets, ''])}
                    className="w-full py-2 rounded-lg border border-dashed border-brand-ghost/30 text-brand-silver/70 hover:text-brand-silver hover:border-brand-ghost/50 transition-colors text-sm"
                  >
                    + Add another tweet to thread
                  </button>
                </div>
              ) : (
                /* Single Tweet Mode */
                <div>
                  <label className="block text-sm font-medium text-brand-silver mb-1">Content</label>
                  <textarea
                    value={tweetText}
                    onChange={(e) => setTweetText(e.target.value)}
                    placeholder="What's happening?"
                    rows={4}
                    maxLength={TWITTER_MAX_LENGTH}
                    className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 resize-none"
                  />
                  <div className="flex justify-between items-center mt-1 text-xs">
                    <span className={`${
                      tweetText.length > TWITTER_MAX_LENGTH - 20 
                        ? tweetText.length > TWITTER_MAX_LENGTH 
                          ? 'text-red-400' 
                          : 'text-amber-400' 
                        : 'text-brand-silver/50'
                    }`}>
                      {tweetText.length} / {TWITTER_MAX_LENGTH} characters
                    </span>
                  </div>
                </div>
              )}

              {/* Reply/Quote Tweet (only for single tweet mode) */}
              {!isThreadMode && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-brand-silver mb-1">Reply to Tweet ID (optional)</label>
                    <input
                      type="text"
                      value={tweetReplyToId}
                      onChange={(e) => setTweetReplyToId(e.target.value)}
                      placeholder="e.g., 1234567890"
                      className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-2 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-brand-silver mb-1">Quote Tweet ID (optional)</label>
                    <input
                      type="text"
                      value={tweetQuoteId}
                      onChange={(e) => setTweetQuoteId(e.target.value)}
                      placeholder="e.g., 1234567890"
                      className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-2 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 text-sm"
                    />
                  </div>
                </div>
              )}

              {/* Media Upload for Twitter */}
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Media (optional)</label>
                <div className="flex items-center gap-3">
                  <label className={`flex items-center gap-2 px-4 py-2 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors cursor-pointer ${uploadingTweetMedia ? 'opacity-50 cursor-not-allowed' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {uploadingTweetMedia ? 'Uploading...' : 'Add Media'}
                    <input
                      type="file"
                      accept={getAcceptedFileTypes(['twitter'])}
                      className="hidden"
                      disabled={uploadingTweetMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          // Create a local preview URL
                          const previewUrl = URL.createObjectURL(file);
                          const isVideo = file.type.startsWith('video/');
                          setTweetMediaPreview({ url: previewUrl, type: isVideo ? 'video' : 'image' });
                          handleMediaUpload(file, setTweetMediaUrns, setUploadingTweetMedia, ['twitter']);
                        }
                        e.target.value = '';
                      }}
                    />
                  </label>
                  {tweetMediaUrns.length > 0 && (
                    <div className="flex items-center gap-2 text-green-400 text-sm">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {tweetMediaUrns.length} file{tweetMediaUrns.length > 1 ? 's' : ''} attached
                      <button
                        onClick={() => {
                          setTweetMediaUrns([]);
                          if (tweetMediaPreview) {
                            URL.revokeObjectURL(tweetMediaPreview.url);
                            setTweetMediaPreview(null);
                          }
                        }}
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
                {/* Media Preview */}
                {tweetMediaPreview && (
                  <div className="mt-3 relative inline-block">
                    {tweetMediaPreview.type === 'video' ? (
                      <video 
                        src={tweetMediaPreview.url} 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30"
                        controls
                      />
                    ) : (
                      <img 
                        src={tweetMediaPreview.url} 
                        alt="Media preview" 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30 object-cover"
                      />
                    )}
                    {uploadingTweetMedia && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                        <div className="flex items-center gap-2 text-white">
                          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Uploading...
                        </div>
                      </div>
                    )}
                  </div>
                )}
                {/* Alt Text for Accessibility */}
                {tweetMediaUrns.length > 0 && (
                  <div className="mt-3">
                    <label className="block text-sm font-medium text-brand-silver mb-1">
                      Alt Text (for accessibility)
                    </label>
                    <input
                      type="text"
                      value={tweetMediaAltText}
                      onChange={(e) => setTweetMediaAltText(e.target.value)}
                      placeholder="Describe your image for screen readers"
                      maxLength={1000}
                      className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-2 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 text-sm"
                    />
                    <p className="text-xs text-brand-silver/50 mt-1">
                      {tweetMediaAltText.length}/1000 characters - Helps users with visual impairments
                    </p>
                  </div>
                )}
                <p className="text-xs text-brand-silver/50 mt-1">{getMediaHelperText(['twitter'])}</p>
              </div>

              {/* Twitter Carousel Mode */}
              {twitterCarouselMode && (
                <div>
                  <label className="block text-sm font-medium text-brand-silver mb-2">
                    Carousel Images ({twitterCarouselImages.length}/4)
                  </label>
                  <p className="text-xs text-brand-silver/50 mb-3">
                    Add 2-4 images. Users can swipe through them.
                  </p>
                  
                  {/* Carousel Image Grid */}
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    {twitterCarouselImages.map((img, index) => (
                      <div key={index} className="relative aspect-square group">
                        <img
                          src={img.url}
                          alt={`Carousel image ${index + 1}`}
                          className="w-full h-full object-cover rounded-lg border border-brand-ghost/30"
                        />
                        <div className="absolute top-1 left-1 w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">
                          {index + 1}
                        </div>
                        <button
                          onClick={() => removeTwitterCarouselImage(index)}
                          className="absolute top-1 right-1 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                    
                    {/* Add Image Button - Inside Grid */}
                    {twitterCarouselImages.length < 4 && (
                      <label className="aspect-square flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-brand-ghost/30 hover:border-blue-500 hover:bg-blue-500/10 transition-colors cursor-pointer">
                        <svg className="w-6 h-6 text-brand-silver" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span className="text-xs text-brand-silver mt-1">Add</span>
                        <input
                          type="file"
                          accept="image/*"
                          multiple
                          className="hidden"
                          onChange={(e) => {
                            addTwitterCarouselImages(e.target.files);
                            e.target.value = '';
                          }}
                        />
                      </label>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowTwitterComposeModal(false);
                  resetTwitterComposeForm();
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={twitterCarouselMode ? handleTwitterCarouselPost : handleTwitterPost}
                disabled={
                  tweetPosting || 
                  uploadingTweetMedia || 
                  !tweetTitle.trim() || 
                  (twitterCarouselMode
                    ? twitterCarouselImages.length < 2 || !tweetText.trim()
                    : isThreadMode 
                      ? threadTweets.filter(t => t.trim()).length === 0 || threadTweets.some(t => t.length > TWITTER_MAX_LENGTH)
                      : !tweetText.trim() || tweetText.length > TWITTER_MAX_LENGTH
                  )
                }
                className="px-6 py-2.5 rounded-lg text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 bg-black hover:bg-gray-800"
              >
                {tweetPosting ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {twitterCarouselMode ? 'Posting Carousel...' : isThreadMode ? 'Posting Thread...' : 'Posting...'}
                  </>
                ) : (
                  twitterCarouselMode 
                    ? `Post Carousel (${twitterCarouselImages.length} images)` 
                    : isThreadMode 
                      ? `Post Thread (${threadTweets.filter(t => t.trim()).length} tweets)` 
                      : 'Post Tweet'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Facebook Compose Modal */}
      {showFacebookComposeModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 relative">
            {/* Close button */}
            <button
              onClick={() => {
                setShowFacebookComposeModal(false);
                resetFacebookComposeForm();
              }}
              className="absolute top-4 right-4 text-brand-silver hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-blue-600 text-white">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-white">Create Facebook Post</h2>
                <p className="text-sm text-brand-silver/70">Share content to your Facebook Page</p>
              </div>
            </div>

            {/* Info about test mode */}
            <div className="mb-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <p className="text-blue-400 text-sm">
                ℹ️ Test mode is automatically enabled when using test credentials. Connect real Facebook Page access to post live content.
              </p>
            </div>

            {/* Post Type Toggle */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-brand-silver mb-2">Post Type</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setFbCarouselMode(false)}
                  className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                    !fbCarouselMode
                      ? 'border-blue-500 bg-blue-500/20 text-blue-400'
                      : 'border-brand-ghost/30 text-brand-silver hover:bg-white/5'
                  }`}
                >
                  📝 Single Post
                </button>
                <button
                  onClick={() => setFbCarouselMode(true)}
                  className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                    fbCarouselMode
                      ? 'border-blue-500 bg-blue-500/20 text-blue-400'
                      : 'border-brand-ghost/30 text-brand-silver hover:bg-white/5'
                  }`}
                >
                  🎠 Carousel (2-10 images)
                </button>
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Title (for tracking)</label>
                <input
                  type="text"
                  value={fbPostTitle}
                  onChange={(e) => setFbPostTitle(e.target.value)}
                  placeholder="Give your post a title"
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Content</label>
                <textarea
                  value={fbPostText}
                  onChange={(e) => setFbPostText(e.target.value)}
                  placeholder="What's on your mind?"
                  rows={5}
                  maxLength={FACEBOOK_MAX_POST_LENGTH}
                  className="w-full bg-brand-midnight border border-brand-ghost/30 rounded-lg p-3 text-white placeholder-brand-silver/50 focus:outline-none focus:ring-2 focus:ring-brand-electric/50 resize-none"
                />
                <div className="flex justify-between items-center mt-1 text-xs">
                  <span className={`${
                    fbPostText.length > FACEBOOK_MAX_POST_LENGTH - 1000 
                      ? fbPostText.length > FACEBOOK_MAX_POST_LENGTH 
                        ? 'text-red-400' 
                        : 'text-amber-400' 
                      : 'text-brand-silver/50'
                  }`}>
                    {fbPostText.length} / {FACEBOOK_MAX_POST_LENGTH} characters
                  </span>
                </div>
              </div>

              {/* Media Upload for Facebook - Single Post Mode */}
              {!fbCarouselMode && (
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">Media (optional)</label>
                <div className="flex items-center gap-3">
                  <label className={`flex items-center gap-2 px-4 py-2 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors cursor-pointer ${uploadingFbMedia ? 'opacity-50 cursor-not-allowed' : ''}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {uploadingFbMedia ? 'Uploading...' : 'Add Media'}
                    <input
                      type="file"
                      accept={getAcceptedFileTypes(['facebook'])}
                      className="hidden"
                      disabled={uploadingFbMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          // Create a local preview URL
                          const previewUrl = URL.createObjectURL(file);
                          const isVideo = file.type.startsWith('video/');
                          setFbMediaPreview({ url: previewUrl, type: isVideo ? 'video' : 'image' });
                          handleMediaUpload(file, setFbMediaUrns, setUploadingFbMedia, ['facebook']);
                        }
                        e.target.value = '';
                      }}
                    />
                  </label>
                  {fbMediaUrns.length > 0 && (
                    <div className="flex items-center gap-2 text-green-400 text-sm">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {fbMediaUrns.length} file{fbMediaUrns.length > 1 ? 's' : ''} attached
                      <button
                        onClick={() => {
                          setFbMediaUrns([]);
                          if (fbMediaPreview) {
                            URL.revokeObjectURL(fbMediaPreview.url);
                            setFbMediaPreview(null);
                          }
                        }}
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
                {/* Media Preview */}
                {fbMediaPreview && (
                  <div className="mt-3 relative inline-block">
                    {fbMediaPreview.type === 'video' ? (
                      <video 
                        src={fbMediaPreview.url} 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30"
                        controls
                      />
                    ) : (
                      <img 
                        src={fbMediaPreview.url} 
                        alt="Media preview" 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30 object-cover"
                      />
                    )}
                    {uploadingFbMedia && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                        <div className="flex items-center gap-2 text-white">
                          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Uploading...
                        </div>
                      </div>
                    )}
                  </div>
                )}
                <p className="text-xs text-brand-silver/50 mt-1">{getMediaHelperText(['facebook'])}</p>
              </div>
              )}

              {/* Carousel Images - Carousel Mode */}
              {fbCarouselMode && (
              <div>
                <label className="block text-sm font-medium text-brand-silver mb-1">
                  Carousel Images ({fbCarouselImages.length}/10)
                </label>
                <p className="text-xs text-brand-silver/50 mb-3">
                  Add 2-10 images for your carousel post. Images will be displayed in the order shown.
                </p>
                
                {/* Image Grid */}
                <div className="grid grid-cols-5 gap-2 mb-3">
                  {fbCarouselImages.map((img, index) => (
                    <div key={index} className="relative aspect-square group">
                      <img
                        src={img.url}
                        alt={`Carousel image ${index + 1}`}
                        className="w-full h-full object-cover rounded-lg border border-brand-ghost/30"
                      />
                      <div className="absolute top-1 left-1 w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <button
                        onClick={() => {
                          const newImages = [...fbCarouselImages];
                          if (newImages[index].url.startsWith('blob:')) {
                            URL.revokeObjectURL(newImages[index].url);
                          }
                          newImages.splice(index, 1);
                          setFbCarouselImages(newImages);
                        }}
                        className="absolute top-1 right-1 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  
                  {/* Add Image Button */}
                  {fbCarouselImages.length < 10 && (
                    <label className={`aspect-square flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-brand-ghost/30 hover:border-blue-500 hover:bg-blue-500/10 transition-colors cursor-pointer ${uploadingCarouselImage ? 'opacity-50 cursor-not-allowed' : ''}`}>
                      {uploadingCarouselImage ? (
                        <svg className="animate-spin w-6 h-6 text-brand-silver" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      ) : (
                        <>
                          <svg className="w-6 h-6 text-brand-silver" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          <span className="text-xs text-brand-silver mt-1">Add</span>
                        </>
                      )}
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        className="hidden"
                        disabled={uploadingCarouselImage}
                        onChange={(e) => {
                          const files = e.target.files;
                          if (files) {
                            const newImages: { url: string; file: File }[] = [];
                            const maxToAdd = 10 - fbCarouselImages.length;
                            
                            Array.from(files).slice(0, maxToAdd).forEach(file => {
                              if (file.type.startsWith('image/')) {
                                const previewUrl = URL.createObjectURL(file);
                                newImages.push({ url: previewUrl, file });
                              }
                            });
                            
                            if (newImages.length > 0) {
                              setFbCarouselImages(prev => [...prev, ...newImages]);
                            }
                            
                            if (files.length > maxToAdd) {
                              setMessage({ type: 'error', text: `Only added ${maxToAdd} images. Maximum is 10.` });
                            }
                          }
                          e.target.value = '';
                        }}
                      />
                    </label>
                  )}
                </div>
                
                {/* Validation Message */}
                {fbCarouselImages.length > 0 && fbCarouselImages.length < 2 && (
                  <p className="text-xs text-amber-400">⚠️ Add at least 2 images for a carousel post</p>
                )}
                {fbCarouselImages.length >= 2 && (
                  <p className="text-xs text-green-400">✓ Ready to post carousel with {fbCarouselImages.length} images</p>
                )}
              </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowFacebookComposeModal(false);
                  resetFacebookComposeForm();
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={fbCarouselMode ? handleFacebookCarouselPost : handleFacebookPost}
                disabled={
                  fbPosting || 
                  uploadingFbMedia || 
                  uploadingCarouselImage ||
                  (!fbCarouselMode && !fbPostText.trim()) ||
                  (fbCarouselMode && fbCarouselImages.length < 2) ||
                  fbPostText.length > FACEBOOK_MAX_POST_LENGTH
                }
                className="px-6 py-2.5 rounded-lg text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
              >
                {fbPosting ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Posting...
                  </>
                ) : (
                  fbCarouselMode ? `Post Carousel (${fbCarouselImages.length} images)` : 'Post to Facebook'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Facebook Stories Modal */}
      {showFacebookStoriesModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 relative">
            {/* Close button */}
            <button
              onClick={() => {
                setShowFacebookStoriesModal(false);
                resetFacebookStoryForm();
              }}
              className="absolute top-4 right-4 text-brand-silver hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 text-white">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-white">Facebook Stories</h2>
                <p className="text-sm text-brand-silver/70">Create 24-hour ephemeral content</p>
              </div>
            </div>

            {/* Active Stories */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-brand-silver mb-3">Active Stories</h3>
              {loadingFbStories ? (
                <div className="flex justify-center py-4">
                  <svg className="animate-spin w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                </div>
              ) : fbStories.length === 0 ? (
                <div className="text-center py-4 text-brand-silver/50 text-sm">
                  No active stories. Stories disappear after 24 hours.
                </div>
              ) : (
                <div className="flex gap-3 overflow-x-auto pb-2">
                  {fbStories.map((story) => (
                    <div key={story.id} className="flex-shrink-0 relative group">
                      <div className="w-20 h-32 rounded-lg bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-orange-500/20 border border-brand-ghost/30 flex items-center justify-center">
                        <span className="text-2xl">{story.media_type === 'VIDEO' ? '🎬' : '📷'}</span>
                      </div>
                      <button
                        onClick={() => handleDeleteFacebookStory(story.id)}
                        disabled={deletingFbStoryId === story.id}
                        className="absolute top-1 right-1 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50"
                      >
                        {deletingFbStoryId === story.id ? '...' : '×'}
                      </button>
                      <p className="text-xs text-brand-silver/50 text-center mt-1">
                        {new Date(story.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Create Story Section */}
            <div className="border-t border-brand-ghost/30 pt-6">
              <h3 className="text-sm font-medium text-brand-silver mb-3">Create New Stories</h3>
              
              {/* Info Banner */}
              <div className="mb-4 p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                <p className="text-purple-400 text-xs">
                  📸 Add multiple photos and videos to post as a sequence of stories. Each file becomes a separate story.
                </p>
                <p className="text-purple-400/70 text-xs mt-1">
                  Photos: JPEG/PNG, max 4MB • Videos: MP4/MOV, max 4GB, 1-60 seconds
                </p>
              </div>

              {/* File Upload Area */}
              <div className="mb-4">
                <label className={`flex flex-col items-center justify-center w-full h-32 rounded-lg border-2 border-dashed border-brand-ghost/30 hover:border-purple-500 hover:bg-purple-500/10 transition-colors cursor-pointer ${postingFbStory ? 'opacity-50 cursor-not-allowed' : ''}`}>
                  <svg className="w-8 h-8 text-brand-silver mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span className="text-brand-silver text-sm">
                    Click to add photos or videos
                  </span>
                  <span className="text-brand-silver/50 text-xs mt-1">
                    Select multiple files at once
                  </span>
                  <input
                    type="file"
                    accept="image/*,video/*"
                    multiple
                    className="hidden"
                    disabled={postingFbStory}
                    onChange={(e) => {
                      addToStoryQueue(e.target.files);
                      e.target.value = '';
                    }}
                  />
                </label>
              </div>

              {/* Story Queue */}
              {fbStoryQueue.length > 0 && (
                <div className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="text-sm text-brand-silver">Story Queue ({fbStoryQueue.length} items)</h4>
                    <button
                      onClick={resetFacebookStoryForm}
                      disabled={postingFbStory}
                      className="text-xs text-red-400 hover:text-red-300 disabled:opacity-50"
                    >
                      Clear All
                    </button>
                  </div>
                  <div className="flex gap-2 overflow-x-auto pb-2">
                    {fbStoryQueue.map((item, index) => (
                      <div key={item.id} className="flex-shrink-0 relative group">
                        <div className={`w-16 h-24 rounded-lg overflow-hidden border-2 ${
                          item.status === 'uploading' ? 'border-blue-500' :
                          item.status === 'success' ? 'border-green-500' :
                          item.status === 'failed' ? 'border-red-500' :
                          'border-brand-ghost/30'
                        }`}>
                          {item.type === 'video' ? (
                            <video 
                              src={item.preview} 
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <img 
                              src={item.preview} 
                              alt={`Story ${index + 1}`} 
                              className="w-full h-full object-cover"
                            />
                          )}
                          {/* Status overlay */}
                          {item.status !== 'pending' && (
                            <div className={`absolute inset-0 flex items-center justify-center ${
                              item.status === 'uploading' ? 'bg-blue-500/50' :
                              item.status === 'success' ? 'bg-green-500/50' :
                              item.status === 'failed' ? 'bg-red-500/50' : ''
                            }`}>
                              {item.status === 'uploading' && (
                                <svg className="animate-spin w-6 h-6 text-white" fill="none" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                                </svg>
                              )}
                              {item.status === 'success' && <span className="text-white text-lg">✓</span>}
                              {item.status === 'failed' && <span className="text-white text-lg">✗</span>}
                            </div>
                          )}
                        </div>
                        {/* Type indicator */}
                        <div className="absolute bottom-1 left-1 text-xs">
                          {item.type === 'video' ? '🎬' : '📷'}
                        </div>
                        {/* Remove button */}
                        {!postingFbStory && item.status === 'pending' && (
                          <button
                            onClick={() => removeFromStoryQueue(item.id)}
                            className="absolute top-0 right-0 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-1 -translate-y-1"
                          >
                            ×
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Upload Progress */}
              {postingFbStory && storyUploadProgress.total > 0 && (
                <div className="mb-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-blue-400 text-sm">Uploading stories...</span>
                    <span className="text-blue-400 text-sm">{storyUploadProgress.current} / {storyUploadProgress.total}</span>
                  </div>
                  <div className="h-2 bg-brand-ghost/30 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 transition-all duration-300"
                      style={{ width: `${(storyUploadProgress.current / storyUploadProgress.total) * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Post Story Button */}
              <button
                onClick={handleFacebookStoryPost}
                disabled={postingFbStory || fbStoryQueue.length === 0}
                className="w-full py-2.5 px-4 rounded-lg text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 hover:from-purple-600 hover:via-pink-600 hover:to-orange-600"
              >
                {postingFbStory ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Posting {storyUploadProgress.current} of {storyUploadProgress.total}...
                  </>
                ) : fbStoryQueue.length === 0 ? (
                  '✨ Add media to share'
                ) : fbStoryQueue.length === 1 ? (
                  '✨ Share to Story'
                ) : (
                  `✨ Share ${fbStoryQueue.length} Stories`
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Facebook Resumable Upload Modal (for large videos > 1GB) */}
      {showResumableUploadModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 relative">
            {/* Close button */}
            <button
              onClick={resetResumableUploadForm}
              className="absolute top-4 right-4 text-brand-silver hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-white">Large Video Upload</h2>
                <p className="text-sm text-brand-silver/70">Resumable upload for videos &gt; 1GB</p>
              </div>
            </div>

            {/* Info Banner */}
            <div className="mb-6 p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
              <p className="text-purple-400 text-sm">
                📹 This upload method supports videos larger than 1GB with:
              </p>
              <ul className="text-purple-400/80 text-sm mt-2 ml-4 list-disc space-y-1">
                <li>Chunked upload (4MB chunks)</li>
                <li>Resume interrupted uploads</li>
                <li>Progress tracking</li>
              </ul>
            </div>

            {/* Active Uploads */}
            {fbResumableUploads.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-brand-silver mb-3">In-Progress Uploads</h3>
                <div className="space-y-2">
                  {fbResumableUploads.map((upload) => (
                    <div key={upload.upload_session_id} className="p-3 rounded-lg bg-brand-obsidian/50 border border-brand-ghost/30">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-white text-sm truncate flex-1">{upload.file_name}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          upload.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          upload.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          upload.status === 'uploading' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {upload.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-brand-ghost/30 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                            style={{ width: `${upload.progress_percent}%` }}
                          />
                        </div>
                        <span className="text-xs text-brand-silver">{upload.progress_percent}%</span>
                      </div>
                      <div className="flex justify-between items-center mt-2 text-xs text-brand-silver/50">
                        <span>{formatFileSize(upload.bytes_uploaded)} / {formatFileSize(upload.file_size)}</span>
                        {upload.status !== 'completed' && upload.status !== 'failed' && (
                          <button
                            onClick={() => resumeUpload(upload.upload_session_id)}
                            className="text-blue-400 hover:text-blue-300"
                          >
                            Resume
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* New Upload Section */}
            <div className="border-t border-brand-ghost/30 pt-6">
              <h3 className="text-sm font-medium text-brand-silver mb-3">Upload New Video</h3>
              
              {/* Title Input */}
              <div className="mb-4">
                <label className="block text-sm text-brand-silver mb-1">Video Title</label>
                <input
                  type="text"
                  value={resumableUploadTitle}
                  onChange={(e) => setResumableUploadTitle(e.target.value)}
                  placeholder="Enter video title..."
                  disabled={resumableUploadStatus === 'uploading'}
                  className="w-full p-3 rounded-lg bg-brand-obsidian border border-brand-ghost/30 text-white placeholder-brand-silver/50 focus:border-purple-500 focus:outline-none disabled:opacity-50"
                />
              </div>

              {/* Description Input */}
              <div className="mb-4">
                <label className="block text-sm text-brand-silver mb-1">Description</label>
                <textarea
                  value={resumableUploadDescription}
                  onChange={(e) => setResumableUploadDescription(e.target.value)}
                  placeholder="Enter video description..."
                  rows={3}
                  disabled={resumableUploadStatus === 'uploading'}
                  className="w-full p-3 rounded-lg bg-brand-obsidian border border-brand-ghost/30 text-white placeholder-brand-silver/50 focus:border-purple-500 focus:outline-none resize-none disabled:opacity-50"
                />
              </div>

              {/* File Selection */}
              <div className="mb-4">
                <label className={`flex flex-col items-center justify-center w-full h-32 rounded-lg border-2 border-dashed border-brand-ghost/30 hover:border-purple-500 hover:bg-purple-500/10 transition-colors cursor-pointer ${resumableUploadStatus === 'uploading' ? 'opacity-50 cursor-not-allowed' : ''}`}>
                  {resumableUploadFile ? (
                    <div className="text-center px-4">
                      <span className="text-3xl">📹</span>
                      <p className="text-white text-sm mt-2 truncate max-w-full">{resumableUploadFile.name}</p>
                      <p className="text-purple-400 text-xs mt-1">{formatFileSize(resumableUploadFile.size)}</p>
                      {resumableUploadFile.size <= ONE_GB && (
                        <p className="text-yellow-400 text-xs mt-1">⚠️ File is under 1GB - use regular upload</p>
                      )}
                    </div>
                  ) : (
                    <>
                      <svg className="w-10 h-10 text-brand-silver mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <span className="text-brand-silver text-sm">Click to select video file (&gt;1GB)</span>
                    </>
                  )}
                  <input
                    type="file"
                    accept="video/*"
                    className="hidden"
                    disabled={resumableUploadStatus === 'uploading'}
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        setResumableUploadFile(file);
                      }
                      e.target.value = '';
                    }}
                  />
                </label>
              </div>

              {/* Upload Progress */}
              {resumableUploadStatus !== 'idle' && (
                <div className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-brand-silver">Upload Progress</span>
                    <span className={`text-sm ${
                      resumableUploadStatus === 'completed' ? 'text-green-400' :
                      resumableUploadStatus === 'failed' ? 'text-red-400' :
                      resumableUploadStatus === 'paused' ? 'text-yellow-400' :
                      'text-blue-400'
                    }`}>
                      {resumableUploadStatus === 'uploading' ? `Uploading... ${resumableUploadProgress}%` :
                       resumableUploadStatus === 'completed' ? 'Completed!' :
                       resumableUploadStatus === 'paused' ? 'Paused' :
                       resumableUploadStatus === 'failed' ? 'Failed' : ''}
                    </span>
                  </div>
                  <div className="h-3 bg-brand-ghost/30 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-300 ${
                        resumableUploadStatus === 'completed' ? 'bg-green-500' :
                        resumableUploadStatus === 'failed' ? 'bg-red-500' :
                        'bg-gradient-to-r from-blue-500 to-purple-500'
                      }`}
                      style={{ width: `${resumableUploadProgress}%` }}
                    />
                  </div>
                  {resumableUploadStatus === 'uploading' && resumableUploadFile && (
                    <p className="text-xs text-brand-silver/50 mt-1 text-center">
                      Uploading in 4MB chunks... Do not close this window.
                    </p>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3">
                {resumableUploadStatus === 'uploading' ? (
                  <button
                    onClick={() => setResumableUploadStatus('paused')}
                    className="flex-1 py-2.5 px-4 rounded-lg border border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10 transition-colors"
                  >
                    ⏸️ Pause Upload
                  </button>
                ) : resumableUploadStatus === 'paused' ? (
                  <button
                    onClick={startResumableUpload}
                    className="flex-1 py-2.5 px-4 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600 transition-colors"
                  >
                    ▶️ Resume Upload
                  </button>
                ) : (
                  <button
                    onClick={startResumableUpload}
                    disabled={!resumableUploadFile || (resumableUploadFile && resumableUploadFile.size <= ONE_GB) || resumableUploadStatus === 'completed'}
                    className="flex-1 py-2.5 px-4 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {resumableUploadStatus === 'completed' ? (
                      '✅ Upload Complete'
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        Start Upload
                      </>
                    )}
                  </button>
                )}
                <button
                  onClick={resetResumableUploadForm}
                  className="py-2.5 px-4 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Schedule Post Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 relative">
            {/* Close button */}
            <button
              onClick={() => {
                setShowScheduleModal(false);
                setScheduleTitle('');
                setScheduleContent('');
                setScheduleDate('');
                setScheduleTime('');
                setScheduleMediaUrns([]);
                setSchedulePlatforms(['linkedin']);
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
                <label className="block text-sm font-medium text-brand-silver mb-2">Platforms</label>
                <div className="space-y-2">
                  {/* LinkedIn Option */}
                  <label className="flex items-center gap-3 cursor-pointer p-2 rounded hover:bg-white/5 transition-colors">
                    <input
                      type="checkbox"
                      checked={schedulePlatforms.includes('linkedin')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSchedulePlatforms([...schedulePlatforms, 'linkedin']);
                        } else {
                          setSchedulePlatforms(schedulePlatforms.filter(p => p !== 'linkedin'));
                        }
                      }}
                      className="w-4 h-4 rounded border-brand-ghost/30 text-brand-electric focus:ring-brand-electric/50"
                    />
                    <div className="p-1.5 rounded bg-[#0A66C2]">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                      </svg>
                    </div>
                    <span className="text-sm text-white">LinkedIn</span>
                    <span className="text-xs text-brand-silver/50 ml-auto">Max 3,000 chars</span>
                  </label>
                  
                  {/* Twitter Option */}
                  <label className="flex items-center gap-3 cursor-pointer p-2 rounded hover:bg-white/5 transition-colors">
                    <input
                      type="checkbox"
                      checked={schedulePlatforms.includes('twitter')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSchedulePlatforms([...schedulePlatforms, 'twitter']);
                        } else {
                          setSchedulePlatforms(schedulePlatforms.filter(p => p !== 'twitter'));
                        }
                      }}
                      className="w-4 h-4 rounded border-brand-ghost/30 text-brand-electric focus:ring-brand-electric/50"
                    />
                    <div className="p-1.5 rounded bg-black">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                      </svg>
                    </div>
                    <span className="text-sm text-white">Twitter/X</span>
                    <span className="text-xs text-brand-silver/50 ml-auto">Max {TWITTER_MAX_LENGTH} chars</span>
                  </label>
                  
                  {/* Facebook Option */}
                  <label className="flex items-center gap-3 cursor-pointer p-2 rounded hover:bg-white/5 transition-colors">
                    <input
                      type="checkbox"
                      checked={schedulePlatforms.includes('facebook')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSchedulePlatforms([...schedulePlatforms, 'facebook']);
                        } else {
                          setSchedulePlatforms(schedulePlatforms.filter(p => p !== 'facebook'));
                        }
                      }}
                      className="w-4 h-4 rounded border-brand-ghost/30 text-brand-electric focus:ring-brand-electric/50"
                    />
                    <div className="p-1.5 rounded bg-[#1877F2]">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                      </svg>
                    </div>
                    <span className="text-sm text-white">Facebook</span>
                    <span className="text-xs text-brand-silver/50 ml-auto">Max 63,206 chars</span>
                  </label>
                </div>
                
                {/* Character limit warning */}
                {schedulePlatforms.includes('twitter') && scheduleContent.length > TWITTER_MAX_LENGTH && (
                  <div className="mt-2 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
                    ⚠️ Content exceeds Twitter&apos;s {TWITTER_MAX_LENGTH} character limit ({scheduleContent.length} chars)
                  </div>
                )}
                
                {schedulePlatforms.length === 0 && (
                  <div className="mt-2 text-xs text-yellow-400">
                    ⚠️ Please select at least one platform
                  </div>
                )}
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
                      accept={getAcceptedFileTypes(schedulePlatforms)}
                      className="hidden"
                      disabled={uploadingScheduleMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          // Create a local preview URL
                          const previewUrl = URL.createObjectURL(file);
                          const isVideo = file.type.startsWith('video/');
                          setScheduleMediaPreview({ url: previewUrl, type: isVideo ? 'video' : 'image' });
                          handleMediaUpload(file, setScheduleMediaUrns, setUploadingScheduleMedia, schedulePlatforms);
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
                        onClick={() => {
                          setScheduleMediaUrns([]);
                          if (scheduleMediaPreview) {
                            URL.revokeObjectURL(scheduleMediaPreview.url);
                            setScheduleMediaPreview(null);
                          }
                        }}
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
                {/* Media Preview */}
                {scheduleMediaPreview && (
                  <div className="mt-3 relative inline-block">
                    {scheduleMediaPreview.type === 'video' ? (
                      <video 
                        src={scheduleMediaPreview.url} 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30"
                        controls
                      />
                    ) : (
                      <img 
                        src={scheduleMediaPreview.url} 
                        alt="Media preview" 
                        className="max-w-full max-h-48 rounded-lg border border-brand-ghost/30 object-cover"
                      />
                    )}
                    {uploadingScheduleMedia && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                        <div className="flex items-center gap-2 text-white">
                          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Uploading...
                        </div>
                      </div>
                    )}
                  </div>
                )}
                <p className="text-xs text-brand-silver/50 mt-1">{getMediaHelperText(schedulePlatforms)}</p>
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
                  if (scheduleMediaPreview) {
                    URL.revokeObjectURL(scheduleMediaPreview.url);
                    setScheduleMediaPreview(null);
                  }
                  setSchedulePlatforms(['linkedin']);
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSchedulePost}
                disabled={scheduling || uploadingScheduleMedia || !scheduleTitle.trim() || !scheduleContent.trim() || !scheduleDate || !scheduleTime || schedulePlatforms.length === 0 || (schedulePlatforms.includes('twitter') && scheduleContent.length > TWITTER_MAX_LENGTH)}
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
                setEditPlatforms([]);
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
                <label className="block text-sm font-medium text-brand-silver mb-2">Platforms</label>
                <div className="space-y-2">
                  {/* LinkedIn Option */}
                  <label className="flex items-center gap-3 cursor-pointer p-2 rounded hover:bg-white/5 transition-colors">
                    <input
                      type="checkbox"
                      checked={editPlatforms.includes('linkedin')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setEditPlatforms([...editPlatforms, 'linkedin']);
                        } else {
                          setEditPlatforms(editPlatforms.filter(p => p !== 'linkedin'));
                        }
                      }}
                      className="w-4 h-4 rounded border-brand-ghost/30 text-brand-electric focus:ring-brand-electric/50"
                    />
                    <div className="p-1.5 rounded bg-[#0A66C2]">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                      </svg>
                    </div>
                    <span className="text-sm text-white">LinkedIn</span>
                    <span className="text-xs text-brand-silver/50 ml-auto">Max 3,000 chars</span>
                  </label>
                  
                  {/* Twitter Option */}
                  <label className="flex items-center gap-3 cursor-pointer p-2 rounded hover:bg-white/5 transition-colors">
                    <input
                      type="checkbox"
                      checked={editPlatforms.includes('twitter')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setEditPlatforms([...editPlatforms, 'twitter']);
                        } else {
                          setEditPlatforms(editPlatforms.filter(p => p !== 'twitter'));
                        }
                      }}
                      className="w-4 h-4 rounded border-brand-ghost/30 text-brand-electric focus:ring-brand-electric/50"
                    />
                    <div className="p-1.5 rounded bg-black">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                      </svg>
                    </div>
                    <span className="text-sm text-white">Twitter/X</span>
                    <span className="text-xs text-brand-silver/50 ml-auto">Max {TWITTER_MAX_LENGTH} chars</span>
                  </label>
                </div>
                
                {/* Character limit warning */}
                {editPlatforms.includes('twitter') && editContent.length > TWITTER_MAX_LENGTH && (
                  <div className="mt-2 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
                    ⚠️ Content exceeds Twitter&apos;s {TWITTER_MAX_LENGTH} character limit ({editContent.length} chars)
                  </div>
                )}
                
                {editPlatforms.length === 0 && (
                  <div className="mt-2 text-xs text-yellow-400">
                    ⚠️ Please select at least one platform
                  </div>
                )}
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
                      accept={getAcceptedFileTypes(editPlatforms)}
                      className="hidden"
                      disabled={uploadingEditMedia}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          handleMediaUpload(file, setEditMediaUrns, setUploadingEditMedia, editPlatforms);
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
                <p className="text-xs text-brand-silver/50 mt-1">{getMediaHelperText(editPlatforms)}</p>
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
                  setEditPlatforms([]);
                }}
                className="px-6 py-2.5 rounded-lg border border-brand-ghost/30 text-brand-silver hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleEditPost}
                disabled={editing || uploadingEditMedia || !editTitle.trim() || !editContent.trim() || !editDate || !editTime || editPlatforms.length === 0 || (editPlatforms.includes('twitter') && editContent.length > TWITTER_MAX_LENGTH)}
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
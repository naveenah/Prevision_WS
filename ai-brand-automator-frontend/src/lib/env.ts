/**
 * Environment configuration
 * Centralized configuration for environment-specific settings
 */

export const env = {
  // API Configuration
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  apiVersion: 'v1',
  
  // Environment
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
  isTest: process.env.NODE_ENV === 'test',
  
  // Feature Flags
  enableErrorTracking: process.env.NEXT_PUBLIC_ENABLE_ERROR_TRACKING === 'true',
  enableAnalytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
  
  // Validation
  validate() {
    const missing: string[] = [];
    
    if (!this.apiUrl) {
      missing.push('NEXT_PUBLIC_API_URL');
    }
    
    if (missing.length > 0) {
      console.error(
        `Missing required environment variables: ${missing.join(', ')}\n` +
        'Please check your .env.local file.'
      );
    }
    
    return missing.length === 0;
  },
  
  // Get full API URL
  getApiUrl(path: string = '') {
    const base = `${this.apiUrl}/api/${this.apiVersion}`;
    return path ? `${base}${path.startsWith('/') ? path : `/${path}`}` : base;
  },
};

// Validate on load in development
if (env.isDevelopment) {
  env.validate();
}

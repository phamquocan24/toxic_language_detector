/**
 * API constants for the Toxic Language Detector
 * Service Worker compatible version (no ES modules)
 */

// API Base URL
const API_BASE_URL = 'http://localhost:7860';

// API Endpoints
const API_ENDPOINTS = {
  // Authentication endpoints
  AUTH: {
    LOGIN: '/auth/token',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/reset-password-request',
    RESET_PASSWORD: '/auth/reset-password',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    EXTENSION_AUTH: '/auth/extension-auth'
  },
  
  // Extension specific endpoints
  EXTENSION: {
    DETECT: '/extension/detect',
    BATCH_DETECT: '/extension/batch-detect',
    STATS: '/extension/stats',
    SETTINGS: '/extension/settings'
  },
  
  // Toxic analysis endpoints
  TOXIC: {
    SIMILAR: '/toxic/similar',
    STATISTICS: '/toxic/statistics',
    TREND: '/toxic/trend',
    TOXIC_KEYWORDS: '/toxic/toxic-keywords',
    COMMENT_CLUSTERS: '/toxic/comment-clusters',
    PLATFORMS: '/toxic/platforms'
  },
  
  // Prediction endpoints
  PREDICT: {
    SINGLE: '/predict/single',
    BATCH: '/predict/batch',
    ANALYZE_TEXT: '/predict/analyze-text',
    UPLOAD_CSV: '/predict/upload-csv',
    SIMILAR: '/predict/similar'
  },
  
  // Health check endpoint
  HEALTH: '/health'
};

// Toxicity categories
const API_TOXICITY_CATEGORIES = {
  CLEAN: 'clean',
  OFFENSIVE: 'offensive',
  HATE: 'hate',
  SPAM: 'spam'
};

// Default settings - renamed to avoid conflict with config/constants.js
const API_DEFAULT_SETTINGS = {
  enabled: true,
  threshold: 0.7,
  notifications: true,
  detectionMode: 'automatic',
  selectedLanguages: ['en', 'vi'],
  blockedSites: []
};

// Supported languages
const API_SUPPORTED_LANGUAGES = [
  { code: 'vi', name: 'Tiếng Việt' },
  { code: 'en', name: 'English' }
]; 
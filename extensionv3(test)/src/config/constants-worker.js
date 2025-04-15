/**
 * Configuration constants for the Toxic Language Detector extension
 * Service Worker compatible version (no ES modules)
 */

// API Configuration
const API_BASE_URL = 'http://localhost:7860';

// Constants object for backward compatibility
const CONSTANTS = {
  API_BASE_URL: 'http://localhost:7860',
  
  // Storage keys
  STORAGE_KEYS: {
    SETTINGS: 'settings',
    HISTORY: 'history',
    USER_DATA: 'userData',
    STATS: 'statistics'
  },
  
  // Default settings
  DEFAULT_SETTINGS: {
    enabled: true,
    threshold: 0.7,
    notifyOnDetection: true,
    autoBlockToxic: false,
    language: 'vi',
    showSuggestions: true,
    syncWithServer: true
  },
  
  // Supported languages
  SUPPORTED_LANGUAGES: [
    { code: 'vi', name: 'Tiếng Việt' },
    { code: 'en', name: 'English' }
  ],
  
  // Toxicity categories
  TOXICITY_CATEGORIES: {
    OFFENSIVE: 'offensive',
    HATE_SPEECH: 'hate_speech',
    PROFANITY: 'profanity',
    SPAM: 'spam',
    CLEAN: 'clean'
  }
};

// Storage keys
const STORAGE_KEYS = CONSTANTS.STORAGE_KEYS;

// Default settings
const DEFAULT_SETTINGS = CONSTANTS.DEFAULT_SETTINGS;

// Supported languages
const SUPPORTED_LANGUAGES = CONSTANTS.SUPPORTED_LANGUAGES;

// Toxicity categories
const TOXICITY_CATEGORIES = CONSTANTS.TOXICITY_CATEGORIES;

// Category labels (Vietnamese)
const CATEGORY_LABELS_VI = {
  [TOXICITY_CATEGORIES.OFFENSIVE]: 'Xúc phạm',
  [TOXICITY_CATEGORIES.HATE_SPEECH]: 'Phát ngôn thù ghét',
  [TOXICITY_CATEGORIES.PROFANITY]: 'Ngôn từ thô tục',
  [TOXICITY_CATEGORIES.SPAM]: 'Spam',
  [TOXICITY_CATEGORIES.CLEAN]: 'Bình thường'
};

// Category labels (English)
const CATEGORY_LABELS_EN = {
  [TOXICITY_CATEGORIES.OFFENSIVE]: 'Offensive',
  [TOXICITY_CATEGORIES.HATE_SPEECH]: 'Hate Speech',
  [TOXICITY_CATEGORIES.PROFANITY]: 'Profanity',
  [TOXICITY_CATEGORIES.SPAM]: 'Spam',
  [TOXICITY_CATEGORIES.CLEAN]: 'Clean'
};

// Notification settings
const NOTIFICATION_SETTINGS = {
  DEFAULT_ICON: 'icons/icon-48.png',
  SUCCESS_ICON: 'icons/icon-success-48.png',
  WARNING_ICON: 'icons/icon-warning-48.png',
  ERROR_ICON: 'icons/icon-error-48.png',
  TIMEOUT: 5000 // ms
}; 
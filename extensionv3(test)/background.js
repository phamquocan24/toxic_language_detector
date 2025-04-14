/**
 * Background script for the Toxic Language Detector Extension
 * Handles API communication, authentication and browser events
 */

// API Configuration
const API_CONFIG = {
  BASE_URL: 'http://localhost:7860',
  AUTH_ENDPOINTS: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/forgot-password',
    REFRESH_TOKEN: '/auth/refresh-token',
    ME: '/auth/me'
  },
  EXTENSION_ENDPOINTS: {
    DETECT: '/extension/detect',
    BATCH_DETECT: '/batch/detect',
    STATS: '/toxic/stats'
  }
};

// Initialize extension state
chrome.runtime.onInstalled.addListener(() => {
  // Default settings
  chrome.storage.sync.set({
    enabled: true,
    threshold: 0.7,
    highlightToxic: true,
    platforms: {
      facebook: true,
      youtube: true,
      twitter: true
    },
    stats: {
      scanned: 0,
      clean: 0,
      offensive: 0,
      hate: 0,
      spam: 0
    }
  });
  
  // Log for debugging
  console.log('Toxic Language Detector Extension installed/updated');
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "analyzeText") {
    analyzeText(message.text, message.platform, message.commentId, message.metadata)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Required for async sendResponse
  }
  
  if (message.action === "analyzeBatch") {
    analyzeBatch(message.items)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }
  
  if (message.action === "getSettings") {
    chrome.storage.sync.get(['enabled', 'threshold', 'highlightToxic', 'platforms', 'stats'], (data) => {
      sendResponse(data);
    });
    return true;
  }
  
  if (message.action === "settingsUpdated") {
    chrome.storage.sync.set(message.settings, () => {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (message.action === "resetStats") {
    chrome.storage.sync.set({
      stats: {
        scanned: 0,
        clean: 0,
        offensive: 0,
        hate: 0,
        spam: 0
      }
    }, () => {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (message.action === "checkAuth") {
    checkAuthentication()
      .then(isAuthenticated => sendResponse({ authenticated: isAuthenticated }))
      .catch(error => sendResponse({ authenticated: false, error: error.message }));
    return true;
  }
  
  if (message.action === "openDashboard") {
    chrome.tabs.create({ url: `${API_CONFIG.BASE_URL}/dashboard` });
    sendResponse({ success: true });
    return true;
  }
});

/**
 * Check if the user is authenticated
 * @returns {Promise<boolean>} true if authenticated
 */
async function checkAuthentication() {
  try {
    const { authToken } = await chrome.storage.local.get(['authToken']);
    
    if (!authToken) {
      return false;
    }
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH_ENDPOINTS.ME}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    return response.ok;
  } catch (error) {
    console.error('Authentication check failed:', error);
    return false;
  }
}

/**
 * Get the authentication token from storage
 * @returns {Promise<string|null>} The token or null
 */
async function getAuthToken() {
  try {
    const { authToken } = await chrome.storage.local.get(['authToken']);
    return authToken || null;
  } catch (error) {
    console.error('Error retrieving auth token:', error);
    return null;
  }
}

/**
 * Analyze text using the API
 * @param {string} text - The text to analyze
 * @param {string} platform - The platform (facebook, youtube, twitter)
 * @param {string} commentId - The ID of the comment
 * @param {Object} metadata - Additional metadata
 * @returns {Promise} - API response
 */
async function analyzeText(text, platform, commentId, metadata = {}) {
  try {
    // Get authentication token
    const authToken = await getAuthToken();
    
    if (!authToken) {
      throw new Error('Bạn cần đăng nhập để sử dụng tính năng này');
    }
    
    // Build request options
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.EXTENSION_ENDPOINTS.DETECT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        text: text,
        platform: platform || 'unknown',
        platform_id: commentId,
        metadata: {
          ...metadata,
          browser: navigator.userAgent
        },
        save_result: true
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Update local stats
    updateStats(result.prediction);
    
    return result;
  } catch (error) {
    console.error('Error analyzing text:', error);
    throw error;
  }
}

/**
 * Analyze batch of texts
 * @param {Array} items - Array of items to analyze
 * @returns {Promise} - API response
 */
async function analyzeBatch(items) {
  try {
    // Get authentication token
    const authToken = await getAuthToken();
    
    if (!authToken) {
      throw new Error('Bạn cần đăng nhập để sử dụng tính năng này');
    }
    
    // Build request
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.EXTENSION_ENDPOINTS.BATCH_DETECT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        items: items,
        store_clean: false
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }
    
    const results = await response.json();
    
    // Update local stats for each result
    if (results.results && Array.isArray(results.results)) {
      results.results.forEach(result => {
        updateStats(result.prediction);
      });
    }
    
    return results;
  } catch (error) {
    console.error('Error analyzing batch:', error);
    throw error;
  }
}

/**
 * Update statistics based on prediction result
 * @param {number} prediction - The prediction category (0-3)
 */
async function updateStats(prediction) {
  try {
    const { stats } = await chrome.storage.sync.get(['stats']);
    
    // Create default stats if not exist
    const currentStats = stats || {
      scanned: 0,
      clean: 0,
      offensive: 0,
      hate: 0,
      spam: 0
    };
    
    // Update counts
    currentStats.scanned += 1;
    
    switch (prediction) {
      case 0:
        currentStats.clean += 1;
        break;
      case 1:
        currentStats.offensive += 1;
        break;
      case 2:
        currentStats.hate += 1;
        break;
      case 3:
        currentStats.spam += 1;
        break;
    }
    
    // Save updated stats
    await chrome.storage.sync.set({ stats: currentStats });
    
  } catch (error) {
    console.error('Error updating stats:', error);
  }
}
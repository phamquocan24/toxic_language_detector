/**
 * Improved Background Script with Retry Logic
 * 
 * This is an improved version of background.js with:
 * - Retry logic with exponential backoff
 * - Better error handling
 * - Network failure recovery
 * - Automatic fallback to individual requests
 * 
 * To use this version, update manifest.json:
 * "background": {
 *   "service_worker": "background-improved.js"
 * }
 */

// Import APIClient (will be loaded via manifest.json)
// Make sure to add "utils/api-client.js" to manifest.json scripts

// Configuration
const API_CONFIG = {
  baseURL: "http://localhost:7860",
  maxRetries: 3,
  retryDelay: 1000,
  timeout: 30000
};

// Create API client instance
let apiClient = null;

// Initialize API client
function initializeAPIClient() {
  // Get auth credentials from storage
  chrome.storage.sync.get(['apiEndpoint', 'authToken'], (data) => {
    const baseURL = data.apiEndpoint || API_CONFIG.baseURL;
    const authToken = data.authToken || btoa("admin:password");
    
    apiClient = new APIClient({
      ...API_CONFIG,
      baseURL,
      authToken
    });
    
    console.log(`[Background] API Client initialized: ${baseURL}`);
  });
}

// Initialize on load
initializeAPIClient();

// Buffer for batch processing
let commentsBuffer = [];
const BATCH_SIZE = 100;
let batchProcessingTimeout = null;

// Initialize extension state
chrome.runtime.onInstalled.addListener(() => {
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
    },
    displayOptions: {
      showClean: true,
      showOffensive: true,
      showHate: true,
      showSpam: true
    },
    useBatchProcessing: true,
    // New settings
    apiEndpoint: API_CONFIG.baseURL,
    retryEnabled: true,
    maxRetries: 3
  });
  
  console.log('[Background] Extension installed and configured');
});

/**
 * Analyze single text (with retry)
 */
async function analyzeText(text, platform, commentId, sourceUrl) {
  if (!apiClient) {
    initializeAPIClient();
    // Wait a bit for initialization
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  try {
    const result = await apiClient.post('/api/extension/detect', {
      text,
      platform,
      platform_id: commentId,
      source_url: sourceUrl,
      save_to_db: false,
      metadata: {
        source: 'extension',
        browser: navigator.userAgent,
        timestamp: new Date().toISOString()
      }
    });

    // Update stats
    updateStats(result.prediction);

    return result;

  } catch (error) {
    console.error('[Background] Analysis failed:', error.message);
    
    // Return a fallback result
    return {
      text,
      prediction: 0,
      prediction_text: "bình thường",
      confidence: 0.5,
      error: error.message,
      fallback: true
    };
  }
}

/**
 * Add comment to batch buffer
 */
function addToBuffer(text, platform, commentId, sourceUrl) {
  return new Promise((resolve, reject) => {
    const commentIdentifier = `${platform}_${commentId}`;
    
    // Check for duplicates
    const existingIndex = commentsBuffer.findIndex(
      item => item.identifier === commentIdentifier
    );
    
    if (existingIndex >= 0) {
      console.log(`[Background] Duplicate comment ignored: ${commentIdentifier}`);
      resolve({ status: "buffered", duplicate: true });
      return;
    }
    
    // Add to buffer
    commentsBuffer.push({
      text,
      platform,
      platform_id: commentId,
      source_url: sourceUrl,
      identifier: commentIdentifier,
      resolve,
      reject
    });
    
    console.log(`[Background] Added to buffer: ${commentsBuffer.length}/${BATCH_SIZE}`);
    
    // Check if we should process now
    if (commentsBuffer.length >= BATCH_SIZE) {
      clearTimeout(batchProcessingTimeout);
      processCommentsBatch();
    } else if (!batchProcessingTimeout) {
      // Set timeout if not already set
      batchProcessingTimeout = setTimeout(() => {
        processCommentsBatch();
        batchProcessingTimeout = null;
      }, 2000); // 2 seconds
    }
  });
}

/**
 * Process buffered comments as batch (with retry)
 */
async function processCommentsBatch() {
  if (commentsBuffer.length === 0) {
    return;
  }
  
  if (!apiClient) {
    initializeAPIClient();
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  const batchToProcess = [...commentsBuffer];
  commentsBuffer = []; // Clear buffer

  console.log(`[Background] Processing batch of ${batchToProcess.length} comments`);

  try {
    // Prepare batch items
    const batchItems = batchToProcess.map(item => ({
      text: item.text,
      platform: item.platform,
      platform_id: item.platform_id,
      source_url: item.source_url,
      metadata: {
        source: 'extension',
        browser: navigator.userAgent,
        timestamp: new Date().toISOString()
      }
    }));

    // Send batch request (with automatic fallback)
    const batchResult = await apiClient.batchRequest(
      '/api/extension/batch-detect',
      batchItems,
      {
        save_to_db: false,
        store_clean: false
      }
    );

    console.log(`[Background] Batch processed: ${batchResult.count} results`);
    
    if (batchResult.fallback) {
      console.warn('[Background] Used fallback to individual requests');
    }

    // Create results map
    const resultsMap = {};
    batchResult.results.forEach((result, index) => {
      const identifier = batchToProcess[index].identifier;
      resultsMap[identifier] = result;
    });

    // Update stats and resolve promises
    batchToProcess.forEach(item => {
      const result = resultsMap[item.identifier];
      if (result) {
        if (!result.error) {
          updateStats(result.prediction);
        }
        item.resolve(result);
      } else {
        item.reject(new Error('No result for this comment'));
      }
    });

  } catch (error) {
    console.error('[Background] Batch processing failed:', error.message);

    // Reject all promises with error
    batchToProcess.forEach(item => {
      item.reject(error);
    });
  }
}

/**
 * Update local statistics
 */
function updateStats(prediction) {
  chrome.storage.sync.get('stats', (data) => {
    const stats = data.stats || {
      scanned: 0,
      clean: 0,
      offensive: 0,
      hate: 0,
      spam: 0
    };

    stats.scanned++;
    
    const categories = ['clean', 'offensive', 'hate', 'spam'];
    const category = categories[prediction] || 'clean';
    stats[category]++;

    chrome.storage.sync.set({ stats });
  });
}

/**
 * Report incorrect analysis
 */
async function reportIncorrectAnalysis(text, predictedCategory, commentId, sourceUrl) {
  if (!apiClient) {
    initializeAPIClient();
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  try {
    const result = await apiClient.post('/api/extension/report', {
      text,
      predicted_category: predictedCategory,
      comment_id: commentId,
      source_url: sourceUrl,
      metadata: {
        source: 'extension',
        browser: navigator.userAgent,
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      }
    });

    console.log('[Background] Report submitted successfully');
    return result;

  } catch (error) {
    console.error('[Background] Report submission failed:', error.message);
    throw error;
  }
}

/**
 * Health check
 */
async function checkAPIHealth() {
  if (!apiClient) {
    initializeAPIClient();
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  const health = await apiClient.healthCheck();
  console.log('[Background] API Health:', health.status);
  return health;
}

// Message listener
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Analyze text
  if (message.action === "analyzeText") {
    chrome.storage.sync.get('useBatchProcessing', (data) => {
      const useBatchProcessing = data.useBatchProcessing !== undefined ? 
        data.useBatchProcessing : true;
      
      if (useBatchProcessing) {
        addToBuffer(message.text, message.platform, message.commentId, sender.tab?.url)
          .then(result => sendResponse(result))
          .catch(error => sendResponse({ error: error.message }));
      } else {
        analyzeText(message.text, message.platform, message.commentId, sender.tab?.url)
          .then(result => sendResponse(result))
          .catch(error => sendResponse({ error: error.message }));
      }
    });
    return true;
  }
  
  // Get settings
  if (message.action === "getSettings") {
    chrome.storage.sync.get(null, (data) => {
      sendResponse(data);
    });
    return true;
  }
  
  // Update settings
  if (message.action === "updateSettings") {
    chrome.storage.sync.set(message.settings, () => {
      // Update API client config if needed
      if (message.settings.apiEndpoint || message.settings.maxRetries) {
        apiClient?.updateConfig({
          baseURL: message.settings.apiEndpoint,
          maxRetries: message.settings.maxRetries
        });
      }
      sendResponse({ success: true });
    });
    return true;
  }
  
  // Reset stats
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
  
  // Flush batch buffer
  if (message.action === "flushBatchBuffer") {
    if (commentsBuffer.length > 0) {
      clearTimeout(batchProcessingTimeout);
      processCommentsBatch()
        .then(() => sendResponse({ success: true }))
        .catch(error => sendResponse({ error: error.message }));
    } else {
      sendResponse({ success: true, message: "Buffer is empty" });
    }
    return true;
  }
  
  // Report incorrect analysis
  if (message.action === "reportIncorrectAnalysis") {
    reportIncorrectAnalysis(
      message.text,
      message.predictedCategory,
      message.commentId,
      message.sourceUrl
    )
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }
  
  // Health check
  if (message.action === "healthCheck") {
    checkAPIHealth()
      .then(health => sendResponse(health))
      .catch(error => sendResponse({ status: 'error', error: error.message }));
    return true;
  }
});

// Periodic health check (every 5 minutes)
setInterval(() => {
  checkAPIHealth();
}, 5 * 60 * 1000);

console.log('[Background] Improved background script loaded');


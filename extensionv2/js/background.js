/**
 * Background script for the Toxic Language Detector Extension
 * Handles API communication and browser events
 */

// Configuration
const API_ENDPOINT = "https://an24-toxic-language-detectorv1.hf.space";
const API_KEY = "IYHvZOJSoqSzLqGfEMPKbOgQDInKLFLKQmTXhlbIQnc"; // Store securely in production

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
      toxic: 0,
      clean: 0
    }
  });
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "analyzeText") {
    analyzeText(message.text, message.platform, message.commentId)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Required for async sendResponse
  }
  
  if (message.action === "getSettings") {
    chrome.storage.sync.get(null, (data) => {
      sendResponse(data);
    });
    return true;
  }
  
  if (message.action === "updateSettings") {
    chrome.storage.sync.set(message.settings, () => {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (message.action === "resetStats") {
    chrome.storage.sync.set({
      stats: {
        scanned: 0,
        toxic: 0,
        clean: 0
      }
    }, () => {
      sendResponse({ success: true });
    });
    return true;
  }
});

/**
 * Analyze text using the API
 * @param {string} text - The text to analyze
 * @param {string} platform - The platform (facebook, youtube, twitter)
 * @param {string} commentId - The ID of the comment
 * @returns {Promise} - API response
 */
async function analyzeText(text, platform, commentId) {
  try {
    const response = await fetch(`${API_ENDPOINT}/extension/detect`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
      },
      body: JSON.stringify({
        text: text,
        platform: platform,
        platform_id: commentId,
        metadata: {
          source: "extension",
          browser: navigator.userAgent
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Update stats
    chrome.storage.sync.get("stats", (data) => {
      const stats = data.stats || { scanned: 0, toxic: 0, clean: 0 };
      stats.scanned += 1;
      
      if (result.prediction > 0) {
        stats.toxic += 1;
      } else {
        stats.clean += 1;
      }
      
      chrome.storage.sync.set({ stats });
    });
    
    return result;
  } catch (error) {
    console.error("Error analyzing text:", error);
    throw error;
  }
}

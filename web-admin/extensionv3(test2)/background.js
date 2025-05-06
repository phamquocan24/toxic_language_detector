// Configuration
const API_URL = 'http://localhost:7860';
let API_TOKEN = null;
let API_TOKEN_EXPIRY = null;

// Initialize settings
let settings = {
    enabled: true,
    notifications: true,
    feedback: true,
    blockHate: false,
    blockOffensive: false,
    blockSpam: false,
    confidenceThreshold: 0.7,
    darkMode: false
};

// Statistics tracking
let sessionStats = {
    total: 0,
    clean: 0,
    offensive: 0,
    hate: 0,
    spam: 0,
    recent: []
};

// Load settings from storage
chrome.storage.sync.get('toxicDetectorSettings', function(data) {
    if (data.toxicDetectorSettings) {
        settings = { ...settings, ...data.toxicDetectorSettings };
    }
});

// Message handling
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'analyzeText') {
        analyzeText(request.text, request.info)
            .then(result => {
                // Update session statistics
                updateSessionStats(result);
                sendResponse({success: true, result: result});
            })
            .catch(error => {
                console.error('Error analyzing text:', error);
                sendResponse({success: false, error: error.message});
            });
        return true; // Indicates async response
    } else if (request.action === 'updateSettings') {
        settings = { ...settings, ...request.settings };
        chrome.storage.sync.set({toxicDetectorSettings: settings});
        sendResponse({success: true});
    } else if (request.action === 'getSettings') {
        sendResponse({success: true, settings: settings});
    } else if (request.action === 'getSessionStats') {
        // Calculate percentages
        const total = sessionStats.total || 1; // Avoid division by zero
        const percentages = {
            clean: Math.round((sessionStats.clean / total) * 100),
            offensive: Math.round((sessionStats.offensive / total) * 100),
            hate: Math.round((sessionStats.hate / total) * 100),
            spam: Math.round((sessionStats.spam / total) * 100)
        };
        
        sendResponse({
            success: true, 
            stats: {
                ...sessionStats,
                percentages: percentages
            }
        });
    } else if (request.action === 'resetSessionStats') {
        sessionStats = {
            total: 0,
            clean: 0,
            offensive: 0,
            hate: 0,
            spam: 0,
            recent: []
        };
        sendResponse({success: true, message: 'Session statistics reset'});
    }
});

/**
 * Get API authentication token via OAuth2 form data
 */
async function getApiToken() {
    // Return cached token if still valid
    if (API_TOKEN && API_TOKEN_EXPIRY && API_TOKEN_EXPIRY > Date.now()) {
        return API_TOKEN;
    }
    
    try {
        // Prepare URL-encoded form data
        const form = new URLSearchParams();
        form.append('username', 'admin');  // replace with dynamic creds if needed
        form.append('password', 'password');
        
        const response = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: form.toString()
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get token: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        API_TOKEN = data.access_token;
        API_TOKEN_EXPIRY = Date.now() + ((data.expires_in || 3600) * 1000);
        return API_TOKEN;
    } catch (error) {
        console.error('Error getting API token:', error);
        return null;
    }
}

/**
 * Analyze text for toxic content
 * @param {string} text - Text to analyze
 * @param {Object} info - Additional information about the content
 * @returns {Promise<Object>} - Analysis results
 */
async function analyzeText(text, info = {}) {
    if (!text || text.trim() === '') {
        return {
            text: text,
            prediction: 0,
            prediction_text: "clean",
            confidence: 1.0,
            keywords: []
        };
    }
    
    try {
        // First try to get a token
        const token = await getApiToken();
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_URL}/extension/detect`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                text: text,
                platform: 'extension',
                platform_id: info.platformId || '',
                source_url: info.sourceUrl || '',
                metadata: {
                    source: 'chrome-extension',
                    version: chrome.runtime.getManifest().version,
                    ...info
                }
            })
        });
        
        if (!response.ok) {
            // If authentication failed, try without token
            if (response.status === 401 && token) {
                // Clear token and try again
                API_TOKEN = null;
                return analyzeText(text, info);
            }
            
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Validate and sanitize the response
        if (!result || typeof result !== 'object') {
            throw new Error('Invalid API response');
        }
        
        return {
            text: result.text || text,
            prediction: result.prediction !== undefined ? result.prediction : 0,
            prediction_text: result.prediction_text || "clean",
            confidence: result.confidence || 0.0,
            keywords: Array.isArray(result.keywords) ? result.keywords : [],
            category: result.category || 'clean',
            probabilities: result.probabilities || {}
        };
    } catch (error) {
        console.error('Error during text analysis:', error);
        
        // Return fallback response
        return {
            text: text,
            prediction: 0,
            prediction_text: "clean",
            confidence: 1.0,
            keywords: [],
            error: error.message
        };
    }
}

/**
 * Update session statistics based on analysis result
 * @param {Object} result - Analysis result
 */
function updateSessionStats(result) {
    if (!result || typeof result !== 'object') {
        return;
    }
    
    sessionStats.total++;
    
    // Determine category from prediction or prediction_text
    let category = 'clean';
    if (result.category) {
        category = result.category;
    } else if (result.prediction_text) {
        category = result.prediction_text;
    } else if (typeof result.prediction === 'number') {
        const categories = ['clean', 'offensive', 'hate', 'spam'];
        category = categories[result.prediction] || 'clean';
    }
    
    // Update counters
    if (category in sessionStats) {
        sessionStats[category]++;
    } else {
        sessionStats.clean++;
    }
    
    // Add to recent items
    const recentItem = {
        text: result.text,
        category: category,
        confidence: result.confidence || 1.0,
        timestamp: new Date().toISOString()
    };
    
    sessionStats.recent.unshift(recentItem);
    
    // Keep only the 10 most recent items
    if (sessionStats.recent.length > 10) {
        sessionStats.recent = sessionStats.recent.slice(0, 10);
    }
} 
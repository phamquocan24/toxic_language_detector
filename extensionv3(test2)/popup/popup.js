/**
 * Popup script for the Toxic Language Detector Extension
 * Handles user settings and statistics for all 4 classification categories
 */

// Extension API Endpoint
const API_ENDPOINT = "http://localhost:7860";

// Authentication credentials - sử dụng credential từ background.js
const AUTH_CREDENTIALS = {
  username: "admin",
  password: "password"
};

// Create a Base64 encoded Basic Auth token
const BASIC_AUTH_TOKEN = btoa(`${AUTH_CREDENTIALS.username}:${AUTH_CREDENTIALS.password}`);

// Tab elements
const tabButtons = document.querySelectorAll('.tab-button');
const tabPanes = document.querySelectorAll('.tab-pane');

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePopup);

/**
 * Initialize the popup UI
 */
function initializePopup() {
  // Lấy các tham chiếu DOM elements
  initializeDOMReferences();
  
  // Thiết lập điều hướng tab
  setupTabNavigation();
  
  // Nạp cài đặt và thống kê
  loadSettings();
  loadStats();
  
  // Thiết lập xử lý sự kiện
  setupEventHandlers();
}

// DOM references
let enableToggle, thresholdSlider, thresholdValue, highlightToxic;
let platformFacebook, platformYoutube, platformTwitter;
let statScanned, statClean, statOffensive, statHate, statSpam, resetStatsBtn;
let showClean, showOffensive, showHate, showSpam;
let analyzeText, analyzeButton, resultContainer, resultCategory, resultConfidence;
let progressClean, progressOffensive, progressHate, progressSpam;
let percentClean, percentOffensive, percentHate, percentSpam;

/**
 * Initialize all DOM references
 */
function initializeDOMReferences() {
  // Settings elements
  enableToggle = document.getElementById('enable-toggle');
  thresholdSlider = document.getElementById('threshold');
  thresholdValue = document.getElementById('threshold-value');
  highlightToxic = document.getElementById('highlight-toxic');
  platformFacebook = document.getElementById('platform-facebook');
  platformYoutube = document.getElementById('platform-youtube');
  platformTwitter = document.getElementById('platform-twitter');

  // Classification visibility toggles
  showClean = document.getElementById('show-clean');
  showOffensive = document.getElementById('show-offensive');
  showHate = document.getElementById('show-hate');
  showSpam = document.getElementById('show-spam');
  
  // Statistics elements
  statScanned = document.getElementById('stat-scanned');
  statClean = document.getElementById('stat-clean');
  statOffensive = document.getElementById('stat-offensive');
  statHate = document.getElementById('stat-hate');
  statSpam = document.getElementById('stat-spam');
  resetStatsBtn = document.getElementById('reset-stats');
  
  // Text analysis elements
  analyzeText = document.getElementById('analyze-text');
  analyzeButton = document.getElementById('analyze-button');
  resultContainer = document.getElementById('result-container');
  resultCategory = document.getElementById('result-category');
  resultConfidence = document.getElementById('result-confidence');
  progressClean = document.getElementById('progress-clean');
  progressOffensive = document.getElementById('progress-offensive');
  progressHate = document.getElementById('progress-hate');
  progressSpam = document.getElementById('progress-spam');
  percentClean = document.getElementById('percent-clean');
  percentOffensive = document.getElementById('percent-offensive');
  percentHate = document.getElementById('percent-hate');
  percentSpam = document.getElementById('percent-spam');
}

// Category mapping
const categoryNames = {
  0: "Bình thường",
  1: "Xúc phạm",
  2: "Thù ghét",
  3: "Spam"
};

const categoryClasses = {
  0: "clean",
  1: "offensive",
  2: "hate",
  3: "spam"
};

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
  if (!tabButtons) return;
  
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Remove active class from all buttons and panes
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));
      
      // Add active class to clicked button
      button.classList.add('active');
      
      // Show corresponding pane
      const tabName = button.getAttribute('data-tab');
      const tabPane = document.getElementById(`${tabName}-tab`);
      if (tabPane) {
        tabPane.classList.add('active');
      }
    });
  });
}

/**
 * Load settings from storage
 */
function loadSettings() {
  chrome.storage.sync.get(null, function(data) {
    // Extension enabled
    if (enableToggle) {
      enableToggle.checked = data.enabled !== undefined ? data.enabled : true;
    }
    
    // Threshold value
    if (thresholdSlider && thresholdValue && data.threshold !== undefined) {
      thresholdSlider.value = data.threshold;
      thresholdValue.textContent = data.threshold;
    }
    
    // Highlight toxic
    if (highlightToxic) {
      highlightToxic.checked = data.highlightToxic !== undefined ? data.highlightToxic : true;
    }
    
    // Platform settings
    if (data.platforms) {
      if (platformFacebook) {
        platformFacebook.checked = data.platforms.facebook !== undefined ? data.platforms.facebook : true;
      }
      if (platformYoutube) {
        platformYoutube.checked = data.platforms.youtube !== undefined ? data.platforms.youtube : true;
      }
      if (platformTwitter) {
        platformTwitter.checked = data.platforms.twitter !== undefined ? data.platforms.twitter : true;
      }
    }
    
    // Display options
    if (data.displayOptions) {
      if (showClean) {
        showClean.checked = data.displayOptions.showClean !== undefined ? data.displayOptions.showClean : true;
      }
      if (showOffensive) {
        showOffensive.checked = data.displayOptions.showOffensive !== undefined ? data.displayOptions.showOffensive : true;
      }
      if (showHate) {
        showHate.checked = data.displayOptions.showHate !== undefined ? data.displayOptions.showHate : true;
      }
      if (showSpam) {
        showSpam.checked = data.displayOptions.showSpam !== undefined ? data.displayOptions.showSpam : true;
      }
    }
  });
}

/**
 * Load statistics from storage
 */
function loadStats() {
  chrome.storage.sync.get('stats', function(data) {
    if (data.stats) {
      if (statScanned) statScanned.textContent = data.stats.scanned || 0;
      if (statClean) statClean.textContent = data.stats.clean || 0;
      if (statOffensive) statOffensive.textContent = data.stats.offensive || 0;
      if (statHate) statHate.textContent = data.stats.hate || 0;
      if (statSpam) statSpam.textContent = data.stats.spam || 0;
    }
  });
}

/**
 * Save settings to chrome storage
 */
function saveSettings() {
  const settings = {
    enabled: enableToggle ? enableToggle.checked : true,
    threshold: thresholdSlider ? parseFloat(thresholdSlider.value) : 0.7,
    highlightToxic: highlightToxic ? highlightToxic.checked : true,
    platforms: {
      facebook: platformFacebook ? platformFacebook.checked : true,
      youtube: platformYoutube ? platformYoutube.checked : true,
      twitter: platformTwitter ? platformTwitter.checked : true
    },
    displayOptions: {
      showClean: showClean ? showClean.checked : true,
      showOffensive: showOffensive ? showOffensive.checked : true,
      showHate: showHate ? showHate.checked : true,
      showSpam: showSpam ? showSpam.checked : true
    }
  };
  
  chrome.storage.sync.set(settings, () => {
    // Thông báo cho content scripts rằng cài đặt đã thay đổi
    try {
      chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        if (tabs && tabs.length > 0 && tabs[0].id) {
          chrome.tabs.sendMessage(tabs[0].id, {
            action: "settingsUpdated",
            settings: settings
          }).catch(err => {
            console.log("Could not send settings update to content script: ", err);
          });
        }
      });
    } catch (err) {
      console.error("Error updating content script: ", err);
    }
  });
}

/**
 * Setup event handlers
 */
function setupEventHandlers() {
  // Enable toggle
  if (enableToggle) {
    enableToggle.addEventListener('change', function() {
      chrome.storage.sync.set({ enabled: this.checked });
    });
  }
  
  // Threshold slider
  if (thresholdSlider && thresholdValue) {
    thresholdSlider.addEventListener('input', function() {
      thresholdValue.textContent = this.value;
      chrome.storage.sync.set({ threshold: parseFloat(this.value) });
    });
  }
  
  // Highlight toxic checkbox
  if (highlightToxic) {
    highlightToxic.addEventListener('change', function() {
      chrome.storage.sync.set({ highlightToxic: this.checked });
    });
  }
  
  // Platform checkboxes
  function updatePlatforms() {
    if (platformFacebook && platformYoutube && platformTwitter) {
      chrome.storage.sync.set({
        platforms: {
          facebook: platformFacebook.checked,
          youtube: platformYoutube.checked,
          twitter: platformTwitter.checked
        }
      });
    }
  }
  
  if (platformFacebook) platformFacebook.addEventListener('change', updatePlatforms);
  if (platformYoutube) platformYoutube.addEventListener('change', updatePlatforms);
  if (platformTwitter) platformTwitter.addEventListener('change', updatePlatforms);
  
  // Display options checkboxes
  function updateDisplayOptions() {
    if (showClean && showOffensive && showHate && showSpam) {
      chrome.storage.sync.set({
        displayOptions: {
          showClean: showClean.checked,
          showOffensive: showOffensive.checked,
          showHate: showHate.checked,
          showSpam: showSpam.checked
        }
      });
    }
  }
  
  if (showClean) showClean.addEventListener('change', updateDisplayOptions);
  if (showOffensive) showOffensive.addEventListener('change', updateDisplayOptions);
  if (showHate) showHate.addEventListener('change', updateDisplayOptions);
  if (showSpam) showSpam.addEventListener('change', updateDisplayOptions);
  
  // Reset stats button
  if (resetStatsBtn) {
    resetStatsBtn.addEventListener('click', function() {
      chrome.runtime.sendMessage({ action: "resetStats" }, function(response) {
        if (response && response.success) {
          loadStats();
        }
      });
    });
  }
  
  // Text analysis
  if (analyzeButton && analyzeText) {
    analyzeButton.addEventListener('click', function() {
      const text = analyzeText.value.trim();
      
      if (!text) {
        alert('Vui lòng nhập văn bản cần phân tích!');
        return;
      }
      
      analyzeButton.disabled = true;
      analyzeButton.textContent = 'Đang phân tích...';
      
      analyzeTextWithAPI(text)
        .then(result => {
          displayAnalysisResult(result);
        })
        .catch(error => {
          alert(`Lỗi: ${error.message}`);
          console.error('Error analyzing text:', error);
        })
        .finally(() => {
          analyzeButton.disabled = false;
          analyzeButton.textContent = 'Phân tích';
        });
    });
  }
}

/**
 * Analyze text using the API
 * @param {string} text - The text to analyze
 * @returns {Promise} - Promise with result
 */
async function analyzeTextWithAPI(text) {
  try {
    const response = await fetch(`${API_ENDPOINT}/extension/detect`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Basic ${BASIC_AUTH_TOKEN}`
      },
      body: JSON.stringify({
        text: text,
        platform: "extension-popup",
        save_to_db: false  // Không lưu vào database, chỉ trả về kết quả phân loại
      })
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Lỗi xác thực. Vui lòng kiểm tra thông tin đăng nhập.");
      }
      throw new Error(`Lỗi API: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error analyzing text:", error);
    throw error;
  }
}

/**
 * Display analysis result
 * @param {Object} result - API response
 */
function displayAnalysisResult(result) {
  // Show result container
  if (!resultContainer || !resultCategory || !resultConfidence) return;
  
  resultContainer.classList.remove('hidden');
  
  // Set category and confidence
  const categoryName = categoryNames[result.prediction] || "Không xác định";
  const categoryClass = categoryClasses[result.prediction] || "";
  
  resultCategory.textContent = categoryName;
  resultCategory.className = `result-value ${categoryClass}`;
  
  resultConfidence.textContent = `${(result.confidence * 100).toFixed(1)}%`;
  
  // Set progress bars
  const probabilities = result.probabilities || {
    "clean": result.prediction === 0 ? result.confidence : 0,
    "offensive": result.prediction === 1 ? result.confidence : 0,
    "hate": result.prediction === 2 ? result.confidence : 0,
    "spam": result.prediction === 3 ? result.confidence : 0
  };
  
  const cleanProb = probabilities.clean || 0;
  const offensiveProb = probabilities.offensive || 0;
  const hateProb = probabilities.hate || 0;
  const spamProb = probabilities.spam || 0;
  
  if (progressClean) progressClean.style.width = `${cleanProb * 100}%`;
  if (progressOffensive) progressOffensive.style.width = `${offensiveProb * 100}%`;
  if (progressHate) progressHate.style.width = `${hateProb * 100}%`;
  if (progressSpam) progressSpam.style.width = `${spamProb * 100}%`;
  
  if (percentClean) percentClean.textContent = `${(cleanProb * 100).toFixed(1)}%`;
  if (percentOffensive) percentOffensive.textContent = `${(offensiveProb * 100).toFixed(1)}%`;
  if (percentHate) percentHate.textContent = `${(hateProb * 100).toFixed(1)}%`;
  if (percentSpam) percentSpam.textContent = `${(spamProb * 100).toFixed(1)}%`;
  
  // Log results for debugging
  console.log("Analysis result:", result);
}

// Handle real-time updates from other parts of the extension
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'sync') {
    // If stats changed, update the display
    if (changes.stats) {
      // Update statistics if they've changed
      if (statScanned) statScanned.textContent = changes.stats.newValue.scanned || 0;
      if (statClean) statClean.textContent = changes.stats.newValue.clean || 0;
      if (statOffensive) statOffensive.textContent = changes.stats.newValue.offensive || 0;
      if (statHate) statHate.textContent = changes.stats.newValue.hate || 0;
      if (statSpam) statSpam.textContent = changes.stats.newValue.spam || 0;
    }
  }
});
/**
 * Popup script for the Vietnamese Toxic Language Detector Extension
 * Handles user settings, analysis, and account management
 */

// Extension API Endpoint
const API_ENDPOINT = "http://localhost:7860";
// Authentication storage key
const AUTH_STORAGE_KEY = "toxicDetector_auth";

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePopup);

// Tab elements
const tabButtons = document.querySelectorAll('.tab-button');
const tabPanes = document.querySelectorAll('.tab-pane');

// DOM references for UI elements
let enableToggle, thresholdSlider, thresholdValue, highlightToxic, saveDataCheckbox;
let platformFacebook, platformYoutube, platformTwitter, platformTiktok, platformZalo;
let statScanned, statClean, statOffensive, statHate, statSpam, resetStatsBtn;
let showClean, showOffensive, showHate, showSpam;
let analyzeText, analyzeButton, resultContainer, resultCategory, resultConfidence;
let progressClean, progressOffensive, progressHate, progressSpam;
let percentClean, percentOffensive, percentHate, percentSpam;
let anonymousMode, regionSelect, reportButton, resultAdvanced, resultEmotion, resultIntent, resultKeywords;
let themeLight, themeDark, themeAuto;
let currentPlatform;

// Authentication UI elements
let loginSection, registerSection, profileSection, resetPasswordSection, changePasswordSection;
let loginForm, registerForm, resetPasswordForm, changePasswordForm;
let showRegisterBtn, showLoginBtn, forgotPasswordBtn, cancelResetBtn, cancelChangePasswordBtn;
let logoutBtn, changePasswordBtn;
let profileUsername, profileEmail, profileName, profileRole;

// Category mappings
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
 * Initialize the popup UI
 */
function initializePopup() {
  // Get DOM references for all elements
  initializeDOMReferences();
  
  // Setup tab navigation
  setupTabNavigation();
  
  // Load settings and statistics
  loadSettings();
  loadStats();
  
  // Setup event handlers for all UI interactions
  setupEventHandlers();
  
  // Check authentication status and update UI
  checkAuthStatus();
  
  // Detect current platform from active tab
  detectCurrentPlatform();
  
  // Setup batch detect UI and stats tab
  setupBatchDetectUI();
  setupStatsTab();
  
  // Setup analyze mode switch
  const singleBtn = document.getElementById('single-mode-btn');
  const batchBtn = document.getElementById('batch-mode-btn');
  const singleArea = document.getElementById('single-analyze-area');
  const batchArea = document.getElementById('batch-analyze-area');
  if (singleBtn && batchBtn && singleArea && batchArea) {
    singleBtn.onclick = function() {
      singleBtn.classList.add('active');
      batchBtn.classList.remove('active');
      singleArea.style.display = '';
      batchArea.style.display = 'none';
    };
    batchBtn.onclick = function() {
      batchBtn.classList.add('active');
      singleBtn.classList.remove('active');
      singleArea.style.display = 'none';
      batchArea.style.display = '';
    };
  }
}

/**
 * Initialize all DOM references
 */
function initializeDOMReferences() {
  // Settings elements
  enableToggle = document.getElementById('enable-toggle');
  thresholdSlider = document.getElementById('threshold');
  thresholdValue = document.getElementById('threshold-value');
  highlightToxic = document.getElementById('highlight-toxic');
  saveDataCheckbox = document.getElementById('save-data');
  
  // Platform settings
  platformFacebook = document.getElementById('platform-facebook');
  platformYoutube = document.getElementById('platform-youtube');
  platformTwitter = document.getElementById('platform-twitter');
  platformTiktok = document.getElementById('platform-tiktok');
  platformZalo = document.getElementById('platform-zalo');

  // Classification visibility toggles
  showClean = document.getElementById('show-clean');
  showOffensive = document.getElementById('show-offensive');
  showHate = document.getElementById('show-hate');
  showSpam = document.getElementById('show-spam');
  
  // Theme settings
  themeLight = document.getElementById('theme-light');
  themeDark = document.getElementById('theme-dark');
  themeAuto = document.getElementById('theme-auto');
  
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
  
  // Advanced analysis elements
  anonymousMode = document.getElementById('anonymous-mode');
  regionSelect = document.getElementById('region');
  reportButton = document.getElementById('report-button');
  resultAdvanced = document.getElementById('result-advanced');
  resultEmotion = document.getElementById('result-emotion');
  resultIntent = document.getElementById('result-intent');
  resultKeywords = document.getElementById('result-keywords');
  
  // Platform detection
  currentPlatform = document.getElementById('current-platform');
  
  // Authentication elements
  loginSection = document.getElementById('login-section');
  registerSection = document.getElementById('register-section');
  profileSection = document.getElementById('profile-section');
  resetPasswordSection = document.getElementById('reset-password-section');
  changePasswordSection = document.getElementById('change-password-section');
  
  loginForm = document.getElementById('login-form');
  registerForm = document.getElementById('register-form');
  resetPasswordForm = document.getElementById('reset-password-form');
  changePasswordForm = document.getElementById('change-password-form');
  
  showRegisterBtn = document.getElementById('show-register');
  showLoginBtn = document.getElementById('show-login');
  forgotPasswordBtn = document.getElementById('forgot-password');
  cancelResetBtn = document.getElementById('cancel-reset');
  cancelChangePasswordBtn = document.getElementById('cancel-change-password');
  
  logoutBtn = document.getElementById('logout-btn');
  changePasswordBtn = document.getElementById('change-password-btn');
  
  profileUsername = document.getElementById('profile-username');
  profileEmail = document.getElementById('profile-email');
  profileName = document.getElementById('profile-name');
  profileRole = document.getElementById('profile-role');
}

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
  if (!tabButtons || !tabButtons.length) return;
  
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
 * Detect the current platform from the active tab
 */
function detectCurrentPlatform() {
  if (!currentPlatform) return;
  
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    if (tabs.length === 0) return;
    
    const url = tabs[0].url;
    
    // Set platform name based on URL
    if (url.includes('facebook.com')) {
      currentPlatform.textContent = 'Facebook';
      currentPlatform.className = 'platform facebook';
    } else if (url.includes('youtube.com')) {
      currentPlatform.textContent = 'YouTube';
      currentPlatform.className = 'platform youtube';
    } else if (url.includes('twitter.com') || url.includes('x.com')) {
      currentPlatform.textContent = 'Twitter';
      currentPlatform.className = 'platform twitter';
    } else if (url.includes('tiktok.com')) {
      currentPlatform.textContent = 'TikTok';
      currentPlatform.className = 'platform tiktok';
    } else if (url.includes('zalo.me')) {
      currentPlatform.textContent = 'Zalo';
      currentPlatform.className = 'platform zalo';
    } else {
      currentPlatform.textContent = 'Khác';
      currentPlatform.className = 'platform other';
    }
  });
}

/**
 * Load settings from storage
 */
async function loadSettings() {
  chrome.storage.sync.get(null, async function(data) {
    let serverSettings = null;
    const authData = await getAuthData();
    if (authData && authData.access_token) {
      serverSettings = await fetchServerSettings();
    }
    const settings = serverSettings || data;
    // Extension enabled
    if (enableToggle) {
      enableToggle.checked = settings.enabled !== undefined ? settings.enabled : true;
    }
    
    // Threshold value
    if (thresholdSlider && thresholdValue && settings.threshold !== undefined) {
      thresholdSlider.value = settings.threshold;
      thresholdValue.textContent = settings.threshold;
    }
    
    // Highlight toxic
    if (highlightToxic) {
      highlightToxic.checked = settings.highlightToxic !== undefined ? settings.highlightToxic : true;
    }
    
    // Save data option
    if (saveDataCheckbox) {
      saveDataCheckbox.checked = settings.saveData !== undefined ? settings.saveData : true;
    }
    
    // Platform settings
    if (settings.platforms) {
      if (platformFacebook) {
        platformFacebook.checked = settings.platforms.facebook !== undefined ? settings.platforms.facebook : true;
      }
      if (platformYoutube) {
        platformYoutube.checked = settings.platforms.youtube !== undefined ? settings.platforms.youtube : true;
      }
      if (platformTwitter) {
        platformTwitter.checked = settings.platforms.twitter !== undefined ? settings.platforms.twitter : true;
      }
      if (platformTiktok) {
        platformTiktok.checked = settings.platforms.tiktok !== undefined ? settings.platforms.tiktok : false;
      }
      if (platformZalo) {
        platformZalo.checked = settings.platforms.zalo !== undefined ? settings.platforms.zalo : false;
      }
    }
    
    // Display options
    if (settings.displayOptions) {
      if (showClean) {
        showClean.checked = settings.displayOptions.showClean !== undefined ? settings.displayOptions.showClean : true;
      }
      if (showOffensive) {
        showOffensive.checked = settings.displayOptions.showOffensive !== undefined ? settings.displayOptions.showOffensive : true;
      }
      if (showHate) {
        showHate.checked = settings.displayOptions.showHate !== undefined ? settings.displayOptions.showHate : true;
      }
      if (showSpam) {
        showSpam.checked = settings.displayOptions.showSpam !== undefined ? settings.displayOptions.showSpam : true;
      }
    }
    
    // Theme settings
    if (settings.theme) {
      setTheme(settings.theme);
    } else {
      // Default to auto
      setTheme('auto');
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
      
      // Initialize statistics charts
      initStatsCharts(data.stats);
    }
  });
}

/**
 * Initialize statistics charts
 */
function initStatsCharts(stats) {
  // Đã loại bỏ code vẽ chart giả lập. Chỉ còn lại hàm rỗng để tránh lỗi gọi hàm cũ.
}

/**
 * Save settings to chrome storage
 */
async function saveSettings() {
  const settings = {
    enabled: enableToggle ? enableToggle.checked : true,
    threshold: thresholdSlider ? parseFloat(thresholdSlider.value) : 0.7,
    highlightToxic: highlightToxic ? highlightToxic.checked : true,
    saveData: saveDataCheckbox ? saveDataCheckbox.checked : true,
    platforms: {
      facebook: platformFacebook ? platformFacebook.checked : true,
      youtube: platformYoutube ? platformYoutube.checked : true,
      twitter: platformTwitter ? platformTwitter.checked : true,
      tiktok: platformTiktok ? platformTiktok.checked : false,
      zalo: platformZalo ? platformZalo.checked : false
    },
    displayOptions: {
      showClean: showClean ? showClean.checked : true,
      showOffensive: showOffensive ? showOffensive.checked : true,
      showHate: showHate ? showHate.checked : true,
      showSpam: showSpam ? showSpam.checked : true
    },
    theme: getActiveTheme()
  };
  
  chrome.storage.sync.set(settings, async () => {
    notifyContentScripts(settings);
    showNotification('Cài đặt đã được lưu', 'success');
    const authData = await getAuthData();
    if (authData && authData.access_token) {
      await saveServerSettings(settings);
    }
  });
}

/**
 * Notify content scripts about settings changes
 */
function notifyContentScripts(settings) {
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
}

/**
 * Set theme for the extension
 */
function setTheme(theme) {
  // Remove any active class from theme buttons
  if (themeLight) themeLight.classList.remove('active');
  if (themeDark) themeDark.classList.remove('active');
  if (themeAuto) themeAuto.classList.remove('active');
  
  // Add active class to selected theme button
  if (theme === 'light' && themeLight) {
    themeLight.classList.add('active');
    document.body.classList.remove('dark-mode');
    document.body.classList.add('light-mode');
  } else if (theme === 'dark' && themeDark) {
    themeDark.classList.add('active');
    document.body.classList.remove('light-mode');
    document.body.classList.add('dark-mode');
  } else if (theme === 'auto' && themeAuto) {
    themeAuto.classList.add('active');
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.body.classList.remove('light-mode');
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
      document.body.classList.add('light-mode');
    }
  }
  
  // Save theme setting
  chrome.storage.sync.set({ theme: theme });
}

/**
 * Get active theme
 */
function getActiveTheme() {
  if (themeLight && themeLight.classList.contains('active')) {
    return 'light';
  } else if (themeDark && themeDark.classList.contains('active')) {
    return 'dark';
  } else {
    return 'auto';
  }
}

// Helper: Show/hide loading spinner
function showLoading(id) {
  const el = document.getElementById(id);
  if (el) {
    el.innerHTML = '<div class="loading-spinner"></div> Đang tải...';
    el.style.display = '';
  }
}
function hideLoading(id) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = '';
}

/**
 * Analyze text using the API
 */
async function processAnalyzeText() {
  const textToAnalyze = analyzeText.value.trim();
  
  if (!textToAnalyze) {
    showNotification('Vui lòng nhập văn bản cần phân tích', 'error');
    return;
  }
  
  try {
    analyzeButton.disabled = true;
    analyzeButton.textContent = 'Đang phân tích...';
    showLoading('result-container');
    
    // Get platform from current tab
    let platform = 'unknown';
    if (currentPlatform && currentPlatform.textContent) {
      platform = currentPlatform.textContent.toLowerCase();
    }
    
    // Get authentication token
    const authData = await getAuthData();
    const token = authData ? authData.access_token : null;
    
    // Create request headers
    const headers = {
      'Content-Type': 'application/json'
    };
    
    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Get save data setting
    const saveData = saveDataCheckbox ? saveDataCheckbox.checked : false;
    
    // Get anonymization option
    const isAnonymous = anonymousMode ? anonymousMode.checked : false;
    
    // Get region context
    const region = regionSelect ? regionSelect.value : 'all';
    
    // Make API request
    const response = await fetch(`${API_ENDPOINT}/extension/detect`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        text: textToAnalyze,
        platform: platform,
        save_to_db: saveData,
        metadata: {
          anonymous: isAnonymous,
          region: region,
          source: 'extension-popup'
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Display analysis result
    displayAnalysisResult(result);
    
    // Update local statistics
    updateLocalStats(result.prediction);
    
  } catch (error) {
    console.error('Error analyzing text:', error);
    showNotification(`Lỗi: ${error.message}`, 'error');
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = 'Phân tích';
    hideLoading('result-container');
  }
}

/**
 * Display the analysis result in the UI
 */
function displayAnalysisResult(result) {
  if (!resultContainer || !resultCategory || !resultConfidence) return;
  
  // Show result container
  resultContainer.classList.remove('hidden');
  
  // Set category and confidence
  const predictionClass = categoryClasses[result.prediction] || 'unknown';
  const predictionText = categoryNames[result.prediction] || 'Không xác định';
  
  resultCategory.textContent = predictionText;
  resultCategory.className = `result-value ${predictionClass}`;
  
  // Format confidence as percentage
  const confidencePercent = Math.round(result.confidence * 100);
  resultConfidence.textContent = `${confidencePercent}%`;
  
  // Update progress bars
  if (result.probabilities) {
    // Set progress bars from probabilities
    setProgressBar(progressClean, percentClean, result.probabilities[0] || 0);
    setProgressBar(progressOffensive, percentOffensive, result.probabilities[1] || 0);
    setProgressBar(progressHate, percentHate, result.probabilities[2] || 0);
    setProgressBar(progressSpam, percentSpam, result.probabilities[3] || 0);
  } else {
    // If no probabilities, set only the predicted class to high value
    setProgressBar(progressClean, percentClean, result.prediction === 0 ? result.confidence : 0.1);
    setProgressBar(progressOffensive, percentOffensive, result.prediction === 1 ? result.confidence : 0.1);
    setProgressBar(progressHate, percentHate, result.prediction === 2 ? result.confidence : 0.1);
    setProgressBar(progressSpam, percentSpam, result.prediction === 3 ? result.confidence : 0.1);
  }
  
  // Show advanced analysis section if data is available
  if (resultAdvanced && (result.keywords || result.sentiment)) {
    resultAdvanced.classList.remove('hidden');
    
    // Set emotion/sentiment if available
    if (resultEmotion && result.sentiment) {
      resultEmotion.textContent = result.sentiment.label || 'Không xác định';
    }
    
    // Set intent if available
    if (resultIntent && result.intent) {
      resultIntent.textContent = result.intent || 'Không xác định';
    }
    
    // Set keywords if available
    if (resultKeywords && result.keywords && result.keywords.length > 0) {
      // Clear existing keywords
      resultKeywords.innerHTML = '';
      
      // Add each keyword as a chip
      result.keywords.forEach(keyword => {
        const keywordChip = document.createElement('span');
        keywordChip.className = 'keyword-chip';
        keywordChip.textContent = keyword;
        resultKeywords.appendChild(keywordChip);
      });
    } else if (resultKeywords) {
      resultKeywords.textContent = 'Không có từ khóa nổi bật';
    }
  } else if (resultAdvanced) {
    resultAdvanced.classList.add('hidden');
  }
}

/**
 * Set a progress bar value and percentage text
 */
function setProgressBar(progressElement, percentElement, value) {
  if (!progressElement || !percentElement) return;
  
  const percent = Math.round(value * 100);
  progressElement.style.width = `${percent}%`;
  percentElement.textContent = `${percent}%`;
}

/**
 * Update local statistics based on prediction
 */
function updateLocalStats(prediction) {
  chrome.storage.sync.get('stats', function(data) {
    const stats = data.stats || {
      scanned: 0,
      clean: 0,
      offensive: 0,
      hate: 0,
      spam: 0
    };
    
    // Increment scanned count
    stats.scanned += 1;
    
    // Increment specific category
    switch(prediction) {
      case 0:
        stats.clean += 1;
        break;
      case 1:
        stats.offensive += 1;
        break;
      case 2:
        stats.hate += 1;
        break;
      case 3:
        stats.spam += 1;
        break;
    }
    
    // Save updated stats
    chrome.storage.sync.set({ stats });
    
    // Update stats display
    if (statScanned) statScanned.textContent = stats.scanned;
    if (statClean) statClean.textContent = stats.clean;
    if (statOffensive) statOffensive.textContent = stats.offensive;
    if (statHate) statHate.textContent = stats.hate;
    if (statSpam) statSpam.textContent = stats.spam;
  });
}

/**
 * Report incorrect analysis to improve the model
 */
async function reportIncorrectAnalysis() {
  const textContent = analyzeText.value.trim();
  if (!textContent) return;
  
  try {
    // Get authentication token
    const authData = await getAuthData();
    const token = authData ? authData.access_token : null;
    
    // Create request headers
    const headers = {
      'Content-Type': 'application/json'
    };
    
    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Make API request to feedback endpoint
    const response = await fetch(`${API_ENDPOINT}/feedback/report`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        text: textContent,
        source: 'extension-popup',
        reported_by: authData ? authData.user_id : null
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    showNotification('Đã gửi báo cáo phân tích sai. Cảm ơn bạn đã giúp cải thiện hệ thống!', 'success');
    
  } catch (error) {
    console.error('Error reporting analysis:', error);
    showNotification(`Lỗi: ${error.message}`, 'error');
  }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
  const notification = document.getElementById('notification');
  if (!notification) return;
  
  // Set notification text and type
  notification.textContent = message;
  notification.className = `notification ${type}`;
  
  // Show notification
  notification.classList.remove('hidden');
  
  // Hide after 3 seconds
  setTimeout(() => {
    notification.classList.add('hidden');
  }, 3000);
}

/**
 * Setup event handlers for all UI interactions
 */
function setupEventHandlers() {
  // Settings tab handlers
  if (enableToggle) {
    enableToggle.addEventListener('change', function() {
      chrome.storage.sync.set({ enabled: this.checked });
    });
  }
  
  if (thresholdSlider && thresholdValue) {
    thresholdSlider.addEventListener('input', function() {
      thresholdValue.textContent = this.value;
    });
    
    thresholdSlider.addEventListener('change', function() {
      saveSettings();
    });
  }
  
  if (highlightToxic) {
    highlightToxic.addEventListener('change', saveSettings);
  }
  
  if (saveDataCheckbox) {
    saveDataCheckbox.addEventListener('change', saveSettings);
  }
  
  // Platform checkboxes
  const platformCheckboxes = [
    platformFacebook, platformYoutube, platformTwitter, platformTiktok, platformZalo
  ];
  
  platformCheckboxes.forEach(checkbox => {
    if (checkbox) {
      checkbox.addEventListener('change', saveSettings);
    }
  });
  
  // Display options
  const displayOptionCheckboxes = [showClean, showOffensive, showHate, showSpam];
  
  displayOptionCheckboxes.forEach(checkbox => {
    if (checkbox) {
      checkbox.addEventListener('change', saveSettings);
    }
  });
  
  // Theme buttons
  if (themeLight) {
    themeLight.addEventListener('click', () => setTheme('light'));
  }
  
  if (themeDark) {
    themeDark.addEventListener('click', () => setTheme('dark'));
  }
  
  if (themeAuto) {
    themeAuto.addEventListener('click', () => setTheme('auto'));
  }
  
  // Reset stats button
  if (resetStatsBtn) {
    resetStatsBtn.addEventListener('click', resetStats);
  }
  
  // Analysis button
  if (analyzeButton) {
    analyzeButton.addEventListener('click', processAnalyzeText);
  }
  
  // Report button
  if (reportButton) {
    reportButton.addEventListener('click', reportIncorrectAnalysis);
  }
  
  // Period selector buttons
  const periodButtons = document.querySelectorAll('.period-button');
  if (periodButtons) {
    periodButtons.forEach(button => {
      button.addEventListener('click', () => {
        periodButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Load stats for the selected period
        loadStatsForPeriod(button.getAttribute('data-period'));
      });
    });
  }
  
  // Authentication form handlers
  setupAuthHandlers();
}

/**
 * Setup authentication form handlers
 */
function setupAuthHandlers() {
  // Show register form
  if (showRegisterBtn) {
    showRegisterBtn.addEventListener('click', () => {
      showAuthSection('register');
    });
  }
  
  // Show login form
  if (showLoginBtn) {
    showLoginBtn.addEventListener('click', () => {
      showAuthSection('login');
    });
  }
  
  // Show forgot password form
  if (forgotPasswordBtn) {
    forgotPasswordBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showAuthSection('reset-password');
    });
  }
  
  // Cancel reset password
  if (cancelResetBtn) {
    cancelResetBtn.addEventListener('click', () => {
      showAuthSection('login');
    });
  }
  
  // Cancel change password
  if (cancelChangePasswordBtn) {
    cancelChangePasswordBtn.addEventListener('click', () => {
      showAuthSection('profile');
    });
  }
  
  // Logout button
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  // Change password button
  if (changePasswordBtn) {
    changePasswordBtn.addEventListener('click', () => {
      showAuthSection('change-password');
    });
  }
  
  // Login form submission
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      login();
    });
  }
  
  // Register form submission
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      register();
    });
  }
  
  // Reset password form submission
  if (resetPasswordForm) {
    resetPasswordForm.addEventListener('submit', (e) => {
      e.preventDefault();
      requestPasswordReset();
    });
  }
  
  // Change password form submission
  if (changePasswordForm) {
    changePasswordForm.addEventListener('submit', (e) => {
      e.preventDefault();
      changePassword();
    });
  }
}

/**
 * Show the specified authentication section and hide others
 */
function showAuthSection(section) {
  // Hide all sections
  const sections = [
    loginSection, registerSection, profileSection, 
    resetPasswordSection, changePasswordSection
  ];
  
  sections.forEach(section => {
    if (section) section.classList.add('hidden');
  });
  
  // Show requested section
  switch (section) {
    case 'login':
      if (loginSection) loginSection.classList.remove('hidden');
      break;
    case 'register':
      if (registerSection) registerSection.classList.remove('hidden');
      break;
    case 'profile':
      if (profileSection) profileSection.classList.remove('hidden');
      break;
    case 'reset-password':
      if (resetPasswordSection) resetPasswordSection.classList.remove('hidden');
      break;
    case 'change-password':
      if (changePasswordSection) changePasswordSection.classList.remove('hidden');
      break;
  }
}

/**
 * Check authentication status and update UI
 */
async function checkAuthStatus() {
  try {
    const authData = await getAuthData();
    
    if (authData && authData.access_token) {
      // Verify token is still valid by making API request
      const response = await fetch(`${API_ENDPOINT}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authData.access_token}`
        }
      });
      
      if (response.ok) {
        // Token is valid, show profile section
        const userData = await response.json();
        updateProfileUI(userData);
        showAuthSection('profile');
      } else {
        // Token expired or invalid, show login screen
        showAuthSection('login');
        clearAuthData();
      }
    } else {
      // No token, show login screen
      showAuthSection('login');
    }
  } catch (error) {
    console.error('Error checking auth status:', error);
    showAuthSection('login');
  }
}

/**
 * Update the profile UI with user data
 */
function updateProfileUI(userData) {
  if (!profileUsername || !profileEmail || !profileName || !profileRole) return;
  
  profileUsername.textContent = userData.username || '';
  profileEmail.textContent = userData.email || '';
  profileName.textContent = userData.name || userData.username || '';
  profileRole.textContent = userData.role || 'user';
}

/**
 * Login using API
 */
async function login() {
  if (!loginForm) return;
  
  try {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const rememberMe = document.getElementById('login-remember').checked;
    
    if (!username || !password) {
      showNotification('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu', 'error');
      return;
    }
    
    // Create form data for token endpoint (API expects form data)
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    // Make API request
    const response = await fetch(`${API_ENDPOINT}/auth/token`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Tên đăng nhập hoặc mật khẩu không đúng');
      }
      throw new Error(`Lỗi đăng nhập: ${response.status}`);
    }
    
    const authData = await response.json();
    
    // Save authentication data
    await saveAuthData(authData, rememberMe);
    
    // Update UI
    const userDataResponse = await fetch(`${API_ENDPOINT}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${authData.access_token}`
      }
    });
    
    if (userDataResponse.ok) {
      const userData = await userDataResponse.json();
      updateProfileUI(userData);
      showAuthSection('profile');
      showNotification('Đăng nhập thành công', 'success');
    }
  } catch (error) {
    console.error('Login error:', error);
    showNotification(error.message || 'Lỗi đăng nhập', 'error');
  }
}

/**
 * Register new user
 */
async function register() {
  if (!registerForm) return;
  
  try {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const name = document.getElementById('register-name').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    // Validate fields
    if (!username || !email || !password || !confirmPassword) {
      showNotification('Vui lòng điền đầy đủ thông tin', 'error');
      return;
    }
    
    if (password !== confirmPassword) {
      showNotification('Mật khẩu xác nhận không khớp', 'error');
      return;
    }
    
    // Make API request
    const response = await fetch(`${API_ENDPOINT}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username,
        email,
        name,
        password
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Lỗi đăng ký');
    }
    
    showNotification('Đăng ký thành công! Vui lòng đăng nhập', 'success');
    showAuthSection('login');
    
    // Pre-fill login form
    if (document.getElementById('login-username')) {
      document.getElementById('login-username').value = username;
    }
  } catch (error) {
    console.error('Registration error:', error);
    showNotification(error.message || 'Lỗi đăng ký', 'error');
  }
}

/**
 * Request password reset
 */
async function requestPasswordReset() {
  if (!resetPasswordForm) return;
  
  try {
    const email = document.getElementById('reset-email').value;
    
    if (!email) {
      showNotification('Vui lòng nhập email', 'error');
      return;
    }
    
    // Make API request
    const response = await fetch(`${API_ENDPOINT}/auth/reset-password-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email
      })
    });
    
    // Always show success even if email doesn't exist (security best practice)
    showNotification('Nếu email tồn tại, bạn sẽ nhận được hướng dẫn khôi phục mật khẩu', 'success');
    showAuthSection('login');
  } catch (error) {
    // Still show success message even on error
    showNotification('Nếu email tồn tại, bạn sẽ nhận được hướng dẫn khôi phục mật khẩu', 'success');
    showAuthSection('login');
  }
}

/**
 * Change password
 */
async function changePassword() {
  if (!changePasswordForm) return;
  
  try {
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmNewPassword = document.getElementById('confirm-new-password').value;
    
    // Validate fields
    if (!currentPassword || !newPassword || !confirmNewPassword) {
      showNotification('Vui lòng điền đầy đủ thông tin', 'error');
      return;
    }
    
    if (newPassword !== confirmNewPassword) {
      showNotification('Mật khẩu mới xác nhận không khớp', 'error');
      return;
    }
    
    // Get authentication token
    const authData = await getAuthData();
    
    if (!authData || !authData.access_token) {
      showNotification('Bạn cần đăng nhập lại', 'error');
      showAuthSection('login');
      return;
    }
    
    // Make API request
    const response = await fetch(`${API_ENDPOINT}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authData.access_token}`
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Lỗi đổi mật khẩu');
    }
    
    showNotification('Đổi mật khẩu thành công', 'success');
    showAuthSection('profile');
    
    // Clear password fields
    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-new-password').value = '';
  } catch (error) {
    console.error('Change password error:', error);
    showNotification(error.message || 'Lỗi đổi mật khẩu', 'error');
  }
}

/**
 * Logout the user
 */
async function logout() {
  try {
    // Get authentication token
    const authData = await getAuthData();
    
    if (authData && authData.access_token) {
      // Call logout API
      await fetch(`${API_ENDPOINT}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authData.access_token}`
        }
      }).catch(() => {
        // Ignore errors from logout API
      });
    }
    
    // Clear local authentication data
    clearAuthData();
    
    // Show login screen
    showAuthSection('login');
    showNotification('Đăng xuất thành công', 'success');
  } catch (error) {
    console.error('Logout error:', error);
    
    // Force logout locally even if API call failed
    clearAuthData();
    showAuthSection('login');
  }
}

/**
 * Save authentication data to storage
 */
async function saveAuthData(authData, persistent = false) {
  return new Promise((resolve) => {
    const storage = persistent ? chrome.storage.sync : chrome.storage.local;
    storage.set({ [AUTH_STORAGE_KEY]: authData }, () => {
      resolve();
    });
  });
}

/**
 * Get authentication data from storage
 */
async function getAuthData() {
  return new Promise((resolve) => {
    // First try local storage
    chrome.storage.local.get([AUTH_STORAGE_KEY], (localData) => {
      if (localData && localData[AUTH_STORAGE_KEY]) {
        resolve(localData[AUTH_STORAGE_KEY]);
      } else {
        // If not in local, try sync storage
        chrome.storage.sync.get([AUTH_STORAGE_KEY], (syncData) => {
          resolve(syncData && syncData[AUTH_STORAGE_KEY] ? syncData[AUTH_STORAGE_KEY] : null);
        });
      }
    });
  });
}

/**
 * Clear authentication data from storage
 */
function clearAuthData() {
  chrome.storage.local.remove([AUTH_STORAGE_KEY]);
  chrome.storage.sync.remove([AUTH_STORAGE_KEY]);
}

/**
 * Load statistics for the selected period
 */
async function loadStatsForPeriod(period) {
  try {
    // Get authentication token
    const authData = await getAuthData();
    
    if (!authData || !authData.access_token) {
      // Use local stats if not authenticated
      return;
    }
    
    // Make API request to get stats for selected period
    const response = await fetch(`${API_ENDPOINT}/extension/stats?period=${period}`, {
      headers: {
        'Authorization': `Bearer ${authData.access_token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const stats = await response.json();
    
    // Update stats UI
    updateStatsUI(stats);
    
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

/**
 * Update statistics UI with data from API
 */
function updateStatsUI(statsData) {
  // Update counters
  if (statScanned) statScanned.textContent = statsData.total_count || 0;
  if (statClean) statClean.textContent = statsData.clean_count || 0;
  if (statOffensive) statOffensive.textContent = statsData.offensive_count || 0;
  if (statHate) statHate.textContent = statsData.hate_count || 0;
  if (statSpam) statSpam.textContent = statsData.spam_count || 0;
  
  // Update platform chart if exists
  updatePlatformChart(statsData.platforms);
}

/**
 * Update platform distribution chart
 */
function updatePlatformChart(platformData) {
  // Skip if Chart.js isn't loaded
  if (typeof Chart === 'undefined') return;
  
  const platformsChartElement = document.getElementById('platforms-chart');
  if (!platformsChartElement) return;
  
  // Get existing chart instance
  const existingChart = Chart.getChart(platformsChartElement);
  if (existingChart) {
    existingChart.destroy();
  }
  
  // Format data for chart
  const labels = [];
  const data = [];
  const colors = {
    facebook: '#4267B2',
    youtube: '#FF0000',
    twitter: '#1DA1F2',
    tiktok: '#000000',
    zalo: '#0068FF',
    other: '#999999'
  };
  const backgroundColor = [];
  
  // Process platform data
  for (const [platform, count] of Object.entries(platformData)) {
    labels.push(platform.charAt(0).toUpperCase() + platform.slice(1));
    data.push(count);
    backgroundColor.push(colors[platform.toLowerCase()] || colors.other);
  }
  
  // Create new chart
  new Chart(platformsChartElement, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: backgroundColor
      }]
    },
    options: {
      responsive: true,
      legend: {
        position: 'right',
        labels: {
          fontColor: '#666',
          boxWidth: 12
        }
      }
    }
  });
}

/**
 * Reset statistics
 */
function resetStats() {
  if (confirm('Bạn có chắc muốn đặt lại thống kê?')) {
    chrome.runtime.sendMessage({ action: "resetStats" }, function(response) {
      if (response && response.success) {
        // Reset UI stats
        if (statScanned) statScanned.textContent = '0';
        if (statClean) statClean.textContent = '0';
        if (statOffensive) statOffensive.textContent = '0';
        if (statHate) statHate.textContent = '0';
        if (statSpam) statSpam.textContent = '0';
        
        showNotification('Đã đặt lại thống kê', 'success');
      }
    });
  }
}

// 1. SETTINGS SYNC
async function fetchServerSettings() {
  const authData = await getAuthData();
  if (!authData || !authData.access_token) return null;
  const res = await fetch(`${API_ENDPOINT}/extension/settings`, {
    headers: { 'Authorization': `Bearer ${authData.access_token}` }
  });
  if (!res.ok) return null;
  const data = await res.json();
  return data.settings;
}
async function saveServerSettings(settings) {
  const authData = await getAuthData();
  if (!authData || !authData.access_token) return;
  await fetch(`${API_ENDPOINT}/extension/settings`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authData.access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
  });
}

// 2. STATISTICS ADVANCED
async function fetchTrend(period = 'week') {
  const authData = await getAuthData();
  if (!authData || !authData.access_token) return null;
  const res = await fetch(`${API_ENDPOINT}/extension/trend?period=${period}`, {
    headers: { 'Authorization': `Bearer ${authData.access_token}` }
  });
  if (!res.ok) return null;
  return await res.json();
}
async function fetchToxicKeywords(limit = 20) {
  const authData = await getAuthData();
  if (!authData || !authData.access_token) return null;
  const res = await fetch(`${API_ENDPOINT}/extension/toxic-keywords?limit=${limit}`, {
    headers: { 'Authorization': `Bearer ${authData.access_token}` }
  });
  if (!res.ok) return null;
  return await res.json();
}
// Hiển thị trend chart và toxic keywords
async function updateAdvancedStats(period = 'week') {
  const trend = await fetchTrend(period);
  console.log('[DEBUG] Trend API response:', trend);
  if (trend && trend.dates && trend.series) {
    // Vẽ lại trend chart
    const trendChartElement = document.getElementById('trend-chart');
    if (trendChartElement && typeof Chart !== 'undefined') {
      // Xóa chart cũ nếu có
      if (window.trendChartInstance) {
        window.trendChartInstance.destroy();
      }
      // Chuẩn bị datasets
      const datasets = [
        {
          label: 'Bình thường',
          data: trend.series.clean,
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderWidth: 2,
          fill: true
        },
        {
          label: 'Xúc phạm',
          data: trend.series.offensive,
          borderColor: '#FF9800',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          borderWidth: 2,
          fill: true
        },
        {
          label: 'Thù ghét',
          data: trend.series.hate,
          borderColor: '#F44336',
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          borderWidth: 2,
          fill: true
        },
        {
          label: 'Spam',
          data: trend.series.spam,
          borderColor: '#9C27B0',
          backgroundColor: 'rgba(156, 39, 176, 0.1)',
          borderWidth: 2,
          fill: true
        }
      ];
      window.trendChartInstance = new Chart(trendChartElement, {
        type: 'line',
        data: {
          labels: trend.dates,
          datasets: datasets
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true, position: 'top' }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  }
  const keywords = await fetchToxicKeywords();
  if (keywords && keywords.keywords) {
    const kwList = document.getElementById('toxic-keywords-list');
    kwList.innerHTML = '';
    keywords.keywords.forEach(k => {
      const span = document.createElement('span');
      span.className = 'keyword-chip';
      span.textContent = `${k.word} (${k.count})`;
      kwList.appendChild(span);
    });
  }
}
// 3. RECENT COMMENTS + DELETE
async function fetchRecentComments(period = 'week') {
  const authData = await getAuthData();
  if (!authData || !authData.access_token) return [];
  const res = await fetch(`${API_ENDPOINT}/extension/stats?period=${period}`, {
    headers: { 'Authorization': `Bearer ${authData.access_token}` }
  });
  if (!res.ok) return [];
  const data = await res.json();
  return data.recent || [];
}
async function deleteComment(commentId) {
  const authData = await getAuthData();
  if (!authData || !authData.access_token) throw new Error('Chưa đăng nhập');
  const res = await fetch(`${API_ENDPOINT}/extension/comments/${commentId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${authData.access_token}` }
  });
  if (!res.ok) throw new Error('Xóa thất bại');
  return await res.json();
}
async function updateRecentComments(period = 'week') {
  const list = document.getElementById('recent-comments-list');
  list.innerHTML = 'Đang tải...';
  const comments = await fetchRecentComments(period);
  list.innerHTML = '';
  comments.forEach(c => {
    const div = document.createElement('div');
    div.className = 'recent-comment-item';
    div.innerHTML = `<span>${c.content}</span> <span class="label ${categoryClasses[c.prediction]}">${categoryNames[c.prediction]}</span> <button class="delete-comment-btn" data-id="${c.id}">Xóa</button>`;
    list.appendChild(div);
  });
  // Gán sự kiện xóa
  list.querySelectorAll('.delete-comment-btn').forEach(btn => {
    btn.onclick = async (e) => {
      const id = btn.getAttribute('data-id');
      try {
        await deleteComment(id);
        showNotification('Đã xóa bình luận', 'success');
        updateRecentComments(period);
      } catch {
        showNotification('Xóa thất bại', 'error');
      }
    };
  });
}
// 4. BATCH DETECT
async function batchDetect(comments) {
  const authData = await getAuthData();
  const headers = { 'Content-Type': 'application/json' };
  if (authData && authData.access_token) {
    headers['Authorization'] = `Bearer ${authData.access_token}`;
  }
  const res = await fetch(`${API_ENDPOINT}/extension/batch-detect`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ items: comments, save_to_db: false })
  });
  if (!res.ok) throw new Error('Batch detect thất bại');
  return await res.json();
}
// Xử lý UI batch detect
function setupBatchDetectUI() {
  const input = document.getElementById('batch-input');
  const btn = document.getElementById('batch-detect-btn');
  const fileInput = document.getElementById('batch-file-input');
  const resultContainer = document.getElementById('batch-result-container');
  const resultList = document.getElementById('batch-result-list');
  btn.onclick = async () => {
    const lines = input.value.split('\n').map(l => l.trim()).filter(l => l);
    if (!lines.length) return showNotification('Nhập ít nhất 1 dòng', 'error');
    btn.disabled = true;
    showLoading('batch-result-list');
    try {
      const comments = lines.map(text => ({ text, platform: 'unknown' }));
      const res = await batchDetect(comments);
      resultList.innerHTML = '';
      res.results.forEach(r => {
        const div = document.createElement('div');
        div.innerHTML = `<span>${r.text}</span> <span class="label ${categoryClasses[r.prediction]}">${categoryNames[r.prediction]}</span> <span>${Math.round(r.confidence*100)}%</span>`;
        resultList.appendChild(div);
      });
      resultContainer.classList.remove('hidden');
    } catch (e) {
      showNotification(e.message, 'error');
    } finally {
      btn.disabled = false;
      hideLoading('batch-result-list');
    }
  };
  fileInput.onchange = async (e) => {
    const file = fileInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async function(ev) {
      const content = ev.target.result;
      const lines = content.split('\n').map(l => l.trim()).filter(l => l);
      if (!lines.length) return showNotification('File rỗng', 'error');
      btn.disabled = true;
      showLoading('batch-result-list');
      try {
        const comments = lines.map(text => ({ text, platform: 'unknown' }));
        const res = await batchDetect(comments);
        resultList.innerHTML = '';
        res.results.forEach(r => {
          const div = document.createElement('div');
          div.innerHTML = `<span>${r.text}</span> <span class="label ${categoryClasses[r.prediction]}">${categoryNames[r.prediction]}</span> <span>${Math.round(r.confidence*100)}%</span>`;
          resultList.appendChild(div);
        });
        resultContainer.classList.remove('hidden');
      } catch (e) {
        showNotification(e.message, 'error');
      } finally {
        btn.disabled = false;
        hideLoading('batch-result-list');
      }
    };
    reader.readAsText(file);
  };
}
// Gọi các hàm update khi chuyển tab statistics
function setupStatsTab() {
  const periodBtns = document.querySelectorAll('.period-button');
  let currentPeriod = 'week';
  periodBtns.forEach(btn => {
    btn.onclick = () => {
      periodBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentPeriod = btn.getAttribute('data-period');
      updateAdvancedStats(currentPeriod);
      updateRecentComments(currentPeriod);
      loadStatsForPeriod(currentPeriod);
    };
  });
  // Khi vào tab, load mặc định
  updateAdvancedStats(currentPeriod);
  updateRecentComments(currentPeriod);
  loadStatsForPeriod(currentPeriod);
}

document.getElementById('single-mode-btn').onclick = function() {
  this.classList.add('active');
  document.getElementById('batch-mode-btn').classList.remove('active');
  document.getElementById('single-analyze-area').style.display = '';
  document.getElementById('batch-analyze-area').style.display = 'none';
};
document.getElementById('batch-mode-btn').onclick = function() {
  this.classList.add('active');
  document.getElementById('single-mode-btn').classList.remove('active');
  document.getElementById('single-analyze-area').style.display = 'none';
  document.getElementById('batch-analyze-area').style.display = '';
};

// Initialize the extension
initializePopup();
/**
 * Popup script for the Vietnamese Toxic Language Detector Extension
 * Handles user settings, analysis, and account management
 */

/**
 * API Endpoint configuration
 * - For production, inject window.TOXIC_API_ENDPOINT in popup.html or set in chrome.storage.sync
 * - For dev, fallback to localhost
 */
let API_ENDPOINT = "http://localhost:7860";
if (typeof window !== 'undefined' && window.TOXIC_API_ENDPOINT) {
  API_ENDPOINT = window.TOXIC_API_ENDPOINT;
} else if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync) {
  chrome.storage.sync.get('api_endpoint', (data) => {
    if (data.api_endpoint) {
      API_ENDPOINT = data.api_endpoint;
    }
  });
}
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

// Batch Analyze UI elements
let singleModeBtn, batchModeBtn, singleAnalyzeArea, batchAnalyzeArea;
let batchInput, batchDetectBtn, batchFileInput, batchResultContainer, batchResultList;

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
  
  // Check authentication status and update UI accordingly FIRST
  checkAuthStatus().then(() => {
    // Setup tab navigation AFTER checking auth (to potentially hide tabs)
    setupTabNavigation();

    // Load settings and statistics
    loadSettings();
    loadStats(); // Local stats for anonymous, API stats for logged in

    // Setup event handlers for all UI interactions
    setupEventHandlers();

    // Detect current platform from active tab
    detectCurrentPlatform();

    // Setup batch detect UI and stats tab AFTER checking auth
    setupBatchDetectUI();
    setupStatsTab(); // Load stats for logged-in user if applicable

    // Setup analyze mode switch AFTER checking auth
    setupAnalyzeModeSwitch();
  });
}

// Đánh dấu các tab cần đăng nhập
document.addEventListener('DOMContentLoaded', function() {
  // Đánh dấu các tab yêu cầu đăng nhập
  const authRequiredTabs = document.querySelectorAll('.tab-button[data-tab="stats"], .tab-button[data-tab="settings"]');
  authRequiredTabs.forEach(tab => {
    tab.classList.add('requires-auth');
  });
  
  // Đánh dấu phần settings "Lưu dữ liệu phân tích" là yêu cầu đăng nhập
  const saveDataCheckbox = document.getElementById('save-data');
  if (saveDataCheckbox) {
    const saveDataItem = saveDataCheckbox.closest('.setting-item');
    if (saveDataItem) {
      saveDataItem.classList.add('requires-auth');
    }
  }
  
  // Đánh dấu batch mode là yêu cầu đăng nhập
  const batchModeBtn = document.getElementById('batch-mode-btn');
  if (batchModeBtn) {
    batchModeBtn.classList.add('requires-auth');
  }
  
  // Đánh dấu nút reset stats là yêu cầu đăng nhập
  const resetStatsBtn = document.getElementById('reset-stats');
  if (resetStatsBtn) {
    const container = resetStatsBtn.parentElement;
    if (container) {
      container.classList.add('requires-auth');
    }
  }
});

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

  // Batch Analyze elements
  singleModeBtn = document.getElementById('single-mode-btn');
  batchModeBtn = document.getElementById('batch-mode-btn');
  singleAnalyzeArea = document.getElementById('single-analyze-area');
  batchAnalyzeArea = document.getElementById('batch-analyze-area');
  batchInput = document.getElementById('batch-input');
  batchDetectBtn = document.getElementById('batch-detect-btn');
  batchFileInput = document.getElementById('batch-file-input');
  batchResultContainer = document.getElementById('batch-result-container');
  batchResultList = document.getElementById('batch-result-list');
}

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
  if (!tabButtons || !tabButtons.length) return;
  
  const isLoggedIn = document.body.classList.contains('logged-in');
  
  tabButtons.forEach(button => {
    const requiresAuth = button.classList.contains('requires-auth');
    
    // Hide tabs that require auth if not logged in
    if (requiresAuth && !isLoggedIn) {
      button.style.display = 'none';
      const tabName = button.getAttribute('data-tab');
      const tabPane = document.getElementById(`${tabName}-tab`);
      if (tabPane) {
        tabPane.style.display = 'none'; // Hide the pane content as well
      }
      return; // Skip adding click listener for hidden tabs
    } else {
      // Ensure visible otherwise
      button.style.display = '';
    }

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
        // Special handling for stats tab to load data when activated
        if (tabName === 'stats' && isLoggedIn) {
           setupStatsTab(); // Reload stats data when tab is clicked
        }
      }
    });
  });

  // Activate the first visible tab by default
  const firstVisibleTab = Array.from(tabButtons).find(btn => btn.style.display !== 'none');
  if (firstVisibleTab) {
    firstVisibleTab.click();
  }
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
  const isLoggedIn = document.body.classList.contains('logged-in');
  
  if (isLoggedIn) {
    // Load stats from API for the default period (e.g., 'week')
    loadStatsForPeriod('week'); 
  } else {
    // Load local stats from chrome.storage for anonymous users
    chrome.storage.sync.get('stats', function(data) {
      if (data.stats) {
        if (statScanned) statScanned.textContent = data.stats.scanned || 0;
        if (statClean) statClean.textContent = data.stats.clean || 0;
        if (statOffensive) statOffensive.textContent = data.stats.offensive || 0;
        if (statHate) statHate.textContent = data.stats.hate || 0;
        if (statSpam) statSpam.textContent = data.stats.spam || 0;
        
        // Initialize statistics charts with local data
        initStatsCharts(data.stats);
      } else {
         // Initialize with zeros if no local stats found
         if (statScanned) statScanned.textContent = 0;
         if (statClean) statClean.textContent = 0;
         if (statOffensive) statOffensive.textContent = 0;
         if (statHate) statHate.textContent = 0;
         if (statSpam) statSpam.textContent = 0;
         initStatsCharts({ scanned: 0, clean: 0, offensive: 0, hate: 0, spam: 0 });
      }
    });
  }
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
    
    // Hiển thị indicator loading nhỏ
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'analysis-loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner"></div> <span>Đang phân tích...</span>';
    loadingIndicator.style.padding = '10px';
    loadingIndicator.style.textAlign = 'center';
    loadingIndicator.style.color = '#0288d1';
    analyzeButton.after(loadingIndicator);
    
    // Hiển thị sẵn container kết quả
    const resultContainer = document.getElementById('result-container');
    if (resultContainer) {
      resultContainer.classList.remove('hidden');
      resultContainer.style.display = 'block'; // Force show
    }
    
    // Get platform from current tab
    let platform = 'unknown';
    if (currentPlatform && currentPlatform.textContent) {
      platform = currentPlatform.textContent.toLowerCase();
    }
    
    // Get authentication token
    const authData = await getAuthData();
    const token = authData ? authData.access_token : null;
    const isLoggedIn = !!token; // Check if logged in
    
    // Create request headers
    const headers = {
      'Content-Type': 'application/json'
    };
    
    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Determine if data should be saved (only if logged in and setting is checked)
    const shouldSaveData = isLoggedIn && saveDataCheckbox && saveDataCheckbox.checked;
    
    // Get anonymization option
    const isAnonymous = anonymousMode ? anonymousMode.checked : false;
    
    // Get region context
    const region = regionSelect ? regionSelect.value : 'all';
    
    console.log('[DEBUG] API Request:', {
      text: textToAnalyze,
      platform: platform,
      save_to_db: shouldSaveData,
      metadata: {
        anonymous: isAnonymous,
        region: region,
        source: 'extension-popup'
      }
    });
    
    // Make API request
    const response = await fetch(`${API_ENDPOINT}/extension/detect`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        text: textToAnalyze,
        platform: platform,
        save_to_db: shouldSaveData, // Use calculated value
        metadata: {
          anonymous: isAnonymous,
          region: region,
          source: 'extension-popup'
        }
      })
    });
    
    if (!response.ok) {
      // Handle potential 401 if token is required but missing/invalid for some reason
      if (response.status === 401) {
         clearAuthData(); // Clear invalid token data
         checkAuthStatus(); // Re-run auth check to update UI
         throw new Error(`Yêu cầu xác thực. Vui lòng đăng nhập lại.`);
      }
      throw new Error(`Lỗi API: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('[DEBUG] API Response:', result);
    
    // Display analysis result
    displayAnalysisResult(result);
    
    // Update local statistics
    updateLocalStats(result.prediction);
    
  } catch (error) {
    console.error('Error analyzing text:', error);
    showNotification(error.message, 'error');
    
    // Hiển thị lỗi trong khu vực kết quả
    const resultContainer = document.getElementById('result-container');
    if (resultContainer) {
      resultContainer.classList.remove('hidden');
      resultContainer.style.display = 'block';
      resultContainer.innerHTML = `<div style="color:#d32f2f; padding: 15px;">
        <h3>Lỗi phân tích</h3>
        <p>${error.message}</p>
        <p>Vui lòng thử lại sau hoặc kiểm tra kết nối mạng.</p>
      </div>`;
    }
    
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = 'Phân tích';
    
    // Xóa indicator loading
    const loadingIndicator = document.getElementById('analysis-loading-indicator');
    if (loadingIndicator) {
      loadingIndicator.remove();
    }
  }
}

/**
 * Display the analysis result in the UI
 */
function displayAnalysisResult(result) {
  console.log('[DEBUG] displayAnalysisResult input:', result);
  
  // Make sure we are using the single-mode result container
  const resultContainer = document.getElementById('result-container');
  const resultCategory = document.getElementById('result-category'); 
  const resultConfidence = document.getElementById('result-confidence');
  
  if (!resultContainer) {
    console.error('[ERROR] resultContainer not found');
    return;
  }
  
  // Kiểm tra dữ liệu đầu vào
  if (typeof result.prediction === 'undefined' || typeof result.confidence === 'undefined') {
    resultContainer.classList.remove('hidden');
    resultContainer.style.display = 'block'; // Force show for debug
    resultContainer.innerHTML = '<div style="color:#d32f2f;">Không có kết quả phân tích hợp lệ từ API.<br>Chi tiết: ' + JSON.stringify(result) + '</div>';
    console.log('[DEBUG] resultContainer.innerHTML (error):', resultContainer.innerHTML);
    return;
  }
  
  // Show result container
  resultContainer.classList.remove('hidden');
  resultContainer.style.display = 'block'; // Force show for debug
  
  // Render kết quả vào DOM elements từ popup.html
  // Cập nhật category và confidence
  const category = document.getElementById('result-category');
  const confidence = document.getElementById('result-confidence');
  
  if (category && confidence) {
    // Cập nhật category
    category.textContent = categoryNames[result.prediction] || 'Không xác định';
    // Xóa tất cả các CSS class cũ và thêm class mới
    category.className = 'result-value ' + (categoryClasses[result.prediction] || 'unknown');
    // Cập nhật confidence
    confidence.textContent = Math.round(result.confidence * 100) + '%';
  } else {
    console.error('[ERROR] result-category or result-confidence elements not found');
  }
  
  // Cập nhật các progress bar
  let p = result.probabilities;
  let clean = 0, offensive = 0, hate = 0, spam = 0;
  
  if (p) {
    if (typeof p === 'object' && !Array.isArray(p)) {
      clean = p.clean || 0;
      offensive = p.offensive || 0;
      hate = p.hate || 0;
      spam = p.spam || 0;
    } else if (Array.isArray(p)) {
      clean = p[0] || 0;
      offensive = p[1] || 0;
      hate = p[2] || 0;
      spam = p[3] || 0;
    }
  } else {
    clean = result.prediction === 0 ? result.confidence : 0.1;
    offensive = result.prediction === 1 ? result.confidence : 0.1;
    hate = result.prediction === 2 ? result.confidence : 0.1;
    spam = result.prediction === 3 ? result.confidence : 0.1;
  }
  
  // Update progress bars using the existing setProgressBar function
  setProgressBar(document.getElementById('progress-clean'), document.getElementById('percent-clean'), clean);
  setProgressBar(document.getElementById('progress-offensive'), document.getElementById('percent-offensive'), offensive);
  setProgressBar(document.getElementById('progress-hate'), document.getElementById('percent-hate'), hate);
  setProgressBar(document.getElementById('progress-spam'), document.getElementById('percent-spam'), spam);
  
  // Update advanced result section if available
  const resultAdvanced = document.getElementById('result-advanced');
  if (resultAdvanced) {
    resultAdvanced.classList.remove('hidden');
    
    const resultEmotion = document.getElementById('result-emotion');
    const resultIntent = document.getElementById('result-intent');
    const resultKeywords = document.getElementById('result-keywords');
    
    if (resultEmotion) {
      resultEmotion.textContent = result.sentiment && result.sentiment.label ? result.sentiment.label : 'Không xác định';
    }
    
    if (resultIntent) {
      resultIntent.textContent = result.intent || 'Không xác định';
    }
    
    if (resultKeywords) {
      resultKeywords.innerHTML = '';
      if (result.keywords && Array.isArray(result.keywords) && result.keywords.length > 0) {
        result.keywords.forEach(keyword => {
          const chip = document.createElement('span');
          chip.className = 'keyword-chip';
          chip.textContent = keyword;
          resultKeywords.appendChild(chip);
        });
      } else {
        resultKeywords.innerHTML = '<span style="color:#888">Không có từ khóa nổi bật</span>';
      }
    }
  }
  
  // Re-attach event listeners if needed
  const reportButton = document.getElementById('report-button');
  if (reportButton) {
    reportButton.onclick = reportIncorrectAnalysis;
  }
  
  // Log after UI update
  console.log('[DEBUG] Result displayed successfully');
  console.log('[DEBUG] resultContainer.classList:', resultContainer.classList.value, '| style.display:', resultContainer.style.display);
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
  // Only update local stats for anonymous users
  const isLoggedIn = document.body.classList.contains('logged-in');
  if (isLoggedIn) return;

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
      throw new Error(`Lỗi API: ${response.status}`);
    }
    
    showNotification('Đã gửi báo cáo phân tích sai. Cảm ơn bạn đã giúp cải thiện hệ thống!', 'success');
    
  } catch (error) {
    console.error('Error reporting analysis:', error);
    showNotification(error.message, 'error');
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
  
  // Analysis button for single text
  if (analyzeButton) {
    analyzeButton.addEventListener('click', processAnalyzeText);
  }
  
  // Analysis button for batch text
  const batchDetectBtn = document.getElementById('batch-detect-btn');
  if (batchDetectBtn) {
    batchDetectBtn.addEventListener('click', processBatchText);
  }
  
  // Report button - using event delegation because it might be dynamically created
  document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'report-button') {
      reportIncorrectAnalysis();
    }
  });
  
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
        document.body.classList.add('logged-in');
        document.body.classList.remove('not-logged-in');
        const userData = await response.json();
        updateProfileUI(userData);
        showAuthSection('profile');
        return true;
      } else {
        // Token expired or invalid, show login screen
        document.body.classList.remove('logged-in');
        document.body.classList.add('not-logged-in');
        showAuthSection('login');
        clearAuthData();
        return false;
      }
    } else {
      // No token, show login screen
      document.body.classList.remove('logged-in');
      document.body.classList.add('not-logged-in');
      showAuthSection('login');
      return false;
    }
  } catch (error) {
    console.error('Error checking auth status:', error);
    document.body.classList.remove('logged-in');
    document.body.classList.add('not-logged-in');
    showAuthSection('login');
    return false;
  }
}

/**
 * Apply simple UI updates based on authentication state
 */
function updateAuthDependentUI(isLoggedIn) {
  console.log("Cập nhật UI dựa trên đăng nhập:", isLoggedIn);
  
  // Quản lý hiển thị tab
  const tabButtons = document.querySelectorAll('.tab-button');
  tabButtons.forEach(button => {
    const tabName = button.getAttribute('data-tab');
    const isAuthRequired = button.classList.contains('requires-auth');
    
    if (isAuthRequired) {
      button.style.display = isLoggedIn ? '' : 'none';
      
      // Ẩn/hiện nội dung tab tương ứng
      const tabPane = document.getElementById(`${tabName}-tab`);
      if (tabPane) {
        tabPane.style.display = isLoggedIn ? '' : 'none';
      }
    }
  });
  
  // Kích hoạt tab hợp lệ đầu tiên
  let activeTabButton = document.querySelector('.tab-button.active');
  // Nếu tab đang kích hoạt không khả dụng, chuyển sang tab đầu tiên khả dụng
  if (!activeTabButton || (activeTabButton.classList.contains('requires-auth') && !isLoggedIn)) {
    const firstVisibleTab = Array.from(tabButtons).find(btn => btn.style.display !== 'none');
    if (firstVisibleTab) {
      // Bỏ active khỏi tất cả tab và pane
      tabButtons.forEach(btn => btn.classList.remove('active'));
      const tabPanes = document.querySelectorAll('.tab-pane');
      tabPanes.forEach(pane => pane.classList.remove('active'));
      
      // Kích hoạt tab đầu tiên khả dụng
      firstVisibleTab.classList.add('active');
      const tabName = firstVisibleTab.getAttribute('data-tab');
      const tabPane = document.getElementById(`${tabName}-tab`);
      if (tabPane) tabPane.classList.add('active');
    }
  }
  
  // Chế độ phân tích
  const batchModeBtn = document.getElementById('batch-mode-btn');
  if (batchModeBtn) {
    batchModeBtn.style.display = isLoggedIn ? '' : 'none';
    
    if (!isLoggedIn) {
      // Nếu đang ở chế độ batch mà đăng xuất, chuyển về chế độ single
      const singleModeBtn = document.getElementById('single-mode-btn');
      if (singleModeBtn && !singleModeBtn.classList.contains('active')) {
        singleModeBtn.click();
      }
    }
  }
  
  // Checkbox "lưu dữ liệu"
  const saveDataCheckbox = document.getElementById('save-data');
  if (saveDataCheckbox) {
    // Vô hiệu hóa nếu chưa đăng nhập
    saveDataCheckbox.disabled = !isLoggedIn;
    // Bỏ chọn nếu chưa đăng nhập
    if (!isLoggedIn) saveDataCheckbox.checked = false;
  }
  
  // Nút reset thống kê
  const resetStatsBtn = document.getElementById('reset-stats');
  if (resetStatsBtn) {
    resetStatsBtn.style.display = isLoggedIn ? '' : 'none';
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
      
      // Add logged-in class to body
      document.body.classList.add('logged-in');
      document.body.classList.remove('not-logged-in');
      
      // Update profile info
      updateProfileUI(userData);
      
      // Show profile section
      showAuthSection('profile');
      
      // Update UI based on authenticated state
      updateAuthDependentUI(true);
      
      // Initialize tab navigation again with new auth status
      setupTabNavigation();
      
      // Switch to analyze tab
      const analyzeTab = document.querySelector('.tab-button[data-tab="analyze"]');
      if (analyzeTab) {
        analyzeTab.click();
      }
      
      // Show notification
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
    
    // Update UI for logged-out state
    document.body.classList.remove('logged-in');
    document.body.classList.add('not-logged-in');
    
    // Show login section
    showAuthSection('login');
    
    // Show notification
    showNotification('Đăng xuất thành công', 'success');
    
    // Switch to analyze tab
    const analyzeTabButton = document.querySelector('.tab-button[data-tab="analyze"]');
    if (analyzeTabButton) {
      analyzeTabButton.click();
    }
    
    // Ensure single mode is active
    const singleModeBtn = document.getElementById('single-mode-btn');
    if (singleModeBtn) {
      singleModeBtn.click();
    }
  } catch (error) {
    console.error('Logout error:', error);
    
    // Force logout UI update on error
    document.body.classList.remove('logged-in');
    document.body.classList.add('not-logged-in');
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
    const isLoggedIn = document.body.classList.contains('logged-in');
    
    if (!authData || !authData.access_token || !isLoggedIn) {
      // Use local stats if not authenticated
      return;
    }
    
    // Show loading indicator
    const batchResultList = document.getElementById('batch-result-list');
    if (batchResultList) {
      const loadingIndicator = document.createElement('div');
      loadingIndicator.id = 'batch-loading-indicator';
      loadingIndicator.innerHTML = '<div class="spinner"></div> <span>Đang tải thống kê...</span>';
      loadingIndicator.style.padding = '10px';
      loadingIndicator.style.textAlign = 'center';
      batchResultList.innerHTML = '';
      batchResultList.appendChild(loadingIndicator);
    }
    
    // Make API request for stats
    const response = await fetch(`${API_ENDPOINT}/extension/stats?period=${period}`, {
      headers: {
        'Authorization': `Bearer ${authData.access_token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    const stats = await response.json();
    
    // Update UI with stats data
    if (stats) {
      // Update statistics for the current period
      if (statScanned) statScanned.textContent = stats.total || 0;
      if (statClean) statClean.textContent = stats.clean || 0;
      if (statOffensive) statOffensive.textContent = stats.offensive || 0;
      if (statHate) statHate.textContent = stats.hate || 0;
      if (statSpam) statSpam.textContent = stats.spam || 0;
      
      // Update charts if they exist
      if (typeof updateTrendChart === 'function' && stats.trend) {
        updateTrendChart(stats.trend, period);
      }
      
      updateAdvancedStats(period);
      updateRecentComments(period);
    }
    
  } catch (error) {
    console.error('Error loading stats:', error);
    showNotification(error.message, 'error');
  } finally {
    // Remove loading indicator
    const loadingIndicator = document.getElementById('batch-loading-indicator');
    if (loadingIndicator) {
      loadingIndicator.remove();
    }
  }
}

// Gọi các hàm update khi chuyển tab statistics
function setupStatsTab() {
  const periodBtns = document.querySelectorAll('.period-button');
  let currentPeriod = 'week';
  const isLoggedIn = document.body.classList.contains('logged-in');
  const statsTabContent = document.getElementById('stats-tab-content'); // Assume stats tab content has this ID

  // Disable period buttons and hide content if not logged in
  periodBtns.forEach(btn => {
      btn.disabled = !isLoggedIn;
      if (!isLoggedIn) {
          btn.classList.add('disabled'); // Add class for styling disabled state
      } else {
          btn.classList.remove('disabled');
      }
  });

  if (statsTabContent) {
      statsTabContent.style.display = isLoggedIn ? '' : 'none';
      const loginPrompt = document.getElementById('stats-login-prompt');
      if (!isLoggedIn) {
          if (!loginPrompt) {
              const promptDiv = document.createElement('div');
              promptDiv.id = 'stats-login-prompt';
              promptDiv.textContent = 'Vui lòng đăng nhập để xem thống kê chi tiết.';
              promptDiv.style.textAlign = 'center';
              promptDiv.style.padding = '20px';
              promptDiv.style.color = '#888';
              statsTabContent.parentNode.insertBefore(promptDiv, statsTabContent);
          } else {
             loginPrompt.style.display = '';
          }
      } else if (loginPrompt) {
         loginPrompt.style.display = 'none';
      }
  }

  periodBtns.forEach(btn => {
    btn.onclick = () => {
      if (!isLoggedIn) return; // Do nothing if not logged in
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

// Setup Analyze Mode Switch
function setupAnalyzeModeSwitch() {
  const isLoggedIn = document.body.classList.contains('logged-in');

  if (singleModeBtn && batchModeBtn && singleAnalyzeArea && batchAnalyzeArea) {
    // Always show single mode button and area
    singleModeBtn.style.display = '';
    singleAnalyzeArea.style.display = '';

    // Show/hide batch mode button and area based on login status
    batchModeBtn.style.display = isLoggedIn ? '' : 'none';
    if (!isLoggedIn && batchInput) {
      // Add login prompt to batch area if not logged in
      if (!document.getElementById('batch-login-prompt')) {
        const loginPrompt = document.createElement('div');
        loginPrompt.id = 'batch-login-prompt';
        loginPrompt.className = 'login-prompt';
        loginPrompt.innerHTML = `
          <p>Đăng nhập để sử dụng tính năng phân tích hàng loạt.</p>
          <button id="batch-login-btn" class="secondary-button">Đăng nhập</button>
        `;
        // Insert before batchAnalyzeArea
        if (batchAnalyzeArea.parentNode) {
          batchAnalyzeArea.parentNode.insertBefore(loginPrompt, batchAnalyzeArea);
        }
        
        // Add event listener to the login button
        const batchLoginBtn = document.getElementById('batch-login-btn');
        if (batchLoginBtn) {
          batchLoginBtn.addEventListener('click', () => {
            // Switch to account tab
            document.querySelector('.tab-button[data-tab="account"]').click();
          });
        }
      }
    } else {
      // Remove login prompt if logged in
      const batchLoginPrompt = document.getElementById('batch-login-prompt');
      if (batchLoginPrompt) {
        batchLoginPrompt.remove();
      }
    }

    // Ensure batch button is disabled if not logged in (redundant but safe)
    if (!isLoggedIn) {
       batchModeBtn.classList.add('disabled'); // Style as disabled
       batchModeBtn.disabled = true;
    } else {
       batchModeBtn.classList.remove('disabled');
       batchModeBtn.disabled = false;
    }

    // Default to single mode active
    singleModeBtn.classList.add('active');
    batchModeBtn.classList.remove('active');
    singleAnalyzeArea.style.display = '';
    batchAnalyzeArea.style.display = 'none'; // Initially hide batch area

    singleModeBtn.onclick = function() {
      singleModeBtn.classList.add('active');
      batchModeBtn.classList.remove('active');
      singleAnalyzeArea.style.display = '';
      batchAnalyzeArea.style.display = 'none';
      // Hide the batch login prompt if it exists
      const batchLoginPrompt = document.getElementById('batch-login-prompt');
      if (batchLoginPrompt) {
        batchLoginPrompt.style.display = 'none';
      }
      // Ensure batch result container is hidden when switching to single mode
      if (batchResultContainer) batchResultContainer.classList.add('hidden');
    };

    // Only attach click handler to batch button if logged in
    if (isLoggedIn) {
        batchModeBtn.onclick = function() {
          batchModeBtn.classList.add('active');
          singleModeBtn.classList.remove('active');
          singleAnalyzeArea.style.display = 'none';
          batchAnalyzeArea.style.display = '';
          // Restore batch results visibility if they exist
          if (batchResultContainer && batchResultList && batchResultList.children.length > 0 && !batchResultList.innerHTML.includes('Không có kết quả phân tích')) {
              batchResultContainer.classList.remove('hidden');
          }
        };
    }
  }
}

// Auth state change observer - monitor login/logout changes
document.addEventListener('DOMContentLoaded', function() {
  // Cấu hình thông báo khi class của body thay đổi
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.attributeName === 'class') {
        const isLoggedIn = document.body.classList.contains('logged-in');
        // Cập nhật UI dựa trên trạng thái đăng nhập
        updateAuthDependentUI(isLoggedIn);
      }
    });
  });
  
  // Bắt đầu theo dõi thay đổi trên body
  observer.observe(document.body, { attributes: true });
  
  // Kiểm tra trạng thái ban đầu
  const isLoggedIn = document.body.classList.contains('logged-in');
  updateAuthDependentUI(isLoggedIn);
});

// Kiểm tra auth ngay khi trang tải
(function checkInitialAuth() {
  const AUTH_STORAGE_KEY = "toxicDetector_auth";
  
  // Kiểm tra token từ local storage
  chrome.storage.local.get([AUTH_STORAGE_KEY], function(localData) {
    if (localData && localData[AUTH_STORAGE_KEY]) {
      document.body.classList.add('logged-in');
    } else {
      // Thử kiểm tra từ sync storage
      chrome.storage.sync.get([AUTH_STORAGE_KEY], function(syncData) {
        if (syncData && syncData[AUTH_STORAGE_KEY]) {
          document.body.classList.add('logged-in');
        } else {
          document.body.classList.add('not-logged-in');
        }
      });
    }
  });
})();

// Initialize the extension
initializePopup();

/**
 * Reset user statistics
 */
async function resetStats() {
  if (!confirm("Bạn có chắc muốn đặt lại tất cả thống kê không?")) {
    return;
  }
  
  try {
    // Get authentication token
    const authData = await getAuthData();
    const token = authData ? authData.access_token : null;
    
    if (!token) {
      showNotification('Vui lòng đăng nhập để đặt lại thống kê', 'warning');
      return;
    }
    
    // Make API request to reset stats endpoint
    const response = await fetch(`${API_ENDPOINT}/user/stats/reset`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`Lỗi API: ${response.status}`);
    }
    
    showNotification('Đã đặt lại thống kê thành công', 'success');
    
    // Reload stats
    loadStats();
    
  } catch (error) {
    console.error('Error resetting stats:', error);
    showNotification(error.message, 'error');
  }
}

/**
 * Update advanced statistics based on period
 */
async function updateAdvancedStats(period) {
  const isLoggedIn = document.body.classList.contains('logged-in');
  if (!isLoggedIn) return;
  
  try {
    const authData = await getAuthData();
    if (!authData || !authData.access_token) return;
    
    // Fetch platform statistics
    const response = await fetch(`${API_ENDPOINT}/toxic-detection/statistics?period=${period}`, {
      headers: {
        'Authorization': `Bearer ${authData.access_token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update platform stats if available
    const platformsChartContainer = document.getElementById('platforms-chart-container');
    if (platformsChartContainer && data.platforms && Object.keys(data.platforms).length > 0) {
      // Implementation depends on your chart library
      console.log("Platform stats data:", data.platforms);
      // You would add chart rendering code here
    }
    
    // Update toxic keywords if available
    const keywordsContainer = document.getElementById('toxic-keywords-list');
    if (keywordsContainer) {
      // Clear current content
      keywordsContainer.innerHTML = '';
      
      // If we have toxic keywords data, populate it
      if (data.toxic_keywords && Array.isArray(data.toxic_keywords) && data.toxic_keywords.length > 0) {
        // Add each keyword to the container
        data.toxic_keywords.forEach(kw => {
          const keywordDiv = document.createElement('div');
          keywordDiv.className = 'keyword-item';
          keywordDiv.innerHTML = `
            <span class="keyword-text">${kw.word}</span>
            <span class="keyword-count">${kw.count}</span>
          `;
          keywordsContainer.appendChild(keywordDiv);
        });
      } else {
        keywordsContainer.innerHTML = '<div class="no-data">Không có dữ liệu</div>';
      }
    }
  } catch (error) {
    console.error("Error updating advanced stats:", error);
  }
}

/**
 * Update recent comments based on period
 */
async function updateRecentComments(period) {
  const isLoggedIn = document.body.classList.contains('logged-in');
  if (!isLoggedIn) return;
  
  const commentsContainer = document.getElementById('recent-comments-list');
  if (!commentsContainer) return;
  
  try {
    const authData = await getAuthData();
    if (!authData || !authData.access_token) return;
    
    // Show loading
    commentsContainer.innerHTML = '<div class="loading">Đang tải...</div>';
    
    // Fetch recent comments
    const response = await fetch(`${API_ENDPOINT}/extension/stats?period=${period}`, {
      headers: {
        'Authorization': `Bearer ${authData.access_token}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Clear container
    commentsContainer.innerHTML = '';
    
    // If we have recent comments, display them
    if (data.recent && Array.isArray(data.recent) && data.recent.length > 0) {
      data.recent.forEach(comment => {
        const commentDiv = document.createElement('div');
        commentDiv.className = 'recent-comment-item';
        commentDiv.innerHTML = `
          <div class="comment-content">${comment.content}</div>
          <div class="comment-meta">
            <span class="label ${categoryClasses[comment.prediction] || 'unknown'}">${categoryNames[comment.prediction] || 'Unknown'}</span>
            <span class="comment-platform">${comment.platform || 'Unknown'}</span>
            <span class="comment-date">${new Date(comment.created_at).toLocaleString()}</span>
          </div>
        `;
        commentsContainer.appendChild(commentDiv);
      });
    } else {
      commentsContainer.innerHTML = '<div class="no-data">Không có bình luận gần đây</div>';
    }
  } catch (error) {
    console.error("Error updating recent comments:", error);
    commentsContainer.innerHTML = '<div class="error">Không thể tải bình luận gần đây</div>';
  }
}

/**
 * Phân tích văn bản hàng loạt
 */
async function processBatchText() {
  // Lấy văn bản từ textarea
  const batchText = batchInput.value.trim();
  
  // Kiểm tra nếu không có văn bản
  if (!batchText) {
    showNotification('Vui lòng nhập văn bản cần phân tích', 'error');
    return;
  }

  // Tách thành từng dòng
  const lines = batchText.split('\n').filter(line => line.trim().length > 0);
  
  if (lines.length === 0) {
    showNotification('Không có dòng nào để phân tích', 'warning');
    return;
  }
  
  try {
    // Hiển thị trạng thái loading
    const batchDetectBtn = document.getElementById('batch-detect-btn');
    batchDetectBtn.disabled = true;
    batchDetectBtn.textContent = 'Đang phân tích...';
    
    // Hiển thị container kết quả và đặt loading
    const batchResultContainer = document.getElementById('batch-result-container');
    const batchResultList = document.getElementById('batch-result-list');
    
    if (batchResultContainer && batchResultList) {
      batchResultContainer.classList.remove('hidden');
      batchResultContainer.style.display = 'block'; // Force show
      
      // Tạo loading indicator
      const loadingIndicator = document.createElement('div');
      loadingIndicator.id = 'batch-loading-indicator';
      loadingIndicator.innerHTML = '<div class="spinner"></div> <span>Đang phân tích ${lines.length} dòng...</span>';
      loadingIndicator.style.padding = '10px';
      loadingIndicator.style.textAlign = 'center';
      batchResultList.innerHTML = '';
      batchResultList.appendChild(loadingIndicator);
    }
    
    // Get authentication token
    const authData = await getAuthData();
    const token = authData ? authData.access_token : null;
    
    if (!token) {
      throw new Error('Bạn cần đăng nhập để sử dụng tính năng này');
    }
    
    // Get platform from current tab
    let platform = 'unknown';
    if (currentPlatform && currentPlatform.textContent) {
      platform = currentPlatform.textContent.toLowerCase();
    }
    
    // Tạo mảng comments
    const comments = lines.map((line) => ({
      content: line,
      platform: platform
    }));
    
    // Thực hiện gọi API
    console.log('[DEBUG] Batch detect API request:', { comments: comments });
    
    const response = await fetch(`${API_ENDPOINT}/extension/batch-detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        comments: comments,
        save_to_db: saveDataCheckbox && saveDataCheckbox.checked,
        metadata: {
          source: 'extension-batch'
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    const results = await response.json();
    console.log('[DEBUG] Batch detect API response:', results);
    
    // Hiển thị kết quả
    if (batchResultList) {
      batchResultList.innerHTML = ''; // Xóa loading indicator
      
      if (!results || !Array.isArray(results) || results.length === 0) {
        batchResultList.innerHTML = '<div style="padding:10px;text-align:center;color:#d32f2f;">Không có kết quả</div>';
        return;
      }
      
      // Tạo kết quả cho mỗi dòng
      results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'batch-result-item';
        
        const classification = result.prediction !== undefined ? result.prediction : 0;
        const confidencePercent = Math.round((result.confidence || 0.5) * 100);
        
        item.innerHTML = `
          <div class="result-text">${result.text || comments[index].content}</div>
          <div class="result-meta">
            <span class="label ${categoryClasses[classification] || 'unknown'}">
              ${categoryNames[classification] || 'Unknown'} (${confidencePercent}%)
            </span>
          </div>
        `;
        
        batchResultList.appendChild(item);
      });
      
      // Thêm thông tin tổng hợp
      const totalResults = results.length;
      const cleanCount = results.filter(r => r.prediction === 0).length;
      const offensiveCount = results.filter(r => r.prediction === 1).length;
      const hateCount = results.filter(r => r.prediction === 2).length;
      const spamCount = results.filter(r => r.prediction === 3).length;
      
      const summary = document.createElement('div');
      summary.className = 'batch-summary';
      summary.innerHTML = `
        <h4>Tổng kết:</h4>
        <div class="summary-stats">
          <div>Tổng số: <strong>${totalResults}</strong></div>
          <div>Bình thường: <strong class="clean">${cleanCount}</strong></div>
          <div>Xúc phạm: <strong class="offensive">${offensiveCount}</strong></div>
          <div>Thù ghét: <strong class="hate">${hateCount}</strong></div>
          <div>Spam: <strong class="spam">${spamCount}</strong></div>
        </div>
      `;
      
      batchResultList.prepend(summary);
    }
    
    // Cập nhật thống kê nếu đăng nhập
    if (authData && authData.access_token) {
      setupStatsTab(); // Reload stats
    }
    
  } catch (error) {
    console.error('Batch detection error:', error);
    showNotification(error.message, 'error');
    
    // Hiển thị lỗi trong container kết quả
    const batchResultList = document.getElementById('batch-result-list');
    if (batchResultList) {
      batchResultList.innerHTML = `
        <div style="color:#d32f2f; padding:15px; text-align:center;">
          <h3>Lỗi phân tích hàng loạt</h3>
          <p>${error.message}</p>
          <p>Vui lòng thử lại hoặc kiểm tra kết nối.</p>
        </div>
      `;
    }
  } finally {
    // Khôi phục trạng thái button
    const batchDetectBtn = document.getElementById('batch-detect-btn');
    if (batchDetectBtn) {
      batchDetectBtn.disabled = false;
      batchDetectBtn.textContent = 'Phân tích hàng loạt';
    }
  }
}
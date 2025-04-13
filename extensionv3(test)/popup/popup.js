/**
 * Toxic Language Detector Extension - Popup Script
 * Handles authentication, settings, statistics and UI interactions
 */

// API Configuration
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  AUTH_ENDPOINTS: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/forgot-password',
    REFRESH_TOKEN: '/auth/refresh-token',
    ME: '/auth/me'
  },
  EXTENSION_ENDPOINTS: {
    DETECT: '/extension/detect',
    STATS: '/toxic/stats'
  },
  WEB_DASHBOARD: 'http://localhost:8000/dashboard'
};

// DOM Elements - Auth
const authContainer = document.getElementById('auth-container');
const loginScreen = document.getElementById('login-screen');
const registerScreen = document.getElementById('register-screen');
const forgotPasswordScreen = document.getElementById('forgot-password-screen');

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const forgotPasswordForm = document.getElementById('forgot-password-form');

const loginEmail = document.getElementById('login-email');
const loginPassword = document.getElementById('login-password');
const registerName = document.getElementById('register-name');
const registerEmail = document.getElementById('register-email');
const registerPassword = document.getElementById('register-password');
const registerPasswordConfirm = document.getElementById('register-password-confirm');
const forgotEmail = document.getElementById('forgot-email');

const loginMessage = document.getElementById('login-message');
const registerMessage = document.getElementById('register-message');
const forgotMessage = document.getElementById('forgot-message');

// DOM Elements - Navigation
const toRegisterLink = document.getElementById('to-register');
const toLoginFromRegisterLink = document.getElementById('to-login-from-register');
const toForgotPasswordLink = document.getElementById('to-forgot-password');
const toLoginFromForgotLink = document.getElementById('to-login-from-forgot');

// DOM Elements - App
const appContainer = document.getElementById('app-container');
const userName = document.getElementById('user-name');
const userRole = document.getElementById('user-role');
const logoutBtn = document.getElementById('logout-btn');
const viewDashboardBtn = document.getElementById('view-dashboard');

// DOM Elements - Settings
const enableToggle = document.getElementById('enable-toggle');
const thresholdSlider = document.getElementById('threshold');
const thresholdValue = document.getElementById('threshold-value');
const highlightToxic = document.getElementById('highlight-toxic');
const platformFacebook = document.getElementById('platform-facebook');
const platformYoutube = document.getElementById('platform-youtube');
const platformTwitter = document.getElementById('platform-twitter');

// DOM Elements - Statistics
const statScanned = document.getElementById('stat-scanned');
const statClean = document.getElementById('stat-clean');
const statOffensive = document.getElementById('stat-offensive');
const statHate = document.getElementById('stat-hate');
const statSpam = document.getElementById('stat-spam');
const resetStatsBtn = document.getElementById('reset-stats');

/**
 * Initialize the popup when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
  // Check if user is logged in
  checkAuthStatus();
  
  // Setup event listeners
  setupEventListeners();
  
  // Load settings and statistics
  loadSettings();
});

/**
 * Set up all event listeners
 */
function setupEventListeners() {
  // Authentication navigation
  if (toRegisterLink) toRegisterLink.addEventListener('click', showRegisterScreen);
  if (toLoginFromRegisterLink) toLoginFromRegisterLink.addEventListener('click', showLoginScreen);
  if (toForgotPasswordLink) toForgotPasswordLink.addEventListener('click', showForgotPasswordScreen);
  if (toLoginFromForgotLink) toLoginFromForgotLink.addEventListener('click', showLoginScreen);
  
  // Form submissions
  if (loginForm) loginForm.addEventListener('submit', handleLogin);
  if (registerForm) registerForm.addEventListener('submit', handleRegister);
  if (forgotPasswordForm) forgotPasswordForm.addEventListener('submit', handleForgotPassword);
  
  // App buttons
  if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
  if (viewDashboardBtn) viewDashboardBtn.addEventListener('click', openDashboard);
  
  // Settings
  if (enableToggle) enableToggle.addEventListener('change', saveSettings);
  if (thresholdSlider) {
    thresholdSlider.addEventListener('input', updateThresholdDisplay);
    thresholdSlider.addEventListener('change', saveSettings);
  }
  if (highlightToxic) highlightToxic.addEventListener('change', saveSettings);
  if (platformFacebook) platformFacebook.addEventListener('change', saveSettings);
  if (platformYoutube) platformYoutube.addEventListener('change', saveSettings);
  if (platformTwitter) platformTwitter.addEventListener('change', saveSettings);
  
  // Statistics
  if (resetStatsBtn) resetStatsBtn.addEventListener('click', resetStatistics);
}

/**
 * Check if user is authenticated
 */
function checkAuthStatus() {
  chrome.storage.local.get(['authToken', 'user'], (data) => {
    if (data.authToken && data.user) {
      // Verify token is still valid
      verifyToken(data.authToken)
        .then(isValid => {
          if (isValid) {
            showAppScreen(data.user);
          } else {
            showLoginScreen();
          }
        })
        .catch(() => {
          showLoginScreen();
        });
    } else {
      showLoginScreen();
    }
  });
}

/**
 * Verify if token is still valid
 */
async function verifyToken(token) {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH_ENDPOINTS.ME}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      const userData = await response.json();
      // Update stored user data
      chrome.storage.local.set({ user: userData });
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error verifying token:', error);
    return false;
  }
}

/**
 * Show login screen
 */
function showLoginScreen(e) {
  if (e) e.preventDefault();
  
  // Hide all screens
  loginScreen.classList.remove('active');
  registerScreen.classList.remove('active');
  forgotPasswordScreen.classList.remove('active');
  
  // Show login screen
  loginScreen.classList.add('active');
  
  // Clear message
  loginMessage.textContent = '';
  loginMessage.classList.remove('error', 'success');
  loginMessage.style.display = 'none';
}

/**
 * Show register screen
 */
function showRegisterScreen(e) {
  if (e) e.preventDefault();
  
  // Hide all screens
  loginScreen.classList.remove('active');
  registerScreen.classList.remove('active');
  forgotPasswordScreen.classList.remove('active');
  
  // Show register screen
  registerScreen.classList.add('active');
  
  // Clear message
  registerMessage.textContent = '';
  registerMessage.classList.remove('error', 'success');
  registerMessage.style.display = 'none';
}

/**
 * Show forgot password screen
 */
function showForgotPasswordScreen(e) {
  if (e) e.preventDefault();
  
  // Hide all screens
  loginScreen.classList.remove('active');
  registerScreen.classList.remove('active');
  forgotPasswordScreen.classList.remove('active');
  
  // Show forgot password screen
  forgotPasswordScreen.classList.add('active');
  
  // Clear message
  forgotMessage.textContent = '';
  forgotMessage.classList.remove('error', 'success');
  forgotMessage.style.display = 'none';
}

/**
 * Show main app screen
 */
function showAppScreen(userData) {
  // Hide auth container
  authContainer.style.display = 'none';
  
  // Update user info
  userName.textContent = userData.name || userData.username;
  userRole.textContent = userData.role || 'user';
  
  // Show app container
  appContainer.classList.remove('hidden');
  
  // Load stats
  loadUserStats();
}

/**
 * Handle login form submission
 */
async function handleLogin(e) {
  e.preventDefault();
  
  const email = loginEmail.value.trim();
  const password = loginPassword.value;
  
  if (!email || !password) {
    showMessage(loginMessage, 'Vui lòng nhập email và mật khẩu', 'error');
    return;
  }
  
  try {
    showMessage(loginMessage, 'Đang đăng nhập...', 'success');
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH_ENDPOINTS.LOGIN}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Đăng nhập thất bại');
    }
    
    // Store token and user data
    chrome.storage.local.set({
      authToken: data.access_token,
      user: data.user
    }, () => {
      showAppScreen(data.user);
    });
    
  } catch (error) {
    showMessage(loginMessage, error.message || 'Đăng nhập thất bại', 'error');
  }
}

/**
 * Handle register form submission
 */
async function handleRegister(e) {
  e.preventDefault();
  
  const name = registerName.value.trim();
  const email = registerEmail.value.trim();
  const password = registerPassword.value;
  const passwordConfirm = registerPasswordConfirm.value;
  
  if (!name || !email || !password) {
    showMessage(registerMessage, 'Vui lòng điền đầy đủ thông tin', 'error');
    return;
  }
  
  if (password !== passwordConfirm) {
    showMessage(registerMessage, 'Mật khẩu xác nhận không khớp', 'error');
    return;
  }
  
  try {
    showMessage(registerMessage, 'Đang đăng ký...', 'success');
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH_ENDPOINTS.REGISTER}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, email, password })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Đăng ký thất bại');
    }
    
    showMessage(registerMessage, 'Đăng ký thành công! Vui lòng đăng nhập.', 'success');
    
    // Clear form
    registerForm.reset();
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      showLoginScreen();
    }, 2000);
    
  } catch (error) {
    showMessage(registerMessage, error.message || 'Đăng ký thất bại', 'error');
  }
}

/**
 * Handle forgot password form submission
 */
async function handleForgotPassword(e) {
  e.preventDefault();
  
  const email = forgotEmail.value.trim();
  
  if (!email) {
    showMessage(forgotMessage, 'Vui lòng nhập email', 'error');
    return;
  }
  
  try {
    showMessage(forgotMessage, 'Đang gửi yêu cầu...', 'success');
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.AUTH_ENDPOINTS.FORGOT_PASSWORD}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Không thể gửi yêu cầu');
    }
    
    showMessage(forgotMessage, 'Kiểm tra email của bạn để đặt lại mật khẩu', 'success');
    
    // Clear form
    forgotPasswordForm.reset();
    
  } catch (error) {
    showMessage(forgotMessage, error.message || 'Không thể gửi yêu cầu', 'error');
  }
}

/**
 * Handle logout
 */
function handleLogout() {
  // Clear stored data
  chrome.storage.local.remove(['authToken', 'user'], () => {
    // Show login screen
    authContainer.style.display = 'block';
    appContainer.classList.add('hidden');
    showLoginScreen();
  });
}

/**
 * Open dashboard in new tab
 */
function openDashboard() {
  chrome.tabs.create({ url: API_CONFIG.WEB_DASHBOARD });
}

/**
 * Show message
 */
function showMessage(element, message, type) {
  if (!element) return;
  
  element.textContent = message;
  element.classList.remove('error', 'success');
  element.classList.add(type);
  element.style.display = 'block';
}

/**
 * Load user statistics from API
 */
async function loadUserStats() {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      console.error('No auth token available');
      return;
    }
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.EXTENSION_ENDPOINTS.STATS}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Could not load statistics');
    }
    
    const stats = await response.json();
    
    // Update UI with stats
    updateStatistics({
      scanned: stats.total || 0,
      clean: stats.clean || 0,
      offensive: stats.offensive || 0,
      hate: stats.hate || 0,
      spam: stats.spam || 0
    });
    
  } catch (error) {
    console.error('Error loading statistics:', error);
    // Fall back to locally stored stats
    loadLocalStatistics();
  }
}

/**
 * Load statistics from local storage
 */
function loadLocalStatistics() {
  chrome.storage.sync.get(['stats'], (data) => {
    if (data.stats) {
      updateStatistics(data.stats);
    }
  });
}

/**
 * Update statistics UI
 */
function updateStatistics(stats) {
  if (statScanned) statScanned.textContent = stats.scanned || 0;
  if (statClean) statClean.textContent = stats.clean || 0;
  if (statOffensive) statOffensive.textContent = stats.offensive || 0;
  if (statHate) statHate.textContent = stats.hate || 0;
  if (statSpam) statSpam.textContent = stats.spam || 0;
}

/**
 * Reset statistics
 */
async function resetStatistics() {
  try {
    chrome.storage.sync.set({
      stats: {
        scanned: 0,
        clean: 0,
        offensive: 0,
        hate: 0,
        spam: 0
      }
    }, () => {
      // Update UI
      updateStatistics({
        scanned: 0,
        clean: 0,
        offensive: 0,
        hate: 0,
        spam: 0
      });
    });
    
    // Notify content script and background
    chrome.runtime.sendMessage({ action: 'resetStats' });
    
  } catch (error) {
    console.error('Error resetting statistics:', error);
  }
}

/**
 * Load settings from storage
 */
function loadSettings() {
  chrome.storage.sync.get([
    'enabled',
    'threshold',
    'highlightToxic',
    'platforms'
  ], (data) => {
    if (enableToggle) {
      enableToggle.checked = data.enabled !== undefined ? data.enabled : true;
    }
    
    if (thresholdSlider && thresholdValue) {
      const threshold = data.threshold !== undefined ? data.threshold : 0.7;
      thresholdSlider.value = threshold;
      thresholdValue.textContent = threshold;
    }
    
    if (highlightToxic) {
      highlightToxic.checked = data.highlightToxic !== undefined ? data.highlightToxic : true;
    }
    
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
  });
}

/**
 * Save settings to storage
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
    }
  };
  
  chrome.storage.sync.set(settings, () => {
    // Notify content scripts
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'settingsUpdated',
          settings: settings
        }).catch(err => console.error('Could not send settings update', err));
      }
    });
    
    // Also notify background script
    chrome.runtime.sendMessage({
      action: 'settingsUpdated',
      settings: settings
    });
  });
}

/**
 * Update threshold value display
 */
function updateThresholdDisplay() {
  if (thresholdSlider && thresholdValue) {
    thresholdValue.textContent = thresholdSlider.value;
  }
}

/**
 * Get authentication token from storage
 */
function getAuthToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['authToken'], (data) => {
      resolve(data.authToken || null);
    });
  });
}
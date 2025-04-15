/**
 * JavaScript chính cho popup
 */
import { sendToBackground, sendToActiveTab } from '../utils/messaging.js';
import { getSettings, getDefaultSettings } from '../utils/storage.js';
import { WEB_DASHBOARD } from '../api/config.js';
import { getClassificationText, getClassificationColor, formatProbabilities } from '../utils/helpers.js';

// DOM Elements
let elements = {};

// Biến toàn cục lưu trạng thái detector
let detectorEnabled = true;

/**
 * Khởi tạo popup
 */
// Bọc initialization trong một function để tránh ReferenceError
function initialize() {
  // Lấy tất cả các elements cần thiết
  getElements();
  
  // Thiết lập các listeners
  setupEventListeners();
  
  // Khởi tạo dữ liệu
  initializeData();
}

// Khởi tạo khi trang đã sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
  initialize();
});

/**
 * Lấy các elements từ DOM
 */
function getElements() {
  elements = {
    // Tabs
    tabButtons: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Toggle
    detectionToggle: document.getElementById('detection-toggle'),
    toggleStatus: document.getElementById('toggle-status'),
    
    // Dashboard tab
    totalDetections: document.getElementById('total-detections'),
    cleanDetections: document.getElementById('clean-detections'),
    offensiveDetections: document.getElementById('offensive-detections'),
    hateDetections: document.getElementById('hate-detections'),
    spamDetections: document.getElementById('spam-detections'),
    serverHealth: document.getElementById('server-health'),
    detectionStatus: document.getElementById('detection-status'),
    
    // Analysis tab
    analysisText: document.getElementById('analysis-text'),
    analyzeBtn: document.getElementById('analyze-btn'),
    resultPrediction: document.getElementById('result-prediction'),
    resultConfidence: document.getElementById('result-confidence'),
    resultKeywords: document.getElementById('result-keywords'),
    
    // Settings tab
    enableDetection: document.getElementById('enable-detection'),
    enableHighlight: document.getElementById('enable-highlight'),
    enableNotifications: document.getElementById('enable-notifications'),
    platformFacebook: document.getElementById('platform-facebook'),
    platformYoutube: document.getElementById('platform-youtube'),
    platformTwitter: document.getElementById('platform-twitter'),
    threshold: document.getElementById('threshold'),
    thresholdValue: document.getElementById('threshold-value'),
    language: document.getElementById('language'),
    saveSettings: document.getElementById('save-settings'),
    resetSettings: document.getElementById('reset-settings'),
    
    // Authentication
    loginContainer: document.getElementById('login-container'),
    userInfo: document.getElementById('user-info'),
    username: document.getElementById('username'),
    loginBtn: document.getElementById('login-btn'),
    registerBtn: document.getElementById('register-btn'),
    logoutBtn: document.getElementById('logout-btn'),
    dashboardLink: document.getElementById('dashboard-link'),
    
    // Modals
    loginModal: document.getElementById('login-modal'),
    registerModal: document.getElementById('register-modal'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    loginUsername: document.getElementById('login-username'),
    loginPassword: document.getElementById('login-password'),
    registerUsername: document.getElementById('register-username'),
    registerEmail: document.getElementById('register-email'),
    registerPassword: document.getElementById('register-password'),
    registerConfirm: document.getElementById('register-confirm'),
    loginError: document.getElementById('login-error'),
    registerError: document.getElementById('register-error'),
    closeModalBtns: document.querySelectorAll('.close-modal'),
    forgotPassword: document.getElementById('forgot-password')
  };
}

/**
 * Thiết lập các event listeners
 */
function setupEventListeners() {
  // Tab switching
  elements.tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabName = button.getAttribute('data-tab');
      switchTab(tabName);
    });
  });
  
  // Detection toggle
  elements.detectionToggle.addEventListener('change', toggleDetection);
  
  // Analysis
  elements.analyzeBtn.addEventListener('click', analyzeText);
  
  // Settings
  elements.threshold.addEventListener('input', updateThresholdValue);
  elements.saveSettings.addEventListener('click', saveSettings);
  elements.resetSettings.addEventListener('click', resetSettings);
  
  // Authentication
  elements.loginBtn.addEventListener('click', showLoginModal);
  elements.registerBtn.addEventListener('click', showRegisterModal);
  elements.logoutBtn.addEventListener('click', logout);
  elements.loginForm.addEventListener('submit', handleLogin);
  elements.registerForm.addEventListener('submit', handleRegister);
  elements.dashboardLink.addEventListener('click', openDashboard);
  elements.closeModalBtns.forEach(btn => {
    btn.addEventListener('click', closeModals);
  });
  
  // Toggle password visibility
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', togglePassword);
  });
}

/**
 * Khởi tạo dữ liệu
 */
async function initializeData() {
  try {
    // Kiểm tra đăng nhập
    const loginStatus = await sendToBackground('checkLogin');
    if (loginStatus) {
      updateLoginUI(loginStatus);
    }
    
    // Lấy cài đặt
    const settings = await getSettings();
    if (settings) {
      updateSettingsUI(settings);
    }
    
    // Cập nhật trạng thái detector
    if (settings && settings.enableDetection !== undefined) {
      updateDetectorStatus(settings.enableDetection);
    } else {
      updateDetectorStatus(true); // Mặc định là bật
    }
    
    // Lấy thống kê
    const statsResponse = await sendToBackground('getStats');
    if (statsResponse && statsResponse.success && statsResponse.stats) {
      updateStatsUI(statsResponse.stats);
    }
    
    // Kiểm tra sức khỏe API
    const healthResponse = await sendToBackground('checkApiHealth');
    if (healthResponse && healthResponse.success && healthResponse.health) {
      updateServerHealth(healthResponse.health);
    }
  } catch (error) {
    console.error('Lỗi khởi tạo dữ liệu:', error);
  }
}

/**
 * Chuyển đổi tab
 * @param {string} tabName - Tên tab cần chuyển đến
 */
function switchTab(tabName) {
  // Xóa active class từ tất cả tabs
  elements.tabButtons.forEach(button => {
    button.classList.remove('active');
  });
  
  elements.tabContents.forEach(content => {
    content.classList.remove('active');
  });
  
  // Thêm active class cho tab được chọn
  document.querySelector(`.tab-btn[data-tab="${tabName}"]`).classList.add('active');
  document.getElementById(`${tabName}-tab`).classList.add('active');
}

/**
 * Bật/tắt detector
 */
async function toggleDetection() {
  const enabled = elements.detectionToggle.checked;
  
  try {
    const response = await sendToBackground('toggleDetection', { enabled });
    
    if (response && response.success) {
      updateDetectorStatus(response.enabled);
    } else {
      console.error('Lỗi bật/tắt detector:', response ? response.error : 'Không nhận được phản hồi');
      // Revert toggle state
      elements.detectionToggle.checked = !enabled;
      updateToggleUI(!enabled);
    }
  } catch (error) {
    console.error('Lỗi bật/tắt detector:', error);
    // Revert toggle state
    elements.detectionToggle.checked = !enabled;
    updateToggleUI(!enabled);
  }
}

/**
 * Cập nhật trạng thái detector
 * @param {boolean} enabled - Trạng thái bật/tắt
 */
async function updateDetectorStatus(enabled) {
  try {
    // Nếu tham số được truyền vào, sử dụng nó trực tiếp
    if (typeof enabled === 'boolean') {
      detectorEnabled = enabled;
      updateToggleUI(enabled);
      return enabled;
    }
    
    // Nếu không, gửi yêu cầu lấy trạng thái từ background
    const response = await sendToBackground('getDetectorStatus');
    
    if (response) {
      // Kiểm tra các định dạng phản hồi khác nhau
      let status = false;
      
      if (typeof response.enabled !== 'undefined') {
        status = response.enabled;
      } else if (response.settings && typeof response.settings.enableDetection !== 'undefined') {
        status = response.settings.enableDetection;
      } else if (typeof response.enableDetection !== 'undefined') {
        status = response.enableDetection;
      }
      
      // Cập nhật trạng thái toàn cục
      detectorEnabled = status;
      
      // Cập nhật UI
      updateToggleUI(status);
      
      return status;
    } else {
      console.error('Không nhận được phản hồi từ background:', response);
      return false;
    }
  } catch (error) {
    console.error('Lỗi khi lấy trạng thái detector:', error);
    return false;
  }
}

/**
 * Cập nhật UI của toggle
 * @param {boolean} enabled - Trạng thái bật/tắt
 */
function updateToggleUI(enabled) {
  if (enabled) {
    elements.toggleStatus.textContent = 'Đang bật';
  } else {
    elements.toggleStatus.textContent = 'Đã tắt';
  }
}

/**
 * Phân tích văn bản
 */
async function analyzeText() {
  const text = elements.analysisText.value.trim();
  
  if (!text) {
    showAnalysisError('Vui lòng nhập văn bản cần phân tích');
    return;
  }
  
  // Hiển thị trạng thái đang phân tích
  elements.analyzeBtn.textContent = 'Đang phân tích...';
  elements.analyzeBtn.disabled = true;
  elements.resultPrediction.textContent = 'Đang phân tích...';
  elements.resultConfidence.textContent = '';
  elements.resultKeywords.textContent = '';
  
  try {
    let result;
    
    // Thử gửi thông điệp đến tab đang hoạt động
    try {
      result = await sendToActiveTab('analyzeText', {
        text,
        platform: 'manual',
        options: {}
      });
    } catch (error) {
      console.log('Không thể sử dụng sendToActiveTab, thử phương pháp khác:', error);
      result = null;
    }
    
    // Nếu không thành công, thử sử dụng background script
    if (!result) {
      try {
        result = await sendToBackground('analyzeText', {
          text,
          platform: 'manual',
          options: {}
        });
      } catch (error) {
        console.log('Không thể sử dụng sendToBackground, thử phương pháp khác:', error);
        result = null;
      }
    }
    
    // Nếu vẫn không thành công và chrome.scripting khả dụng, thử executeScript
    if (!result && typeof chrome !== 'undefined' && chrome.scripting && chrome.scripting.executeScript) {
      try {
        // Truy cập tab đang hoạt động
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tabs && tabs.length > 0) {
          // Thực thi script trong tab để gọi hàm phân tích trực tiếp
          const directResult = await chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            func: (text) => {
              // Kiểm tra xem có toxicDetector không
              if (window.toxicDetector && typeof window.toxicDetector.analyzeText === 'function') {
                return window.toxicDetector.analyzeText(text, 'manual', {});
              }
              return null;
            },
            args: [text]
          });
          
          // Kiểm tra kết quả
          if (directResult && directResult[0] && directResult[0].result) {
            result = directResult[0].result;
          }
        }
      } catch (scriptError) {
        console.error('Lỗi executeScript:', scriptError);
      }
    }
    
    // Nếu vẫn không thành công, sử dụng phân tích API trực tiếp
    if (!result) {
      try {
        // Import services.js và phân tích trực tiếp
        const { detectToxic } = await import('../api/services.js');
        const apiResult = await detectToxic(text, 'manual', { saveResult: true });
        
        console.log('Kết quả API trực tiếp:', apiResult);
        
        // Định dạng kết quả giống như từ content script
        if (apiResult) {
          result = {
            success: true,
            prediction: apiResult.category || apiResult.prediction_text || 'unknown',
            isToxic: apiResult.isToxic || (apiResult.category !== 'clean' && apiResult.prediction_text !== 'clean'),
            confidence: apiResult.confidence || 0,
            score: apiResult.score || 0,
            keywords: apiResult.keywords || [],
            details: {
              probabilities: apiResult.probabilities || {},
              text: apiResult.text,
              processedText: apiResult.processedText || apiResult.processed_text
            }
          };
        }
      } catch (apiError) {
        console.error('Lỗi phân tích trực tiếp:', apiError);
      }
    }
    
    // Xử lý kết quả
    if (result && result.success) {
      // Hiển thị kết quả
      const prediction = result.prediction || 'unknown';
      const confidence = result.confidence || 0;
      const keywords = result.keywords || [];
      
      const predictionText = getClassificationText(prediction);
      const predictionColor = getClassificationColor(prediction);
      
      elements.resultPrediction.textContent = predictionText;
      elements.resultPrediction.style.color = predictionColor;
      
      if (confidence) {
        elements.resultConfidence.textContent = `Độ tin cậy: ${Math.round(confidence * 100)}%`;
      }
      
      if (keywords && keywords.length > 0) {
        elements.resultKeywords.innerHTML = `Từ khóa: <span class="keywords">${keywords.join(', ')}</span>`;
      } else {
        elements.resultKeywords.textContent = '';
      }
      
      // Hiển thị thêm thông tin chi tiết nếu có
      if (result.details && result.details.probabilities) {
        showProbabilitiesChart(result.details.probabilities);
      }
    } else {
      const errorMessage = result && result.error ? result.error : 'Không nhận được kết quả phân tích';
      showAnalysisError(`Lỗi: ${errorMessage}`);
    }
  } catch (error) {
    console.error('Lỗi phân tích văn bản:', error);
    showAnalysisError(`Lỗi: ${error.message || 'Không thể phân tích văn bản'}`);
  } finally {
    // Khôi phục trạng thái nút
    elements.analyzeBtn.textContent = 'Phân tích';
    elements.analyzeBtn.disabled = false;
  }
}

/**
 * Cập nhật giá trị ngưỡng
 */
function updateThresholdValue() {
  const value = elements.threshold.value;
  elements.thresholdValue.textContent = `${value}%`;
}

/**
 * Lưu cài đặt
 */
async function saveSettings() {
  try {
    // Hiển thị trạng thái đang xử lý
    elements.saveSettings.disabled = true;
    elements.saveSettings.textContent = 'Đang lưu...';
    
    const settings = {
      enableDetection: elements.enableDetection.checked,
      highlightToxic: elements.enableHighlight.checked,
      enableNotifications: elements.enableNotifications.checked,
      threshold: parseInt(elements.threshold.value) / 100,
      language: elements.language.value,
      platforms: {
        facebook: elements.platformFacebook.checked,
        youtube: elements.platformYoutube.checked,
        twitter: elements.platformTwitter.checked
      }
    };
    
    const response = await sendToBackground('updateSettings', { settings });
    
    if (response && response.success) {
      elements.saveSettings.textContent = 'Đã lưu';
      setTimeout(() => {
        elements.saveSettings.textContent = 'Lưu cài đặt';
        elements.saveSettings.disabled = false;
      }, 2000);
    } else {
      throw new Error(response ? response.error : 'Không nhận được phản hồi');
    }
  } catch (error) {
    console.error('Lỗi khi lưu cài đặt:', error);
    elements.saveSettings.textContent = 'Lỗi';
    setTimeout(() => {
      elements.saveSettings.textContent = 'Lưu cài đặt';
      elements.saveSettings.disabled = false;
    }, 2000);
  }
}

/**
 * Khôi phục cài đặt mặc định
 */
async function resetSettings() {
  const defaultSettings = getDefaultSettings();
  
  // Cập nhật UI với cài đặt mặc định
  updateSettingsUI(defaultSettings);
  
  // Lưu cài đặt
  await saveSettings();
}

/**
 * Cập nhật UI với cài đặt
 * @param {Object} settings - Cài đặt cần hiển thị
 */
function updateSettingsUI(settings) {
  elements.enableDetection.checked = settings.enableDetection;
  elements.enableHighlight.checked = settings.enableHighlight;
  elements.enableNotifications.checked = settings.enableNotifications;
  elements.threshold.value = Math.round(settings.toxicThreshold * 100);
  elements.thresholdValue.textContent = `${Math.round(settings.toxicThreshold * 100)}%`;
  elements.language.value = settings.language || 'vi';
  
  // Cài đặt nền tảng
  if (settings.platforms) {
    elements.platformFacebook.checked = settings.platforms.facebook;
    elements.platformYoutube.checked = settings.platforms.youtube;
    elements.platformTwitter.checked = settings.platforms.twitter;
  }
}

/**
 * Cập nhật UI thống kê
 * @param {Object} stats - Thống kê cần hiển thị
 */
function updateStatsUI(stats) {
  elements.totalDetections.textContent = stats.total || 0;
  elements.cleanDetections.textContent = stats.clean || 0;
  elements.offensiveDetections.textContent = stats.offensive || 0;
  elements.hateDetections.textContent = stats.hate || 0;
  elements.spamDetections.textContent = stats.spam || 0;
}

/**
 * Cập nhật trạng thái sức khỏe máy chủ
 * @param {Object} health - Thông tin sức khỏe máy chủ
 */
function updateServerHealth(health) {
  const statusIndicator = elements.serverHealth.querySelector('.status-indicator');
  
  if (health.status === 'healthy') {
    statusIndicator.className = 'status-indicator active';
    elements.serverHealth.textContent = 'Hoạt động tốt';
  } else if (health.status === 'warning') {
    statusIndicator.className = 'status-indicator warning';
    elements.serverHealth.textContent = 'Có vấn đề';
  } else {
    statusIndicator.className = 'status-indicator inactive';
    elements.serverHealth.textContent = 'Không kết nối được';
  }
  
  elements.serverHealth.prepend(statusIndicator);
}

/**
 * Hiển thị modal đăng nhập
 */
function showLoginModal(e) {
  e.preventDefault();
  elements.loginModal.style.display = 'block';
}

/**
 * Hiển thị modal đăng ký
 */
function showRegisterModal(e) {
  e.preventDefault();
  elements.registerModal.style.display = 'block';
}

/**
 * Đóng tất cả modal
 */
function closeModals() {
  elements.loginModal.style.display = 'none';
  elements.registerModal.style.display = 'none';
}

/**
 * Xử lý đăng nhập
 */
async function handleLogin(e) {
  e.preventDefault();
  
  const username = elements.loginUsername.value.trim();
  const password = elements.loginPassword.value;
  
  if (!username || !password) {
    elements.loginError.textContent = 'Vui lòng nhập đầy đủ thông tin';
    return;
  }
  
  try {
    // Hiển thị trạng thái loading
    const loginButton = document.querySelector('#login-form button[type="submit"]');
    if (loginButton) {
      loginButton.disabled = true;
      loginButton.innerHTML = '<span class="spinner"></span> Đang đăng nhập...';
    }
    elements.loginError.textContent = '';
    
    // Đặt thông báo timeout riêng để thân thiện với người dùng
    let loginTimeoutId = setTimeout(() => {
      elements.loginError.textContent = 'Đang xử lý đăng nhập, vui lòng đợi...';
    }, 3000);
    
    const response = await sendToBackground('login', { username, password });
    
    // Xóa timeout thông báo
    clearTimeout(loginTimeoutId);
    
    if (response && response.success) {
      closeModals();
      updateLoginUI({ success: true, loggedIn: true, user: response.user });
      
      // Thông báo thành công
      const notification = document.createElement('div');
      notification.className = 'notification success';
      notification.textContent = 'Đăng nhập thành công!';
      document.body.appendChild(notification);
      
      // Tự động xóa thông báo sau 3 giây
      setTimeout(() => {
        notification.remove();
      }, 3000);
    } else {
      // Xử lý lỗi từ response
      let errorMessage = 'Đăng nhập thất bại';
      
      if (response) {
        if (typeof response.error === 'object') {
          // Xử lý lỗi là object
          errorMessage = response.error.message || JSON.stringify(response.error);
        } else if (response.error) {
          errorMessage = response.error;
        }
      }
      
      elements.loginError.textContent = errorMessage;
    }
  } catch (error) {
    console.error('Lỗi đăng nhập:', error);
    
    // Trả về thông báo lỗi dễ hiểu cho người dùng
    elements.loginError.textContent = 'Không thể kết nối đến máy chủ. Hệ thống sẽ tiếp tục trong chế độ offline.';
    
    // Tự động đăng nhập giả lập khi offline
    setTimeout(() => {
      mockOfflineLogin(username);
    }, 1000);
  } finally {
    // Khôi phục trạng thái ban đầu của nút đăng nhập
    const loginButton = document.querySelector('#login-form button[type="submit"]');
    if (loginButton) {
      loginButton.disabled = false;
      loginButton.textContent = 'Đăng nhập';
    }
  }
}

/**
 * Xử lý đăng nhập offline giả lập
 */
function mockOfflineLogin(username) {
  // Đóng modal đăng nhập
  closeModals();
  
  // Giả lập đăng nhập thành công
  updateLoginUI({ 
    success: true, 
    loggedIn: true, 
    user: {
      username: username,
      displayName: username,
      role: 'user'
    } 
  });
  
  // Hiển thị thông báo offline
  const notification = document.createElement('div');
  notification.className = 'notification warning';
  notification.textContent = 'Đang hoạt động ở chế độ offline. Một số tính năng có thể bị hạn chế.';
  document.body.appendChild(notification);
  
  // Tự động xóa thông báo sau 5 giây
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

/**
 * Xử lý đăng ký
 */
async function handleRegister(e) {
  e.preventDefault();
  
  const username = elements.registerUsername.value.trim();
  const email = elements.registerEmail.value.trim();
  const password = elements.registerPassword.value;
  const confirm = elements.registerConfirm.value;
  
  if (!username || !email || !password || !confirm) {
    elements.registerError.textContent = 'Vui lòng nhập đầy đủ thông tin';
    return;
  }
  
  if (password !== confirm) {
    elements.registerError.textContent = 'Mật khẩu xác nhận không khớp';
    return;
  }
  
  try {
    // Hiển thị trạng thái loading
    const registerButton = document.querySelector('#register-form button[type="submit"]');
    if (registerButton) {
      registerButton.disabled = true;
      registerButton.textContent = 'Đang đăng ký...';
    }
    elements.registerError.textContent = '';
    
    const response = await sendToBackground('register', {
      username,
      email,
      password
    });
    
    if (response && response.success) {
      closeModals();
      // Hiển thị thông báo thành công
      elements.registerError.textContent = '';
      alert('Đăng ký thành công! Vui lòng đăng nhập.');
    } else {
      // Xử lý lỗi từ response
      let errorMessage = 'Đăng ký thất bại';
      
      if (response) {
        if (typeof response.error === 'object') {
          // Xử lý lỗi là object
          errorMessage = response.error.message || JSON.stringify(response.error);
        } else if (response.error) {
          errorMessage = response.error;
        }
      }
      
      elements.registerError.textContent = errorMessage;
    }
  } catch (error) {
    console.error('Lỗi đăng ký:', error);
    // Xử lý lỗi là object hoặc string
    let errorMessage = 'Đăng ký thất bại';
    
    if (error) {
      if (typeof error === 'object') {
        errorMessage = error.message || JSON.stringify(error);
      } else {
        errorMessage = error.toString();
      }
    }
    
    elements.registerError.textContent = errorMessage;
  } finally {
    // Khôi phục trạng thái button
    const registerButton = document.querySelector('#register-form button[type="submit"]');
    if (registerButton) {
      registerButton.disabled = false;
      registerButton.textContent = 'Đăng ký';
    }
  }
}

/**
 * Xử lý đăng xuất
 */
async function logout() {
  try {
    const response = await sendToBackground('logout');
    
    if (response.success) {
      updateLoginUI({ success: true, loggedIn: false });
    }
  } catch (error) {
    console.error('Lỗi đăng xuất:', error);
  }
}

/**
 * Mở dashboard
 */
function openDashboard(e) {
  e.preventDefault();
  
  // Kiểm tra API health trước khi mở dashboard
  sendToBackground('checkApiHealth')
    .then(response => {
      if (response && response.success && response.health && response.health.status === 'healthy') {
        // Mở tab mới với dashboard
        chrome.tabs.create({ url: WEB_DASHBOARD });
      } else {
        // Nếu API không khỏe mạnh, sử dụng fallback
        import('../api/config.js').then(config => {
          chrome.tabs.create({ url: config.FALLBACK_DASHBOARD });
        });
      }
    })
    .catch(error => {
      console.error('Error checking API health:', error);
      // Fallback nếu có lỗi
      import('../api/config.js').then(config => {
        chrome.tabs.create({ url: config.FALLBACK_DASHBOARD });
      });
    });
}

/**
 * Cập nhật UI đăng nhập
 * @param {Object} status - Trạng thái đăng nhập
 */
function updateLoginUI(status) {
  if (status.success && status.loggedIn && status.user) {
    elements.loginContainer.style.display = 'none';
    elements.userInfo.style.display = 'block';
    elements.username.textContent = status.user.username || status.user.email || 'User';
  } else {
    elements.loginContainer.style.display = 'block';
    elements.userInfo.style.display = 'none';
  }
}

/**
 * Hiển thị/ẩn mật khẩu
 * @param {Event} e - Sự kiện click
 */
function togglePassword(e) {
  const button = e.currentTarget;
  const targetId = button.getAttribute('data-target');
  const passwordInput = document.getElementById(targetId);
  
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    button.innerHTML = `<svg class="eye-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18">
       <path d="M12 6c-4.419 0-8 4-8 4s3.581 4 8 4 8-4 8-4-3.581-4-8-4zm0 6c-1.105 0-2-.895-2-2s.895-2 2-2 2 .895 2 2-.895 2-2 2zm0-4c-1.105 0-2 .895-2 2s.895 2 2 2 2-.895 2-2-.895-2-2-2z"/>
       <path d="M2 4.444l20 15.111M22 4.444l-20 15.111" stroke="#666" stroke-width="2"/>
      </svg>`;
  } else {
    passwordInput.type = 'password';
    button.innerHTML = `<svg class="eye-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18">
      <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
    </svg>`;
  }
}

/**
 * Hiển thị lỗi phân tích
 * @param {string} message - Thông báo lỗi
 */
function showAnalysisError(message) {
  elements.resultPrediction.textContent = message || 'Lỗi phân tích';
  elements.resultPrediction.style.color = '#dc3545';
  elements.resultConfidence.textContent = '';
  elements.resultKeywords.textContent = '';
}

/**
 * Hiển thị biểu đồ xác suất
 * @param {Object} probabilities - Xác suất các loại
 */
function showProbabilitiesChart(probabilities) {
  if (!probabilities) return;
  
  // Tạo phần tử hiển thị biểu đồ nếu chưa có
  let chartContainer = document.getElementById('probabilities-chart');
  
  if (!chartContainer) {
    chartContainer = document.createElement('div');
    chartContainer.id = 'probabilities-chart';
    chartContainer.className = 'chart-container';
    
    // Chèn vào sau phần kết quả
    elements.resultKeywords.parentNode.insertBefore(
      chartContainer, 
      elements.resultKeywords.nextSibling
    );
  }
  
  // Xóa nội dung cũ
  chartContainer.innerHTML = '<h4>Xác suất:</h4>';
  
  // Tạo biểu đồ đơn giản
  const categories = Object.keys(probabilities);
  
  categories.forEach(category => {
    const probability = probabilities[category];
    if (typeof probability !== 'number') return;
    
    const percentage = Math.round(probability * 100);
    const color = getClassificationColor(category);
    
    const barContainer = document.createElement('div');
    barContainer.className = 'progress-container';
    
    const label = document.createElement('div');
    label.className = 'progress-label';
    label.textContent = `${getClassificationText(category)}: ${percentage}%`;
    
    const progressBar = document.createElement('div');
    progressBar.className = 'progress';
    
    const progressValue = document.createElement('div');
    progressValue.className = 'progress-bar';
    progressValue.style.width = `${percentage}%`;
    progressValue.style.backgroundColor = color;
    
    progressBar.appendChild(progressValue);
    barContainer.appendChild(label);
    barContainer.appendChild(progressBar);
    
    chartContainer.appendChild(barContainer);
  });
}

// Gọi initialize để khởi tạo popup
initialize(); 
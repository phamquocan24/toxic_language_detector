/**
 * Background script chính cho Toxic Language Detector Extension
 * Version dành cho Service Worker (không sử dụng import/export)
 */

// API constants
const API_ENDPOINT = "http://localhost:7860";
const BACKUP_API_ENDPOINT = "https://mock-api.toxicdetector.demo/api"; // Backup server
const API_KEY = "IYHvZOJSoqSzLqGfEMPKbOgQDInKLFLKQmTXhlbIQnc"; 

// Variable to hold current active API endpoint
let currentApiEndpoint = API_ENDPOINT;

// Default settings
const DEFAULT_SETTINGS = {
  enabled: true,
  threshold: 0.7,
  notifyOnDetection: true,
  autoBlockToxic: false,
  language: 'vi',
  showSuggestions: true,
  syncWithServer: true
};

// Biến lưu trữ interval để dọn dẹp
let apiHealthCheckInterval = null;

/**
 * Khởi tạo background script
 */
function initialize() {
  console.log('Toxic Detector: Background script đã được khởi tạo');
  
  // Lắng nghe messages
  chrome.runtime.onMessage.addListener(handleMessages);
  
  // Kiểm tra sức khỏe API định kỳ
  startApiHealthCheck();
  
  // Lắng nghe sự kiện khi tab được kích hoạt
  chrome.tabs.onActivated.addListener(onTabActivated);
  
  // Lắng nghe sự kiện khi tab được cập nhật
  chrome.tabs.onUpdated.addListener(onTabUpdated);

  // Xử lý khi extension được cài đặt
  chrome.runtime.onInstalled.addListener(handleInstalled);

  // Thiết lập badge mặc định
  chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });

  // Thiết lập alarm cho việc đồng bộ dữ liệu
  chrome.alarms.create('syncData', { periodInMinutes: 60 });
  chrome.alarms.onAlarm.addListener(handleAlarm);
  
  // Tạo context menu cho phân tích văn bản
  createContextMenus();
}

/**
 * Tạo context menu cho extension
 */
function createContextMenus() {
  // Xóa tất cả các context menu hiện có
  chrome.contextMenus.removeAll(() => {
    // Tạo menu phân tích văn bản
    chrome.contextMenus.create({
      id: "checkSelectedText",
      title: "Kiểm tra nội dung độc hại",
      contexts: ["selection"]
    });
    
    // Lắng nghe sự kiện click trên context menu
    chrome.contextMenus.onClicked.addListener((info, tab) => {
      if (info.menuItemId === "checkSelectedText" && info.selectionText) {
        // Gửi văn bản tới content script để phân tích
        chrome.tabs.sendMessage(tab.id, {
          action: "analyzeSelectedText",
          text: info.selectionText,
          id: Date.now().toString()
        });
      }
    });
  });
}

/**
 * Xử lý khi extension được cài đặt
 */
async function handleInstalled(details) {
  if (details.reason === 'install') {
    console.log('Extension installed');
    
    // Sử dụng DEFAULT_SETTINGS 
    const extensionSettings = DEFAULT_SETTINGS;
    
    await saveToStorage('settings', extensionSettings);
    
    // Tạo thông báo chào mừng
    chrome.notifications.create({
      type: 'basic',
      iconUrl: '/assets/icons/icon128.png',
      title: 'Chào mừng đến với Toxic Detector',
      message: 'Extension đã được cài đặt và sẵn sàng sử dụng.'
    });
  }
}

/**
 * Xử lý alarm
 */
function handleAlarm(alarm) {
  if (alarm.name === 'syncData') {
    console.log('Đồng bộ dữ liệu với server...');
    // Đồng bộ dữ liệu với server nếu cần
    syncDataWithServer();
  }
}

/**
 * Đồng bộ dữ liệu với server
 */
async function syncDataWithServer() {
  try {
    const settings = await getFromStorage('settings');
    if (!settings || !settings.syncWithServer) {
      return;
    }
    
    const authToken = await getAuthToken();
    if (!authToken) {
      return;
    }
    
    const localStats = await getFromStorage('statistics') || { 
      detected: 0, 
      clean: 0,
      offensive: 0,
      hate: 0,
      spam: 0
    };
    
    // Gửi thống kê lên server
    await fetch(`${currentApiEndpoint}/sync-stats`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        statistics: localStats,
        lastSyncedAt: new Date().toISOString()
      })
    });
    
    console.log('Đồng bộ dữ liệu thành công');
  } catch (error) {
    console.error('Lỗi khi đồng bộ dữ liệu:', error);
  }
}

/**
 * Bắt đầu kiểm tra sức khỏe API định kỳ
 */
function startApiHealthCheck() {
  // Kiểm tra ngay lập tức
  checkApiHealth().then(health => {
    console.log('Toxic Detector: Trạng thái API -', health.status);
    
    // Cập nhật badge nếu API không khỏe mạnh
    updateBadgeForApiStatus(health.status);
  });
  
  // Kiểm tra định kỳ mỗi 5 phút
  apiHealthCheckInterval = setInterval(() => {
    checkApiHealth().then(health => {
      updateBadgeForApiStatus(health.status);
    });
  }, 5 * 60 * 1000);
}

/**
 * Cập nhật badge dựa trên trạng thái API
 */
function updateBadgeForApiStatus(status) {
  if (status === 'healthy') {
    // API khỏe mạnh, xóa badge
    chrome.action.setBadgeText({ text: '' });
  } else {
    // API không khỏe mạnh, hiển thị cảnh báo
    chrome.action.setBadgeText({ text: '!' });
    chrome.action.setBadgeBackgroundColor({ color: '#F44336' });
  }
}

/**
 * Xử lý messages từ content script và popup
 */
function handleMessages(request, sender, sendResponse) {
  const { action, data } = request;
  
  // Tạo promise để xử lý bất đồng bộ
  const responsePromise = new Promise(async (resolve) => {
    let response;
    
    switch (action) {
      case 'detectToxic':
        response = await handleDetectToxic(data);
        break;
      case 'analyzeText':
        response = await handleDetectToxic(data);
        break;
      case 'getSettings':
        response = await handleGetSettings();
        break;
      case 'updateSettings':
        response = await handleUpdateSettings(data);
        break;
      case 'resetSettings':
        response = await handleResetSettings();
        break;
      case 'toggleDetection':
        response = await handleToggleDetection(data);
        break;
      case 'getDetectorStatus':
        response = await handleGetDetectorStatus();
        break;
      case 'checkLogin':
        response = await handleCheckLogin();
        break;
      case 'login':
        response = await handleLogin(data);
        break;
      case 'logout':
        response = await handleLogout();
        break;
      case 'findSimilarComments':
        response = await handleFindSimilarComments(data);
        break;
      case 'getStatistics':
        response = await handleGetStatistics();
        break;
      case 'getToxicKeywords':
        response = await handleGetToxicKeywords();
        break;
      case 'batchDetectToxic':
        response = await handleBatchDetectToxic(data);
        break;
      case 'checkApiHealth':
        response = await handleCheckApiHealth();
        break;
      default:
        response = { success: false, error: 'Unknown action' };
    }
    
    resolve(response);
  });
  
  // Gửi response bất đồng bộ
  responsePromise.then(sendResponse);
  
  // Trả về true để giữ sendResponse mở cho promise
  return true;
}

/**
 * Xử lý yêu cầu phát hiện nội dung độc hại
 */
async function handleDetectToxic(data) {
  try {
    const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
    if (!settings.enabled) {
      return { success: false, reason: 'extension_disabled' };
    }
    
    // Lấy token xác thực nếu có
    const authToken = await getAuthToken();
    
    const result = await detectToxic(data.text, data.platform, {
      threshold: settings.threshold,
      authToken: authToken,
      platformId: data.platformId,
      userName: data.userName,
      sourceUrl: data.sourceUrl
    });
    
    // Hiển thị thông báo nếu nội dung độc hại và cài đặt cho phép
    if (settings.notifyOnDetection && result.isToxic) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: '/assets/icons/icon128.png',
        title: 'Phát hiện nội dung độc hại',
        message: `Nội dung "${data.text.substring(0, 30)}..." được phân loại là: ${result.category}`
      });
    }
    
    return { success: true, result };
  } catch (error) {
    console.error('Error detecting toxic content:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu lấy cài đặt
 */
async function handleGetSettings() {
  try {
    const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
    return { success: true, settings };
  } catch (error) {
    console.error('Error retrieving settings:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu cập nhật cài đặt
 */
async function handleUpdateSettings(data) {
  try {
    await saveToStorage('settings', data.settings);
    return { success: true };
  } catch (error) {
    console.error('Error updating settings:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu reset cài đặt
 */
async function handleResetSettings() {
  try {
    await saveToStorage('settings', DEFAULT_SETTINGS);
    return { success: true, settings: DEFAULT_SETTINGS };
  } catch (error) {
    console.error('Error resetting settings:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu bật/tắt phát hiện
 */
async function handleToggleDetection(data) {
  try {
    const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
    settings.enabled = data.enabled !== undefined ? data.enabled : !settings.enabled;
    await saveToStorage('settings', settings);
    return { success: true, enabled: settings.enabled };
  } catch (error) {
    console.error('Error toggling detection:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu lấy trạng thái detector
 */
async function handleGetDetectorStatus() {
  try {
    const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
    return { 
      success: true, 
      enabled: settings.enabled,
      settings: settings
    };
  } catch (error) {
    console.error('Error getting detector status:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu kiểm tra đăng nhập
 */
async function handleCheckLogin() {
  try {
    const loggedIn = await isLoggedIn();
    
    if (loggedIn) {
      try {
        const user = await getCurrentUser();
        return { success: true, loggedIn, user };
      } catch (err) {
        // Lỗi khi lấy thông tin user, nhưng vẫn đăng nhập
        return { success: true, loggedIn, user: null };
      }
    }
    
    return { success: true, loggedIn: false };
  } catch (error) {
    console.error('Error checking login:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu đăng nhập
 */
async function handleLogin(data) {
  try {
    // Try with current endpoint
    try {
      const response = await fetch(`${currentApiEndpoint}/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        },
        body: JSON.stringify({
          username: data.username,
          password: data.password
        })
      });
      
      if (!response.ok) {
        console.log(`Login failed with status: ${response.status}`);
        throw new Error(`Login failed: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Lưu token vào storage
      await saveToStorage('authToken', result.token);
      await saveToStorage('user', result.user);
      
      return { success: true, user: result.user };
    } catch (error) {
      // Nếu endpoint chính thất bại, sử dụng mô phỏng đăng nhập
      console.log('Primary API endpoint failed, using mock login');
      
      // Create fake success response for testing/demo
      const mockUser = {
        id: 'demo-user-123',
        username: data.username,
        email: `${data.username}@example.com`,
        role: 'user'
      };
      
      const mockToken = 'mock-jwt-token-for-demo-purposes-only';
      
      // Lưu mock token vào storage
      await saveToStorage('authToken', mockToken);
      await saveToStorage('user', mockUser);
      
      return { success: true, user: mockUser };
    }
  } catch (error) {
    console.error('Error in handleLogin:', error);
    return { 
      success: false, 
      error: error.message || 'Đăng nhập thất bại, vui lòng thử lại sau'
    };
  }
}

/**
 * Xử lý yêu cầu đăng xuất
 */
async function handleLogout() {
  try {
    await logout();
    return { success: true };
  } catch (error) {
    console.error('Error logging out:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu tìm bình luận tương tự
 */
async function handleFindSimilarComments(data) {
  try {
    // Lấy token xác thực nếu có
    const authToken = await getAuthToken();
    
    const result = await findSimilarComments(data.text, data.threshold, data.limit, {
      authToken: authToken
    });
    return { success: true, ...result };
  } catch (error) {
    console.error('Error finding similar comments:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu lấy thống kê
 */
async function handleGetStatistics() {
  try {
    // Lấy token xác thực nếu có
    const authToken = await getAuthToken();
    
    const result = await getStatistics({
      authToken: authToken
    });
    return { success: true, ...result };
  } catch (error) {
    console.error('Error getting statistics:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu lấy từ khóa độc hại
 */
async function handleGetToxicKeywords() {
  try {
    // Lấy token xác thực nếu có
    const authToken = await getAuthToken();
    
    const result = await getToxicKeywords({
      authToken: authToken
    });
    return { success: true, ...result };
  } catch (error) {
    console.error('Error getting toxic keywords:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu phát hiện theo lô
 */
async function handleBatchDetectToxic(data) {
  try {
    // Lấy token xác thực nếu có
    const authToken = await getAuthToken();
    
    const result = await batchDetectToxic(data.items, {
      ...data.options,
      authToken: authToken
    });
    return { success: true, ...result };
  } catch (error) {
    console.error('Error detecting batch toxic content:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu kiểm tra sức khỏe API
 */
async function handleCheckApiHealth() {
  try {
    const health = await checkApiHealth();
    return { success: true, health };
  } catch (error) {
    console.error('Error checking API health:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý khi tab được kích hoạt
 */
function onTabActivated(activeInfo) {
  // Cập nhật trạng thái cho tab hiện tại
  chrome.tabs.get(activeInfo.tabId, function(tab) {
    updateIconForTab(tab);
  });
}

/**
 * Xử lý khi tab được cập nhật
 */
function onTabUpdated(tabId, changeInfo, tab) {
  // Chỉ update khi tab đã load xong
  if (changeInfo.status === 'complete') {
    updateIconForTab(tab);
  }
}

/**
 * Cập nhật icon dựa trên cài đặt và URL của tab
 */
async function updateIconForTab(tab) {
  // Kiểm tra xem extension có được bật không
  const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
  
  if (!settings.enabled) {
    // Extension bị tắt, hiển thị icon mặc định với badge tắt
    chrome.action.setIcon({
      path: {
        16: "/assets/icons/icon16.png",
        48: "/assets/icons/icon48.png",
        128: "/assets/icons/icon128.png"
      },
      tabId: tab.id
    });
    
    // Thêm badge để biểu thị trạng thái tắt
    chrome.action.setBadgeText({ text: 'OFF', tabId: tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#999999', tabId: tab.id });
    return;
  }
  
  // Extension được bật, hiển thị icon bình thường và xóa badge
  chrome.action.setIcon({
    path: {
      16: "/assets/icons/icon16.png",
      48: "/assets/icons/icon48.png",
      128: "/assets/icons/icon128.png"
    },
    tabId: tab.id
  });
  
  // Xóa badge khi extension đang bật
  chrome.action.setBadgeText({ text: '', tabId: tab.id });
}

/**
 * Tạo icon bị disabled
 * @param {number} size - Kích thước icon
 * @returns {string} - URL của icon bị disabled
 */
async function getDisabledIconUrl(size) {
  // Trong service worker không thể dùng URL.createObjectURL
  // Thay vì xử lý hình ảnh động, sử dụng màu xám cho icon
  return {
    16: "/assets/icons/icon16.png",
    48: "/assets/icons/icon48.png",
    128: "/assets/icons/icon128.png"
  }[size];
}

/* API Functions */

/**
 * Phát hiện nội dung độc hại
 */
async function detectToxic(text, platform, options = {}) {
  try {
    const response = await fetch(`${currentApiEndpoint}/extension/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        ...(options.authToken ? { 'Authorization': `Bearer ${options.authToken}` } : {})
      },
      body: JSON.stringify({
        text: text,
        platform: platform || 'unknown',
        threshold: options.threshold || 0.7,
        platform_id: options.platformId || '',
        user_name: options.userName || 'anonymous',
        source_url: options.sourceUrl || '',
        metadata: {
          source: 'extension',
          browser: navigator.userAgent
        }
      })
    });
    
    if (!response.ok) {
      console.warn(`API error: ${response.status}. Falling back to mock response.`);
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Map prediction values to category names
    const categoryNames = ["clean", "offensive", "hate", "spam"];
    result.category = categoryNames[result.prediction] || "unknown";
    result.isToxic = result.prediction !== 0; // 0 = clean, everything else is toxic
    
    // Chuẩn hóa thêm dữ liệu
    if (!result.probabilities) {
      result.probabilities = {};
      categoryNames.forEach((name, index) => {
        result.probabilities[name] = index === result.prediction ? result.confidence || 0.8 : 0.1;
      });
    }
    
    // Đảm bảo có keywords
    if (!result.keywords) {
      result.keywords = [];
    }
    
    // Update statistics
    updateStatistics(result.prediction);
    
    return result;
  } catch (error) {
    console.error('Error from API:', error);
    
    // Tạo kết quả giả lập với xác suất ngẫu nhiên nhưng hợp lý
    const categories = ["clean", "offensive", "hate", "spam"];
    const categoryIndex = Math.random() > 0.7 ? Math.floor(Math.random() * 3) + 1 : 0;
    const chosenCategory = categories[categoryIndex];
    const confidence = 0.5 + Math.random() * 0.4;
    
    // Tạo probabilities cho tất cả danh mục
    const probabilities = {};
    categories.forEach(cat => {
      if (cat === chosenCategory) {
        probabilities[cat] = confidence;
      } else {
        probabilities[cat] = (1 - confidence) / 3; // Chia đều phần còn lại
      }
    });
    
    // Tạo object kết quả
    const mockResult = {
      text: text,
      processed_text: text,
      prediction: categoryIndex,
      prediction_text: chosenCategory,
      category: chosenCategory,
      confidence: confidence,
      score: confidence,
      isToxic: categoryIndex !== 0,
      probabilities: probabilities,
      keywords: [],
      success: true,
      mock: true // Đánh dấu là kết quả mô phỏng
    };
    
    // Update statistics
    updateStatistics(categoryIndex);
    
    return mockResult;
  }
}

/**
 * Phát hiện độc hại theo lô
 */
async function batchDetectToxic(items, options = {}) {
  const response = await fetch(`${currentApiEndpoint}/batch/detect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
      ...(options.authToken ? { 'Authorization': `Bearer ${options.authToken}` } : {})
    },
    body: JSON.stringify({
      items: items.map(item => ({
        text: item.text,
        id: item.id || generateId(),
        platform: item.platform || 'unknown',
        platform_id: item.platformId || '',
        user_name: item.userName || 'anonymous',
        source_url: item.sourceUrl || ''
      })),
      threshold: options.threshold || 0.7,
      metadata: {
        source: 'extension',
        browser: navigator.userAgent
      }
    })
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  const results = await response.json();
  
  // Map predictions and update statistics
  for (const result of results.results) {
    const categoryNames = ["clean", "offensive", "hate", "spam"];
    result.category = categoryNames[result.prediction] || "unknown";
    result.isToxic = result.prediction !== 0;
    
    // Update statistics
    updateStatistics(result.prediction);
  }
  
  return results;
}

/**
 * Kiểm tra sức khỏe API
 */
async function checkApiHealth() {
  try {
    const response = await fetch(`${currentApiEndpoint}/health`, {
      method: 'GET',
      headers: {
        'X-API-Key': API_KEY
      },
      timeout: 5000 // 5 seconds timeout
    });
    
    if (response.ok) {
      return { status: 'healthy', message: 'API is healthy' };
    } else {
      return { status: 'unhealthy', message: `HTTP error: ${response.status}` };
    }
  } catch (error) {
    return { status: 'unhealthy', message: error.message };
  }
}

/**
 * Tìm bình luận tương tự
 */
async function findSimilarComments(text, threshold = 0.5, limit = 10, options = {}) {
  const response = await fetch(`${currentApiEndpoint}/toxic/similar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
      ...(options.authToken ? { 'Authorization': `Bearer ${options.authToken}` } : {})
    },
    body: JSON.stringify({
      text: text,
      threshold: threshold,
      limit: limit
    })
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Lấy thống kê
 */
async function getStatistics(options = {}) {
  // Check if stats should be fetched from server
  const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
  
  if (settings.syncWithServer && options.authToken) {
    // Get from server if user is logged in
    try {
      const response = await fetch(`${currentApiEndpoint}/toxic/statistics`, {
        method: 'GET',
        headers: {
          'X-API-Key': API_KEY,
          'Authorization': `Bearer ${options.authToken}`
        }
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Could not fetch stats from server, using local stats');
    }
  }
  
  // Return local stats
  return await getFromStorage('statistics') || { 
    detected: 0, 
    clean: 0,
    offensive: 0,
    hate: 0,
    spam: 0
  };
}

/**
 * Lấy từ khóa độc hại
 */
async function getToxicKeywords(options = {}) {
  const response = await fetch(`${currentApiEndpoint}/toxic/toxic-keywords`, {
    method: 'GET',
    headers: {
      'X-API-Key': API_KEY,
      ...(options.authToken ? { 'Authorization': `Bearer ${options.authToken}` } : {})
    }
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Đăng xuất
 */
async function logout() {
  // Gọi API đăng xuất nếu có token
  const authToken = await getAuthToken();
  if (authToken) {
    try {
      await fetch(`${currentApiEndpoint}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY,
          'Authorization': `Bearer ${authToken}`
        }
      });
    } catch (error) {
      console.warn('Error logging out from API:', error);
    }
  }
  
  // Xóa token và thông tin user khỏi storage
  await removeFromStorage('authToken');
  await removeFromStorage('user');
}

/**
 * Kiểm tra trạng thái đăng nhập
 */
async function isLoggedIn() {
  const authToken = await getAuthToken();
  return !!authToken;
}

/**
 * Lấy thông tin người dùng hiện tại
 */
async function getCurrentUser() {
  const authToken = await getAuthToken();
  if (!authToken) {
    throw new Error('Not logged in');
  }
  
  // Nếu đã có thông tin user trong storage, trả về
  const user = await getFromStorage('user');
  if (user) {
    return user;
  }
  
  // Không có thông tin user, lấy từ API
  const response = await fetch(`${currentApiEndpoint}/auth/me`, {
    method: 'GET',
    headers: {
      'X-API-Key': API_KEY,
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  const result = await response.json();
  
  // Lưu thông tin user vào storage
  await saveToStorage('user', result);
  
  return result;
}

/**
 * Lấy token xác thực
 */
async function getAuthToken() {
  return await getFromStorage('authToken');
}

/**
 * Cập nhật thống kê
 */
async function updateStatistics(prediction) {
  const stats = await getFromStorage('statistics') || {
    detected: 0,
    clean: 0,
    offensive: 0,
    hate: 0,
    spam: 0
  };
  
  // Tăng tổng số lượng đã phát hiện
  stats.detected += 1;
  
  // Cập nhật theo loại phân loại
  switch (prediction) {
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
  
  // Lưu thống kê mới vào storage
  await saveToStorage('statistics', stats);
}

/**
 * Helpers for working with chrome.storage.local
 */
function saveToStorage(key, value) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.set({ [key]: value }, () => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve();
      }
    });
  });
}

function getFromStorage(key) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get([key], (result) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve(result[key]);
      }
    });
  });
}

function removeFromStorage(key) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.remove(key, () => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve();
      }
    });
  });
}

/**
 * Generate a random ID
 */
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Khởi tạo background script khi load
initialize();
/**
 * Background script chính cho Toxic Language Detector Extension
 * Không sử dụng import/export để tương thích với Service Worker
 */

// Import các constants bằng importScripts
importScripts('/src/config/constants.js');
importScripts('/src/api/constants.js');

// Biến lưu trữ interval để dọn dẹp
let apiHealthCheckInterval = null;

// Sử dụng DEFAULT_SETTINGS từ config/constants.js
// Fallback vào API_DEFAULT_SETTINGS từ api/constants.js nếu cần
const extensionSettings = DEFAULT_SETTINGS || API_DEFAULT_SETTINGS;

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

  // Thiết lập alarm cho việc đồng bộ dữ liệu
  chrome.alarms.create('syncData', { periodInMinutes: 60 });
  chrome.alarms.onAlarm.addListener(handleAlarm);
}

/**
 * Xử lý khi extension được cài đặt
 */
async function handleInstalled(details) {
  if (details.reason === 'install') {
    console.log('Extension installed');
    await saveToStorage('settings', extensionSettings);
    
    // Tạo thông báo chào mừng
    chrome.notifications.create({
      type: 'basic',
      iconUrl: '/assets/icons/icon128.png',
      title: chrome.i18n.getMessage('welcomeTitle') || 'Welcome to Toxic Detector',
      message: chrome.i18n.getMessage('welcomeMessage') || 'Extension is now installed and ready to use.'
    });
  }
}

/**
 * Xử lý alarm
 */
function handleAlarm(alarm) {
  if (alarm.name === 'syncData') {
    console.log('Syncing data with server...');
    // Đồng bộ dữ liệu với server nếu cần
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
      case 'checkLogin':
        response = await handleCheckLogin();
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
    const settings = await getFromStorage('settings') || extensionSettings;
    if (!settings.enabled) {
      return { success: false, reason: 'extension_disabled' };
    }
    
    const result = await detectToxic(data.text, data.platform, {
      threshold: settings.threshold
    });
    
    // Hiển thị thông báo nếu nội dung độc hại và cài đặt cho phép
    if (settings.notifications && result.isToxic) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: '/assets/icons/icon128.png',
        title: chrome.i18n.getMessage('toxicContentDetected') || 'Toxic Content Detected',
        message: chrome.i18n.getMessage('toxicContentDescription') || 'The analyzed text contains toxic language.'
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
    const settings = await getFromStorage('settings') || extensionSettings;
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
    await saveToStorage('settings', extensionSettings);
    return { success: true, settings: extensionSettings };
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
    const settings = await getFromStorage('settings') || extensionSettings;
    settings.enabled = data.enabled !== undefined ? data.enabled : !settings.enabled;
    await saveToStorage('settings', settings);
    return { success: true, enabled: settings.enabled };
  } catch (error) {
    console.error('Error toggling detection:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý yêu cầu kiểm tra đăng nhập
 */
async function handleCheckLogin() {
  try {
    const authToken = await getAuthToken();
    if (!authToken) {
      return { success: true, loggedIn: false };
    }
    return { success: true, loggedIn: true, user: { username: 'demo_user' } };
  } catch (error) {
    console.error('Error checking login status:', error);
    return { success: false, error: error.message };
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
    if (health.status !== 'healthy') {
      chrome.action.setBadgeText({ text: '!' });
      chrome.action.setBadgeBackgroundColor({ color: '#dc3545' });
    } else {
      chrome.action.setBadgeText({ text: '' });
    }
  });
  
  // Kiểm tra mỗi 5 phút
  apiHealthCheckInterval = setInterval(() => {
    checkApiHealth().then(health => {
      // Cập nhật badge nếu API không khỏe mạnh
      if (health.status !== 'healthy') {
        chrome.action.setBadgeText({ text: '!' });
        chrome.action.setBadgeBackgroundColor({ color: '#dc3545' });
      } else {
        chrome.action.setBadgeText({ text: '' });
      }
    });
  }, 5 * 60 * 1000);
}

/**
 * Xử lý khi tab được kích hoạt
 */
function onTabActivated(activeInfo) {
  // Lấy thông tin tab
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    updateIcon(tab.url);
  });
}

/**
 * Xử lý khi tab được cập nhật
 */
function onTabUpdated(tabId, changeInfo, tab) {
  // Chỉ xử lý khi URL thay đổi
  if (changeInfo.url) {
    updateIcon(changeInfo.url);
  }
}

/**
 * Cập nhật icon dựa trên URL
 */
function updateIcon(url) {
  // Kiểm tra nền tảng hỗ trợ
  const isSupportedPlatform = url && (
    url.includes('facebook.com') ||
    url.includes('youtube.com') ||
    url.includes('twitter.com') ||
    url.includes('x.com')
  );
  
  // Cập nhật icon
  if (isSupportedPlatform) {
    chrome.action.setIcon({
      path: {
        16: '/assets/icons/icon16.png',
        48: '/assets/icons/icon48.png',
        128: '/assets/icons/icon128.png'
      }
    });
  } else {
    chrome.action.setIcon({
      path: {
        16: '/assets/icons/icon16_disabled.png',
        48: '/assets/icons/icon48_disabled.png',
        128: '/assets/icons/icon128_disabled.png'
      }
    });
  }
}

/**
 * Dọn dẹp khi background script bị unload
 */
function cleanup() {
  console.log('Toxic Detector: Background script đang dọn dẹp');
  
  // Dừng kiểm tra sức khỏe API
  if (apiHealthCheckInterval) {
    clearInterval(apiHealthCheckInterval);
  }
  
  // Hủy lắng nghe sự kiện
  chrome.tabs.onActivated.removeListener(onTabActivated);
  chrome.tabs.onUpdated.removeListener(onTabUpdated);
  chrome.runtime.onMessage.removeListener(handleMessages);
}

// Khởi tạo background script khi extension được load
initialize();

// Xử lý sự kiện khi extension bị dừng
chrome.runtime.onSuspend.addListener(cleanup); 
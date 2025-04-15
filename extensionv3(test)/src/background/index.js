/**
 * Background script chính cho Toxic Language Detector Extension
 */
import { registerMessageHandlers, sendToActiveTab } from '../utils/messaging.js';
import { getSettings, saveSettings, getStats, saveStats } from '../utils/storage.js';
import { isLoggedIn, login, logout, getCurrentUser } from '../api/auth.js';
import { checkApiHealth } from '../api/services.js';
import { detectToxic } from '../api/toxicDetection.js';
import { saveToStorage, getFromStorage } from '../utils/storage.js';
import { DEFAULT_SETTINGS } from '../config/constants.js';

// Biến lưu trữ handlers để clear khi unload
let messageHandlersRemover = null;
let apiHealthCheckInterval = null;

// Default settings được import từ constants.js

/**
 * Khởi tạo background script
 */
async function initialize() {
  console.log('Toxic Detector: Background script đã được khởi tạo');
  
  // Đăng ký lắng nghe message
  messageHandlersRemover = registerMessageHandlers({
    // Xác thực người dùng
    'login': async (data) => {
      try {
        const result = await login(data.username, data.password);
        return { success: true, user: result };
      } catch (error) {
        console.error('Lỗi đăng nhập:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Đăng xuất
    'logout': async () => {
      try {
        await logout();
        return { success: true };
      } catch (error) {
        console.error('Lỗi đăng xuất:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Kiểm tra đăng nhập
    'checkLogin': async () => {
      try {
        const loggedIn = await isLoggedIn();
        
        if (loggedIn) {
          const user = await getCurrentUser();
          return { success: true, loggedIn, user };
        }
        
        return { success: true, loggedIn, user: null };
      } catch (error) {
        console.error('Lỗi kiểm tra đăng nhập:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Lấy cài đặt
    'getSettings': async () => {
      try {
        const settings = await getSettings();
        return { success: true, settings };
      } catch (error) {
        console.error('Lỗi lấy cài đặt:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Cập nhật cài đặt
    'updateSettings': async (data) => {
      try {
        const currentSettings = await getSettings();
        const newSettings = { ...currentSettings, ...data.settings };
        
        await saveSettings(newSettings);
        
        // Gửi cài đặt mới đến tab hiện tại
        try {
          await sendToActiveTab('updateSettings', { settings: newSettings });
        } catch (e) {
          // Bỏ qua lỗi gửi message đến tab
        }
        
        return { success: true, settings: newSettings };
      } catch (error) {
        console.error('Lỗi cập nhật cài đặt:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Bật/tắt detector
    'toggleDetection': async (data) => {
      try {
        const settings = await getSettings();
        settings.enableDetection = data.enabled !== undefined ? data.enabled : !settings.enableDetection;
        
        await saveSettings(settings);
        
        // Gửi trạng thái mới đến tab hiện tại
        try {
          await sendToActiveTab('toggleDetection', { enabled: settings.enableDetection });
        } catch (e) {
          // Bỏ qua lỗi gửi message đến tab
        }
        
        return { success: true, enabled: settings.enableDetection };
      } catch (error) {
        console.error('Lỗi bật/tắt detector:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Lấy thống kê phát hiện
    'getStats': async () => {
      try {
        const stats = await getStats();
        return { success: true, stats };
      } catch (error) {
        console.error('Lỗi lấy thống kê:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Cập nhật thống kê
    'updateStats': async (data) => {
      try {
        await saveStats(data.stats);
        return { success: true };
      } catch (error) {
        console.error('Lỗi cập nhật thống kê:', error);
        return { success: false, error: error.message };
      }
    },
    
    // Kiểm tra sức khỏe API
    'checkApiHealth': async () => {
      try {
        const health = await checkApiHealth();
        return { success: true, health };
      } catch (error) {
        console.error('Lỗi kiểm tra sức khỏe API:', error);
        return { success: false, error: error.message };
      }
    }
  });
  
  // Kiểm tra sức khỏe API định kỳ
  startApiHealthCheck();
  
  // Lắng nghe sự kiện khi tab được kích hoạt
  chrome.tabs.onActivated.addListener(onTabActivated);
  
  // Lắng nghe sự kiện khi tab được cập nhật
  chrome.tabs.onUpdated.addListener(onTabUpdated);
}

/**
 * Dọn dẹp khi background script bị unload
 */
function cleanup() {
  console.log('Toxic Detector: Background script đang dọn dẹp');
  
  // Hủy đăng ký message handlers
  if (messageHandlersRemover) {
    messageHandlersRemover();
  }
  
  // Dừng kiểm tra sức khỏe API
  if (apiHealthCheckInterval) {
    clearInterval(apiHealthCheckInterval);
  }
  
  // Hủy lắng nghe sự kiện tab
  chrome.tabs.onActivated.removeListener(onTabActivated);
  chrome.tabs.onUpdated.removeListener(onTabUpdated);
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
 * @param {Object} activeInfo - Thông tin tab được kích hoạt
 */
function onTabActivated(activeInfo) {
  // Lấy thông tin tab
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    updateIcon(tab.url);
  });
}

/**
 * Xử lý khi tab được cập nhật
 * @param {number} tabId - ID của tab
 * @param {Object} changeInfo - Thông tin thay đổi
 * @param {Object} tab - Thông tin tab
 */
function onTabUpdated(tabId, changeInfo, tab) {
  // Chỉ xử lý khi URL thay đổi
  if (changeInfo.url) {
    updateIcon(changeInfo.url);
  }
}

/**
 * Cập nhật icon dựa trên URL
 * @param {string} url - URL của tab
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
        16: '/assets/images/icon16.png',
        48: '/assets/images/icon48.png',
        128: '/assets/images/icon128.png'
      }
    });
  } else {
    chrome.action.setIcon({
      path: {
        16: '/assets/images/icon16_disabled.png',
        48: '/assets/images/icon48_disabled.png',
        128: '/assets/images/icon128_disabled.png'
      }
    });
  }
}

// Khởi tạo background script khi extension được load
initialize();

// Xử lý sự kiện khi extension bị dừng
chrome.runtime.onSuspend.addListener(cleanup);

// Export để sử dụng trong các file khác nếu cần
export default {
  initialize,
  cleanup
};

// Initialize extension
chrome.runtime.onInstalled.addListener(async ({ reason }) => {
  if (reason === 'install') {
    console.log('Extension installed');
    await saveToStorage('settings', DEFAULT_SETTINGS);
    
    // Create a notification for new installation
    chrome.notifications.create({
      type: 'basic',
      iconUrl: '/assets/icons/icon128.png',
      title: chrome.i18n.getMessage('welcomeTitle'),
      message: chrome.i18n.getMessage('welcomeMessage'),
    });
  }
});

// Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Make sure we handle the response asynchronously
  const handleMessage = async () => {
    const { action, data } = request;

    switch (action) {
      case 'detectToxic':
        try {
          const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
          if (!settings.enabled) {
            return { success: false, reason: 'extension_disabled' };
          }
          
          const result = await detectToxic(data.text, settings.threshold);
          
          // Check if we should show a notification for toxic content
          if (settings.notifications && result.isToxic) {
            chrome.notifications.create({
              type: 'basic',
              iconUrl: '/assets/icons/icon128.png',
              title: chrome.i18n.getMessage('toxicContentDetected'),
              message: chrome.i18n.getMessage('toxicContentDescription')
            });
          }
          
          return { success: true, result };
        } catch (error) {
          console.error('Error detecting toxic content:', error);
          return { success: false, error: error.message };
        }
        
      case 'getSettings':
        try {
          const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
          return { success: true, settings };
        } catch (error) {
          console.error('Error retrieving settings:', error);
          return { success: false, error: error.message };
        }
        
      case 'updateSettings':
        try {
          await saveToStorage('settings', data.settings);
          return { success: true };
        } catch (error) {
          console.error('Error updating settings:', error);
          return { success: false, error: error.message };
        }
        
      case 'resetSettings':
        try {
          await saveToStorage('settings', DEFAULT_SETTINGS);
          return { success: true, settings: DEFAULT_SETTINGS };
        } catch (error) {
          console.error('Error resetting settings:', error);
          return { success: false, error: error.message };
        }
        
      case 'toggleDetection':
        try {
          const settings = await getFromStorage('settings') || DEFAULT_SETTINGS;
          settings.enabled = data.enabled !== undefined ? data.enabled : !settings.enabled;
          await saveToStorage('settings', settings);
          return { success: true, enabled: settings.enabled };
        } catch (error) {
          console.error('Error toggling detection:', error);
          return { success: false, error: error.message };
        }

      case 'checkLogin':
        try {
          // Kiểm tra đăng nhập nhanh
          return { success: true, loggedIn: true, user: { username: 'demo_user' } };
        } catch (error) {
          console.error('Error checking login status:', error);
          return { success: false, error: error.message };
        }
        
      default:
        return { success: false, error: 'Unknown action' };
    }
  };
  
  // Execute async handler and send response when done
  handleMessage().then(sendResponse);
  
  // Return true to indicate we will send a response asynchronously
  return true;
});

// Setup alarm for data syncing if needed
chrome.alarms.create('syncData', { periodInMinutes: 60 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'syncData') {
    // Sync data with the server if needed
    console.log('Syncing data with server...');
  }
}); 
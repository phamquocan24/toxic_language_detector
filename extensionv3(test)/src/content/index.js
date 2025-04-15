/**
 * Content Script chính cho Toxic Language Detector Extension
 */
// Import modules trực tiếp sử dụng ES module
import detector from './detector.js';
import { registerMessageHandlers } from '../utils/messaging.js';
import { getSettings, saveSettings } from '../utils/storage.js';

// Biến lưu trữ handlers để clear khi unload
let messageHandlersRemover = null;

/**
 * Kiểm tra xem chrome extension API có khả dụng không
 * @returns {boolean} true nếu chrome API khả dụng
 */
function isChromeAPIAvailable() {
  return typeof chrome !== 'undefined' && 
         chrome.runtime && 
         chrome.runtime.onMessage && 
         typeof chrome.runtime.onMessage.addListener === 'function';
}

/**
 * Khởi tạo content script
 */
async function initialize() {
  try {
    console.log('Toxic Detector: Content script đã được khởi tạo');
    
    // Kiểm tra API có sẵn không
    if (isChromeAPIAvailable()) {
      console.log('Toxic Detector: Chrome API khả dụng, đăng ký message handlers');
      // Đăng ký lắng nghe message
      messageHandlersRemover = registerMessageHandlers({
        // Bật/tắt detector
        'toggleDetection': async (data) => {
          const settings = await getSettings();
          settings.enableDetection = data.enabled !== undefined ? data.enabled : !settings.enableDetection;
          
          await saveSettings(settings);
          
          if (settings.enableDetection) {
            detector.startDetection();
          } else {
            detector.stopDetection();
          }
          
          return { success: true, enabled: settings.enableDetection };
        },
        
        // Cập nhật cài đặt
        'updateSettings': async (data) => {
          const currentSettings = await getSettings();
          const newSettings = { ...currentSettings, ...data.settings };
          
          await saveSettings(newSettings);
          
          // Áp dụng cài đặt mới
          if (newSettings.enableDetection) {
            detector.startDetection();
          } else {
            detector.stopDetection();
          }
          
          return { success: true, settings: newSettings };
        },
        
        // Phân tích văn bản cụ thể
        'analyzeText': async (data) => {
          return await analyzeTextHandler(data);
        },
        
        // Lấy trạng thái detector
        'getDetectorStatus': async () => {
          const settings = await getSettings();
          return {
            enabled: settings.enableDetection,
            settings
          };
        }
      });
    } else {
      console.warn('Toxic Detector: Chrome API không khả dụng - chuyển sang chế độ tự xử lý');
      // Theo dõi các yêu cầu phân tích văn bản thông qua cơ chế thay thế
      // (Chế độ hạn chế - chỉ phát hiện trên trang, không có thông báo)
      setupDirectAnalysisHandler();
    }
    
    // Khởi tạo detector (vẫn hoạt động ngay cả khi không có message handlers)
    detector.init();
  } catch (error) {
    console.error('Toxic Detector: Lỗi khởi tạo content script', error);
  }
}

/**
 * Hàm xử lý phân tích văn bản
 */
async function analyzeTextHandler(data) {
  try {
    // Kiểm tra dữ liệu đầu vào
    if (!data || !data.text || !data.text.trim()) {
      return { 
        success: false, 
        error: 'Văn bản không được để trống' 
      };
    }
    
    // Phân tích văn bản
    const result = await detector.analyzeText(
      data.text, 
      data.platform || 'manual', 
      data.options || {}
    );
    
    // Định dạng kết quả
    if (result) {
      return {
        success: true,
        prediction: result.prediction || 'unknown',
        isToxic: result.isToxic || false,
        confidence: result.confidence || 0,
        score: result.score || 0,
        keywords: result.keywords || [],
        details: result.details || {}
      };
    } else {
      return { 
        success: false, 
        error: 'Không nhận được kết quả phân tích' 
      };
    }
  } catch (error) {
    console.error('Lỗi khi phân tích văn bản:', error);
    return { 
      success: false, 
      error: error.message || 'Lỗi phân tích văn bản' 
    };
  }
}

/**
 * Thiết lập cơ chế xử lý phân tích trực tiếp khi không có Chrome API
 */
function setupDirectAnalysisHandler() {
  // Tạo một biến global mà popup có thể truy cập
  window.toxicDetector = {
    analyzeText: async (text, platform, options) => {
      const data = { text, platform, options };
      return await analyzeTextHandler(data);
    },
    getSettings: getSettings,
    saveSettings: saveSettings
  };
  
  console.log('Toxic Detector: Đã thiết lập phân tích trực tiếp');
}

/**
 * Dọn dẹp khi content script bị unload
 */
function cleanup() {
  console.log('Toxic Detector: Content script đang dọn dẹp');
  
  // Hủy đăng ký message handlers
  if (messageHandlersRemover) {
    messageHandlersRemover();
  }
  
  // Dừng detector
  if (detector) {
    detector.stopDetection();
  }
  
  // Xóa biến global
  if (window.toxicDetector) {
    delete window.toxicDetector;
  }
}

// Thêm CSS cho content script
function injectStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .toxicity-offensive {
      position: relative;
    }
    
    .toxicity-hate {
      position: relative;
    }
    
    .toxicity-spam {
      position: relative;
    }
    
    .toxic-detector-marker {
      z-index: 9999;
    }
    
    .toxic-detector-tooltip {
      z-index: 10000;
    }
  `;
  
  document.head.appendChild(style);
}

// Khởi tạo khi trang đã sẵn sàng
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    injectStyles();
    initialize();
  });
} else {
  injectStyles();
  initialize();
}

// Dọn dẹp khi unload
window.addEventListener('unload', cleanup);

// Export để sử dụng trong các file khác nếu cần
export default {
  initialize,
  cleanup
}; 
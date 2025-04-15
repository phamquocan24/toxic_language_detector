/**
 * Tiện ích xử lý lưu trữ trong extension
 * Sử dụng ES modules exports
 */

/**
 * Lưu dữ liệu vào local storage
 * @param {string} key - Khóa lưu trữ
 * @param {any} data - Dữ liệu cần lưu
 * @returns {Promise} - Kết quả lưu trữ
 */
export function saveToStorage(key, data) {
  return new Promise((resolve, reject) => {
    const saveData = {};
    saveData[key] = data;
    
    chrome.storage.local.set(saveData, () => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve({ success: true });
      }
    });
  });
}

/**
 * Lấy dữ liệu từ local storage
 * @param {string} key - Khóa cần lấy
 * @returns {Promise<any>} - Dữ liệu đã lưu
 */
export function getFromStorage(key) {
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

/**
 * Xóa dữ liệu từ local storage
 * @param {Array|string} keys - Khóa hoặc danh sách khóa cần xóa
 * @returns {Promise} - Kết quả xóa
 */
export function removeFromStorage(keys) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.remove(keys, () => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve({ success: true });
      }
    });
  });
}

/**
 * Xóa toàn bộ dữ liệu trong local storage
 * @returns {Promise} - Kết quả xóa
 */
export function clearStorage() {
  return new Promise((resolve, reject) => {
    chrome.storage.local.clear(() => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve({ success: true });
      }
    });
  });
}

/**
 * Lưu cài đặt extension
 * @param {Object} settings - Cài đặt cần lưu
 * @returns {Promise} - Kết quả lưu trữ
 */
export function saveSettings(settings) {
  return saveToStorage('extension_settings', settings);
}

/**
 * Lấy cài đặt extension
 * @returns {Promise} - Cài đặt đã lưu
 */
export function getSettings() {
  return getFromStorage('extension_settings')
    .then(settings => settings || getDefaultSettings());
}

/**
 * Lấy cài đặt mặc định
 * @returns {Object} - Cài đặt mặc định
 */
export function getDefaultSettings() {
  return {
    enableDetection: true,
    enableHighlight: true,
    enableNotifications: true,
    toxicThreshold: 0.7,
    language: 'vi',
    platforms: {
      facebook: true,
      youtube: true,
      twitter: true
    },
    blockCategories: {
      offensive: true,
      hate: true,
      spam: false
    }
  };
}

/**
 * Lưu thống kê phát hiện
 * @param {Object} stats - Thống kê cần lưu
 * @returns {Promise} - Kết quả lưu trữ
 */
export function saveStats(stats) {
  return getFromStorage('detection_stats')
    .then(currentStats => {
      const defaultStats = {
        total: 0,
        clean: 0,
        offensive: 0,
        hate: 0,
        spam: 0,
        lastUpdate: null
      };
      
      const current = currentStats || defaultStats;
      
      // Cập nhật thống kê
      const updatedStats = {
        total: (current.total || 0) + (stats.total || 1),
        clean: (current.clean || 0) + (stats.clean || 0),
        offensive: (current.offensive || 0) + (stats.offensive || 0),
        hate: (current.hate || 0) + (stats.hate || 0),
        spam: (current.spam || 0) + (stats.spam || 0),
        lastUpdate: new Date().toISOString()
      };
      
      return saveToStorage('detection_stats', updatedStats);
    });
}

/**
 * Lấy thống kê phát hiện
 * @returns {Promise} - Thống kê đã lưu
 */
export function getStats() {
  return getFromStorage('detection_stats')
    .then(stats => stats || {
      total: 0,
      clean: 0,
      offensive: 0,
      hate: 0,
      spam: 0,
      lastUpdate: null
    });
}

/**
 * Lấy token xác thực từ storage
 * @returns {Promise<string|null>} Token hoặc null
 */
export function getAuthToken() {
  return getFromStorage('authToken')
    .then(token => token || null);
} 
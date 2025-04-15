/**
 * Cấu hình API endpoints cho Toxic Language Detector Extension
 */

export const API_CONFIG = {
  // Server chính - localhost
  BASE_URL: 'http://localhost:7860',
  
  // Server dự phòng khi localhost không hoạt động
  BACKUP_URLS: [
    'https://toxicdetector.azurewebsites.net', // Thay bằng server thực tế của bạn
    'https://toxicapi.herokuapp.com'            // Thay bằng server thực tế của bạn
  ],
  
  AUTH_ENDPOINTS: {
    LOGIN: '/auth/token',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/reset-password-request',
    RESET_PASSWORD: '/auth/reset-password',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    EXTENSION_AUTH: '/auth/extension-auth'
  },
  EXTENSION_ENDPOINTS: {
    DETECT: '/extension/detect',
    BATCH_DETECT: '/batch/detect',
    STATS: '/extension/stats',
    SETTINGS: '/extension/settings',
    UPDATE_SETTINGS: '/extension/settings'
  },
  TOXIC_ENDPOINTS: {
    SIMILAR: '/toxic/similar',
    STATISTICS: '/toxic/statistics',
    TREND: '/toxic/trend',
    TOXIC_KEYWORDS: '/toxic/toxic-keywords'
  },
  PREDICT_ENDPOINTS: {
    SINGLE: '/predict/single',
    BATCH: '/predict/batch',
    ANALYZE_TEXT: '/predict/analyze-text'
  },
  HEALTH_ENDPOINT: '/health'
};

// URL API hiện đang sử dụng
let currentApiUrl = API_CONFIG.BASE_URL;

/**
 * Kiểm tra kết nối tới API endpoint
 * @param {string} url - URL API cần kiểm tra
 * @returns {Promise<boolean>} - Kết quả kiểm tra
 */
export async function checkApiConnection(url) {
  try {
    const response = await fetch(`${url}${API_CONFIG.HEALTH_ENDPOINT}`, {
      method: 'GET',
      timeout: 3000 // 3 giây timeout
    });
    return response.ok;
  } catch (error) {
    console.error(`Không thể kết nối tới server ${url}:`, error);
    return false;
  }
}

/**
 * Tìm server API khả dụng
 * @returns {Promise<string>} - URL API khả dụng
 */
export async function findAvailableApiServer() {
  // Kiểm tra server chính
  if (await checkApiConnection(API_CONFIG.BASE_URL)) {
    currentApiUrl = API_CONFIG.BASE_URL;
    return currentApiUrl;
  }
  
  // Thử các server dự phòng
  for (const backupUrl of API_CONFIG.BACKUP_URLS) {
    if (await checkApiConnection(backupUrl)) {
      currentApiUrl = backupUrl;
      return currentApiUrl;
    }
  }
  
  // Nếu không có server nào khả dụng, vẫn giữ server hiện tại
  return currentApiUrl;
}

/**
 * Lấy URL server API hiện tại
 * @returns {string} - URL API hiện tại
 */
export function getCurrentApiUrl() {
  return currentApiUrl;
}

/**
 * Xây dựng URL đầy đủ cho endpoint
 * @param {string} endpoint - Endpoint API
 * @returns {string} - URL API đầy đủ
 */
export function buildApiUrl(endpoint) {
  return `${currentApiUrl}${endpoint}`;
}

export const WEB_DASHBOARD = `${currentApiUrl}/dashboard`;

// Fallback dashboard URL in case the API is not available
export const FALLBACK_DASHBOARD = 'https://fallback-dashboard.toxicdetector.demo';

export default API_CONFIG; 
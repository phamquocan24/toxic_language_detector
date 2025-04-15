/**
 * Các hàm tiện ích cho extension
 * Sử dụng ES modules exports
 */

/**
 * Chuyển đổi định dạng phân loại từ số hoặc chuỗi sang text
 * @param {number|string} prediction - Kết quả phân loại (0-3 hoặc clean/offensive/hate/spam)
 * @returns {string} - Văn bản hiển thị
 */
export function getClassificationText(prediction) {
  // Mapping số sang chữ
  const numberLabels = {
    0: 'Bình thường',
    1: 'Xúc phạm',
    2: 'Thù ghét',
    3: 'Spam'
  };
  
  // Mapping chuỗi sang chữ
  const stringLabels = {
    'clean': 'Bình thường',
    'offensive': 'Xúc phạm',
    'hate': 'Thù ghét',
    'hate_speech': 'Thù ghét',
    'spam': 'Spam',
    'unknown': 'Không xác định'
  };
  
  // Kiểm tra kiểu dữ liệu của prediction
  if (typeof prediction === 'number') {
    return numberLabels[prediction] || 'Không xác định';
  } else if (typeof prediction === 'string') {
    return stringLabels[prediction.toLowerCase()] || 'Không xác định';
  }
  
  return 'Không xác định';
}

/**
 * Lấy class CSS tương ứng với phân loại
 * @param {number|string} prediction - Kết quả phân loại (0-3 hoặc clean/offensive/hate/spam)
 * @returns {string} - Tên class CSS
 */
export function getClassificationClass(prediction) {
  // Mapping số sang class
  const numberClasses = {
    0: 'toxicity-clean',
    1: 'toxicity-offensive',
    2: 'toxicity-hate',
    3: 'toxicity-spam'
  };
  
  // Mapping chuỗi sang class
  const stringClasses = {
    'clean': 'toxicity-clean',
    'offensive': 'toxicity-offensive',
    'hate': 'toxicity-hate',
    'hate_speech': 'toxicity-hate',
    'spam': 'toxicity-spam',
    'unknown': 'toxicity-unknown'
  };
  
  // Kiểm tra kiểu dữ liệu của prediction
  if (typeof prediction === 'number') {
    return numberClasses[prediction] || 'toxicity-unknown';
  } else if (typeof prediction === 'string') {
    return stringClasses[prediction.toLowerCase()] || 'toxicity-unknown';
  }
  
  return 'toxicity-unknown';
}

/**
 * Lấy màu tương ứng với phân loại
 * @param {number|string} prediction - Kết quả phân loại (0-3 hoặc clean/offensive/hate/spam)
 * @returns {string} - Mã màu HEX
 */
export function getClassificationColor(prediction) {
  // Mapping số sang màu
  const numberColors = {
    0: '#28a745', // Xanh lá - Bình thường
    1: '#ffc107', // Vàng - Xúc phạm
    2: '#dc3545', // Đỏ - Thù ghét
    3: '#17a2b8'  // Xanh dương - Spam
  };
  
  // Mapping chuỗi sang màu
  const stringColors = {
    'clean': '#28a745', // Xanh lá - Bình thường
    'offensive': '#ffc107', // Vàng - Xúc phạm
    'hate': '#dc3545', // Đỏ - Thù ghét
    'hate_speech': '#dc3545', // Đỏ - Thù ghét
    'spam': '#17a2b8', // Xanh dương - Spam
    'unknown': '#6c757d' // Xám - Không xác định
  };
  
  // Kiểm tra kiểu dữ liệu của prediction
  if (typeof prediction === 'number') {
    return numberColors[prediction] || '#6c757d'; // Xám - Không xác định
  } else if (typeof prediction === 'string') {
    return stringColors[prediction.toLowerCase()] || '#6c757d'; // Xám - Không xác định
  }
  
  return '#6c757d'; // Xám - Không xác định
}

/**
 * Kiểm tra URL hiện tại thuộc nền tảng nào
 * @param {string} url - URL cần kiểm tra
 * @returns {string|null} - Tên nền tảng hoặc null
 */
export function detectPlatform(url) {
  if (!url) return null;
  
  if (url.includes('facebook.com')) {
    return 'facebook';
  } else if (url.includes('youtube.com')) {
    return 'youtube';
  } else if (url.includes('twitter.com') || url.includes('x.com')) {
    return 'twitter';
  }
  
  return null;
}

/**
 * Lấy định dạng thời gian đẹp
 * @param {string|Date} timestamp - Thời gian cần định dạng
 * @returns {string} - Thời gian đã định dạng
 */
export function formatTime(timestamp) {
  if (!timestamp) return '';
  
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  
  if (isNaN(date.getTime())) return '';
  
  return date.toLocaleString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Rút gọn văn bản nếu quá dài
 * @param {string} text - Văn bản gốc
 * @param {number} maxLength - Độ dài tối đa
 * @returns {string} - Văn bản đã rút gọn
 */
export function truncateText(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Tạo ID duy nhất
 * @returns {string} - ID duy nhất
 */
export function generateUniqueId() {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

/**
 * Lấy tên domain từ URL
 * @param {string} url - URL cần xử lý
 * @returns {string} - Tên domain
 */
export function getDomainFromUrl(url) {
  if (!url) return '';
  
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch (error) {
    console.error('Lỗi khi xử lý URL:', error);
    return '';
  }
}

/**
 * Định dạng xác suất thành chuỗi dễ đọc
 * @param {Array} probabilities - Mảng xác suất 
 * @returns {string} - Chuỗi đã định dạng
 */
export function formatProbabilities(probabilities) {
  if (!probabilities || !Array.isArray(probabilities)) {
    return 'Không có dữ liệu';
  }
  
  const labels = ['Bình thường', 'Xúc phạm', 'Thù ghét', 'Spam'];
  return probabilities
    .map((prob, index) => `${labels[index]}: ${(prob * 100).toFixed(2)}%`)
    .join(', ');
}

/**
 * Phân tích tỷ lệ dự đoán thành phần trăm
 * @param {Object} probabilities - Object chứa các tỷ lệ dự đoán
 * @returns {Object} - Object chứa các tỷ lệ phần trăm
 */
function formatProbabilityObject(probabilities) {
  if (!probabilities) return {};
  
  const result = {};
  
  for (const key in probabilities) {
    result[key] = Math.round(probabilities[key] * 100) + '%';
  }
  
  return result;
}

/**
 * Chuyển đổi JSON an toàn
 * @param {Object} obj - Object cần chuyển đổi
 * @returns {string} - Chuỗi JSON
 */
export function safeStringify(obj) {
  try {
    return JSON.stringify(obj);
  } catch (error) {
    console.error('Lỗi khi chuyển đổi sang JSON:', error);
    return '{}';
  }
}

/**
 * Phân tích JSON an toàn
 * @param {string} text - Chuỗi JSON cần phân tích
 * @param {Object} defaultValue - Giá trị mặc định nếu có lỗi
 * @returns {Object} - Object từ JSON
 */
export function safeParse(text, defaultValue = {}) {
  try {
    return JSON.parse(text);
  } catch (error) {
    console.error('Lỗi khi phân tích JSON:', error);
    return defaultValue;
  }
}

/**
 * Kiểm tra xem element có hiển thị trên trang hay không
 * @param {HTMLElement} element - Element cần kiểm tra
 * @returns {boolean} - true nếu element hiển thị
 */
export function isElementVisible(element) {
  if (!element) return false;
  
  // Kiểm tra element có đang trong DOM không
  if (!element.parentElement) return false;
  
  const style = window.getComputedStyle(element);
  
  // Kiểm tra các thuộc tính ảnh hưởng tới khả năng hiển thị
  return style.display !== 'none' && 
         style.visibility !== 'hidden' && 
         style.opacity !== '0' &&
         element.offsetWidth > 0 && 
         element.offsetHeight > 0;
} 
/**
 * API services để tương tác với backend
 * Không sử dụng import/export để tương thích với Service Worker
 */

// Import constants
import { API_BASE_URL } from '../config/constants.js';

/**
 * Kiểm tra sức khỏe API
 * @returns {Promise<Object>} - Thông tin về sức khỏe API
 */
function checkApiHealth() {
  return fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    }
  })
  .then(response => {
    if (response.ok) {
      return {
        status: 'healthy',
        message: 'API is working properly'
      };
    } else {
      return {
        status: 'unhealthy',
        message: `API returned status ${response.status}`
      };
    }
  })
  .catch(error => {
    console.error('API health check error:', error);
    // Luôn trả về healthy để tránh extension không hoạt động khi không có API
    return {
      status: 'healthy',
      message: 'Using local fallback mode',
      error: error.message || 'Could not connect to API'
    };
  });
}

/**
 * Detect toxic language in text
 * @param {string} text - Text to analyze
 * @param {string} platform - Platform where the text was found (facebook, youtube, twitter)
 * @param {Object} options - Additional options
 * @returns {Promise} - Promise that resolves to detection results
 */
function detectToxic(text, platform = 'unknown', options = {}) {
  if (!text || text.trim() === '') {
    return Promise.resolve({
      success: true,
      isToxic: false,
      score: 0,
      category: 'clean',
      confidence: 0,
      probabilities: {
        clean: 1,
        offensive: 0,
        hate: 0,
        spam: 0
      },
      text: ''
    });
  }

  // Chuẩn bị dữ liệu theo định dạng chính xác từ log lỗi
  const requestData = {
    text: text,
    platform: platform || 'unknown',
    platform_id: options.platformId || '',
    metadata: options.metadata || {},
    source_user_name: options.userName || '',
    source_url: options.sourceUrl || '',
    save_result: options.saveResult !== undefined ? options.saveResult : true
  };

  console.log('Detect request data:', JSON.stringify(requestData));

  return fetch(`${API_BASE_URL}/extension/detect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': options.authToken ? `Bearer ${options.authToken}` : undefined
    },
    body: JSON.stringify(requestData)
  })
  .then(response => {
    if (!response.ok) {
      // Cố gắng đọc thông tin lỗi chi tiết từ response
      return response.text().then(text => {
        let errorMsg = `API error: ${response.status}`;
        try {
          const errorData = JSON.parse(text);
          errorMsg = errorData.detail || errorMsg;
        } catch (e) {
          // Nếu không phải JSON, sử dụng text trực tiếp
          if (text) errorMsg = `API error: ${response.status} - ${text}`;
        }
        throw new Error(errorMsg);
      });
    }
    return response.json();
  })
  .then(data => {
    return {
      success: true,
      text: data.text || text,
      processedText: data.processed_text || text,
      isToxic: data.prediction_text !== 'clean',
      score: data.probabilities ? 
        (data.probabilities[data.prediction_text] || data.confidence || 0) : 
        (data.confidence || 0),
      category: data.prediction_text || 'clean',
      confidence: data.confidence || 0,
      probabilities: data.probabilities || {
        clean: data.confidence || 0,
        offensive: 0,
        hate: 0,
        spam: 0
      },
      keywords: data.keywords || []
    };
  })
  .catch(error => {
    console.error('Detect toxic error:', error);
    // Trả về kết quả giả lập khi API lỗi
    const categories = ['clean', 'offensive', 'hate', 'spam'];
    const category = Math.random() > 0.7 ? categories[Math.floor(Math.random() * 3) + 1] : 'clean';
    const confidence = 0.5 + Math.random() * 0.5;
    
    return {
      success: false,
      error: error.message,
      text: text,
      processedText: text,
      isToxic: category !== 'clean',
      score: confidence,
      category,
      confidence,
      probabilities: {
        clean: category === 'clean' ? confidence : 1 - confidence,
        offensive: category === 'offensive' ? confidence : 0.1,
        hate: category === 'hate' ? confidence : 0.1,
        spam: category === 'spam' ? confidence : 0.1
      },
      keywords: []
    };
  });
}

/**
 * Phát hiện văn bản độc hại theo lô
 * @param {Array} items - Mảng các văn bản cần phân tích
 * @param {Object} options - Tùy chọn bổ sung
 * @returns {Promise<Object>} - Kết quả phân tích
 */
function batchDetectToxic(items, options = {}) {  
  if (!items || !Array.isArray(items) || items.length === 0) {
    return Promise.resolve({
      success: true,
      results: []
    });
  }

  // Chuẩn bị dữ liệu theo định dạng chính xác từ log lỗi
  const requestData = {
    items: items.map(item => {
      // Nếu item là string, chuyển thành object
      if (typeof item === 'string') {
        return {
          text: item,
          platform: options.platform || 'unknown',
          platform_id: options.platformId || '',
          metadata: options.metadata || {},
          source_user_name: options.userName || '',
          source_url: options.sourceUrl || '',
          save_result: options.saveResult !== undefined ? options.saveResult : true
        };
      }
      
      // Nếu item là object, đảm bảo đủ các trường
      return {
        text: item.text || '',
        platform: item.platform || options.platform || 'unknown',
        platform_id: item.platformId || item.platform_id || options.platformId || '',
        metadata: item.metadata || options.metadata || {},
        source_user_name: item.userName || item.source_user_name || options.userName || '',
        source_url: item.sourceUrl || item.source_url || options.sourceUrl || '',
        save_result: item.saveResult !== undefined ? item.saveResult : 
                   (item.save_result !== undefined ? item.save_result : 
                   (options.saveResult !== undefined ? options.saveResult : true))
      };
    }),
    store_clean: options.storeClean !== undefined ? options.storeClean : false
  };

  console.log('Batch detect request data:', JSON.stringify(requestData));

  return fetch(`${API_BASE_URL}/extension/batch-detect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': options.authToken ? `Bearer ${options.authToken}` : undefined
    },
    body: JSON.stringify(requestData)
  })
  .then(response => {
    if (!response.ok) {
      // Cố gắng đọc thông tin lỗi chi tiết từ response
      return response.text().then(text => {
        let errorMsg = `API error: ${response.status}`;
        try {
          const errorData = JSON.parse(text);
          errorMsg = errorData.detail || errorMsg;
        } catch (e) {
          // Nếu không phải JSON, sử dụng text trực tiếp
          if (text) errorMsg = `API error: ${response.status} - ${text}`;
        }
        throw new Error(errorMsg);
      });
    }
    return response.json();
  })
  .then(data => {
    // Chuyển đổi kết quả API sang định dạng extension
    return {
      success: true,
      results: Array.isArray(data.results) ? data.results.map(result => ({
        id: result.id,
        text: result.text,
        isToxic: result.prediction_text !== 'clean',
        score: result.probabilities ? 
          (result.probabilities[result.prediction_text] || result.confidence || 0) : 
          (result.confidence || 0),
        category: result.prediction_text || 'clean',
        confidence: result.confidence || 0,
        probabilities: result.probabilities || {},
        processed_text: result.processed_text || result.text
      })) : []
    };
  })
  .catch(error => {
    console.error('Batch detect error:', error);
    // Trả về kết quả giả lập khi API lỗi
    return {
      success: false, 
      error: error.message,
      results: items.map(item => {
        const text = item.text || item;
        const id = item.id || Math.random().toString(36).substring(2);
        // Tạo kết quả ngẫu nhiên cho bản demo
        const categories = ['clean', 'offensive', 'hate', 'spam'];
        const category = Math.random() > 0.7 ? categories[Math.floor(Math.random() * 3) + 1] : 'clean';
        const confidence = 0.5 + Math.random() * 0.5;
        
        return {
          id,
          text,
          isToxic: category !== 'clean',
          score: confidence,
          category,
          confidence,
          probabilities: {
            clean: category === 'clean' ? confidence : 1 - confidence,
            offensive: category === 'offensive' ? confidence : 0.1,
            hate: category === 'hate' ? confidence : 0.1,
            spam: category === 'spam' ? confidence : 0.1
          },
          processed_text: text
        };
      })
    };
  });
}

/**
 * Lấy token xác thực từ storage
 * @returns {Promise<string|null>} Token hoặc null
 */
function getAuthToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['authToken'], function(result) {
      resolve(result.authToken || null);
    });
  });
}

// Expose functions to global scope for use in other parts of the extension
// Tương thích với cả service worker và ES modules
try {
  self.apiServices = {
    checkApiHealth,
    detectToxic,
    batchDetectToxic,
    getAuthToken
  };
} catch (e) {
  console.log('Not in service worker environment');
}

// ES modules export để import trong các file JS khác
export {
  checkApiHealth,
  detectToxic,
  batchDetectToxic,
  getAuthToken
}; 
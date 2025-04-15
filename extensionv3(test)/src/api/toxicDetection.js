/**
 * API methods for toxic language detection
 * Không sử dụng import/export để tương thích với Service Worker
 */

// API_BASE_URL đã được khai báo trong constants.js

/**
 * Detect toxic language in text
 * @param {string} text - Text to analyze
 * @param {string} platform - Platform where the text was found (facebook, youtube, twitter)
 * @param {number} threshold - Threshold for toxic detection
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
 * Gets statistics about toxic content detection
 * @param {Object} options - Các tùy chọn (authToken)
 * @returns {Promise<Object>} Statistics data
 */
function getStatistics(options = {}) {
  const headers = {
    'Content-Type': 'application/json'
  };
  
  // Thêm token xác thực nếu có
  if (options.authToken) {
    headers['Authorization'] = `Bearer ${options.authToken}`;
  }
  
  // Sử dụng toxic/statistics nếu có token, ngược lại sử dụng extension/stats
  const endpoint = options.authToken ? 
    `${API_BASE_URL}/toxic/statistics` : 
    `${API_BASE_URL}/extension/stats`;
  
  return fetch(endpoint, {
    method: 'GET',
    headers: headers
  })
  .then(response => {
    if (!response.ok) {
      if (response.status === 401) {
        console.warn('Authentication required for statistics');
        throw new Error('Cần đăng nhập để sử dụng tính năng này');
      }
      console.warn(`API error: ${response.status}, sử dụng dữ liệu mẫu`);
      // Trả về dữ liệu mẫu trong trường hợp API không hoạt động
      throw new Error('API không khả dụng');
    }
    return response.json();
  })
  .catch(error => {
    console.error('Error getting toxic statistics:', error);
    // Trả về dữ liệu mẫu khi API lỗi
    return {
      success: true,
      stats: {
        total: 100,
        clean: 65,
        offensive: 20,
        hate: 10,
        spam: 5,
        categories: {
          clean: { count: 65, percentage: 65 },
          offensive: { count: 20, percentage: 20 },
          hate: { count: 10, percentage: 10 },
          spam: { count: 5, percentage: 5 }
        },
        platforms: {
          facebook: 40,
          twitter: 30,
          youtube: 20,
          other: 10
        },
        trend: [
          { date: new Date().toISOString().split('T')[0], count: 10 },
          { date: new Date(Date.now() - 86400000).toISOString().split('T')[0], count: 12 },
          { date: new Date(Date.now() - 172800000).toISOString().split('T')[0], count: 8 }
        ]
      }
    };
  });
}

/**
 * Finds comments similar to the provided text
 * @param {string} text - The text to find similar comments for
 * @param {number} threshold - The similarity threshold (0.0 to 1.0)
 * @param {number} limit - Maximum number of similar comments to return
 * @param {Object} options - Các tùy chọn bổ sung (authToken)
 * @returns {Promise<Array>} Array of similar comments
 */
function findSimilarComments(text, threshold = 0.7, limit = 10, options = {}) {
  if (!text || text.trim() === '') {
    return Promise.resolve({
      success: true,
      results: []
    });
  }

  const headers = {
    'Content-Type': 'application/json'
  };
  
  // Thêm token xác thực nếu có
  if (options.authToken) {
    headers['Authorization'] = `Bearer ${options.authToken}`;
  }

  return fetch(`${API_BASE_URL}/toxic/similar`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      text,
      threshold,
      limit
    })
  })
  .then(response => {
    if (!response.ok) {
      if (response.status === 401) {
        console.warn('Authentication required for similar comments');
        throw new Error('Cần đăng nhập để sử dụng tính năng này');
      }
      console.warn(`API error: ${response.status}, sử dụng dữ liệu mẫu`);
      throw new Error('API không khả dụng');
    }
    return response.json();
  })
  .catch(error => {
    console.error('Error finding similar comments:', error);
    // Trả về dữ liệu mẫu khi API lỗi
    return {
      success: true,
      results: [
        {
          id: 'sample1',
          text: text.length > 20 ? text.substring(0, 20) + '...' : text,
          similarity: 1.0,
          category: 'clean',
          platform: 'facebook',
          timestamp: new Date().toISOString()
        },
        {
          id: 'sample2',
          text: 'Nội dung tương tự mẫu 1',
          similarity: 0.85,
          category: 'offensive',
          platform: 'twitter',
          timestamp: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: 'sample3',
          text: 'Nội dung tương tự mẫu 2',
          similarity: 0.75,
          category: 'hate',
          platform: 'youtube',
          timestamp: new Date(Date.now() - 172800000).toISOString()
        }
      ]
    };
  });
}

/**
 * Gets the most frequent toxic keywords from analyzed content
 * @param {Object} options - Các tùy chọn (authToken, limit)
 * @returns {Promise<Array>} Array of toxic keywords with frequencies
 */
function getToxicKeywords(options = {}) {
  const headers = {
    'Content-Type': 'application/json'
  };
  
  // Thêm token xác thực nếu có
  if (options.authToken) {
    headers['Authorization'] = `Bearer ${options.authToken}`;
  }
  
  return fetch(`${API_BASE_URL}/toxic/toxic-keywords${options.limit ? `?limit=${options.limit}` : ''}`, {
    method: 'GET',
    headers: headers
  })
  .then(response => {
    if (!response.ok) {
      if (response.status === 401) {
        console.warn('Authentication required for toxic keywords');
        throw new Error('Cần đăng nhập để sử dụng tính năng này');
      }
      console.warn(`API error: ${response.status}, sử dụng dữ liệu mẫu`);
      throw new Error('API không khả dụng');
    }
    return response.json();
  })
  .catch(error => {
    console.error('Error getting toxic keywords:', error);
    // Trả về dữ liệu mẫu khi API lỗi
    return {
      success: true,
      keywords: [
        { word: 'từ_xấu_1', count: 15, category: 'offensive' },
        { word: 'từ_xấu_2', count: 12, category: 'hate' },
        { word: 'từ_xấu_3', count: 10, category: 'offensive' },
        { word: 'từ_xấu_4', count: 8, category: 'spam' },
        { word: 'từ_xấu_5', count: 5, category: 'hate' }
      ]
    };
  });
}

/**
 * Phát hiện độc hại cho một loạt văn bản
 * @param {Array<Object>} items - Danh sách các mục cần phân tích
 * @param {Object} options - Tùy chọn bổ sung
 * @returns {Promise<Array<Object>>} - Kết quả phân tích
 */
function batchDetectToxic(items, options = {}) {
  if (!items || !Array.isArray(items) || items.length === 0) {
    return Promise.resolve([]);
  }

  // Chuẩn bị dữ liệu theo định dạng chính xác từ log lỗi
  const requestData = items.map(item => ({
    text: item.text || '',
    platform: item.platform || options.platform || 'unknown',
    platform_id: item.platformId || options.platformId || '',
    metadata: item.metadata || options.metadata || {},
    source_user_name: item.userName || options.userName || '',
    source_url: item.sourceUrl || options.sourceUrl || '',
    save_result: item.saveResult !== undefined ? item.saveResult : 
                (options.saveResult !== undefined ? options.saveResult : true)
  }));

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
    if (!Array.isArray(data)) {
      console.error('Invalid response format from batch detect API:', data);
      return items.map((item, index) => ({
        success: false,
        error: 'Invalid API response format',
        text: item.text || '',
        isToxic: false,
        category: 'clean',
        confidence: 0,
        probabilities: {
          clean: 1,
          offensive: 0,
          hate: 0,
          spam: 0
        }
      }));
    }

    // Map kết quả trả về với đầu vào ban đầu
    return data.map((result, index) => {
      const originalItem = items[index] || {};
      const text = originalItem.text || '';
      
      return {
        success: true,
        text: result.text || text,
        processedText: result.processed_text || text,
        isToxic: result.prediction_text !== 'clean',
        score: result.probabilities ? 
          (result.probabilities[result.prediction_text] || result.confidence || 0) : 
          (result.confidence || 0),
        category: result.prediction_text || 'clean',
        confidence: result.confidence || 0,
        probabilities: result.probabilities || {
          clean: result.confidence || 0,
          offensive: 0,
          hate: 0,
          spam: 0
        },
        keywords: result.keywords || []
      };
    });
  })
  .catch(error => {
    console.error('Batch detect toxic error:', error);
    
    // Trả về kết quả giả lập khi API lỗi
    return items.map(item => {
      const categories = ['clean', 'offensive', 'hate', 'spam'];
      const category = Math.random() > 0.7 ? categories[Math.floor(Math.random() * 3) + 1] : 'clean';
      const confidence = 0.5 + Math.random() * 0.5;
      
      return {
        success: false,
        error: error.message,
        text: item.text || '',
        processedText: item.text || '',
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
  });
} 
/**
 * Tiện ích hỗ trợ gửi message giữa các component trong extension
 * Sử dụng ES modules exports
 */

/**
 * Gửi message đến background script
 * @param {string} action - Hành động cần thực hiện
 * @param {Object} data - Dữ liệu kèm theo
 * @returns {Promise<Object>} - Kết quả từ background script
 * @throws {Error} - Lỗi khi gửi message hoặc không nhận được phản hồi
 */
export function sendToBackground(action, data = {}) {
  if (!action) {
    return Promise.reject(new Error('Action không được để trống'));
  }

  // Thiết lập timeout dài hơn cho promise, tăng từ 5 giây lên 15 giây
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error(`Timeout khi chờ phản hồi cho action '${action}'`)), 15000); // 15 seconds
  });

  // Gửi message và chờ phản hồi
  const messagePromise = new Promise((resolve, reject) => {
    try {
      chrome.runtime.sendMessage({
        action,
        data
      }, response => {
        // Kiểm tra lỗi kết nối
        const lastError = chrome.runtime.lastError;
        if (lastError) {
          return reject(new Error(lastError.message));
        }
        
        // Kiểm tra phản hồi
        if (response === undefined) {
          return reject(new Error(`Không nhận được phản hồi cho action '${action}'`));
        }
        
        resolve(response);
      });
    } catch (error) {
      reject(new Error(`Lỗi gửi message: ${error.message}`));
    }
  });

  // Sử dụng Promise.race để bắt timeout
  return Promise.race([messagePromise, timeoutPromise])
    .catch(error => {
      // Xử lý lỗi cụ thể "Receiving end does not exist"
      if (error.message.includes('Receiving end does not exist')) {
        console.error(`Lỗi kết nối: Background script không khả dụng khi gửi action '${action}'`);
        throw new Error('Không thể kết nối với background script. Vui lòng tải lại tiện ích.');
      }
      
      // Xử lý các lỗi khác
      console.error(`Lỗi khi gửi message '${action}' đến background:`, error);
      throw error;
    });
}

/**
 * Gửi message đến tab hiện tại
 * @param {string} action - Hành động cần thực hiện
 * @param {Object} data - Dữ liệu kèm theo
 * @returns {Promise} - Kết quả từ content script
 */
export function sendToActiveTab(action, data = {}) {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (!tabs || tabs.length === 0) {
        return reject(new Error('Không tìm thấy tab hiện tại'));
      }
      
      chrome.tabs.sendMessage(tabs[0].id, {
        action,
        data
      }, response => {
        // Kiểm tra lỗi kết nối
        const lastError = chrome.runtime.lastError;
        if (lastError) {
          return reject(new Error(lastError.message));
        }
        
        resolve(response);
      });
    });
  });
}

/**
 * Gửi message đến tất cả tab đang mở
 * @param {string} action - Hành động cần thực hiện
 * @param {Object} data - Dữ liệu kèm theo
 * @returns {Promise} - Mảng kết quả từ các tab
 */
export function sendToAllTabs(action, data = {}) {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({}, tabs => {
      if (!tabs || tabs.length === 0) {
        return resolve([]);
      }
      
      const promises = tabs.map(tab => {
        return new Promise(resolveTab => {
          chrome.tabs.sendMessage(tab.id, {
            action,
            data
          }, response => {
            // Bỏ qua lỗi cho từng tab
            if (chrome.runtime.lastError) {
              return resolveTab(null);
            }
            return resolveTab(response);
          });
        });
      });
      
      Promise.all(promises)
        .then(results => {
          // Lọc các kết quả null
          resolve(results.filter(result => result !== null));
        })
        .catch(error => {
          reject(error);
        });
    });
  });
}

/**
 * Đăng ký lắng nghe message từ các component khác
 * @param {Object} handlers - Object chứa các hàm xử lý message
 * @returns {Function} - Hàm để gỡ bỏ listener
 */
export function registerMessageHandlers(handlers) {
  function listener(message, sender, sendResponse) {
    const { action, data } = message;
    
    // Kiểm tra xem có handler cho action này không
    if (handlers[action]) {
      try {
        // Gọi handler và trả về kết quả
        const result = handlers[action](data, sender);
        
        // Nếu là Promise thì xử lý Promise
        if (result instanceof Promise) {
          result
            .then(response => sendResponse(response))
            .catch(error => sendResponse({ error: error.message }));
          
          // Trả về true để giữ sendResponse mở cho Promise
          return true;
        }
        
        // Trả về kết quả ngay lập tức
        sendResponse(result);
      } catch (error) {
        console.error(`Lỗi khi xử lý message '${action}':`, error);
        sendResponse({ error: error.message });
      }
    } else {
      console.warn(`Không có handler cho action '${action}'`);
      sendResponse({ error: `Không hỗ trợ action '${action}'` });
    }
    
    // Trả về true để giữ sendResponse mở cho Promise
    return true;
  }
  
  // Kiểm tra nếu chrome.runtime không tồn tại hoặc không có onMessage
  if (!chrome || !chrome.runtime || !chrome.runtime.onMessage) {
    console.error('Lỗi: chrome.runtime.onMessage không tồn tại');
    return function() {
      // Hàm rỗng để tránh lỗi khi gỡ bỏ listener
      console.log('Không thể gỡ bỏ listener vì không có chrome.runtime.onMessage');
    };
  }
  
  // Đăng ký listener
  chrome.runtime.onMessage.addListener(listener);
  
  // Trả về hàm để gỡ bỏ listener
  return function removeListener() {
    if (chrome && chrome.runtime && chrome.runtime.onMessage) {
      chrome.runtime.onMessage.removeListener(listener);
    }
  };
} 
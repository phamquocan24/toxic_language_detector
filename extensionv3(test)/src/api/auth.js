/**
 * API methods for authentication
 * Không sử dụng import/export để tương thích với Service Worker
 */

// API_BASE_URL đã được khai báo trong constants.js

/**
 * Login user with username and password
 * @param {string} username - User's username
 * @param {string} password - User's password
 * @returns {Promise} - Promise that resolves to user data and tokens
 */
function login(username, password) {
  // Tạo dữ liệu form thay vì JSON
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  return fetch(`${API_BASE_URL}/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString()
  })
  .then(response => {
    if (!response.ok) {
      if (response.status === 401 || response.status === 422) {
        return response.json().then(data => {
          throw new Error(data.detail || 'Tên đăng nhập hoặc mật khẩu không đúng');
        });
      }
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    // Lưu token vào storage
    chrome.storage.local.set({
      authToken: data.access_token,
      refreshToken: data.refresh_token,
      tokenExpiry: new Date().getTime() + (data.expires_in * 1000 || 86400000)
    });
    return data;
  })
  .catch(error => {
    console.error('Login error:', error);
    throw error;
  });
}

/**
 * Register a new user
 * @param {string} username - User's username
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @returns {Promise} - Promise that resolves to registration result
 */
function register(username, email, password) {
  return fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username,
      email,
      password
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  })
  .catch(error => {
    console.error('Registration error:', error);
    throw error;
  });
}

/**
 * Check if user is logged in
 * @returns {Promise<boolean>} - Promise that resolves to login status
 */
function isLoggedIn() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['authToken', 'tokenExpiry'], function(result) {
      const { authToken, tokenExpiry } = result;
      
      if (!authToken) {
        resolve(false);
        return;
      }
      
      // Kiểm tra xem token đã hết hạn chưa
      if (tokenExpiry && new Date().getTime() > tokenExpiry) {
        // Token đã hết hạn
        chrome.storage.local.remove(['authToken', 'refreshToken', 'tokenExpiry']);
        resolve(false);
        return;
      }
      
      resolve(true);
    });
  });
}

/**
 * Get current user information
 * @returns {Promise<Object>} - Promise that resolves to user information
 */
function getCurrentUser() {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get(['authToken'], function(result) {
      const { authToken } = result;
      
      if (!authToken) {
        reject(new Error('Not logged in'));
        return;
      }
      
      fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        }
      })
      .then(response => {
        if (response.status === 401) {
          // Token không hợp lệ hoặc hết hạn
          chrome.storage.local.remove(['authToken', 'refreshToken', 'tokenExpiry']);
          reject(new Error('Invalid or expired token'));
          return;
        }
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        return response.json();
      })
      .then(data => {
        resolve(data);
      })
      .catch(error => {
        console.error('Error getting current user:', error);
        reject(error);
      });
    });
  });
}

/**
 * Logout the current user
 * @returns {Promise} - Promise that resolves on successful logout
 */
function logout() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['refreshToken'], function(result) {
      const { refreshToken } = result;
      
      if (refreshToken) {
        // Gửi logout request tới server
        fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            refresh_token: refreshToken
          })
        })
        .catch(error => {
          console.error('Logout API error:', error);
        })
        .finally(() => {
          // Luôn xóa tokens khỏi storage
          chrome.storage.local.remove(['authToken', 'refreshToken', 'tokenExpiry']);
          resolve({ success: true });
        });
      } else {
        // Nếu không có refresh token, chỉ cần xóa dữ liệu local
        chrome.storage.local.remove(['authToken', 'refreshToken', 'tokenExpiry']);
        resolve({ success: true });
      }
    });
  });
}
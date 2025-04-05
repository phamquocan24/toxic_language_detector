/**
 * api.js - API client for the Toxic Language Detector
 * Handles all communication between the extension and the backend API
 */

class APIClient {
    /**
     * Create a new API client
     * @param {Object} options - Configuration options
     * @param {string} options.baseUrl - Base URL for the API
     * @param {string} options.apiKey - API key for authentication
     * @param {number} options.timeout - Request timeout in milliseconds
     */
    constructor(options = {}) {
      this.baseUrl = options.baseUrl || '';
      this.apiKey = options.apiKey || '';
      this.timeout = options.timeout || 10000; // 10 seconds default
      
      // Bind methods
      this.setBaseUrl = this.setBaseUrl.bind(this);
      this.setApiKey = this.setApiKey.bind(this);
      this.request = this.request.bind(this);
      this.analyzeText = this.analyzeText.bind(this);
      this.login = this.login.bind(this);
      this.register = this.register.bind(this);
      this.getStats = this.getStats.bind(this);
    }
  
    /**
     * Set the base URL for the API
     * @param {string} baseUrl - Base URL for the API
     */
    setBaseUrl(baseUrl) {
      this.baseUrl = baseUrl;
    }
  
    /**
     * Set the API key for authentication
     * @param {string} apiKey - API key
     */
    setApiKey(apiKey) {
      this.apiKey = apiKey;
    }
  
    /**
     * Make a request to the API
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} - API response
     */
    async request(endpoint, options = {}) {
      const url = `${this.baseUrl}${endpoint}`;
      
      // Default headers
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      };
      
      // Add API key if available
      if (this.apiKey) {
        headers['X-API-Key'] = this.apiKey;
      }
      
      // Add authorization header if token is provided
      if (options.token) {
        headers['Authorization'] = `Bearer ${options.token}`;
      }
      
      // Create request options
      const requestOptions = {
        method: options.method || 'GET',
        headers: headers,
        body: options.body ? JSON.stringify(options.body) : undefined
      };
      
      try {
        // Set up timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        requestOptions.signal = controller.signal;
        
        // Make the request
        const response = await fetch(url, requestOptions);
        
        // Clear timeout
        clearTimeout(timeoutId);
        
        // Handle non-JSON responses
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          
          // Handle error responses
          if (!response.ok) {
            throw {
              status: response.status,
              message: data.detail || 'Unknown error',
              data: data
            };
          }
          
          return data;
        } else {
          // Handle non-JSON response
          const text = await response.text();
          
          if (!response.ok) {
            throw {
              status: response.status,
              message: text || 'Unknown error',
              data: text
            };
          }
          
          return { text };
        }
      } catch (error) {
        // Handle aborted requests
        if (error.name === 'AbortError') {
          throw {
            status: 408,
            message: 'Request timeout',
            data: null
          };
        }
        
        // Re-throw API errors
        if (error.status) {
          throw error;
        }
        
        // Handle network errors
        throw {
          status: 0,
          message: 'Network error',
          data: error
        };
      }
    }
    
    /**
     * Analyze text for toxic language
     * @param {Object} params - Analysis parameters
     * @param {string} params.text - Text to analyze
     * @param {string} params.platform - Platform where the text was found
     * @param {string} params.platformId - ID of the comment on the platform
     * @param {Object} params.metadata - Additional metadata
     * @returns {Promise<Object>} - Analysis results
     */
    async analyzeText(params) {
      return this.request('/extension/detect', {
        method: 'POST',
        body: {
          text: params.text,
          platform: params.platform || 'unknown',
          platform_id: params.platformId || '',
          metadata: params.metadata || {}
        }
      });
    }
    
    /**
     * Login to the API
     * @param {Object} credentials - Login credentials
     * @param {string} credentials.username - Username
     * @param {string} credentials.password - Password
     * @returns {Promise<Object>} - Login response with token
     */
    async login(credentials) {
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      
      return this.request('/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });
    }
    
    /**
     * Register a new user
     * @param {Object} userData - User data
     * @param {string} userData.username - Username
     * @param {string} userData.email - Email
     * @param {string} userData.password - Password
     * @returns {Promise<Object>} - Registration response
     */
    async register(userData) {
      return this.request('/auth/register', {
        method: 'POST',
        body: {
          username: userData.username,
          email: userData.email,
          password: userData.password
        }
      });
    }
    
    /**
     * Get user statistics
     * @param {string} token - Authentication token
     * @param {Object} params - Query parameters
     * @param {string} params.timeRange - Time range for stats
     * @returns {Promise<Object>} - Statistics data
     */
    async getStats(token, params = {}) {
      const queryParams = new URLSearchParams();
      
      if (params.timeRange) {
        queryParams.append('time_range', params.timeRange);
      }
      
      if (params.platform) {
        queryParams.append('platform', params.platform);
      }
      
      const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
      
      return this.request(`/detect/statistics${queryString}`, {
        token: token
      });
    }
    
    /**
     * Get user history
     * @param {string} token - Authentication token
     * @param {Object} params - Query parameters
     * @param {number} params.skip - Number of items to skip
     * @param {number} params.limit - Maximum number of items to return
     * @returns {Promise<Object>} - History data
     */
    async getHistory(token, params = {}) {
      const queryParams = new URLSearchParams();
      
      if (params.skip) {
        queryParams.append('skip', params.skip.toString());
      }
      
      if (params.limit) {
        queryParams.append('limit', params.limit.toString());
      }
      
      if (params.platform) {
        queryParams.append('platform', params.platform);
      }
      
      if (params.prediction !== undefined) {
        queryParams.append('prediction', params.prediction.toString());
      }
      
      const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
      
      return this.request(`/user/history${queryString}`, {
        token: token
      });
    }
    
    /**
     * Get admin dashboard data
     * @param {string} token - Authentication token
     * @returns {Promise<Object>} - Dashboard data
     */
    async getAdminDashboard(token) {
      return this.request('/admin/dashboard', {
        token: token
      });
    }
    
    /**
     * Get system users (admin only)
     * @param {string} token - Authentication token
     * @param {Object} params - Query parameters
     * @param {number} params.skip - Number of items to skip
     * @param {number} params.limit - Maximum number of items to return
     * @returns {Promise<Object>} - Users data
     */
    async getUsers(token, params = {}) {
      const queryParams = new URLSearchParams();
      
      if (params.skip) {
        queryParams.append('skip', params.skip.toString());
      }
      
      if (params.limit) {
        queryParams.append('limit', params.limit.toString());
      }
      
      const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
      
      return this.request(`/admin/users${queryString}`, {
        token: token
      });
    }
    
    /**
     * Create a system report (admin only)
     * @param {string} token - Authentication token
     * @param {Object} reportParams - Report parameters
     * @returns {Promise<Object>} - Report data
     */
    async createReport(token, reportParams) {
      return this.request('/admin/reports', {
        method: 'POST',
        token: token,
        body: reportParams
      });
    }
  }
  
  // Create a singleton instance
  const api = new APIClient();
  
  // Export the instance
  export default api;
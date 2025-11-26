/**
 * API Client with Retry Logic and Error Handling
 * 
 * Features:
 * - Exponential backoff retry
 * - Network error handling
 * - Request timeout
 * - Automatic fallback
 */

class APIClient {
  constructor(config = {}) {
    this.baseURL = config.baseURL || "http://localhost:7860";
    this.maxRetries = config.maxRetries || 3;
    this.retryDelay = config.retryDelay || 1000; // 1 second
    this.timeout = config.timeout || 30000; // 30 seconds
    this.authToken = config.authToken || null;
  }

  /**
   * Sleep utility for delays
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Calculate exponential backoff delay
   */
  getBackoffDelay(attempt) {
    // Exponential backoff: 1s, 2s, 4s, 8s...
    const delay = this.retryDelay * Math.pow(2, attempt);
    // Add jitter (random 0-1000ms) to avoid thundering herd
    const jitter = Math.random() * 1000;
    return delay + jitter;
  }

  /**
   * Check if error is retryable
   */
  isRetryableError(error) {
    // Network errors
    if (error.name === 'NetworkError' || error.message.includes('NetworkError')) {
      return true;
    }
    
    // Timeout errors
    if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
      return true;
    }
    
    // HTTP 5xx errors (server errors)
    if (error.status >= 500 && error.status < 600) {
      return true;
    }
    
    // HTTP 429 (rate limit)
    if (error.status === 429) {
      return true;
    }
    
    // Connection refused
    if (error.message.includes('Failed to fetch')) {
      return true;
    }
    
    return false;
  }

  /**
   * Fetch with timeout
   */
  async fetchWithTimeout(url, options) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }

  /**
   * Make request with retry logic
   */
  async request(endpoint, options = {}, attempt = 0) {
    const url = `${this.baseURL}${endpoint}`;
    
    // Prepare headers
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    // Add auth token if available
    if (this.authToken) {
      headers['Authorization'] = `Basic ${this.authToken}`;
    }

    const fetchOptions = {
      ...options,
      headers
    };

    try {
      console.log(`[API] Request attempt ${attempt + 1}/${this.maxRetries + 1}: ${endpoint}`);
      
      const response = await this.fetchWithTimeout(url, fetchOptions);

      // Check if response is successful
      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        error.status = response.status;
        error.response = response;
        
        // Try to parse error body
        try {
          const errorData = await response.json();
          error.data = errorData;
          error.message = errorData.detail || error.message;
        } catch (e) {
          // Body is not JSON, ignore
        }
        
        throw error;
      }

      // Parse response
      const data = await response.json();
      console.log(`[API] Success: ${endpoint}`);
      return data;

    } catch (error) {
      console.error(`[API] Error attempt ${attempt + 1}: ${error.message}`);

      // Check if we should retry
      if (attempt < this.maxRetries && this.isRetryableError(error)) {
        const delay = this.getBackoffDelay(attempt);
        console.log(`[API] Retrying in ${Math.round(delay)}ms...`);
        
        // Wait before retrying
        await this.sleep(delay);
        
        // Retry
        return this.request(endpoint, options, attempt + 1);
      }

      // Max retries exceeded or non-retryable error
      console.error(`[API] Failed after ${attempt + 1} attempts: ${error.message}`);
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, {
      method: 'GET'
    });
  }

  /**
   * POST request
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }

  /**
   * Batch request with individual error handling
   */
  async batchRequest(endpoint, items, options = {}) {
    try {
      // Try batch request first
      return await this.post(endpoint, { items, ...options });
    } catch (error) {
      console.warn(`[API] Batch request failed: ${error.message}`);
      console.log(`[API] Falling back to individual requests...`);
      
      // Fallback: Process items individually
      const results = [];
      for (const item of items) {
        try {
          const result = await this.post(endpoint.replace('/batch-detect', '/detect'), item);
          results.push(result);
        } catch (itemError) {
          console.error(`[API] Individual item failed:`, itemError);
          // Return error result for this item
          results.push({
            text: item.text,
            error: itemError.message,
            prediction: 0,
            confidence: 0,
            prediction_text: "error"
          });
        }
      }
      
      return {
        results,
        count: results.length,
        fallback: true
      };
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await this.get('/health');
      return {
        status: 'healthy',
        data: response
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message
      };
    }
  }

  /**
   * Update configuration
   */
  updateConfig(config) {
    if (config.baseURL) this.baseURL = config.baseURL;
    if (config.maxRetries !== undefined) this.maxRetries = config.maxRetries;
    if (config.retryDelay !== undefined) this.retryDelay = config.retryDelay;
    if (config.timeout !== undefined) this.timeout = config.timeout;
    if (config.authToken) this.authToken = config.authToken;
  }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = APIClient;
}


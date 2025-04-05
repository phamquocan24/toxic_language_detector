/**
 * auth.js - Authentication module for the Toxic Language Detector
 * Handles user authentication, token management, and permissions
 */

import api from './api.js';
import storage from './storage.js';

class Auth {
  constructor() {
    // Initialize auth state
    this.currentUser = null;
    this.authToken = null;
    this.role = null;
    
    // Bind methods
    this.initialize = this.initialize.bind(this);
    this.login = this.login.bind(this);
    this.register = this.register.bind(this);
    this.logout = this.logout.bind(this);
    this.isAuthenticated = this.isAuthenticated.bind(this);
    this.isAdmin = this.isAdmin.bind(this);
    this.getToken = this.getToken.bind(this);
    this.getCurrentUser = this.getCurrentUser.bind(this);
    this.handleTokenExpiration = this.handleTokenExpiration.bind(this);
  }

  /**
   * Initialize authentication state from storage
   * @returns {Promise<boolean>} - Whether initialization was successful
   */
  async initialize() {
    try {
      // Get auth data from storage
      const authData = await storage.get('authData');
      
      if (!authData) {
        return false;
      }
      
      // Check if token is expired
      if (authData.expiresAt && authData.expiresAt < Date.now()) {
        console.log('Token expired, logging out');
        await this.logout();
        return false;
      }
      
      // Set auth state
      this.currentUser = authData.username;
      this.authToken = authData.token;
      this.role = authData.role;
      
      return true;
    } catch (error) {
      console.error('Error initializing authentication:', error);
      return false;
    }
  }

  /**
   * Login with username and password
   * @param {string} username - Username
   * @param {string} password - Password
   * @param {boolean} rememberMe - Whether to remember the login
   * @returns {Promise<Object>} - Login result
   */
  async login(username, password, rememberMe = false) {
    try {
      // Call login API
      const response = await api.login({ username, password });
      
      // Calculate token expiration
      const expiresAt = rememberMe ? null : Date.now() + (24 * 60 * 60 * 1000); // 24 hours
      
      // Store auth data
      const authData = {
        token: response.access_token,
        username: username,
        role: response.role,
        expiresAt: expiresAt
      };
      
      await storage.set('authData', authData);
      
      // Update auth state
      this.currentUser = username;
      this.authToken = response.access_token;
      this.role = response.role;
      
      return {
        success: true,
        user: username,
        role: response.role
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.message || 'Login failed'
      };
    }
  }

  /**
   * Register a new user
   * @param {string} username - Username
   * @param {string} email - Email
   * @param {string} password - Password
   * @returns {Promise<Object>} - Registration result
   */
  async register(username, email, password) {
    try {
      // Call register API
      const response = await api.register({ username, email, password });
      
      return {
        success: true,
        user: response
      };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        error: error.message || 'Registration failed'
      };
    }
  }

  /**
   * Logout the current user
   * @returns {Promise<void>}
   */
  async logout() {
    // Clear auth data from storage
    await storage.remove('authData');
    
    // Clear auth state
    this.currentUser = null;
    this.authToken = null;
    this.role = null;
  }

  /**
   * Check if a user is authenticated
   * @returns {boolean} - Whether the user is authenticated
   */
  isAuthenticated() {
    return !!this.authToken;
  }

  /**
   * Check if the current user is an admin
   * @returns {boolean} - Whether the user is an admin
   */
  isAdmin() {
    return this.role === 'admin';
  }

  /**
   * Get the current authentication token
   * @returns {string|null} - Authentication token
   */
  getToken() {
    return this.authToken;
  }

  /**
   * Get the current user
   * @returns {string|null} - Current username
   */
  getCurrentUser() {
    return this.currentUser;
  }

  /**
   * Handle token expiration
   * Called automatically when a token expires during a request
   * @returns {Promise<void>}
   */
  async handleTokenExpiration() {
    await this.logout();
    
    // Redirect to login page
    if (window.location.pathname !== '/pages/login/login.html') {
      window.location.href = '/pages/login/login.html?expired=true';
    }
  }
}

// Create a singleton instance
const auth = new Auth();

// Initialize auth on module load
auth.initialize().catch(error => {
  console.error('Error initializing auth:', error);
});

// Export the singleton instance
export default auth;
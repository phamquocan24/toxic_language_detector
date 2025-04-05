/**
 * storage.js - Storage module for the Toxic Language Detector
 * Handles persistent storage using Chrome's storage API and provides
 * a unified interface for storage operations
 */

class Storage {
    constructor() {
      // Determine which storage to use
      this.storage = chrome.storage.sync || chrome.storage.local;
      
      // Bind methods
      this.get = this.get.bind(this);
      this.set = this.set.bind(this);
      this.remove = this.remove.bind(this);
      this.clear = this.clear.bind(this);
      this.getMultiple = this.getMultiple.bind(this);
      this.setMultiple = this.setMultiple.bind(this);
    }
  
    /**
     * Get a value from storage
     * @param {string} key - Storage key
     * @param {any} defaultValue - Default value if key doesn't exist
     * @returns {Promise<any>} - Stored value or default
     */
    get(key, defaultValue = null) {
      return new Promise((resolve) => {
        this.storage.get(key, (result) => {
          const value = result[key];
          resolve(value === undefined ? defaultValue : value);
        });
      });
    }
  
    /**
     * Set a value in storage
     * @param {string} key - Storage key
     * @param {any} value - Value to store
     * @returns {Promise<void>}
     */
    set(key, value) {
      return new Promise((resolve) => {
        const data = {};
        data[key] = value;
        this.storage.set(data, resolve);
      });
    }
  
    /**
     * Remove a value from storage
     * @param {string} key - Storage key
     * @returns {Promise<void>}
     */
    remove(key) {
      return new Promise((resolve) => {
        this.storage.remove(key, resolve);
      });
    }
  
    /**
     * Clear all storage
     * @returns {Promise<void>}
     */
    clear() {
      return new Promise((resolve) => {
        this.storage.clear(resolve);
      });
    }
    
    /**
     * Get multiple values from storage
     * @param {string[]} keys - Storage keys
     * @returns {Promise<Object>} - Object with key-value pairs
     */
    getMultiple(keys) {
      return new Promise((resolve) => {
        this.storage.get(keys, resolve);
      });
    }
    
    /**
     * Set multiple values in storage
     * @param {Object} data - Object with key-value pairs
     * @returns {Promise<void>}
     */
    setMultiple(data) {
      return new Promise((resolve) => {
        this.storage.set(data, resolve);
      });
    }
    
    /**
     * Listen for changes to storage
     * @param {Function} callback - Callback function(changes, areaName)
     * @returns {void}
     */
    onChanged(callback) {
      chrome.storage.onChanged.addListener(callback);
    }
    
    /**
     * Check if a key exists in storage
     * @param {string} key - Storage key
     * @returns {Promise<boolean>} - Whether the key exists
     */
    async exists(key) {
      const value = await this.get(key);
      return value !== null;
    }
    
    /**
     * Get the size of storage in bytes
     * @returns {Promise<number>} - Size in bytes
     */
    async getSize() {
      return new Promise((resolve) => {
        chrome.storage.local.getBytesInUse(null, (bytes) => {
          resolve(bytes);
        });
      });
    }
    
    /**
     * Store an object with expiration
     * @param {string} key - Storage key
     * @param {any} value - Value to store
     * @param {number} ttl - Time to live in milliseconds
     * @returns {Promise<void>}
     */
    async setWithExpiration(key, value, ttl) {
      const item = {
        value: value,
        expiration: Date.now() + ttl
      };
      
      await this.set(key, item);
    }
    
    /**
     * Get a value with expiration check
     * @param {string} key - Storage key
     * @param {any} defaultValue - Default value if key doesn't exist or is expired
     * @returns {Promise<any>} - Stored value or default
     */
    async getWithExpiration(key, defaultValue = null) {
      const item = await this.get(key);
      
      if (!item) {
        return defaultValue;
      }
      
      if (item.expiration && item.expiration < Date.now()) {
        await this.remove(key);
        return defaultValue;
      }
      
      return item.value;
    }
    
    /**
     * Import data from JSON
     * @param {string} json - JSON string
     * @returns {Promise<void>}
     */
    async importFromJson(json) {
      try {
        const data = JSON.parse(json);
        await this.setMultiple(data);
        return { success: true };
      } catch (error) {
        console.error('Error importing from JSON:', error);
        return { success: false, error: error.message };
      }
    }
    
    /**
     * Export data to JSON
     * @param {string[]} keys - Keys to export (all if not specified)
     * @returns {Promise<string>} - JSON string
     */
    async exportToJson(keys = null) {
      try {
        const data = await (keys ? this.getMultiple(keys) : this.getMultiple(null));
        return JSON.stringify(data, null, 2);
      } catch (error) {
        console.error('Error exporting to JSON:', error);
        throw error;
      }
    }
  }
  
  // Create a singleton instance
  const storage = new Storage();
  
  // Export the instance
  export default storage;
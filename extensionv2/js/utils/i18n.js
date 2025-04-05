// js/utils/i18n.js

/**
 * Tiện ích quốc tế hóa cho extension
 */
const I18n = {
    /**
     * Lấy chuỗi dịch từ messages.json
     * @param {string} key - Khóa của chuỗi cần dịch
     * @param {Array} substitutions - Các giá trị thay thế (nếu có)
     * @returns {string} - Chuỗi đã được dịch
     */
    getMessage(key, substitutions = []) {
      return chrome.i18n.getMessage(key, substitutions);
    },
    
    /**
     * Cập nhật tất cả các phần tử có thuộc tính data-i18n
     */
    translatePage() {
      const elements = document.querySelectorAll('[data-i18n]');
      elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = this.getMessage(key);
      });
      
      // Xử lý các thuộc tính placeholder
      const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
      placeholders.forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        element.placeholder = this.getMessage(key);
      });
      
      // Xử lý các thuộc tính title
      const titles = document.querySelectorAll('[data-i18n-title]');
      titles.forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        element.title = this.getMessage(key);
      });
    }
  };
  
  // Tự động dịch trang khi DOM sẵn sàng
  document.addEventListener('DOMContentLoaded', () => {
    I18n.translatePage();
  });
  
  // Export để sử dụng trong các module khác
  export default I18n;
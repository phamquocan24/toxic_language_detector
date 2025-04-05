// utils/notifications.js

/**
 * Show a notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, info, warning)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Create notification container if it doesn't exist
    let notificationContainer = document.querySelector('.notification-container');
    if (!notificationContainer) {
      notificationContainer = document.createElement('div');
      notificationContainer.className = 'notification-container';
      document.body.appendChild(notificationContainer);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Add icon based on type
    let icon = '';
    switch (type) {
      case 'success':
        icon = '✅';
        break;
      case 'error':
        icon = '❌';
        break;
      case 'warning':
        icon = '⚠️';
        break;
      case 'info':
      default:
        icon = 'ℹ️';
        break;
    }
    
    // Create content
    notification.innerHTML = `
      <div class="notification-icon">${icon}</div>
      <div class="notification-message">${message}</div>
      <button class="notification-close">&times;</button>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Close button
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
      notification.classList.add('notification-closing');
      setTimeout(() => {
        notification.remove();
      }, 300);
    });
    
    // Auto close after duration
    setTimeout(() => {
      if (notification.parentNode) {
        notification.classList.add('notification-closing');
        setTimeout(() => {
          notification.remove();
        }, 300);
      }
    }, duration);
    
    // Show notification with animation
    setTimeout(() => {
      notification.classList.add('notification-show');
    }, 10);
  }
  
  /**
   * Show a success notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds
   */
  function showSuccess(message, duration = 3000) {
    showNotification(message, 'success', duration);
  }
  
  /**
   * Show an error notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds
   */
  function showError(message, duration = 3000) {
    showNotification(message, 'error', duration);
  }
  
  /**
   * Show a warning notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds
   */
  function showWarning(message, duration = 3000) {
    showNotification(message, 'warning', duration);
  }
  
  /**
   * Show an info notification
   * @param {string} message - Notification message
   * @param {number} duration - Duration in milliseconds
   */
  function showInfo(message, duration = 3000) {
    showNotification(message, 'info', duration);
  }
  
  /**
   * Show a toast notification (simpler, smaller notification)
   * @param {string} message - Toast message
   * @param {string} type - Toast type (success, error, info, warning)
   * @param {number} duration - Duration in milliseconds
   */
  function showToast(message, type = 'info', duration = 2000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container';
      document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Show with animation
    setTimeout(() => {
      toast.classList.add('toast-show');
    }, 10);
    
    // Auto close
    setTimeout(() => {
      toast.classList.add('toast-closing');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, duration);
  }
  
  /**
   * Clear all notifications
   */
  function clearAllNotifications() {
    const notificationContainer = document.querySelector('.notification-container');
    if (notificationContainer) {
      notificationContainer.innerHTML = '';
    }
    
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
      toastContainer.innerHTML = '';
    }
  }
  
  // Export all functions
  export { 
    showNotification, 
    showSuccess, 
    showError, 
    showWarning, 
    showInfo, 
    showToast, 
    clearAllNotifications 
  };
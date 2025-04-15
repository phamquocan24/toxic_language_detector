/**
 * Content script wrapper
 * Sử dụng ES modules để load content script
 */

// Tạo script element để load code
const script = document.createElement('script');
script.src = chrome.runtime.getURL('src/content/index.js');
script.type = 'module'; // Thay đổi type thành module
script.onload = function() {
  console.log('Content script loaded successfully');
  // Gửi message để thông báo content script đã được load
  chrome.runtime.sendMessage({ action: 'contentScriptLoaded' });
};
script.onerror = function(error) {
  console.error('Error loading content script:', error);
  // Log thêm thông tin chi tiết về lỗi
  console.error('Error details:', {
    message: error.message,
    filename: error.filename,
    lineno: error.lineno,
    colno: error.colno
  });
};

// Thêm script vào document
(document.head || document.documentElement).appendChild(script);

// Lắng nghe message từ background
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  // Gửi sự kiện tới content script
  window.dispatchEvent(new CustomEvent('toxicDetector', { 
    detail: { message, sender }
  }));
  
  // Cho phép gửi response bất đồng bộ
  return true;
}); 
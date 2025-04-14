/**
 * Content script for the Toxic Language Detector Extension
 * Runs on supported social media platforms and analyzes comments for toxic content
 */

// Định nghĩa các màu và nhãn cho từng loại phân loại
const CATEGORY_STYLES = {
  clean: {
    color: '#4CAF50',  // Green
    label: 'Bình thường',
    className: 'toxic-indicator-clean'
  },
  offensive: {
    color: '#FF9800',  // Orange 
    label: 'Xúc phạm',
    className: 'toxic-indicator-offensive'
  },
  hate: {
    color: '#F44336',  // Red
    label: 'Thù ghét',
    className: 'toxic-indicator-hate'
  },
  spam: {
    color: '#9C27B0',  // Purple
    label: 'Spam',
    className: 'toxic-indicator-spam'
  }
};

// API Configuration
const API_CONFIG = {
  WEB_DASHBOARD: 'http://localhost:7860/dashboard'
};

// Platform definitions
const PLATFORMS = {
  FACEBOOK: "facebook",
  YOUTUBE: "youtube",
  TWITTER: "twitter",
  UNKNOWN: "unknown"
};

// Detect current platform
let currentPlatform = '';
if (window.location.hostname.includes("facebook.com")) {
  currentPlatform = PLATFORMS.FACEBOOK;
} else if (window.location.hostname.includes("youtube.com") || window.location.hostname.includes("youtu.be")) {
  currentPlatform = PLATFORMS.YOUTUBE;
} else if (window.location.hostname.includes("twitter.com") || window.location.hostname.includes("x.com")) {
  currentPlatform = PLATFORMS.TWITTER;
} else {
  currentPlatform = PLATFORMS.UNKNOWN;
}
console.log(`Phát hiện nền tảng: ${currentPlatform}`);

// Extension state
let extensionEnabled = true;
let toxicThreshold = 0.7;
let highlightToxic = true;
let platformEnabled = true;
let isAuthenticated = false;

// Cache for processed comments
const processedComments = new Set();
const commentCache = new Map(); // Cache for comment analysis results

// Initialize extension
initialize();

/**
 * Initialize the extension
 */
function initialize() {
  // Check authentication status first
  checkAuthStatus().then(authStatus => {
    isAuthenticated = authStatus;
    
    if (!isAuthenticated) {
      console.log('Người dùng chưa đăng nhập. Extension sẽ không phân tích bình luận.');
      return;
    }

    // Load settings from storage
    chrome.storage.sync.get(['enabled', 'threshold', 'highlightToxic', 'platforms'], (data) => {
      extensionEnabled = data.enabled !== undefined ? data.enabled : true;
      toxicThreshold = data.threshold || 0.7;
      highlightToxic = data.highlightToxic !== undefined ? data.highlightToxic : true;

      if (data.platforms) {
        switch (currentPlatform) {
          case PLATFORMS.FACEBOOK:
            platformEnabled = data.platforms.facebook !== undefined ? data.platforms.facebook : true;
            break;
          case PLATFORMS.YOUTUBE:
            platformEnabled = data.platforms.youtube !== undefined ? data.platforms.youtube : true;
            break;
          case PLATFORMS.TWITTER:
            platformEnabled = data.platforms.twitter !== undefined ? data.platforms.twitter : true;
            break;
          default:
            platformEnabled = false;
        }
      }
      
      // Start observing comments if extension is enabled and user is authenticated
      if (extensionEnabled && platformEnabled && isAuthenticated) {
        startObservingComments();
        processExistingComments();
      }
    });
  });
  
  // Listen for setting changes
  chrome.storage.onChanged.addListener(async (changes) => {
    let shouldRestart = false;
    
    // Check user authentication in storage
    if (changes.authToken) {
      isAuthenticated = changes.authToken.newValue ? true : false;
      shouldRestart = true;
    }
    
    // Check extension settings
    if (changes.enabled) {
      extensionEnabled = changes.enabled.newValue;
      shouldRestart = true;
    }
    
    if (changes.threshold) {
      toxicThreshold = changes.threshold.newValue;
    }
    
    if (changes.highlightToxic) {
      highlightToxic = changes.highlightToxic.newValue;
    }
    
    if (changes.platforms) {
      const platforms = changes.platforms.newValue;
      
      switch (currentPlatform) {
        case PLATFORMS.FACEBOOK:
          platformEnabled = platforms.facebook;
          break;
        case PLATFORMS.YOUTUBE:
          platformEnabled = platforms.youtube;
          break;
        case PLATFORMS.TWITTER:
          platformEnabled = platforms.twitter;
          break;
        default:
          platformEnabled = false;
      }
      shouldRestart = true;
    }
    
    // Restart observer if needed
    if (shouldRestart) {
      if (extensionEnabled && platformEnabled && isAuthenticated) {
        startObservingComments();
        processExistingComments();
      } else {
        stopObservingComments();
      }
    }
  });
  
  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'settingsUpdated') {
      // Update local settings
      if (message.settings) {
        extensionEnabled = message.settings.enabled !== undefined ? message.settings.enabled : extensionEnabled;
        toxicThreshold = message.settings.threshold || toxicThreshold;
        highlightToxic = message.settings.highlightToxic !== undefined ? message.settings.highlightToxic : highlightToxic;
        
        if (message.settings.platforms) {
          switch (currentPlatform) {
            case PLATFORMS.FACEBOOK:
              platformEnabled = message.settings.platforms.facebook !== undefined ? message.settings.platforms.facebook : platformEnabled;
              break;
            case PLATFORMS.YOUTUBE:
              platformEnabled = message.settings.platforms.youtube !== undefined ? message.settings.platforms.youtube : platformEnabled;
              break;
            case PLATFORMS.TWITTER:
              platformEnabled = message.settings.platforms.twitter !== undefined ? message.settings.platforms.twitter : platformEnabled;
              break;
          }
        }
        
        // Restart observer if needed
        if (extensionEnabled && platformEnabled && isAuthenticated) {
          startObservingComments();
          processExistingComments();
        } else {
          stopObservingComments();
        }
      }
      
      sendResponse({ success: true });
    }
    
    return true;
  });
}

/**
 * Check authentication status
 * @returns {Promise<boolean>} true if authenticated
 */
async function checkAuthStatus() {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ action: 'checkAuth' }, response => {
      resolve(response && response.authenticated === true);
    });
  });
}

// Observer instances
let commentObserver = null;

/**
 * Start observing comments on the page
 */
function startObservingComments() {
  if (commentObserver) {
    // Observer đã tồn tại, không cần tạo lại
    return;
  }
  
  // Cấu hình MutationObserver để theo dõi các thay đổi DOM
  commentObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      // Xử lý các node mới được thêm vào
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const commentSelectors = getCommentSelectors();
            
            // Kiểm tra xem node mới có phải là comment không
            if (node.matches && node.matches(commentSelectors)) {
              processComment(node);
            } else if (node.querySelectorAll) {
              // Tìm các comments bên trong node mới
              const comments = node.querySelectorAll(commentSelectors);
              comments.forEach(comment => processComment(comment));
            }
          }
        }
      }
    }
  });
  
  // Bắt đầu theo dõi thay đổi DOM
  commentObserver.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Xử lý các comments hiện có trên trang
  processExistingComments();
}

/**
 * Stop observing comments
 */
function stopObservingComments() {
  if (commentObserver) {
    commentObserver.disconnect();
    commentObserver = null;
  }
}

/**
 * Process existing comments on the page
 */
function processExistingComments() {
  const commentSelectors = getCommentSelectors();
  const comments = document.querySelectorAll(commentSelectors);
  
  console.log(`Đã tìm thấy ${comments.length} bình luận hiện tại`);
  
  // Xử lý từng comment một
  comments.forEach(comment => {
    processComment(comment);
  });
}

/**
 * Get the appropriate comment selectors for the current platform
 * @returns {string} - CSS selector for comments
 */
function getCommentSelectors() {
  switch (currentPlatform) {
    case PLATFORMS.FACEBOOK:
      return `
        div[aria-label*="Bình luận"],
        div[aria-label*="Comment"],
        div[data-testid="UFI2Comment/root"],
        div[data-testid="comment-row"],
        div.UFIComment,
        div.UFICommentContent,
        div[data-testid="comment"],
        div[data-ft*="\"tn\":\"R\""]
      `;
      
    case PLATFORMS.YOUTUBE:
      return `
        ytd-comment-thread-renderer,
        ytd-comment-renderer,
        yt-formatted-string#content-text
      `;
      
    case PLATFORMS.TWITTER:
      return `
        article[data-testid="tweet"],
        div[data-testid="tweetText"],
        div[role="group"][data-testid="reply"],
        div.tweet-reply
      `;
      
    default:
      return `
        .comment, 
        .article-comment, 
        .user-comment, 
        [class*="comment"],
        [class*="Comment"]
      `;
  }
}

/**
 * Get the comment ID or generate one if not available
 * @param {Element} commentElement - The comment element
 * @returns {string} - Comment ID
 */
function getCommentId(commentElement) {
  if (!commentElement) return null;
  
  let commentId = '';
  
  switch (currentPlatform) {
    case PLATFORMS.FACEBOOK:
      // Try to get Facebook comment ID
      commentId = commentElement.id || 
                  commentElement.dataset.ftid || 
                  commentElement.getAttribute('data-testid');
      break;
      
    case PLATFORMS.YOUTUBE:
      // Try to get YouTube comment ID
      const ytCommentRenderer = commentElement.closest('ytd-comment-renderer');
      commentId = ytCommentRenderer ? ytCommentRenderer.id : '';
      break;
      
    case PLATFORMS.TWITTER:
      // Try to get Twitter tweet ID
      const tweetArticle = commentElement.closest('article[data-testid="tweet"]');
      commentId = tweetArticle ? 
                tweetArticle.getAttribute('aria-labelledby') : '';
      break;
  }
  
  // If no ID found, generate a hash from the content and position
  if (!commentId) {
    const commentText = getCommentText(commentElement);
    const position = getElementPosition(commentElement);
    commentId = `comment-${hashString(commentText + position)}`;
  }
  
  return commentId;
}

/**
 * Get text content of a comment
 * @param {Element} commentElement - The comment element
 * @returns {string} - Text content
 */
function getCommentText(commentElement) {
  if (!commentElement) return '';
  
  let text = '';
  
  switch (currentPlatform) {
    case PLATFORMS.FACEBOOK:
      // For Facebook, find the text elements
      const fbTextContainers = commentElement.querySelectorAll('span[dir="auto"], div[dir="auto"], div[data-ad-comet-preview="message"], div[data-contents="true"]');
      for (const container of fbTextContainers) {
        if (container.textContent && container.textContent.trim().length > 0) {
          text += container.textContent + ' ';
        }
      }
      break;
      
    case PLATFORMS.YOUTUBE:
      // For YouTube, get text from content-text
      const ytTextElement = commentElement.querySelector('#content-text') || commentElement;
      text = ytTextElement.textContent || '';
      break;
      
    case PLATFORMS.TWITTER:
      // For Twitter, find the tweet text
      const twitterTextElement = commentElement.querySelector('[data-testid="tweetText"]') || commentElement;
      text = twitterTextElement.textContent || '';
      break;
      
    default:
      // Default fallback
      text = commentElement.textContent || '';
  }
  
  return text.trim();
}

/**
 * Get the position of an element on the page for identification
 * @param {Element} element - DOM element
 * @returns {string} - Position string
 */
function getElementPosition(element) {
  if (!element || !element.getBoundingClientRect) {
    return '0,0';
  }
  
  const rect = element.getBoundingClientRect();
  return `${Math.floor(rect.top)},${Math.floor(rect.left)}`;
}

/**
 * Process a comment element
 * @param {Element} commentElement - The comment element to process
 */
function processComment(commentElement) {
  // Kiểm tra xác thực, extension và cấu hình
  if (!extensionEnabled || !platformEnabled || !isAuthenticated) {
    return;
  }
  
  // Lấy text và ID của comment
  const commentText = getCommentText(commentElement);
  const commentId = getCommentId(commentElement);
  
  // Bỏ qua nếu comment là rỗng, quá ngắn, hoặc đã xử lý
  if (!commentText || commentText.trim().length < 5 || processedComments.has(commentId)) {
    return;
  }
  
  // Đánh dấu comment này đã được xử lý
  processedComments.add(commentId);
  
  // Kiểm tra trong cache trước
  if (commentCache.has(commentText)) {
    const cachedResult = commentCache.get(commentText);
    applyToxicityIndicator(commentElement, cachedResult);
    return;
  }
  
  // Tạo metadata cho comment
  const metadata = {
    url: window.location.href,
    pageTitle: document.title,
    timestamp: new Date().toISOString()
  };
  
  // Hiển thị indicator "đang phân tích"
  const loadingIndicator = createLoadingIndicator();
  commentElement.appendChild(loadingIndicator);
  
  // Gửi đến API để phân tích
  chrome.runtime.sendMessage({
    action: "analyzeText",
    text: commentText,
    platform: currentPlatform,
    commentId: commentId,
    metadata: metadata
  }, (response) => {
    // Xóa loading indicator
    if (loadingIndicator && loadingIndicator.parentNode) {
      loadingIndicator.parentNode.removeChild(loadingIndicator);
    }
    
    // Xử lý kết quả
    if (response && !response.error) {
      // Lưu vào cache
      commentCache.set(commentText, response);
      
      // Hiển thị kết quả
      applyToxicityIndicator(commentElement, response);
    } else {
      console.error('Error analyzing comment:', response ? response.error : 'Unknown error');
      
      // Hiển thị lỗi nhẹ nhàng
      const errorIndicator = document.createElement('span');
      errorIndicator.classList.add('toxic-error-indicator');
      errorIndicator.title = 'Không thể phân tích comment này';
      errorIndicator.textContent = '⚠️';
      errorIndicator.style.fontSize = '16px';
      errorIndicator.style.marginLeft = '5px';
      commentElement.appendChild(errorIndicator);
      
      // Tự động xóa sau 5 giây
      setTimeout(() => {
        if (errorIndicator && errorIndicator.parentNode) {
          errorIndicator.parentNode.removeChild(errorIndicator);
        }
      }, 5000);
    }
  });
}

/**
 * Create a loading indicator while analyzing content
 * @returns {HTMLElement} - The loading indicator element
 */
function createLoadingIndicator() {
  const indicator = document.createElement('span');
  indicator.classList.add('toxic-loading-indicator');
  indicator.innerHTML = '🔍';
  indicator.title = 'Đang phân tích...';
  indicator.style.fontSize = '16px';
  indicator.style.marginLeft = '5px';
  indicator.style.animation = 'toxic-pulse 1.5s infinite';
  
  // Add animation style if not already present
  if (!document.getElementById('toxic-animations')) {
    const style = document.createElement('style');
    style.id = 'toxic-animations';
    style.textContent = `
      @keyframes toxic-pulse {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
      }
    `;
    document.head.appendChild(style);
  }
  
  return indicator;
}

/**
 * Apply toxicity indicator based on analysis results
 * @param {Element} commentElement - The comment element
 * @param {Object} result - The prediction result
 */
function applyToxicityIndicator(commentElement, result) {
  if (!commentElement || !result) return;
  
  // Đảm bảo có prediction
  if (typeof result.prediction !== 'number') {
    console.error('Invalid prediction result:', result);
    return;
  }
  
  // Ánh xạ giá trị dự đoán sang tên danh mục
  const categoryNames = ['clean', 'offensive', 'hate', 'spam'];
  const categoryName = categoryNames[result.prediction] || 'unknown';
  
  // Lấy style cho danh mục
  const style = CATEGORY_STYLES[categoryName] || {
    color: '#777777',
    label: 'Không xác định',
    className: 'toxic-indicator-unknown'
  };
  
  // Chỉ highlight nếu vượt ngưỡng và không phải là 'clean'
  const shouldHighlight = highlightToxic && 
                          result.confidence >= toxicThreshold && 
                          categoryName !== 'clean';
  
  // Tạo indicator
  const indicator = document.createElement('span');
  indicator.classList.add('toxic-indicator', style.className);
  indicator.title = `${style.label} (${Math.round(result.confidence * 100)}% độ tin cậy)`;
  indicator.style.fontSize = '13px';
  indicator.style.padding = '2px 6px';
  indicator.style.borderRadius = '12px';
  indicator.style.marginLeft = '8px';
  indicator.style.display = 'inline-flex';
  indicator.style.alignItems = 'center';
  indicator.style.color = style.color;
  
  if (shouldHighlight) {
    // Thêm icon và nhãn nếu cần highlight
    indicator.innerHTML = `
      <span style="margin-right: 3px;">⚠️</span>
      <span>${style.label}</span>
    `;
    indicator.style.backgroundColor = `${style.color}15`;
    indicator.style.border = `1px solid ${style.color}30`;
  } else {
    // Chỉ thêm chấm màu nếu là 'clean' hoặc dưới ngưỡng
    indicator.innerHTML = `<span style="
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: ${style.color};
      margin-right: 4px;
    "></span>`;
    
    // Thêm nhãn nếu là nội dung tiêu cực
    if (categoryName !== 'clean') {
      indicator.innerHTML += `<span>${style.label}</span>`;
    }
  }
  
  // Thêm indicator vào comment
  // Kiểm tra nền tảng để chèn vào vị trí phù hợp
  switch (currentPlatform) {
    case PLATFORMS.FACEBOOK:
      // Chèn vào cuối comment
      commentElement.appendChild(indicator);
      break;
      
    case PLATFORMS.YOUTUBE:
      // Tìm phần header của comment để chèn vào
      const ytHeader = commentElement.querySelector('#header-author, .ytd-comment-renderer');
      if (ytHeader) {
        ytHeader.appendChild(indicator);
      } else {
        commentElement.appendChild(indicator);
      }
      break;
      
    case PLATFORMS.TWITTER:
      // Tìm footer của tweet để chèn vào
      const tweetActions = commentElement.querySelector('.tweet-actions, .css-1dbjc4n[role="group"]');
      if (tweetActions) {
        tweetActions.parentNode.insertBefore(indicator, tweetActions);
      } else {
        commentElement.appendChild(indicator);
      }
      break;
      
    default:
      commentElement.appendChild(indicator);
  }
  
  // Highlight nội dung comment nếu là nội dung tiêu cực và cấu hình cho phép
  if (shouldHighlight) {
    // Tìm text container của comment
    const textContainer = findCommentTextContainer(commentElement);
    if (textContainer) {
      textContainer.style.backgroundColor = `${style.color}10`;
      textContainer.style.padding = '8px';
      textContainer.style.borderRadius = '8px';
      textContainer.style.border = `1px solid ${style.color}20`;
    }
  }
}

/**
 * Find the text container of a comment
 * @param {Element} commentElement - The comment element
 * @returns {Element|null} - The text container element
 */
function findCommentTextContainer(commentElement) {
  switch (currentPlatform) {
    case PLATFORMS.FACEBOOK:
      return commentElement.querySelector('span[dir="auto"], div[dir="auto"], div[data-ad-comet-preview="message"], div[data-contents="true"]');
    
    case PLATFORMS.YOUTUBE:
      return commentElement.querySelector('#content-text, .ytd-comment-renderer');
    
    case PLATFORMS.TWITTER:
      return commentElement.querySelector('[data-testid="tweetText"], .css-901oao');
    
    default:
      return null;
  }
}

/**
 * Vietnamese toxicity labels for UI display
 */
const VIETNAMESE_LABELS = {
  0: "Bình thường",
  1: "Xúc phạm",
  2: "Thù ghét",
  3: "Spam"
};

/**
 * Vietnamese color names for UI display
 */
const VIETNAMESE_COLORS = {
  1: "cam",      // orange for offensive
  2: "đỏ",       // red for hate speech
  3: "tím"       // purple for spam
};

/**
 * Vietnamese interface texts
 */
const VI_TEXTS = {
  revealBtn: "Hiện nội dung",
  revealTooltip: "Nhấn để hiện nội dung bị ẩn",
  tooltipPrefix: "Nội dung này đã được phát hiện là: "
};

/**
 * Get comment selectors for common Vietnamese social platforms
 * Adding more selector patterns for Vietnamese social media platforms
 * @returns {string} - CSS selector
 */
function getVietnameseCommentSelectors() {
  const standard = getCommentSelectors(); // Get standard selectors
  
  // Add more Vietnamese-specific selectors
  // For example, Vietnamese forums, news sites, etc.
  const vietnameseSelectors = [
    // Vietnamese forums
    '.bilutv-comment .content',
    '.phimmoi-comment .text',
    '.forum-comment-content',
    // Vietnamese news sites
    '.vnexpress-comment-body',
    '.vietnamnet-comment-content',
    '.dantri-comment-text',
    // Vietnamese social media with different selectors
    '.zalo-comment-text',
    '.tinhte-comment-body'
  ].join(', ');
  
  return standard + (standard ? ', ' : '') + vietnameseSelectors;
}

/**
 * Apply toxicity indicator with Vietnamese labels
 * @param {Element} commentElement - The comment DOM element
 * @param {Object} prediction - The prediction result
 */
function applyVietnameseToxicityIndicator(commentElement, prediction) {
  if (!highlightToxic || prediction.prediction === 0) {
    return;
  }
  
  // Create toxicity indicator with Vietnamese label
  const indicator = document.createElement('div');
  indicator.className = 'toxic-indicator';
  
  // Set color and Vietnamese label based on toxicity type
  let color, label;
  switch (prediction.prediction) {
    case 1: // Offensive
      color = 'orange';
      label = 'Xúc phạm';
      break;
    case 2: // Hate
      color = 'red';
      label = 'Thù ghét';
      break;
    case 3: // Spam
      color = 'purple';
      label = 'Spam';
      break;
    default:
      return;
  }
  
  indicator.style.backgroundColor = color;
  indicator.textContent = label;
  
  // Add tooltip in Vietnamese
  indicator.title = VI_TEXTS.tooltipPrefix + label.toLowerCase();
  
  // Add indicator near the comment
  commentElement.style.position = 'relative';
  commentElement.parentNode.insertBefore(indicator, commentElement.nextSibling);
  
  // Optional: blur toxic content
  if (prediction.prediction === 2) { // Only blur hate speech
    commentElement.classList.add('toxic-blur');
    
    // Add a button to reveal with Vietnamese text
    const revealBtn = document.createElement('button');
    revealBtn.className = 'toxic-reveal-btn';
    revealBtn.textContent = VI_TEXTS.revealBtn;
    revealBtn.title = VI_TEXTS.revealTooltip;
    revealBtn.onclick = function() {
      commentElement.classList.remove('toxic-blur');
      revealBtn.remove();
    };
    
    commentElement.parentNode.insertBefore(revealBtn, commentElement.nextSibling);
  }
}

// Modifications to popup.js for Vietnamese language support

/**
 * Add Vietnamese language interface to popup
 */
function initializeVietnameseUI() {
  // Map of UI elements to translate
  const translations = {
    '.toggle-label': 'Kích hoạt tiện ích',
    'h2:first-of-type': 'Cài đặt',
    'label[for="threshold"]': 'Ngưỡng nhạy cảm:',
    '#highlight-toxic + span + .checkmark + span': 'Đánh dấu nội dung độc hại',
    'h3': 'Kích hoạt trên nền tảng:',
    '#platform-facebook + span + .checkmark + span': 'Facebook',
    '#platform-youtube + span + .checkmark + span': 'YouTube',
    '#platform-twitter + span + .checkmark + span': 'Twitter',
    'h2:last-of-type': 'Thống kê',
    '#stat-scanned + .stat-label': 'Đã quét',
    '#stat-toxic + .stat-label': 'Độc hại',
    '#stat-clean + .stat-label': 'Bình thường',
    '#reset-stats': 'Đặt lại thống kê',
    '.footer p:first-child': 'Công cụ Phát hiện Ngôn từ Độc hại v1.0.0',
    '.footer p.small': 'Phát triển cho Nghiên cứu'
  };
  
  // Apply translations based on user language preference
  if (navigator.language.startsWith('vi')) {
    Object.entries(translations).forEach(([selector, text]) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        el.textContent = text;
      });
    });
  }
}

// Add to initialize() in popup.js
// document.addEventListener('DOMContentLoaded', () => {
//   loadSettings();
//   initializeVietnameseUI();
// });
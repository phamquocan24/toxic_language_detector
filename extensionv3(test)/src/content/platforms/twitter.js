/**
 * Module xử lý phát hiện và đánh dấu nội dung độc hại trên Twitter
 */
import { isElementVisible } from '../../utils/helpers.js';

// Selectors cho các loại phần tử trên Twitter
const SELECTORS = {
  // Tweets
  TWEETS: [
    'article[data-testid="tweet"]',
    'div[data-testid="cellInnerDiv"] > div:has(div[data-testid="tweetText"])',
  ],
  
  // Replies
  REPLIES: [
    'article[data-testid="tweet"]:has(div[data-testid="reply"])',
  ],
  
  // Tweet content
  TWEET_TEXT: 'div[data-testid="tweetText"]',
  
  // User info
  USER_NAME: 'a[data-testid="User-Name"]',
  
  // Tweet timestamp
  TIMESTAMP: 'time',
};

/**
 * Tìm các tweet trên Twitter
 * @returns {Array<HTMLElement>} - Danh sách các element tweet
 */
export function findComments() {
  const comments = [];
  
  // Tìm tất cả replies theo các selector
  for (const selector of SELECTORS.REPLIES) {
    const elements = document.querySelectorAll(selector);
    
    for (const element of elements) {
      if (isElementVisible(element) && !element.hasAttribute('data-toxic-processed')) {
        comments.push(element);
      }
    }
  }
  
  return comments;
}

/**
 * Tìm các tweets chính (không phải replies)
 * @returns {Array<HTMLElement>} - Danh sách các element tweet chính
 */
export function findPosts() {
  const posts = [];
  
  // Tìm tất cả tweets theo các selector
  for (const selector of SELECTORS.TWEETS) {
    const elements = document.querySelectorAll(selector);
    
    for (const element of elements) {
      // Bỏ qua các replies đã được xử lý ở findComments
      if (element.querySelector('div[data-testid="reply"]')) continue;
      
      if (isElementVisible(element) && !element.hasAttribute('data-toxic-processed')) {
        posts.push(element);
      }
    }
  }
  
  return posts;
}

/**
 * Trích xuất nội dung từ reply
 * @param {HTMLElement} commentElement - Element reply
 * @returns {Object} - Thông tin reply
 */
export function extractCommentData(commentElement) {
  if (!commentElement) return null;
  
  // Đánh dấu element đã được xử lý
  commentElement.setAttribute('data-toxic-processed', 'true');
  
  // Tìm nội dung reply
  const textElement = commentElement.querySelector(SELECTORS.TWEET_TEXT);
  if (!textElement || !textElement.textContent) return null;
  
  const text = textElement.textContent.trim();
  if (!text) return null;
  
  // Tìm thông tin người dùng
  let username = '';
  const usernameElement = commentElement.querySelector(SELECTORS.USER_NAME);
  
  if (usernameElement) {
    username = usernameElement.textContent.trim();
  }
  
  // Tìm URL tweet
  let url = '';
  const timeElement = commentElement.querySelector(SELECTORS.TIMESTAMP);
  
  if (timeElement && timeElement.parentElement && timeElement.parentElement.tagName === 'A') {
    url = timeElement.parentElement.href;
  } else {
    // Sử dụng URL hiện tại nếu không tìm thấy URL cụ thể
    url = window.location.href;
  }
  
  // Tìm ID của tweet
  let id = null;
  try {
    if (url.includes('/status/')) {
      id = url.split('/status/')[1].split('/')[0];
    }
  } catch (error) {
    console.error('Không thể trích xuất ID tweet:', error);
  }
  
  return {
    text,
    element: commentElement,
    platform: 'twitter',
    platformId: id,
    sourceUserName: username,
    sourceUrl: url,
    type: 'comment'
  };
}

/**
 * Trích xuất nội dung từ tweet
 * @param {HTMLElement} postElement - Element tweet
 * @returns {Object} - Thông tin tweet
 */
export function extractPostData(postElement) {
  if (!postElement) return null;
  
  // Đánh dấu element đã được xử lý
  postElement.setAttribute('data-toxic-processed', 'true');
  
  // Tìm nội dung tweet
  const textElement = postElement.querySelector(SELECTORS.TWEET_TEXT);
  if (!textElement || !textElement.textContent) return null;
  
  const text = textElement.textContent.trim();
  if (!text) return null;
  
  // Tìm thông tin người dùng
  let username = '';
  const usernameElement = postElement.querySelector(SELECTORS.USER_NAME);
  
  if (usernameElement) {
    username = usernameElement.textContent.trim();
  }
  
  // Tìm URL tweet
  let url = '';
  const timeElement = postElement.querySelector(SELECTORS.TIMESTAMP);
  
  if (timeElement && timeElement.parentElement && timeElement.parentElement.tagName === 'A') {
    url = timeElement.parentElement.href;
  } else {
    // Sử dụng URL hiện tại nếu không tìm thấy URL cụ thể
    url = window.location.href;
  }
  
  // Tìm ID của tweet
  let id = null;
  try {
    if (url.includes('/status/')) {
      id = url.split('/status/')[1].split('/')[0];
    }
  } catch (error) {
    console.error('Không thể trích xuất ID tweet:', error);
  }
  
  return {
    text,
    element: postElement,
    platform: 'twitter',
    platformId: id,
    sourceUserName: username,
    sourceUrl: url,
    type: 'post'
  };
}

/**
 * Đánh dấu phần tử có nội dung độc hại
 * @param {HTMLElement} element - Element cần đánh dấu
 * @param {Object} result - Kết quả phân tích
 */
export function markToxicElement(element, result) {
  if (!element || !result) return;
  
  const prediction = result.prediction;
  const confidence = result.confidence;
  
  // Không đánh dấu nội dung bình thường
  if (prediction === 0) return;
  
  // Tạo wrapper cho tooltip
  const wrapper = document.createElement('div');
  wrapper.className = 'toxic-detector-wrapper';
  wrapper.style.position = 'relative';
  
  // Thêm class cho element
  let toxicClass = '';
  let iconColor = '#dc3545';
  let warningText = 'Nội dung không phù hợp';
  
  switch (prediction) {
    case 1:
      toxicClass = 'toxicity-offensive';
      iconColor = '#ffc107';
      warningText = 'Nội dung xúc phạm';
      break;
    case 2:
      toxicClass = 'toxicity-hate';
      iconColor = '#dc3545';
      warningText = 'Nội dung thù ghét';
      break;
    case 3:
      toxicClass = 'toxicity-spam';
      iconColor = '#17a2b8';
      warningText = 'Nội dung spam';
      break;
  }
  
  // Thêm visual cue
  const marker = document.createElement('div');
  marker.className = 'toxic-detector-marker';
  marker.style.cssText = `
    position: absolute;
    top: 0;
    right: -10px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: ${iconColor};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    font-size: 12px;
    z-index: 999;
    cursor: pointer;
  `;
  marker.innerHTML = '!';
  marker.title = `${warningText} (${Math.round(confidence * 100)}% độ tin cậy)`;
  
  // Thêm tooltip khi hover
  marker.addEventListener('mouseenter', () => {
    const tooltip = document.createElement('div');
    tooltip.className = 'toxic-detector-tooltip';
    tooltip.style.cssText = `
      position: absolute;
      top: 20px;
      right: -10px;
      background-color: #333;
      color: white;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 12px;
      z-index: 1000;
      width: 180px;
      pointer-events: none;
    `;
    tooltip.innerHTML = `<strong>${warningText}</strong><br>Độ tin cậy: ${Math.round(confidence * 100)}%`;
    marker.appendChild(tooltip);
  });
  
  marker.addEventListener('mouseleave', () => {
    const tooltip = marker.querySelector('.toxic-detector-tooltip');
    if (tooltip) {
      tooltip.remove();
    }
  });
  
  // Bao quanh element gốc
  const parent = element.parentNode;
  parent.insertBefore(wrapper, element);
  wrapper.appendChild(element);
  wrapper.appendChild(marker);
  
  // Thêm hiệu ứng mờ nếu cấu hình cho phép
  element.style.opacity = '0.7';
  element.style.transition = 'opacity 0.3s ease';
}

export default {
  findComments,
  findPosts,
  extractCommentData,
  extractPostData,
  markToxicElement
}; 
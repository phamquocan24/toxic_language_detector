/**
 * Module xử lý phát hiện và đánh dấu nội dung độc hại trên YouTube
 */
import { isElementVisible } from '../../utils/helpers.js';

// Selectors cho các loại phần tử trên YouTube
const SELECTORS = {
  // Comments
  COMMENTS: [
    'ytd-comment-thread-renderer',
    'ytd-comment-renderer:not([is-reply])'
  ],
  
  // Comment replies
  COMMENT_REPLIES: [
    'ytd-comment-renderer[is-reply]'
  ],
  
  // Video description
  VIDEO_DESCRIPTION: [
    'ytd-video-secondary-info-renderer #description'
  ],
  
  // Comment content
  COMMENT_TEXT: '#content-text',
  
  // Video description content
  DESCRIPTION_TEXT: '#description-text'
};

/**
 * Tìm các bình luận trên YouTube
 * @returns {Array<HTMLElement>} - Danh sách các element bình luận
 */
export function findComments() {
  const comments = [];
  
  // Tìm tất cả bình luận theo các selector
  for (const selector of SELECTORS.COMMENTS) {
    const elements = document.querySelectorAll(selector);
    
    for (const element of elements) {
      if (isElementVisible(element) && !element.hasAttribute('data-toxic-processed')) {
        comments.push(element);
      }
    }
  }
  
  // Tìm tất cả phản hồi bình luận
  for (const selector of SELECTORS.COMMENT_REPLIES) {
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
 * Tìm các nội dung mô tả video YouTube
 * @returns {Array<HTMLElement>} - Danh sách các element mô tả video
 */
export function findPosts() {
  const posts = [];
  
  // Tìm tất cả mô tả video theo các selector
  for (const selector of SELECTORS.VIDEO_DESCRIPTION) {
    const elements = document.querySelectorAll(selector);
    
    for (const element of elements) {
      if (isElementVisible(element) && !element.hasAttribute('data-toxic-processed')) {
        posts.push(element);
      }
    }
  }
  
  return posts;
}

/**
 * Trích xuất nội dung từ bình luận
 * @param {HTMLElement} commentElement - Element bình luận
 * @returns {Object} - Thông tin bình luận
 */
export function extractCommentData(commentElement) {
  if (!commentElement) return null;
  
  // Đánh dấu element đã được xử lý
  commentElement.setAttribute('data-toxic-processed', 'true');
  
  // Tìm nội dung bình luận
  const textElement = commentElement.querySelector(SELECTORS.COMMENT_TEXT);
  if (!textElement || !textElement.textContent) return null;
  
  const text = textElement.textContent.trim();
  if (!text) return null;
  
  // Tìm thông tin người dùng nếu có
  let username = '';
  const usernameElement = commentElement.querySelector('#author-text');
  
  if (usernameElement) {
    username = usernameElement.textContent.trim();
  }
  
  // Tìm URL bình luận
  let url = '';
  const timestampElement = commentElement.querySelector('.published-time-text a');
  
  if (timestampElement) {
    url = timestampElement.href;
  } else {
    // Sử dụng URL video nếu không tìm thấy URL cụ thể của bình luận
    url = window.location.href;
  }
  
  return {
    text,
    element: commentElement,
    platform: 'youtube',
    platformId: commentElement.id || null,
    sourceUserName: username,
    sourceUrl: url,
    type: 'comment'
  };
}

/**
 * Trích xuất nội dung từ mô tả video
 * @param {HTMLElement} postElement - Element mô tả video
 * @returns {Object} - Thông tin mô tả video
 */
export function extractPostData(postElement) {
  if (!postElement) return null;
  
  // Đánh dấu element đã được xử lý
  postElement.setAttribute('data-toxic-processed', 'true');
  
  // Tìm nội dung mô tả video
  const textElements = postElement.querySelectorAll(SELECTORS.DESCRIPTION_TEXT);
  let text = '';
  
  if (textElements.length === 0) {
    // Nếu không tìm thấy qua selector cụ thể, lấy toàn bộ nội dung
    text = postElement.textContent.trim();
  } else {
    for (const element of textElements) {
      if (element.textContent) {
        text += element.textContent + ' ';
      }
    }
    text = text.trim();
  }
  
  if (!text) return null;
  
  // Tìm thông tin người tải video
  let username = '';
  const usernameElement = document.querySelector('#owner #text-container');
  
  if (usernameElement) {
    username = usernameElement.textContent.trim();
  }
  
  // URL của video
  const url = window.location.href;
  
  return {
    text,
    element: postElement,
    platform: 'youtube',
    platformId: postElement.id || new URL(url).searchParams.get('v') || null,
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
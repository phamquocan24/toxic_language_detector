/**
 * Module phát hiện và đánh dấu ngôn từ độc hại
 */
import { detectToxic, batchDetectToxic } from '../api/services.js';
import { getSettings, getAuthToken } from '../utils/storage.js';
import facebook from './platforms/facebook.js';
import twitter from './platforms/twitter.js'; 
import youtube from './platforms/youtube.js';
import { detectPlatform } from '../utils/helpers.js';

// Cấu hình thời gian giữa các lần quét
const SCAN_INTERVAL = 2000; // 2 giây
const BATCH_SIZE = 10; // Số lượng items tối đa trong 1 lần gửi

// Biến theo dõi trạng thái quét
let isScanRunning = false;
let scanTimer = null;
let platformInstance = null;

/**
 * Khởi tạo detector dựa trên nền tảng
 */
export function init() {
  // Xác định nền tảng hiện tại
  const platform = detectPlatform(window.location.href);
  
  if (!platform) {
    console.log('Toxic Detector: Không hỗ trợ nền tảng này');
    return;
  }
  
  // Khởi tạo nền tảng
  switch (platform) {
    case 'facebook':
      platformInstance = facebook;
      break;
    case 'youtube':
      platformInstance = youtube;
      break;
    case 'twitter':
      platformInstance = twitter;
      break;
    default:
      console.log(`Toxic Detector: Chưa có module cho nền tảng ${platform}`);
      return;
  }
  
  // Khởi động detector
  startDetection();
}

/**
 * Bắt đầu quét và phát hiện
 */
export async function startDetection() {
  // Kiểm tra cài đặt
  const settings = await getSettings();
  
  if (!settings.enableDetection) {
    console.log('Toxic Detector: Chức năng phát hiện đã bị tắt');
    return;
  }
  
  // Nếu đang chạy thì không làm gì
  if (isScanRunning) return;
  
  isScanRunning = true;
  
  // Bắt đầu quét định kỳ
  scanContent();
  scanTimer = setInterval(scanContent, SCAN_INTERVAL);
  
  console.log('Toxic Detector: Đã bắt đầu quét nội dung độc hại');
}

/**
 * Dừng quét và phát hiện
 */
export function stopDetection() {
  isScanRunning = false;
  
  if (scanTimer) {
    clearInterval(scanTimer);
    scanTimer = null;
  }
  
  console.log('Toxic Detector: Đã dừng quét nội dung độc hại');
}

/**
 * Quét nội dung trên trang
 */
async function scanContent() {
  if (!isScanRunning || !platformInstance) return;
  
  try {
    // Kiểm tra cài đặt
    const settings = await getSettings();
    
    if (!settings.enableDetection) {
      stopDetection();
      return;
    }
    
    // Tìm các bình luận và bài đăng
    const comments = platformInstance.findComments();
    const posts = platformInstance.findPosts();
    
    // Chuẩn bị dữ liệu để phân tích
    const commentItems = [];
    const postItems = [];
    
    // Xử lý bình luận
    for (const comment of comments) {
      const data = platformInstance.extractCommentData(comment);
      if (data && data.text.trim()) {
        commentItems.push({
          text: data.text,
          element: comment,
          platform: data.platform,
          platformId: data.platformId,
          sourceUserName: data.sourceUserName,
          sourceUrl: data.sourceUrl,
          type: 'comment'
        });
      }
    }
    
    // Xử lý bài đăng
    for (const post of posts) {
      const data = platformInstance.extractPostData(post);
      if (data && data.text.trim()) {
        postItems.push({
          text: data.text,
          element: post,
          platform: data.platform,
          platformId: data.platformId,
          sourceUserName: data.sourceUserName,
          sourceUrl: data.sourceUrl,
          type: 'post'
        });
      }
    }
    
    // Kết hợp thành 1 danh sách
    const items = [...commentItems, ...postItems];
    
    // Nếu không có gì để phân tích thì dừng
    if (items.length === 0) return;
    
    // Chia thành các batch nhỏ để tránh quá tải API
    const batches = [];
    for (let i = 0; i < items.length; i += BATCH_SIZE) {
      batches.push(items.slice(i, i + BATCH_SIZE));
    }
    
    // Xử lý từng batch
    for (const batch of batches) {
      await processBatch(batch, settings);
    }
  } catch (error) {
    console.error('Toxic Detector - Lỗi khi quét nội dung:', error);
  }
}

/**
 * Xử lý một batch các items
 * @param {Array} items - Danh sách items cần phân tích
 * @param {Object} settings - Cài đặt extension
 */
async function processBatch(items, settings) {
  try {
    // Chuẩn bị payload cho API
    const payload = items.map(item => ({
      text: item.text,
      platform: item.platform,
      platform_id: item.platformId,
      source_user_name: item.sourceUserName,
      source_url: item.sourceUrl || window.location.href
    }));
    
    console.log('Gửi batch phân tích với', payload.length, 'items');
    
    // Gọi API để phân tích
    const response = await batchDetectToxic(payload, {
      saveResult: true,
      authToken: await getAuthToken()
    });
    
    // Xử lý kết quả
    if (response && response.results && Array.isArray(response.results)) {
      console.log('Nhận được kết quả batch:', response.results.length);
      
      // Kết hợp kết quả với element tương ứng
      for (let i = 0; i < response.results.length && i < items.length; i++) {
        const result = response.results[i];
        const item = items[i];
        
        if (!result || !item || !item.element) continue;
        
        // Đánh dấu nội dung độc hại nếu cài đặt cho phép
        if (settings.enableHighlight && result.isToxic && item.element) {
          platformInstance.markToxicElement(item.element, result);
        }
      }
    } else {
      console.warn('Kết quả batch không hợp lệ hoặc trống:', response);
    }
  } catch (error) {
    console.error('Toxic Detector - Lỗi khi xử lý batch:', error);
  }
}

/**
 * Phân tích một văn bản cụ thể
 * @param {string} text - Văn bản cần phân tích
 * @param {string} platform - Nền tảng nguồn
 * @param {Object} options - Tùy chọn bổ sung
 * @returns {Promise<Object>} - Kết quả phân tích
 */
export async function analyzeText(text, platform = 'unknown', options = {}) {
  try {
    // Kiểm tra văn bản
    if (!text || !text.trim()) {
      return {
        success: false,
        error: 'Văn bản không được để trống'
      };
    }
    
    // Lấy cài đặt hiện tại
    const settings = await getSettings();
    
    // Thêm thông tin URL và tên người dùng (nếu có)
    const requestOptions = {
      threshold: settings.threshold || 0.7,
      sourceUrl: window.location.href,
      saveResult: true,
      ...options
    };

    // Gọi API để phân tích
    console.log('Gửi yêu cầu phân tích cho văn bản:', text);
    const result = await detectToxic(text, platform, requestOptions);
    
    // Kiểm tra kết quả
    if (!result) {
      console.error('Không nhận được kết quả phân tích');
      return {
        success: false,
        error: 'Không nhận được kết quả phân tích'
      };
    }
    
    console.log('Kết quả phân tích:', result);
    
    // Trả về kết quả với format thống nhất
    return {
      success: true,
      prediction: result.category || 'unknown',
      confidence: result.confidence || 0,
      isToxic: result.isToxic || false,
      score: result.score || 0,
      keywords: result.keywords || [],
      details: {
        probabilities: result.probabilities || {},
        text: result.text || text,
        processedText: result.processedText || text
      }
    };
  } catch (error) {
    console.error('Toxic Detector - Lỗi khi phân tích văn bản:', error);
    return {
      success: false,
      error: error.message || 'Lỗi không xác định khi phân tích văn bản'
    };
  }
}

export default {
  init,
  startDetection,
  stopDetection,
  analyzeText
}; 
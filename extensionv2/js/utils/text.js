/**
 * text.js - Text processing utilities for the Toxic Language Detector
 * Provides helper functions for text manipulation and analysis
 */

/**
 * Clean and normalize text
 * @param {string} text - Text to clean
 * @returns {string} - Cleaned text
 */
export function cleanText(text) {
    // Remove URLs
    text = text.replace(/https?:\/\/\S+/g, '');
    
    // Remove HTML tags
    text = text.replace(/<[^>]*>/g, '');
    
    // Normalize whitespace
    text = text.replace(/\s+/g, ' ').trim();
    
    return text;
  }
  
  /**
   * Truncate text to a maximum length
   * @param {string} text - Text to truncate
   * @param {number} [maxLength=100] - Maximum length
   * @param {string} [ellipsis='...'] - Ellipsis to append
   * @returns {string} - Truncated text
   */
  export function truncate(text, maxLength = 100, ellipsis = '...') {
    if (text.length <= maxLength) {
      return text;
    }
    
    return text.slice(0, maxLength - ellipsis.length) + ellipsis;
  }
  
  /**
   * Highlight specific terms in text
   * @param {string} text - Text to highlight
   * @param {string|string[]} terms - Terms to highlight
   * @param {string} [highlightClass='highlight'] - CSS class for highlight
   * @returns {string} - HTML with highlighted terms
   */
  export function highlightTerms(text, terms, highlightClass = 'highlight') {
    if (!terms) {
      return text;
    }
    
    const termArray = Array.isArray(terms) ? terms : [terms];
    let result = text;
    
    termArray.forEach(term => {
      if (!term) return;
      
      const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
      result = result.replace(regex, `<span class="${highlightClass}">$1</span>`);
    });
    
    return result;
  }
  
  /**
   * Escape string for use in regular expression
   * @param {string} string - String to escape
   * @returns {string} - Escaped string
   */
  export function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  
  /**
   * Extract keywords from text
   * @param {string} text - Text to extract keywords from
   * @param {Object} [options] - Options
   * @param {number} [options.minLength=3] - Minimum keyword length
   * @param {string[]} [options.stopWords=[]] - Stop words to exclude
   * @param {number} [options.maxKeywords=10] - Maximum number of keywords to return
   * @returns {string[]} - Array of keywords
   */
  export function extractKeywords(text, options = {}) {
    const {
      minLength = 3,
      stopWords = [],
      maxKeywords = 10
    } = options;
    
    // Default Vietnamese stop words
    const defaultStopWords = [
      'và', 'hoặc', 'của', 'là', 'có', 'trong', 'cho', 'với', 'các', 'được',
      'để', 'không', 'tôi', 'bạn', 'anh', 'chị', 'em', 'họ', 'nó', 'này',
      'đã', 'sẽ', 'đang', 'từ', 'lên', 'xuống', 'ra', 'vào', 'khi', 'nếu'
    ];
    
    const allStopWords = [...defaultStopWords, ...stopWords];
    
    // Clean and normalize text
    const cleanedText = cleanText(text).toLowerCase();
    
    // Split into words and filter
    const words = cleanedText.split(/\s+/)
      .filter(word => word.length >= minLength)
      .filter(word => !allStopWords.includes(word.toLowerCase()));
    
    // Count word frequency
    const wordCount = {};
    words.forEach(word => {
      wordCount[word] = (wordCount[word] || 0) + 1;
    });
    
    // Sort by frequency and return top keywords
    return Object.entries(wordCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxKeywords)
      .map(([word]) => word);
  }
  
  /**
   * Calculate text statistics
   * @param {string} text - Text to analyze
   * @returns {Object} - Statistics object
   */
  export function textStats(text) {
    // Clean text
    const cleanedText = cleanText(text);
    
    // Count words
    const words = cleanedText.split(/\s+/).filter(word => word.length > 0);
    const wordCount = words.length;
    
    // Count characters
    const charCount = cleanedText.length;
    
    // Count sentences
    const sentenceCount = cleanedText.split(/[.!?]+/).filter(sentence => sentence.length > 0).length;
    
    // Calculate average word length
    const avgWordLength = wordCount > 0 ? charCount / wordCount : 0;
    
    // Calculate average sentence length
    const avgSentenceLength = sentenceCount > 0 ? wordCount / sentenceCount : 0;
    
    return {
      wordCount,
      charCount,
      sentenceCount,
      avgWordLength,
      avgSentenceLength
    };
  }
  
  /**
   * Detect language of text (simple heuristic)
   * @param {string} text - Text to detect language for
   * @returns {string} - Language code ('vi' for Vietnamese, 'en' for English, 'unknown' for others)
   */
  export function detectLanguage(text) {
    // Clean text
    const cleanedText = cleanText(text);
    
    // Vietnamese diacritical marks and special characters
    const vnMarks = /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i;
    
    // Count Vietnamese and English characters
    const vnCount = (cleanedText.match(vnMarks) || []).length;
    const totalChars = cleanedText.length;
    
    if (totalChars === 0) {
      return 'unknown';
    }
    
    // If more than 5% of characters have Vietnamese diacritical marks, assume it's Vietnamese
    if (vnCount / totalChars > 0.05) {
      return 'vi';
    }
    
    // Assume it's English or another language
    const enMarks = /[a-z]/i;
    const enCount = (cleanedText.match(enMarks) || []).length;
    
    if (enCount / totalChars > 0.5) {
      return 'en';
    }
    
    return 'unknown';
  }
  
  /**
   * Format number with comma separators
   * @param {number} number - Number to format
   * @param {number} [decimals=0] - Number of decimal places
   * @param {string} [decimalPoint='.'] - Decimal point character
   * @param {string} [thousandsSeparator=','] - Thousands separator character
   * @returns {string} - Formatted number
   */
  export function formatNumber(number, decimals = 0, decimalPoint = '.', thousandsSeparator = ',') {
    const numberStr = parseFloat(number).toFixed(decimals);
    const parts = numberStr.split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandsSeparator);
    return parts.join(decimalPoint);
  }
  
  /**
   * Format date in Vietnamese style
   * @param {Date|string|number} date - Date to format
   * @param {string} [format='dd/MM/yyyy'] - Format string
   * @returns {string} - Formatted date
   */
  export function formatDate(date, format = 'dd/MM/yyyy') {
    const d = new Date(date);
    
    if (isNaN(d.getTime())) {
      return '';
    }
    
    // Format mapping
    const formats = {
      dd: String(d.getDate()).padStart(2, '0'),
      MM: String(d.getMonth() + 1).padStart(2, '0'),
      yyyy: d.getFullYear(),
      HH: String(d.getHours()).padStart(2, '0'),
      mm: String(d.getMinutes()).padStart(2, '0'),
      ss: String(d.getSeconds()).padStart(2, '0')
    };
    
    // Replace format tokens
    return format.replace(/dd|MM|yyyy|HH|mm|ss/g, match => formats[match]);
  }
  
  /**
   * Format relative time (e.g., "5 minutes ago")
   * @param {Date|string|number} date - Date to format
   * @param {string} [locale='vi'] - Locale for formatting
   * @returns {string} - Formatted relative time
   */
  export function formatRelativeTime(date, locale = 'vi') {
    const d = new Date(date);
    
    if (isNaN(d.getTime())) {
      return '';
    }
    
    const now = new Date();
    const diffMs = now - d;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    // Vietnamese translations
    const vi = {
      justNow: 'vừa xong',
      secondsAgo: seconds => `${seconds} giây trước`,
      minutesAgo: minutes => `${minutes} phút trước`,
      hoursAgo: hours => `${hours} giờ trước`,
      daysAgo: days => `${days} ngày trước`,
      weeksAgo: weeks => `${weeks} tuần trước`,
      monthsAgo: months => `${months} tháng trước`,
      yearsAgo: years => `${years} năm trước`
    };
    
    // English translations
    const en = {
      justNow: 'just now',
      secondsAgo: seconds => `${seconds} seconds ago`,
      minutesAgo: minutes => `${minutes} minutes ago`,
      hoursAgo: hours => `${hours} hours ago`,
      daysAgo: days => `${days} days ago`,
      weeksAgo: weeks => `${weeks} weeks ago`,
      monthsAgo: months => `${months} months ago`,
      yearsAgo: years => `${years} years ago`
    };
    
    const t = locale === 'vi' ? vi : en;
    
    if (diffSec < 10) {
      return t.justNow;
    } else if (diffSec < 60) {
      return t.secondsAgo(diffSec);
    } else if (diffMin < 60) {
      return t.minutesAgo(diffMin);
    } else if (diffHour < 24) {
      return t.hoursAgo(diffHour);
    } else if (diffDay < 7) {
      return t.daysAgo(diffDay);
    } else if (diffDay < 30) {
      return t.weeksAgo(Math.floor(diffDay / 7));
    } else if (diffDay < 365) {
      return t.monthsAgo(Math.floor(diffDay / 30));
    } else {
      return t.yearsAgo(Math.floor(diffDay / 365));
    }
  }
  
  /**
   * Convert HTML to plain text
   * @param {string} html - HTML string
   * @returns {string} - Plain text
   */
  export function htmlToText(html) {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return doc.body.textContent || '';
  }
  
  /**
   * Encode HTML entities
   * @param {string} text - Text to encode
   * @returns {string} - Encoded text
   */
  export function encodeHTML(text) {
    const element = document.createElement('div');
    element.textContent = text;
    return element.innerHTML;
  }
  
  /**
   * Decode HTML entities
   * @param {string} html - HTML to decode
   * @returns {string} - Decoded text
   */
  export function decodeHTML(html) {
    const element = document.createElement('div');
    element.innerHTML = html;
    return element.textContent || '';
  }
  
  // Export all functions as a group
  export default {
    cleanText,
    truncate,
    highlightTerms,
    escapeRegExp,
    extractKeywords,
    textStats,
    detectLanguage,
    formatNumber,
    formatDate,
    formatRelativeTime,
    htmlToText,
    encodeHTML,
    decodeHTML
  };
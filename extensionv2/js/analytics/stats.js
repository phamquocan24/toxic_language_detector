// js/analytics/stats.js

/**
 * Stats Module
 * Xử lý thống kê và phân tích dữ liệu cho extension
 */

// Cấu trúc dữ liệu thống kê
const StatsTypes = {
    SCANNED: 'scanned',      // Số lượng đã quét
    CLEAN: 'clean',          // Số lượng bình thường
    OFFENSIVE: 'offensive',  // Số lượng xúc phạm
    HATE: 'hate',            // Số lượng thù ghét 
    SPAM: 'spam'             // Số lượng spam
  };
  
  // Cấu trúc dữ liệu phân tích theo nền tảng
  const Platforms = {
    FACEBOOK: 'facebook',
    YOUTUBE: 'youtube',
    TWITTER: 'twitter'
  };
  
  /**
   * Module thống kê
   */
  class StatsManager {
    constructor() {
      // Khởi tạo thống kê
      this.stats = {
        global: {
          [StatsTypes.SCANNED]: 0,
          [StatsTypes.CLEAN]: 0,
          [StatsTypes.OFFENSIVE]: 0,
          [StatsTypes.HATE]: 0,
          [StatsTypes.SPAM]: 0
        },
        platforms: {
          [Platforms.FACEBOOK]: {
            [StatsTypes.SCANNED]: 0,
            [StatsTypes.CLEAN]: 0,
            [StatsTypes.OFFENSIVE]: 0,
            [StatsTypes.HATE]: 0,
            [StatsTypes.SPAM]: 0
          },
          [Platforms.YOUTUBE]: {
            [StatsTypes.SCANNED]: 0,
            [StatsTypes.CLEAN]: 0,
            [StatsTypes.OFFENSIVE]: 0,
            [StatsTypes.HATE]: 0,
            [StatsTypes.SPAM]: 0
          },
          [Platforms.TWITTER]: {
            [StatsTypes.SCANNED]: 0,
            [StatsTypes.CLEAN]: 0,
            [StatsTypes.OFFENSIVE]: 0,
            [StatsTypes.HATE]: 0,
            [StatsTypes.SPAM]: 0
          }
        },
        history: [],
        lastUpdated: Date.now()
      };
      
      // Tải thống kê từ storage
      this.loadStats();
    }
    
    /**
     * Tải thống kê từ storage
     */
    async loadStats() {
      try {
        const data = await new Promise(resolve => {
          chrome.storage.sync.get('stats', (result) => {
            resolve(result.stats);
          });
        });
        
        if (data) {
          this.stats = data;
        }
      } catch (error) {
        console.error('Error loading stats:', error);
      }
    }
    
    /**
     * Lưu thống kê vào storage
     */
    async saveStats() {
      try {
        this.stats.lastUpdated = Date.now();
        await new Promise(resolve => {
          chrome.storage.sync.set({ stats: this.stats }, () => {
            resolve();
          });
        });
      } catch (error) {
        console.error('Error saving stats:', error);
      }
    }
    
    /**
     * Cập nhật thống kê
     * @param {number} prediction - Kết quả dự đoán (0-3)
     * @param {string} platform - Nền tảng (facebook, youtube, twitter)
     * @param {string} text - Nội dung đã phân tích
     * @param {number} confidence - Độ tin cậy
     */
    async updateStats(prediction, platform, text, confidence) {
      // Cập nhật thống kê toàn cục
      this.stats.global[StatsTypes.SCANNED]++;
      
      // Cập nhật theo loại
      switch (prediction) {
        case 0:
          this.stats.global[StatsTypes.CLEAN]++;
          break;
        case 1:
          this.stats.global[StatsTypes.OFFENSIVE]++;
          break;
        case 2:
          this.stats.global[StatsTypes.HATE]++;
          break;
        case 3:
          this.stats.global[StatsTypes.SPAM]++;
          break;
      }
      
      // Cập nhật theo nền tảng
      if (this.stats.platforms[platform]) {
        this.stats.platforms[platform][StatsTypes.SCANNED]++;
        
        switch (prediction) {
          case 0:
            this.stats.platforms[platform][StatsTypes.CLEAN]++;
            break;
          case 1:
            this.stats.platforms[platform][StatsTypes.OFFENSIVE]++;
            break;
          case 2:
            this.stats.platforms[platform][StatsTypes.HATE]++;
            break;
          case 3:
            this.stats.platforms[platform][StatsTypes.SPAM]++;
            break;
        }
      }
      
      // Thêm vào lịch sử (giới hạn 100 mục)
      this.stats.history.unshift({
        timestamp: Date.now(),
        prediction,
        platform,
        text: text.substring(0, 100), // Giới hạn độ dài
        confidence
      });
      
      // Giới hạn kích thước lịch sử
      if (this.stats.history.length > 100) {
        this.stats.history = this.stats.history.slice(0, 100);
      }
      
      // Lưu thống kê
      await this.saveStats();
    }
    
    /**
     * Lấy thống kê tổng quan
     * @returns {Object} Thống kê tổng quan
     */
    getOverviewStats() {
      const { global } = this.stats;
      return {
        scanned: global[StatsTypes.SCANNED],
        clean: global[StatsTypes.CLEAN],
        offensive: global[StatsTypes.OFFENSIVE],
        hate: global[StatsTypes.HATE],
        spam: global[StatsTypes.SPAM],
        lastUpdated: this.stats.lastUpdated
      };
    }
    
    /**
     * Lấy thống kê theo nền tảng
     * @param {string} platform - Tên nền tảng (không bắt buộc)
     * @returns {Object} Thống kê theo nền tảng
     */
    getPlatformStats(platform = null) {
      if (platform && this.stats.platforms[platform]) {
        return this.stats.platforms[platform];
      }
      return this.stats.platforms;
    }
    
    /**
     * Lấy lịch sử phát hiện
     * @param {number} limit - Số lượng mục cần lấy
     * @returns {Array} Lịch sử phát hiện
     */
    getHistory(limit = 10) {
      return this.stats.history.slice(0, limit);
    }
    
    /**
     * Tính tỷ lệ phần trăm phát hiện
     * @returns {Object} Tỷ lệ phần trăm các loại
     */
    getDistributionPercentage() {
      const { global } = this.stats;
      const total = global[StatsTypes.SCANNED];
      
      if (total === 0) {
        return {
          clean: 0,
          offensive: 0,
          hate: 0,
          spam: 0
        };
      }
      
      return {
        clean: Math.round((global[StatsTypes.CLEAN] / total) * 100),
        offensive: Math.round((global[StatsTypes.OFFENSIVE] / total) * 100),
        hate: Math.round((global[StatsTypes.HATE] / total) * 100),
        spam: Math.round((global[StatsTypes.SPAM] / total) * 100)
      };
    }
    
    /**
     * Lấy dữ liệu cho biểu đồ phân bố
     * @returns {Object} Dữ liệu cho biểu đồ
     */
    getChartData() {
      const { global } = this.stats;
      
      return {
        labels: ['Bình thường', 'Xúc phạm', 'Thù ghét', 'Spam'],
        datasets: [{
          data: [
            global[StatsTypes.CLEAN],
            global[StatsTypes.OFFENSIVE],
            global[StatsTypes.HATE],
            global[StatsTypes.SPAM]
          ],
          backgroundColor: [
            'rgba(76, 175, 80, 0.7)',   // Clean - green
            'rgba(255, 152, 0, 0.7)',   // Offensive - orange
            'rgba(244, 67, 54, 0.7)',   // Hate - red
            'rgba(156, 39, 176, 0.7)'   // Spam - purple
          ],
          borderColor: [
            'rgba(76, 175, 80, 1)',
            'rgba(255, 152, 0, 1)',
            'rgba(244, 67, 54, 1)',
            'rgba(156, 39, 176, 1)'
          ],
          borderWidth: 1
        }]
      };
    }
    
    /**
     * Lấy dữ liệu cho biểu đồ nền tảng
     * @returns {Object} Dữ liệu cho biểu đồ
     */
    getPlatformChartData() {
      const { platforms } = this.stats;
      
      return {
        labels: ['Facebook', 'YouTube', 'Twitter'],
        datasets: [{
          data: [
            platforms[Platforms.FACEBOOK][StatsTypes.SCANNED],
            platforms[Platforms.YOUTUBE][StatsTypes.SCANNED],
            platforms[Platforms.TWITTER][StatsTypes.SCANNED]
          ],
          backgroundColor: [
            'rgba(59, 89, 152, 0.7)',   // Facebook blue
            'rgba(255, 0, 0, 0.7)',     // YouTube red
            'rgba(29, 161, 242, 0.7)'   // Twitter blue
          ],
          borderColor: [
            'rgba(59, 89, 152, 1)',
            'rgba(255, 0, 0, 1)',
            'rgba(29, 161, 242, 1)'
          ],
          borderWidth: 1
        }]
      };
    }
    
    /**
     * Đặt lại thống kê
     */
    async resetStats() {
      this.stats = {
        global: {
          [StatsTypes.SCANNED]: 0,
          [StatsTypes.CLEAN]: 0,
          [StatsTypes.OFFENSIVE]: 0,
          [StatsTypes.HATE]: 0,
          [StatsTypes.SPAM]: 0
        },
        platforms: {
          [Platforms.FACEBOOK]: {
            [StatsTypes.SCANNED]: 0,
            [StatsTypes.CLEAN]: 0,
            [StatsTypes.OFFENSIVE]: 0,
            [StatsTypes.HATE]: 0,
            [StatsTypes.SPAM]: 0
          },
          [Platforms.YOUTUBE]: {
            [StatsTypes.SCANNED]: 0,
            [StatsTypes.CLEAN]: 0,
            [StatsTypes.OFFENSIVE]: 0,
            [StatsTypes.HATE]: 0,
            [StatsTypes.SPAM]: 0
          },
          [Platforms.TWITTER]: {
            [StatsTypes.SCANNED]: 0,
            [StatsTypes.CLEAN]: 0,
            [StatsTypes.OFFENSIVE]: 0,
            [StatsTypes.HATE]: 0,
            [StatsTypes.SPAM]: 0
          }
        },
        history: [],
        lastUpdated: Date.now()
      };
      
      await this.saveStats();
    }
    
    /**
     * Xuất thống kê dưới dạng JSON
     * @returns {string} Thống kê định dạng JSON
     */
    exportStatsAsJSON() {
      return JSON.stringify(this.stats, null, 2);
    }
    
    /**
     * Xuất thống kê dưới dạng CSV
     * @returns {string} Thống kê định dạng CSV
     */
    exportStatsAsCSV() {
      // Header
      let csv = 'Type,Total,Clean,Offensive,Hate,Spam\n';
      
      // Global stats
      const { global } = this.stats;
      csv += `Global,${global[StatsTypes.SCANNED]},${global[StatsTypes.CLEAN]},${global[StatsTypes.OFFENSIVE]},${global[StatsTypes.HATE]},${global[StatsTypes.SPAM]}\n`;
      
      // Platform stats
      const { platforms } = this.stats;
      Object.entries(platforms).forEach(([platform, stats]) => {
        csv += `${platform},${stats[StatsTypes.SCANNED]},${stats[StatsTypes.CLEAN]},${stats[StatsTypes.OFFENSIVE]},${stats[StatsTypes.HATE]},${stats[StatsTypes.SPAM]}\n`;
      });
      
      return csv;
    }
  }
  
  // Tạo singleton instance
  const statsManager = new StatsManager();
  
  // Export module
  export default statsManager;
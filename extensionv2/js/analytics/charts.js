// scripts/charts.js
document.addEventListener('DOMContentLoaded', () => {
    // Chart.js Global Configuration
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#607D8B';
    
    // Colors for different toxicity categories
    const chartColors = {
      clean: {
        main: 'rgba(76, 175, 80, 0.7)',
        light: 'rgba(76, 175, 80, 0.1)',
        border: 'rgba(76, 175, 80, 1)'
      },
      offensive: {
        main: 'rgba(255, 152, 0, 0.7)',
        light: 'rgba(255, 152, 0, 0.1)',
        border: 'rgba(255, 152, 0, 1)'
      },
      hate: {
        main: 'rgba(244, 67, 54, 0.7)',
        light: 'rgba(244, 67, 54, 0.1)',
        border: 'rgba(244, 67, 54, 1)'
      },
      spam: {
        main: 'rgba(156, 39, 176, 0.7)',
        light: 'rgba(156, 39, 176, 0.1)',
        border: 'rgba(156, 39, 176, 1)'
      }
    };
    
    // Simulate data for demo - would be replaced with real API calls
    function generateTimelineData() {
      const days = 7;
      const labels = [];
      const datasets = [
        {
          label: 'Bình thường',
          backgroundColor: chartColors.clean.light,
          borderColor: chartColors.clean.border,
          data: [],
          tension: 0.4
        },
        {
          label: 'Xúc phạm',
          backgroundColor: chartColors.offensive.light,
          borderColor: chartColors.offensive.border,
          data: [],
          tension: 0.4
        },
        {
          label: 'Thù ghét',
          backgroundColor: chartColors.hate.light,
          borderColor: chartColors.hate.border,
          data: [],
          tension: 0.4
        },
        {
          label: 'Spam',
          backgroundColor: chartColors.spam.light,
          borderColor: chartColors.spam.border,
          data: [],
          tension: 0.4
        }
      ];
      
      const now = new Date();
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' }));
        
        // Generate random data with realistic trends
        datasets[0].data.push(Math.floor(Math.random() * 30) + 50); // Clean: 50-80
        datasets[1].data.push(Math.floor(Math.random() * 10) + 5);  // Offensive: 5-15
        datasets[2].data.push(Math.floor(Math.random() * 3) + 1);   // Hate: 1-4
        datasets[3].data.push(Math.floor(Math.random() * 8) + 3);   // Spam: 3-11
      }
      
      return { labels, datasets };
    }
    
    function generateDistributionData() {
      // Generate data for pie chart
      const total = 538;
      const cleanCount = 458;
      const offensiveCount = 32;
      const hateCount = 7;
      const spamCount = 41;
      
      return {
        labels: ['Bình thường', 'Xúc phạm', 'Thù ghét', 'Spam'],
        datasets: [{
          data: [cleanCount, offensiveCount, hateCount, spamCount],
          backgroundColor: [
            chartColors.clean.main,
            chartColors.offensive.main,
            chartColors.hate.main,
            chartColors.spam.main
          ],
          borderColor: [
            chartColors.clean.border,
            chartColors.offensive.border,
            chartColors.hate.border,
            chartColors.spam.border
          ],
          borderWidth: 1
        }]
      };
    }
    
    // Render Timeline Chart
    function renderTimelineChart() {
      const ctx = document.getElementById('timeline-chart');
      if (!ctx) return;
      
      const data = generateTimelineData();
      
      const timelineChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          plugins: {
            tooltip: {
              usePointStyle: true,
              callbacks: {
                title: function(context) {
                  return context[0].label;
                },
                label: function(context) {
                  return `${context.dataset.label}: ${context.parsed.y}`;
                }
              }
            },
            legend: {
              position: 'bottom',
              labels: {
                usePointStyle: true,
                padding: 20
              }
            }
          },
          scales: {
            x: {
              grid: {
                display: false
              }
            },
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(0, 0, 0, 0.05)'
              }
            }
          }
        }
      });
      
      // Add event handlers for chart action buttons
      const chartActions = document.querySelectorAll('.chart-action');
      chartActions.forEach(action => {
        action.addEventListener('click', function() {
          const chartType = this.getAttribute('data-type');
          
          // Update active state
          chartActions.forEach(btn => btn.setAttribute('data-active', 'false'));
          this.setAttribute('data-active', 'true');
          
          // Change chart type
          timelineChart.config.type = chartType;
          timelineChart.update();
        });
      });
    }
    
    // Render Distribution Chart
    function renderDistributionChart() {
      const ctx = document.getElementById('distribution-chart');
      if (!ctx) return;
      
      const data = generateDistributionData();
      
      const distributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '70%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 20
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.parsed || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          },
          elements: {
            arc: {
              borderWidth: 1
            }
          }
        }
      });
    }
    
    // Initialize History Table
    function initializeHistoryTable() {
      const tableBody = document.querySelector('.data-table tbody');
      if (!tableBody) return;
      
      // Sample data for the table
      const sampleData = [
        {
          time: '15:32 - 15/03/2025',
          platform: 'facebook',
          content: 'Sản phẩm này thật tuyệt vời, tôi rất hài lòng!',
          classification: 'clean',
          confidence: 0.94
        },
        {
          time: '14:28 - 15/03/2025',
          platform: 'youtube',
          content: 'Video này thật vô dụng, ai làm thế này chắc ngu lắm',
          classification: 'offensive',
          confidence: 0.87
        },
        {
          time: '13:15 - 15/03/2025',
          platform: 'twitter',
          content: 'GIẢM GIÁ 80% TẤT CẢ SẢN PHẨM! MUA NGAY KẺO HẾT: https://example.com',
          classification: 'spam',
          confidence: 0.93
        },
        {
          time: '11:42 - 15/03/2025',
          platform: 'facebook',
          content: 'Những người như thế này nên bị cấm sử dụng mạng xã hội vĩnh viễn',
          classification: 'hate',
          confidence: 0.79
        },
        {
          time: '10:30 - 15/03/2025',
          platform: 'youtube',
          content: 'Video này giúp mình hiểu rõ hơn về chủ đề, cảm ơn tác giả!',
          classification: 'clean',
          confidence: 0.96
        },
        {
          time: '09:15 - 15/03/2025',
          platform: 'twitter',
          content: 'Thời tiết hôm nay thật đẹp, hi vọng mọi người có một ngày tốt lành',
          classification: 'clean',
          confidence: 0.98
        },
        {
          time: '20:45 - 14/03/2025',
          platform: 'facebook',
          content: 'KIẾM 5 TRIỆU MỖI NGÀY VỚI PHƯƠNG PHÁP ĐƠN GIẢN! LIÊN HỆ NGAY: 09812345xx',
          classification: 'spam',
          confidence: 0.95
        }
      ];
      
      // Generate table rows
      let tableHTML = '';
      sampleData.forEach(item => {
        const classLabel = {
          'clean': 'Bình thường',
          'offensive': 'Xúc phạm',
          'hate': 'Thù ghét',
          'spam': 'Spam'
        };
        
        const platformIcon = {
          'facebook': '<img src="../icons/facebook.png" alt="Facebook" width="16">',
          'youtube': '<img src="../icons/youtube.png" alt="YouTube" width="16">',
          'twitter': '<img src="../icons/twitter.png" alt="Twitter" width="16">'
        };
        
        tableHTML += `
          <tr>
            <td>${item.time}</td>
            <td>${platformIcon[item.platform]} ${item.platform.charAt(0).toUpperCase() + item.platform.slice(1)}</td>
            <td>${item.content}</td>
            <td><span class="detection-result ${item.classification}">${classLabel[item.classification]}</span></td>
            <td>${(item.confidence * 100).toFixed(1)}%</td>
            <td>
              <button class="table-action" title="Xem chi tiết">👁️</button>
              <button class="table-action" title="Xuất">📤</button>
              <button class="table-action" title="Báo cáo không chính xác">🚩</button>
            </td>
          </tr>
        `;
      });
      
      tableBody.innerHTML = tableHTML;
    }
    
    // Initialize charts when the page loads
    renderTimelineChart();
    renderDistributionChart();
    initializeHistoryTable();
    
    // Handle date range change
    const dateRange = document.getElementById('date-range');
    if (dateRange) {
      dateRange.addEventListener('change', function() {
        // In a real application, this would trigger an API call to get new data
        console.log(`Date range changed to: ${this.value}`);
        
        // For demo purposes, we'll just update the charts with new random data
        renderTimelineChart();
        renderDistributionChart();
      });
    }
    
    // Handle refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function() {
        // Show loading state
        this.innerHTML = '<span class="loading-spinner"></span> Đang tải...';
        this.disabled = true;
        
        // Simulate loading
        setTimeout(() => {
          renderTimelineChart();
          renderDistributionChart();
          initializeHistoryTable();
          
          // Reset button
          this.innerHTML = 'Làm mới';
          this.disabled = false;
        }, 1000);
      });
    }
    
    // Handle navigation
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const sections = document.querySelectorAll('.dashboard-section');
    
    navLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        
        // Update active navigation
        navLinks.forEach(link => link.parentElement.classList.remove('active'));
        this.parentElement.classList.add('active');
        
        // Show target section
        sections.forEach(section => {
          section.classList.remove('active');
          if (section.id === targetId) {
            section.classList.add('active');
          }
        });
      });
    });
  });
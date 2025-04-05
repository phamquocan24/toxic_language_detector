// scripts/admin_charts.js
document.addEventListener('DOMContentLoaded', () => {
    // Chart.js Configuration
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
      },
      // Additional colors for admin charts
      users: {
        main: 'rgba(33, 150, 243, 0.7)',
        light: 'rgba(33, 150, 243, 0.1)',
        border: 'rgba(33, 150, 243, 1)'
      },
      facebook: {
        main: 'rgba(59, 89, 152, 0.7)',
        light: 'rgba(59, 89, 152, 0.1)',
        border: 'rgba(59, 89, 152, 1)'
      },
      youtube: {
        main: 'rgba(255, 0, 0, 0.7)',
        light: 'rgba(255, 0, 0, 0.1)', 
        border: 'rgba(255, 0, 0, 1)'
      },
      twitter: {
        main: 'rgba(29, 161, 242, 0.7)',
        light: 'rgba(29, 161, 242, 0.1)',
        border: 'rgba(29, 161, 242, 1)'
      }
    };
    
    // Generate data for Activity Chart
    function generateActivityData() {
      const days = 7;
      const labels = [];
      const datasets = [
        {
          label: 'Lượt quét',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          borderColor: 'rgba(33, 150, 243, 0.7)',
          data: [],
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'Phát hiện độc hại',
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          borderColor: 'rgba(244, 67, 54, 0.7)',
          data: [],
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: 'Người dùng hoạt động',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderColor: 'rgba(76, 175, 80, 0.7)',
          data: [],
          tension: 0.4,
          yAxisID: 'y1'
        }
      ];
      
      const now = new Date();
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' }));
        
        // Generate random data
        datasets[0].data.push(Math.floor(Math.random() * 1000) + 3000); // Scans: 3000-4000
        datasets[1].data.push(Math.floor(Math.random() * 300) + 200);   // Toxic: 200-500
        datasets[2].data.push(Math.floor(Math.random() * 30) + 100);    // Users: 100-130
      }
      
      return { labels, datasets };
    }
    
    // Generate Platform Distribution data
    function generatePlatformData() {
      return {
        labels: ['Facebook', 'YouTube', 'Twitter'],
        datasets: [{
          data: [60, 25, 15],
          backgroundColor: [
            chartColors.facebook.main,
            chartColors.youtube.main,
            chartColors.twitter.main
          ],
          borderColor: [
            chartColors.facebook.border,
            chartColors.youtube.border,
            chartColors.twitter.border
          ],
          borderWidth: 1
        }]
      };
    }
    
    // Generate Categories Distribution data
    function generateCategoriesData() {
      return {
        labels: ['Bình thường', 'Xúc phạm', 'Thù ghét', 'Spam'],
        datasets: [{
          data: [80, 10, 3, 7],
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
    
    // Generate Performance data
    function generatePerformanceData() {
      const days = 7;
      const labels = [];
      const datasets = [
        {
          label: 'Độ chính xác',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          borderColor: 'rgba(33, 150, 243, 0.7)',
          data: [],
          tension: 0.4
        },
        {
          label: 'Độ chuẩn xác',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderColor: 'rgba(76, 175, 80, 0.7)',
          data: [],
          tension: 0.4
        },
        {
          label: 'Độ phủ',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          borderColor: 'rgba(255, 152, 0, 0.7)',
          data: [],
          tension: 0.4
        },
        {
          label: 'F1 Score',
          backgroundColor: 'rgba(156, 39, 176, 0.1)',
          borderColor: 'rgba(156, 39, 176, 0.7)',
          data: [],
          tension: 0.4
        }
      ];
      
      const now = new Date();
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' }));
        
        // Generate realistic performance metrics with slight variations
        datasets[0].data.push(90 + Math.random() * 5);  // Accuracy: 90-95%
        datasets[1].data.push(89 + Math.random() * 5);  // Precision: 89-94%
        datasets[2].data.push(92 + Math.random() * 5);  // Recall: 92-97%
        datasets[3].data.push(91 + Math.random() * 4);  // F1: 91-95%
      }
      
      return { labels, datasets };
    }
    
    // Generate Time Distribution data
    function generateTimeDistributionData(view = 'day') {
      let labels = [];
      let data = [];
      
      if (view === 'hour') {
        // Hours in a day
        for (let i = 0; i < 24; i++) {
          labels.push(`${i}:00`);
          
          // More activity during daytime (8AM-10PM)
          let baseValue = 100;
          if (i >= 8 && i <= 22) {
            baseValue = 300 + Math.sin((i - 8) * Math.PI / 14) * 200;
          }
          
          data.push(Math.round(baseValue + Math.random() * 50));
        }
      } else if (view === 'week') {
        // Days of week
        labels = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN'];
        
        // More activity on weekdays
        data = [
          800 + Math.random() * 100,  // Monday
          750 + Math.random() * 100,  // Tuesday
          820 + Math.random() * 100,  // Wednesday
          780 + Math.random() * 100,  // Thursday
          850 + Math.random() * 100,  // Friday
          600 + Math.random() * 100,  // Saturday
          500 + Math.random() * 100   // Sunday
        ];
      } else {
        // Days in a month (last 30 days)
        const now = new Date();
        for (let i = 29; i >= 0; i--) {
          const date = new Date(now);
          date.setDate(date.getDate() - i);
          labels.push(date.getDate().toString());
          
          // Random data with weekend dips
          const dayOfWeek = date.getDay();
          let baseValue = 700;
          
          // Weekend adjustment
          if (dayOfWeek === 0 || dayOfWeek === 6) {
            baseValue = 500;
          }
          
          data.push(Math.round(baseValue + Math.random() * 200));
        }
      }
      
      return {
        labels,
        datasets: [{
          label: 'Hoạt động',
          backgroundColor: 'rgba(33, 150, 243, 0.5)',
          borderColor: 'rgba(33, 150, 243, 1)',
          data: data,
          borderRadius: 5
        }]
      };
    }
    
    // Render Activity Chart
    function renderActivityChart() {
      const ctx = document.getElementById('activity-chart');
      if (!ctx) return;
      
      const data = generateActivityData();
      
      const activityChart = new Chart(ctx, {
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
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: 'Lượt quét / Phát hiện',
                color: '#607D8B'
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.05)'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: 'Người dùng',
                color: '#607D8B'
              },
              grid: {
                drawOnChartArea: false
              }
            }
          }
        }
      });
      
      // Add event handlers for chart tab buttons
      const chartTabs = document.querySelectorAll('.chart-tab');
      chartTabs.forEach(tab => {
        tab.addEventListener('click', function() {
          const period = this.getAttribute('data-period') || 'day';
          
          // Update active state
          chartTabs.forEach(btn => btn.classList.remove('active'));
          this.classList.add('active');
          
          // Update chart data
          // In a real app, this would fetch new data from the API
          console.log(`Switching to ${period} view`);
          
          // For demo, just regenerate random data
          const newData = generateActivityData();
          activityChart.data.labels = newData.labels;
          activityChart.data.datasets.forEach((dataset, i) => {
            dataset.data = newData.datasets[i].data;
          });
          activityChart.update();
        });
      });
    }
    
    // Render Platforms Chart
    function renderPlatformsChart() {
      const ctx = document.getElementById('platforms-chart');
      if (!ctx) return;
      
      const data = generatePlatformData();
      
      const platformsChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '60%',
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
                  return `${label}: ${percentage}%`;
                }
              }
            }
          }
        }
      });
    }
    
    // Render Categories Chart
    function renderCategoriesChart() {
      const ctx = document.getElementById('categories-chart');
      if (!ctx) return;
      
      const data = generateCategoriesData();
      
      const categoriesChart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
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
                  return `${label}: ${percentage}%`;
                }
              }
            }
          }
        }
      });
    }
    
    // Render Performance Chart
    function renderPerformanceChart() {
      const ctx = document.getElementById('performance-chart');
      if (!ctx) return;
      
      const data = generatePerformanceData();
      
      const performanceChart = new Chart(ctx, {
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
              min: 85,
              max: 100,
              grid: {
                color: 'rgba(0, 0, 0, 0.05)'
              }
            }
          }
        }
      });
    }
    
    // Render Time Distribution Chart
    function renderTimeDistributionChart() {
      const ctx = document.getElementById('time-distribution-chart');
      if (!ctx) return;
      
      const data = generateTimeDistributionData('day');
      
      const timeDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              grid: {
                display: false
              }
            },
            y: {
              grid: {
                color: 'rgba(0, 0, 0, 0.05)'
              }
            }
          }
        }
      });
      
      // Add event handlers for chart tab buttons
      const chartTabs = document.querySelectorAll('.chart-tabs.small .chart-tab');
      chartTabs.forEach(tab => {
        tab.addEventListener('click', function() {
          const view = this.getAttribute('data-view') || 'day';
          
          // Update active state
          chartTabs.forEach(btn => btn.classList.remove('active'));
          this.classList.add('active');
          
          // Update chart data
          const newData = generateTimeDistributionData(view);
          timeDistributionChart.data.labels = newData.labels;
          timeDistributionChart.data.datasets[0].data = newData.datasets[0].data;
          timeDistributionChart.update();
        });
      });
    }
    
    // Generate and render heatmap
    function renderHeatmap() {
      const heatmapGrid = document.querySelector('.heatmap-grid');
      if (!heatmapGrid) return;
      
      // Clear existing cells
      heatmapGrid.innerHTML = '';
      
      // Generate heatmap data (7 days x 24 hours)
      for (let hour = 0; hour < 24; hour++) {
        for (let day = 0; day < 7; day++) {
          // Generate intensity (higher during working hours)
          let intensity = 0.1; // Base intensity
          
          // Increase intensity during working hours
          if (hour >= 8 && hour <= 22) {
            intensity = 0.3 + Math.random() * 0.6;
            
            // Lower intensity on weekends
            if (day >= 5) {
              intensity *= 0.5;
            }
          }
          
          // Create cell
          const cell = document.createElement('div');
          cell.className = 'heatmap-cell';
          cell.style.backgroundColor = `rgba(76, 175, 80, ${intensity})`;
          
          // Add tooltip
          const dayNames = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN'];
          const toxicCount = Math.round(intensity * 100);
          cell.setAttribute('data-tooltip', `${dayNames[day]} ${hour}:00 - ${toxicCount} phát hiện`);
          
          heatmapGrid.appendChild(cell);
        }
      }
    }
    
    // Initialize all charts
    function initializeCharts() {
      renderActivityChart();
      renderPlatformsChart();
      renderCategoriesChart();
      renderPerformanceChart();
      renderTimeDistributionChart();
      renderHeatmap();
    }
    
    // Initialize on load
    initializeCharts();
    
    // Handle refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function() {
        // Show loading state
        this.innerHTML = '<span class="loading-spinner"></span> Đang tải...';
        this.disabled = true;
        
        // Simulate loading
        setTimeout(() => {
          initializeCharts();
          
          // Reset button
          this.innerHTML = 'Làm mới';
          this.disabled = false;
        }, 1000);
      });
    }
  });
  
// scripts/settings.js

/**
 * Initialize settings functionality
 */
function initializeSettings() {
    const settingsSection = document.getElementById('settings');
    if (!settingsSection) return;
    
    // Get settings elements
    const apiKeyInput = document.getElementById('api-key');
    const apiUrlInput = document.getElementById('api-url');
    const modelThresholdInput = document.getElementById('model-threshold');
    const emailNotificationsToggle = document.getElementById('email-notifications');
    const emailFrequencySelect = document.getElementById('email-frequency');
    const emailAddressInput = document.getElementById('email-address');
    const saveSettingsBtn = document.getElementById('save-settings');
    const testApiBtn = document.getElementById('test-api');
    const resetSettingsBtn = document.getElementById('reset-settings');
    
    // Load current settings
    loadSettings();
    
    // Add event listeners
    if (saveSettingsBtn) {
      saveSettingsBtn.addEventListener('click', saveSettings);
    }
    
    if (testApiBtn) {
      testApiBtn.addEventListener('click', testApiConnection);
    }
    
    if (resetSettingsBtn) {
      resetSettingsBtn.addEventListener('click', resetSettings);
    }
    
    // Toggle email settings visibility based on notifications toggle
    if (emailNotificationsToggle) {
      emailNotificationsToggle.addEventListener('change', function() {
        const emailSettingsContainer = document.querySelector('.email-settings');
        if (emailSettingsContainer) {
          emailSettingsContainer.style.display = this.checked ? 'block' : 'none';
        }
      });
    }
    
    /**
     * Load settings from storage or set defaults
     */
    function loadSettings() {
      chrome.storage.sync.get('adminSettings', (data) => {
        const settings = data.adminSettings || {
          apiKey: 'your-api-key',
          apiUrl: 'https://your-huggingface-space-url.hf.space',
          modelThreshold: 0.7,
          emailNotifications: false,
          emailFrequency: 'daily',
          emailAddress: ''
        };
        
        if (apiKeyInput) apiKeyInput.value = settings.apiKey;
        if (apiUrlInput) apiUrlInput.value = settings.apiUrl;
        if (modelThresholdInput) modelThresholdInput.value = settings.modelThreshold;
        if (emailNotificationsToggle) emailNotificationsToggle.checked = settings.emailNotifications;
        if (emailFrequencySelect) emailFrequencySelect.value = settings.emailFrequency;
        if (emailAddressInput) emailAddressInput.value = settings.emailAddress;
        
        // Update email settings visibility
        const emailSettingsContainer = document.querySelector('.email-settings');
        if (emailSettingsContainer) {
          emailSettingsContainer.style.display = settings.emailNotifications ? 'block' : 'none';
        }
      });
    }
    
    /**
     * Save settings to storage
     */
    function saveSettings() {
      // Validate inputs
      if (apiKeyInput && apiKeyInput.value.trim() === '') {
        showNotification('API Key không được để trống', 'error');
        return;
      }
      
      if (apiUrlInput && apiUrlInput.value.trim() === '') {
        showNotification('API URL không được để trống', 'error');
        return;
      }
      
      if (emailNotificationsToggle && emailNotificationsToggle.checked) {
        if (emailAddressInput && !isValidEmail(emailAddressInput.value)) {
          showNotification('Email không hợp lệ', 'error');
          return;
        }
      }
      
      // Create settings object
      const settings = {
        apiKey: apiKeyInput ? apiKeyInput.value : 'your-api-key',
        apiUrl: apiUrlInput ? apiUrlInput.value : 'https://your-huggingface-space-url.hf.space',
        modelThreshold: modelThresholdInput ? parseFloat(modelThresholdInput.value) : 0.7,
        emailNotifications: emailNotificationsToggle ? emailNotificationsToggle.checked : false,
        emailFrequency: emailFrequencySelect ? emailFrequencySelect.value : 'daily',
        emailAddress: emailAddressInput ? emailAddressInput.value : ''
      };
      
      // Save to storage
      chrome.storage.sync.set({ adminSettings: settings }, () => {
        showNotification('Đã lưu cài đặt thành công', 'success');
      });
    }
    
    /**
     * Test API connection
     */
    function testApiConnection() {
      const apiUrl = apiUrlInput ? apiUrlInput.value : '';
      const apiKey = apiKeyInput ? apiKeyInput.value : '';
      
      if (!apiUrl || !apiKey) {
        showNotification('API URL và API Key không được để trống', 'error');
        return;
      }
      
      // Show loading state
      if (testApiBtn) {
        testApiBtn.disabled = true;
        testApiBtn.innerHTML = '<span class="loading-spinner"></span> Đang kiểm tra...';
      }
      
      // Test API connection with a simple request
      fetch(`${apiUrl}/extension/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({
          text: 'Đây là văn bản kiểm tra API.',
          platform: 'test',
          platform_id: 'test',
          metadata: { source: 'test' }
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        showNotification('Kết nối API thành công!', 'success');
      })
      .catch(error => {
        showNotification(`Lỗi kết nối: ${error.message}`, 'error');
      })
      .finally(() => {
        // Reset button state
        if (testApiBtn) {
          testApiBtn.disabled = false;
          testApiBtn.textContent = 'Kiểm tra kết nối';
        }
      });
    }
    
    /**
     * Reset settings to defaults
     */
    function resetSettings() {
      // Show confirmation dialog
      showModal(
        'Đặt lại cài đặt',
        '<p>Bạn có chắc chắn muốn đặt lại tất cả các cài đặt về giá trị mặc định?</p>',
        () => {
          // Default settings
          const defaultSettings = {
            apiKey: 'your-api-key',
            apiUrl: 'https://your-huggingface-space-url.hf.space',
            modelThreshold: 0.7,
            emailNotifications: false,
            emailFrequency: 'daily',
            emailAddress: ''
          };
          
          // Save defaults to storage
          chrome.storage.sync.set({ adminSettings: defaultSettings }, () => {
            // Update UI
            loadSettings();
            showNotification('Đã đặt lại cài đặt về mặc định', 'success');
          });
        }
      );
    }
    
    /**
     * Validate email address
     * @param {string} email - Email address to validate
     * @returns {boolean} - True if valid, false otherwise
     */
    function isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }
  }
  
  // Create settings section for admin dashboard
  function createSettingsSection() {
    return `
      <div class="section-header with-actions">
        <h3>Cài đặt hệ thống</h3>
        <div class="section-actions">
          <button id="reset-settings" class="secondary-button">Đặt lại mặc định</button>
          <button id="save-settings" class="primary-button">Lưu cài đặt</button>
        </div>
      </div>
      
      <div class="settings-container">
        <div class="settings-card">
          <div class="settings-card-header">
            <h4>API & Tích hợp</h4>
          </div>
          <div class="settings-card-body">
            <div class="form-group">
              <label for="api-key">API Key</label>
              <div class="input-with-action">
                <input type="password" id="api-key" placeholder="API Key của bạn">
                <button class="input-action toggle-password">👁️</button>
              </div>
            </div>
            <div class="form-group">
              <label for="api-url">API URL</label>
              <input type="text" id="api-url" placeholder="https://your-huggingface-space-url.hf.space">
            </div>
            <div class="form-group">
              <label for="model-threshold">Ngưỡng phát hiện</label>
              <input type="range" id="model-threshold" min="0.5" max="0.9" step="0.05" value="0.7">
              <div class="range-value"><span id="threshold-value">0.7</span></div>
            </div>
            <div class="form-actions">
              <button id="test-api" class="secondary-button">Kiểm tra kết nối</button>
            </div>
          </div>
        </div>
        
        <div class="settings-card">
          <div class="settings-card-header">
            <h4>Thông báo</h4>
          </div>
          <div class="settings-card-body">
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" id="email-notifications">
                <span class="checkbox-custom"></span>
                <span>Gửi thông báo qua email</span>
              </label>
            </div>
            
            <div class="email-settings" style="display: none;">
              <div class="form-group">
                <label for="email-frequency">Tần suất</label>
                <select id="email-frequency">
                  <option value="realtime">Thời gian thực</option>
                  <option value="hourly">Hàng giờ</option>
                  <option value="daily" selected>Hàng ngày</option>
                  <option value="weekly">Hàng tuần</option>
                </select>
              </div>
              <div class="form-group">
                <label for="email-address">Địa chỉ email</label>
                <input type="email" id="email-address" placeholder="your-email@example.com">
              </div>
            </div>
          </div>
        </div>
        
        <div class="settings-card">
          <div class="settings-card-header">
            <h4>Phát hiện</h4>
          </div>
          <div class="settings-card-body">
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" id="detect-offensive" checked>
                <span class="checkbox-custom"></span>
                <span>Phát hiện nội dung xúc phạm</span>
              </label>
            </div>
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" id="detect-hate" checked>
                <span class="checkbox-custom"></span>
                <span>Phát hiện nội dung thù ghét</span>
              </label>
            </div>
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" id="detect-spam" checked>
                <span class="checkbox-custom"></span>
                <span>Phát hiện spam</span>
              </label>
            </div>
            <div class="form-group">
              <label for="detection-action">Hành động mặc định</label>
              <select id="detection-action">
                <option value="highlight">Chỉ đánh dấu</option>
                <option value="blur" selected>Làm mờ và cảnh báo</option>
                <option value="hide">Ẩn hoàn toàn</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="settings-card">
          <div class="settings-card-header">
            <h4>Cơ sở dữ liệu</h4>
          </div>
          <div class="settings-card-body">
            <div class="db-status">
              <div class="status-item">
                <div class="status-label">Kích thước cơ sở dữ liệu</div>
                <div class="status-value">24.7 MB</div>
              </div>
              <div class="status-item">
                <div class="status-label">Số lượng mẫu</div>
                <div class="status-value">12,457</div>
              </div>
              <div class="status-item">
                <div class="status-label">Cập nhật gần nhất</div>
                <div class="status-value">15/03/2025 09:45</div>
              </div>
            </div>
            <div class="form-actions">
              <button class="secondary-button">Sao lưu dữ liệu</button>
              <button class="secondary-button warning">Xóa dữ liệu</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  
  // Add settings to admin dashboard
  document.addEventListener('DOMContentLoaded', () => {
    const settingsSection = document.getElementById('settings');
    if (settingsSection) {
      settingsSection.innerHTML = createSettingsSection();
      
      // Initialize settings
      initializeSettings();
      
      // Initialize toggle password visibility
      const togglePassword = document.querySelector('.toggle-password');
      if (togglePassword) {
        togglePassword.addEventListener('click', function() {
          const apiKeyInput = document.getElementById('api-key');
          if (apiKeyInput) {
            if (apiKeyInput.type === 'password') {
              apiKeyInput.type = 'text';
              this.textContent = '👁️‍🗨️';
            } else {
              apiKeyInput.type = 'password';
              this.textContent = '👁️';
            }
          }
        });
      }
      
      // Initialize threshold display
      const thresholdInput = document.getElementById('model-threshold');
      const thresholdValue = document.getElementById('threshold-value');
      if (thresholdInput && thresholdValue) {
        thresholdInput.addEventListener('input', function() {
          thresholdValue.textContent = this.value;
        });
      }
    }
  });
// scripts/admin_dashboard.js
document.addEventListener('DOMContentLoaded', () => {
  // Check authentication
  chrome.storage.sync.get('authData', (data) => {
    if (!data.authData) {
      // Redirect to login if not authenticated
      window.location.href = 'login.html';
      return;
    }
    
    const { token, username, role, expiresAt } = data.authData;
    
    // Check if token is expired
    if (expiresAt && expiresAt < Date.now()) {
      // Token expired, redirect to login
      chrome.storage.sync.remove('authData');
      window.location.href = 'login.html';
      return;
    }
    
    // Check if user trying to access admin dashboard without admin role
    if (role !== 'admin') {
      window.location.href = 'user_dashboard.html';
      return;
    }
    
    // Populate user info
    populateUserInfo(username, role);
  });
  
  // Populate user information in sidebar
  function populateUserInfo(username, role) {
    const userNameElement = document.querySelector('.user-name');
    const userRoleElement = document.querySelector('.user-role');
    
    if (userNameElement) {
      userNameElement.textContent = username;
    }
    
    if (userRoleElement) {
      userRoleElement.textContent = role === 'admin' ? 'Quản trị viên' : 'Người dùng';
    }
  }
  
  // Handle logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      // Show confirmation dialog
      if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
        // Clear authentication data
        chrome.storage.sync.remove('authData', () => {
          // Redirect to login page
          window.location.href = 'login.html';
        });
      }
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
  
  // Initialize export functionality
  initializeExport();
  
  // Initialize user management
  initializeUserManagement();
  
  // Initialize alerts management
  initializeAlerts();
  
  // Initialize reports functionality
  initializeReports();
  
  // Initialize settings page
  initializeSettings();
});

// Export functionality
function initializeExport() {
  const exportAllBtn = document.getElementById('export-all-btn');
  if (!exportAllBtn) return;
  
  exportAllBtn.addEventListener('click', () => {
    // Create export menu options
    const menuOptions = [
      { format: 'excel', label: 'Excel (.xlsx)', icon: '📊' },
      { format: 'csv', label: 'CSV (.csv)', icon: '📋' },
      { format: 'pdf', label: 'PDF (.pdf)', icon: '📄' },
      { format: 'print', label: 'In báo cáo', icon: '🖨️' }
    ];
    
    // Create dropdown menu
    const menu = document.createElement('div');
    menu.className = 'export-menu';
    
    menuOptions.forEach(option => {
      const menuItem = document.createElement('div');
      menuItem.className = 'export-option';
      menuItem.innerHTML = `<span class="export-icon">${option.icon}</span> ${option.label}`;
      menuItem.addEventListener('click', () => exportDashboard(option.format));
      menu.appendChild(menuItem);
    });
    
    // Remove existing menu if any
    const existingMenu = document.querySelector('.export-menu');
    if (existingMenu) {
      existingMenu.remove();
    }
    
    // Add menu to DOM
    exportAllBtn.parentNode.style.position = 'relative';
    exportAllBtn.parentNode.appendChild(menu);
    
    // Hide menu when clicking outside
    document.addEventListener('click', (event) => {
      if (!menu.contains(event.target) && event.target !== exportAllBtn) {
        menu.remove();
      }
    }, { once: true });
  });
}

// Export dashboard data in different formats
function exportDashboard(format) {
  // Get current date for filename
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10);
  const filename = `toxic-detector-dashboard-${dateStr}`;
  
  // Show loading notification
  showNotification('Đang chuẩn bị báo cáo...', 'info');
  
  // Simulate processing delay
  setTimeout(() => {
    // Handle different export formats
    switch (format) {
      case 'excel':
        showNotification('Đã xuất báo cáo Excel thành công', 'success');
        break;
      case 'csv':
        showNotification('Đã xuất báo cáo CSV thành công', 'success');
        break;
      case 'pdf':
        showNotification('Đã xuất báo cáo PDF thành công', 'success');
        break;
      case 'print':
        window.print();
        break;
    }
  }, 1500);
}

// User management functionality
function initializeUserManagement() {
  // Get user table
  const userTable = document.querySelector('#users .data-table tbody');
  if (!userTable) return;
  
  // Attach event listeners to user action buttons
  const actionButtons = userTable.querySelectorAll('.table-action');
  
  actionButtons.forEach(button => {
    button.addEventListener('click', function() {
      const action = this.getAttribute('title');
      const row = this.closest('tr');
      const userId = row.cells[0].textContent;
      const username = row.cells[1].textContent.trim();
      
      switch (action) {
        case 'Chỉnh sửa':
          editUser(userId, username);
          break;
        case 'Đặt lại mật khẩu':
          resetPassword(userId, username);
          break;
        case 'Vô hiệu hóa':
          disableUser(userId, username, row);
          break;
        case 'Kích hoạt':
          enableUser(userId, username, row);
          break;
      }
    });
  });
  
  // User search functionality
  const searchInput = document.querySelector('#users .search-box input');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      const rows = userTable.querySelectorAll('tr');
      
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
  
  // Add user button
  const addUserBtn = document.querySelector('#users .primary-button');
  if (addUserBtn) {
    addUserBtn.addEventListener('click', () => {
      showAddUserModal();
    });
  }
}

// Edit user
function editUser(userId, username) {
  showModal(
    'Chỉnh sửa người dùng',
    `
    <form id="edit-user-form">
      <div class="form-group">
        <label for="edit-username">Tên người dùng</label>
        <input type="text" id="edit-username" value="${username}" required>
      </div>
      <div class="form-group">
        <label for="edit-email">Email</label>
        <input type="email" id="edit-email" value="${username}@example.com" required>
      </div>
      <div class="form-group">
        <label for="edit-role">Vai trò</label>
        <select id="edit-role">
          <option value="user">Người dùng</option>
          <option value="moderator">Người kiểm duyệt</option>
          <option value="admin">Quản trị viên</option>
        </select>
      </div>
    </form>
    `,
    () => {
      // Handle form submission
      showNotification(`Đã cập nhật thông tin người dùng ${username}`, 'success');
    }
  );
}

// Reset password
function resetPassword(userId, username) {
  showModal(
    'Đặt lại mật khẩu',
    `
    <p>Bạn có chắc chắn muốn đặt lại mật khẩu cho người dùng <strong>${username}</strong>?</p>
    <p>Mật khẩu mới sẽ được gửi đến email của người dùng.</p>
    `,
    () => {
      // Handle confirmation
      showNotification(`Đã đặt lại mật khẩu cho người dùng ${username}`, 'success');
    }
  );
}

// Disable user
function disableUser(userId, username, row) {
  showModal(
    'Vô hiệu hóa người dùng',
    `
    <p>Bạn có chắc chắn muốn vô hiệu hóa người dùng <strong>${username}</strong>?</p>
    <p>Người dùng sẽ không thể đăng nhập cho đến khi được kích hoạt lại.</p>
    `,
    () => {
      // Update UI
      const statusCell = row.querySelector('.status');
      statusCell.textContent = 'Không hoạt động';
      statusCell.className = 'status inactive';
      
      // Update action buttons
      const actionsCell = row.querySelector('.actions');
      actionsCell.innerHTML = `
        <button class="table-action" title="Chỉnh sửa">✏️</button>
        <button class="table-action" title="Đặt lại mật khẩu">🔑</button>
        <button class="table-action" title="Kích hoạt">✓</button>
      `;
      
      // Add event listeners to new buttons
      initializeUserManagement();
      
      showNotification(`Đã vô hiệu hóa người dùng ${username}`, 'success');
    }
  );
}

// Enable user
function enableUser(userId, username, row) {
  showModal(
    'Kích hoạt người dùng',
    `
    <p>Bạn có chắc chắn muốn kích hoạt người dùng <strong>${username}</strong>?</p>
    `,
    () => {
      // Update UI
      const statusCell = row.querySelector('.status');
      statusCell.textContent = 'Hoạt động';
      statusCell.className = 'status active';
      
      // Update action buttons
      const actionsCell = row.querySelector('.actions');
      actionsCell.innerHTML = `
        <button class="table-action" title="Chỉnh sửa">✏️</button>
        <button class="table-action" title="Đặt lại mật khẩu">🔑</button>
        <button class="table-action" title="Vô hiệu hóa">🚫</button>
      `;
      
      // Add event listeners to new buttons
      initializeUserManagement();
      
      showNotification(`Đã kích hoạt người dùng ${username}`, 'success');
    }
  );
}

// Show add user modal
function showAddUserModal() {
  showModal(
    'Thêm người dùng mới',
    `
    <form id="add-user-form">
      <div class="form-group">
        <label for="add-username">Tên người dùng</label>
        <input type="text" id="add-username" required>
      </div>
      <div class="form-group">
        <label for="add-email">Email</label>
        <input type="email" id="add-email" required>
      </div>
      <div class="form-group">
        <label for="add-password">Mật khẩu</label>
        <input type="password" id="add-password" required>
      </div>
      <div class="form-group">
        <label for="add-role">Vai trò</label>
        <select id="add-role">
          <option value="user">Người dùng</option>
          <option value="moderator">Người kiểm duyệt</option>
          <option value="admin">Quản trị viên</option>
        </select>
      </div>
    </form>
    `,
    () => {
      // Get form values
      const username = document.getElementById('add-username').value;
      const email = document.getElementById('add-email').value;
      const role = document.getElementById('add-role').value;
      
      // In a real app, this would send data to the API
      console.log('Adding new user:', { username, email, role });
      
      // Show notification
      showNotification(`Đã thêm người dùng mới: ${username}`, 'success');
      
      // Refresh user list (in a real app, this would fetch updated data)
      // For demo, we'll just add a new row to the table
      const userTable = document.querySelector('#users .data-table tbody');
      if (userTable) {
        const newRow = document.createElement('tr');
        const nextId = userTable.querySelectorAll('tr').length + 1;
        
        newRow.innerHTML = `
          <td>${nextId}</td>
          <td class="with-avatar">
            <span class="avatar">👨</span> ${username}
          </td>
          <td>${email}</td>
          <td><span class="badge ${role}">${role === 'admin' ? 'Quản trị viên' : (role === 'moderator' ? 'Người kiểm duyệt' : 'Người dùng')}</span></td>
          <td><span class="status active">Hoạt động</span></td>
          <td>${new Date().toLocaleDateString('vi-VN')}</td>
          <td>Vừa tạo</td>
          <td class="actions">
            <button class="table-action" title="Chỉnh sửa">✏️</button>
            <button class="table-action" title="Đặt lại mật khẩu">🔑</button>
            <button class="table-action" title="Vô hiệu hóa">🚫</button>
          </td>
        `;
        
        userTable.appendChild(newRow);
        
        // Add event listeners to new row
        initializeUserManagement();
      }
    }
  );
}

// Alerts management
function initializeAlerts() {
  const alertsList = document.querySelector('.alerts-list');
  if (!alertsList) return;
  
  // Handle alert actions
  const alertActions = alertsList.querySelectorAll('.alert-action');
  
  alertActions.forEach(action => {
    action.addEventListener('click', function() {
      const alertItem = this.closest('.alert-item');
      const actionType = this.getAttribute('title');
      const alertTitle = alertItem.querySelector('.alert-title').textContent;
      
      switch (actionType) {
        case 'Đánh dấu đã đọc':
          alertItem.style.opacity = '0.6';
          showNotification('Đã đánh dấu cảnh báo là đã đọc', 'success');
          break;
        case 'Chi tiết':
          showAlertDetails(alertTitle, alertItem);
          break;
        case 'Chặn IP':
          showBlockIPModal(alertTitle);
          break;
        case 'Cảnh báo người dùng':
          showWarnUserModal(alertTitle);
          break;
        case 'Thêm vào cơ sở dữ liệu':
          showAddToDBModal(alertTitle);
          break;
      }
    });
  });
}

// Show alert details
function showAlertDetails(alertTitle, alertItem) {
  // Get alert type
  let alertType = 'default';
  if (alertItem.classList.contains('high')) alertType = 'high';
  if (alertItem.classList.contains('medium')) alertType = 'medium';
  if (alertItem.classList.contains('low')) alertType = 'low';
  
  // Create sample details based on alert type
  let detailsHTML = '';
  
  if (alertType === 'high') {
    detailsHTML = `
      <div class="alert-detail-section">
        <h4>Thông tin IP</h4>
        <p><strong>Địa chỉ IP:</strong> 192.168.1.45</p>
        <p><strong>Vị trí:</strong> Hà Nội, Việt Nam</p>
        <p><strong>ISP:</strong> Viettel</p>
      </div>
      <div class="alert-detail-section">
        <h4>Các bình luận có vấn đề</h4>
        <div class="comment-list">
          <div class="comment-item hate">
            <div class="comment-text">"Tôi ghét tất cả những ai nghĩ khác tôi, họ nên biến mất khỏi thế giới này"</div>
            <div class="comment-meta">Facebook - 12:30 15/03/2025</div>
          </div>
          <div class="comment-item hate">
            <div class="comment-text">"Dân tộc đó nên bị xóa sổ hoàn toàn, không còn một ai"</div>
            <div class="comment-meta">YouTube - 12:31 15/03/2025</div>
          </div>
          <div class="comment-item hate">
            <div class="comment-text">"Tôi muốn gây tổn hại cho tất cả những người không đồng ý với quan điểm của tôi"</div>
            <div class="comment-meta">Twitter - 12:33 15/03/2025</div>
          </div>
        </div>
      </div>
    `;
  } else if (alertType === 'medium') {
    detailsHTML = `
      <div class="alert-detail-section">
        <h4>Thông tin người dùng</h4>
        <p><strong>Tên người dùng:</strong> user123</p>
        <p><strong>Email:</strong> user123@example.com</p>
        <p><strong>Ngày đăng ký:</strong> 10/02/2025</p>
      </div>
      <div class="alert-detail-section">
        <h4>Lịch sử báo cáo</h4>
        <ul>
          <li>15/03/2025 - Báo cáo bởi user456: "Ngôn từ xúc phạm"</li>
          <li>14/03/2025 - Báo cáo bởi user789: "Bình luận gây khó chịu"</li>
          <li>12/03/2025 - Báo cáo bởi user234: "Ngôn từ không phù hợp"</li>
          <li>10/03/2025 - Báo cáo bởi user567: "Xúc phạm người khác"</li>
          <li>08/03/2025 - Báo cáo bởi user890: "Bình luận tiêu cực"</li>
        </ul>
      </div>
    `;
  } else {
    detailsHTML = `
      <div class="alert-detail-section">
        <h4>Mẫu spam mới</h4>
        <div class="spam-sample">
          <p>"Giảm giá 90% tất cả sản phẩm chính hãng! Mua ngay kẻo hết: bit.ly/abcxyz"</p>
        </div>
      </div>
      <div class="alert-detail-section">
        <h4>Phân tích</h4>
        <p>Mẫu này sử dụng kỹ thuật đánh lừa mới, kết hợp các từ khóa "chính hãng" để tránh bộ lọc.</p>
        <p>Tỷ lệ xuất hiện: 23 lần trong 2 giờ qua</p>
        <p>Nền tảng: Facebook (78%), Twitter (22%)</p>
      </div>
    `;
  }
  
  showModal(
    alertTitle,
    detailsHTML,
    null, // No confirmation action
    false // No confirmation button
  );
}

// Show block IP modal
function showBlockIPModal(alertTitle) {
  showModal(
    'Chặn địa chỉ IP',
    `
    <p>Bạn có chắc chắn muốn chặn địa chỉ IP liên quan đến cảnh báo:</p>
    <p><strong>${alertTitle}</strong></p>
    <div class="form-group">
      <label for="block-duration">Thời gian chặn:</label>
      <select id="block-duration">
        <option value="24h">24 giờ</option>
        <option value="48h">48 giờ</option>
        <option value="1w">1 tuần</option>
        <option value="1m">1 tháng</option>
        <option value="perm" selected>Vĩnh viễn</option>
      </select>
    </div>
    <div class="form-group">
      <label for="block-reason">Lý do:</label>
      <textarea id="block-reason" rows="3">Phát hiện ngôn từ thù ghét</textarea>
    </div>
    `,
    () => {
      const duration = document.getElementById('block-duration').value;
      showNotification(`Đã chặn IP đến ${duration === 'perm' ? 'vĩnh viễn' : duration}`, 'success');
    }
  );
}

// Show warn user modal
function showWarnUserModal(alertTitle) {
  showModal(
    'Cảnh báo người dùng',
    `
    <p>Gửi cảnh báo đến người dùng liên quan đến:</p>
    <p><strong>${alertTitle}</strong></p>
    <div class="form-group">
      <label for="warning-template">Mẫu cảnh báo:</label>
      <select id="warning-template">
        <option value="offensive">Ngôn từ xúc phạm</option>
        <option value="hate" selected>Ngôn từ thù ghét</option>
        <option value="spam">Spam/Quảng cáo trái phép</option>
        <option value="custom">Tùy chỉnh</option>
      </select>
    </div>
    <div class="form-group">
      <label for="warning-message">Nội dung cảnh báo:</label>
      <textarea id="warning-message" rows="5">Chúng tôi phát hiện tài khoản của bạn có hành vi sử dụng ngôn từ không phù hợp trên nền tảng của chúng tôi. Vui lòng xem lại Quy tắc cộng đồng và điều chỉnh cách ứng xử để tránh bị đình chỉ tài khoản.

Đây là cảnh báo chính thức.</textarea>
    </div>
    `,
    () => {
      showNotification('Đã gửi cảnh báo đến người dùng', 'success');
    }
  );
}

// Show add to database modal
function showAddToDBModal(alertTitle) {
  showModal(
    'Thêm vào cơ sở dữ liệu',
    `
    <p>Thêm mẫu spam vào cơ sở dữ liệu:</p>
    <p><strong>${alertTitle}</strong></p>
    <div class="form-group">
      <label for="pattern-type">Loại mẫu:</label>
      <select id="pattern-type">
        <option value="exact">Khớp chính xác</option>
        <option value="regex" selected>Biểu thức chính quy</option>
        <option value="fuzzy">Khớp tương đối</option>
      </select>
    </div>
    <div class="form-group">
      <label for="pattern-text">Mẫu:</label>
      <input type="text" id="pattern-text" value="Giảm giá (\d+)% .* (bit\.ly|goo\.gl|tinyurl\.com)" />
    </div>
    <div class="form-group">
      <label for="pattern-category">Phân loại:</label>
      <select id="pattern-category">
        <option value="offensive">Xúc phạm</option>
        <option value="hate">Thù ghét</option>
        <option value="spam" selected>Spam</option>
      </select>
    </div>
    `,
    () => {
      showNotification('Đã thêm mẫu vào cơ sở dữ liệu', 'success');
    }
  );
}

// Reports functionality
function initializeReports() {
  const reportsList = document.querySelector('.reports-list');
  if (!reportsList) return;
  
  // Handle report actions
  const reportActions = reportsList.querySelectorAll('.report-action');
  
  reportActions.forEach(action => {
    action.addEventListener('click', function() {
      const reportItem = this.closest('.report-item');
      const actionType = this.getAttribute('title');
      const reportTitle = reportItem.querySelector('.report-title').textContent;
      
      switch (actionType) {
        case 'Tải xuống':
          showNotification(`Đang tải xuống báo cáo: ${reportTitle}`, 'info');
          break;
        case 'Xem':
          showReportPreview(reportTitle, reportItem);
          break;
        case 'Gửi email':
          showSendReportModal(reportTitle);
          break;
        case 'Xóa':
          showDeleteReportModal(reportTitle, reportItem);
          break;
      }
    });
  });
  
  // Handle "Create new report" button
  const createReportBtn = document.querySelector('#reports .export-button');
  if (createReportBtn) {
    createReportBtn.addEventListener('click', () => {
      showCreateReportModal();
    });
  }
}

// Show report preview
function showReportPreview(reportTitle, reportItem) {
  // Get report type from icon
  const iconElement = reportItem.querySelector('.report-icon');
  const reportType = iconElement.classList[1]; // e.g., "system", "content", "user", "performance"
  
  // Create sample report preview based on report type
  let previewHTML = `
    <div class="report-preview-header">
      <h4>${reportTitle}</h4>
      <div class="report-meta">
        <span class="report-date">${reportItem.querySelector('.report-date').textContent}</span>
        <span class="report-author">${reportItem.querySelector('.report-author').textContent}</span>
      </div>
    </div>
    <div class="report-preview-body">
  `;
  
  // Add content based on report type
  if (reportType === 'system') {
    previewHTML += `
      <div class="report-section">
        <h5>Tổng quan hệ thống</h5>
        <div class="report-chart-placeholder">
          <img src="https://via.placeholder.com/600x300?text=System+Activity+Chart" alt="System Activity Chart" />
        </div>
        <table class="report-table">
          <thead>
            <tr>
              <th>Chỉ số</th>
              <th>Giá trị</th>
              <th>Thay đổi</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Uptime</td>
              <td>99.8%</td>
              <td class="positive">+0.3%</td>
            </tr>
            <tr>
              <td>Thời gian phản hồi trung bình</td>
              <td>245ms</td>
              <td class="positive">-15ms</td>
            </tr>
            <tr>
              <td>Lượt quét</td>
              <td>24,891</td>
              <td class="positive">+23%</td>
            </tr>
            <tr>
              <td>API Calls</td>
              <td>152,478</td>
              <td class="positive">+18%</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="report-section">
        <h5>Cảnh báo hệ thống</h5>
        <p>Không có cảnh báo hệ thống nào trong khoảng thời gian này.</p>
      </div>
    `;
  } else if (reportType === 'content') {
    previewHTML += `
      <div class="report-section">
        <h5>Phân tích nội dung độc hại</h5>
        <div class="report-chart-placeholder">
          <img src="https://via.placeholder.com/600x300?text=Content+Analysis+Chart" alt="Content Analysis Chart" />
        </div>
        <div class="report-subsection">
          <h6>Các mẫu phổ biến</h6>
          <table class="report-table">
            <thead>
              <tr>
                <th>Mẫu</th>
                <th>Loại</th>
                <th>Số lần xuất hiện</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>"đồ ngu dốt"</td>
                <td>Xúc phạm</td>
                <td>145</td>
              </tr>
              <tr>
                <td>"thật là vô dụng"</td>
                <td>Xúc phạm</td>
                <td>98</td>
              </tr>
              <tr>
                <td>"nên bị cấm"</td>
                <td>Thù ghét</td>
                <td>52</td>
              </tr>
              <tr>
                <td>"giảm giá 90%"</td>
                <td>Spam</td>
                <td>203</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (reportType === 'user') {
    previewHTML += `
      <div class="report-section">
        <h5>Thống kê người dùng</h5>
        <div class="report-chart-placeholder">
          <img src="https://via.placeholder.com/600x300?text=User+Activity+Chart" alt="User Activity Chart" />
        </div>
        <div class="report-subsection">
          <h6>Người dùng hoạt động nhiều nhất</h6>
          <table class="report-table">
            <thead>
              <tr>
                <th>Người dùng</th>
                <th>Số lượt quét</th>
                <th>Ngày hoạt động</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>nguyen.van.a</td>
                <td>432</td>
                <td>28</td>
              </tr>
              <tr>
                <td>tran.thi.b</td>
                <td>385</td>
                <td>26</td>
              </tr>
              <tr>
                <td>le.van.c</td>
                <td>312</td>
                <td>22</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  } else if (reportType === 'performance') {
    previewHTML += `
      <div class="report-section">
        <h5>Hiệu suất hệ thống</h5>
        <div class="report-chart-placeholder">
          <img src="https://via.placeholder.com/600x300?text=Performance+Chart" alt="Performance Chart" />
        </div>
        <div class="report-subsection">
          <h6>Chi tiết API</h6>
          <table class="report-table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Thời gian phản hồi</th>
                <th>Số lượt gọi</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>/extension/detect</td>
                <td>245ms</td>
                <td>18,456</td>
              </tr>
              <tr>
                <td>/predict/single</td>
                <td>320ms</td>
                <td>3,221</td>
              </tr>
              <tr>
                <td>/predict/batch</td>
                <td>580ms</td>
                <td>942</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }
  
  previewHTML += `</div>`;
  
  showModal(
    reportTitle,
    previewHTML,
    null, // No confirmation action
    false // No confirmation button
  );
}

// Download report
function downloadReport(reportTitle, reportItem) {
  // Get report format
  const formatElement = reportItem.querySelector('.report-format');
  const format = formatElement ? formatElement.textContent.toLowerCase() : 'pdf';
  
  // Show loading notification
  showNotification(`Đang tải xuống báo cáo: ${reportTitle}...`, 'info');
  
  // Simulate download delay
  setTimeout(() => {
    showNotification(`Đã tải xuống báo cáo: ${reportTitle}`, 'success');
  }, 1500);
}

// Show send report modal
function showSendReportModal(reportTitle) {
  showModal(
    'Gửi báo cáo qua email',
    `
    <p>Gửi báo cáo <strong>${reportTitle}</strong> qua email.</p>
    <div class="form-group">
      <label for="email-recipients">Người nhận:</label>
      <input type="text" id="email-recipients" placeholder="email@example.com, email2@example.com" />
    </div>
    <div class="form-group">
      <label for="email-subject">Tiêu đề:</label>
      <input type="text" id="email-subject" value="Báo cáo: ${reportTitle}" />
    </div>
    <div class="form-group">
      <label for="email-message">Nội dung:</label>
      <textarea id="email-message" rows="4">Kính gửi,

Vui lòng xem báo cáo đính kèm.

Trân trọng,
Hệ thống Toxic Language Detector</textarea>
    </div>
    <div class="form-group checkbox-group">
      <label class="checkbox-label">
        <input type="checkbox" id="email-attach-pdf" checked>
        <span class="checkbox-custom"></span>
        <span>Đính kèm PDF</span>
      </label>
    </div>
    `,
    () => {
      const recipients = document.getElementById('email-recipients').value;
      showNotification(`Đã gửi báo cáo đến: ${recipients}`, 'success');
    }
  );
}

// Show delete report modal
function showDeleteReportModal(reportTitle, reportItem) {
  showModal(
    'Xóa báo cáo',
    `
    <p>Bạn có chắc chắn muốn xóa báo cáo <strong>${reportTitle}</strong>?</p>
    <p>Hành động này không thể hoàn tác.</p>
    `,
    () => {
      // Remove report item from DOM
      reportItem.style.height = reportItem.offsetHeight + 'px';
      reportItem.style.overflow = 'hidden';
      setTimeout(() => {
        reportItem.style.height = '0';
        reportItem.style.padding = '0';
        reportItem.style.margin = '0';
        
        setTimeout(() => {
          reportItem.remove();
          showNotification(`Đã xóa báo cáo: ${reportTitle}`, 'success');
        }, 300);
      }, 10);
    }
  );
}

// Show create report modal
function showCreateReportModal() {
  showModal(
    'Tạo báo cáo mới',
    `
    <div class="form-group">
      <label for="report-type">Loại báo cáo:</label>
      <select id="report-type">
        <option value="system">Hoạt động hệ thống</option>
        <option value="content">Phân tích nội dung</option>
        <option value="user">Người dùng</option>
        <option value="performance">Hiệu suất</option>
        <option value="custom">Tùy chỉnh</option>
      </select>
    </div>
    <div class="form-group">
      <label for="report-title">Tiêu đề báo cáo:</label>
      <input type="text" id="report-title" placeholder="Nhập tiêu đề báo cáo" />
    </div>
    <div class="form-group">
      <label for="report-timerange">Khoảng thời gian:</label>
      <select id="report-timerange">
        <option value="day">24 giờ qua</option>
        <option value="week" selected>7 ngày qua</option>
        <option value="month">30 ngày qua</option>
        <option value="year">12 tháng qua</option>
        <option value="custom">Tùy chỉnh</option>
      </select>
    </div>
    <div id="custom-timerange" style="display: none;">
      <div class="form-group">
        <label for="report-start-date">Từ ngày:</label>
        <input type="date" id="report-start-date" />
      </div>
      <div class="form-group">
        <label for="report-end-date">Đến ngày:</label>
        <input type="date" id="report-end-date" />
      </div>
    </div>
    <div class="form-group">
      <label for="report-format">Định dạng:</label>
      <select id="report-format">
        <option value="pdf" selected>PDF</option>
        <option value="xlsx">Excel (XLSX)</option>
        <option value="csv">CSV</option>
      </select>
    </div>
    <div class="form-group checkbox-group">
      <label class="checkbox-label">
        <input type="checkbox" id="report-schedule" />
        <span class="checkbox-custom"></span>
        <span>Lên lịch tự động</span>
      </label>
    </div>
    <div id="report-schedule-options" style="display: none;">
      <div class="form-group">
        <label for="report-frequency">Tần suất:</label>
        <select id="report-frequency">
          <option value="daily">Hàng ngày</option>
          <option value="weekly" selected>Hàng tuần</option>
          <option value="monthly">Hàng tháng</option>
        </select>
      </div>
      <div class="form-group">
        <label for="report-recipients">Gửi đến email:</label>
        <input type="text" id="report-recipients" placeholder="email@example.com" />
      </div>
    </div>
    `,
    () => {
      // Get report values
      const type = document.getElementById('report-type').value;
      const title = document.getElementById('report-title').value || 'Báo cáo mới';
      const timerange = document.getElementById('report-timerange').value;
      const format = document.getElementById('report-format').value;
      
      // Show creating notification
      showNotification('Đang tạo báo cáo...', 'info');
      
      // Simulate report creation delay
      setTimeout(() => {
        // Show success notification
        showNotification('Đã tạo báo cáo thành công', 'success');
        
        // Add new report to list
        const reportsList = document.querySelector('.reports-list');
        if (reportsList) {
          const newReport = document.createElement('div');
          newReport.className = 'report-item';
          newReport.innerHTML = `
            <div class="report-icon ${type}">📊</div>
            <div class="report-details">
              <div class="report-title">${title}</div>
              <div class="report-description">Báo cáo ${
                type === 'system' ? 'hoạt động hệ thống' :
                type === 'content' ? 'phân tích nội dung' :
                type === 'user' ? 'người dùng' :
                type === 'performance' ? 'hiệu suất' : 'tùy chỉnh'
              } (${
                timerange === 'day' ? '24 giờ qua' :
                timerange === 'week' ? '7 ngày qua' :
                timerange === 'month' ? '30 ngày qua' :
                timerange === 'year' ? '12 tháng qua' : 'khoảng thời gian tùy chỉnh'
              })</div>
              <div class="report-meta">
                <span class="report-date">${new Date().toLocaleDateString('vi-VN')}</span>
                <span class="report-author">Admin</span>
              </div>
            </div>
            <div class="report-format">${format.toUpperCase()}</div>
            <div class="report-actions">
              <button class="report-action" title="Tải xuống">📥</button>
              <button class="report-action" title="Xem">👁️</button>
              <button class="report-action" title="Gửi email">📧</button>
              <button class="report-action" title="Xóa">🗑️</button>
            </div>
          `;
          
          // Add to DOM
          reportsList.prepend(newReport);
          
          // Add event listeners to new report
          initializeReports();
        }
      }, 2000);
    }
  );
  
  // Handle timerange change
  const timerangeSelect = document.getElementById('report-timerange');
  const customTimerange = document.getElementById('custom-timerange');
  
  if (timerangeSelect && customTimerange) {
    timerangeSelect.addEventListener('change', function() {
      customTimerange.style.display = this.value === 'custom' ? 'block' : 'none';
    });
  }
  
  // Handle schedule checkbox
  const scheduleCheckbox = document.getElementById('report-schedule');
  const scheduleOptions = document.getElementById('report-schedule-options');
  
  if (scheduleCheckbox && scheduleOptions) {
    scheduleCheckbox.addEventListener('change', function() {
      scheduleOptions.style.display = this.checked ? 'block' : 'none';
    });
  }
}

// Initialize analytics data
function initializeAnalytics() {
  // For demo purposes, we'll just populate the Analytics section with sample data
  const analyticsSection = document.getElementById('analytics');
  if (!analyticsSection) return;
  
  // Generate heatmap
  generateHeatmap();
  
  // Add interaction to chart tabs in the Analytics section
  const chartTabs = analyticsSection.querySelectorAll('.chart-tab');
  
  chartTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const tabGroup = this.closest('.chart-tabs');
      const view = this.getAttribute('data-view');
      
      // Update active tab
      tabGroup.querySelectorAll('.chart-tab').forEach(t => {
        t.classList.remove('active');
      });
      this.classList.add('active');
      
      // In a real app, this would update the chart data based on the selected view
      console.log(`Changing view to ${view}`);
      
      // Show notification
      showNotification(`Đã chuyển sang chế độ xem: ${
        view === 'day' ? 'Theo ngày' : 
        view === 'week' ? 'Theo tuần' : 
        view === 'hour' ? 'Theo giờ' : 'Mặc định'
      }`, 'info');
    });
  });
}

// Generate heatmap
function generateHeatmap() {
  const heatmapGrid = document.querySelector('.heatmap-grid');
  if (!heatmapGrid) return;
  
  // Clear any existing cells
  heatmapGrid.innerHTML = '';
  
  // Generate cells for a 7x24 heatmap (days of week x hours of day)
  const days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN'];
  
  for (let hour = 0; hour < 24; hour++) {
    for (let day = 0; day < 7; day++) {
      // Generate intensity (higher during working hours, lower on weekends)
      let intensity = 0.1; // Base low intensity
      
      // Increase intensity during working hours (8am-6pm)
      if (hour >= 8 && hour <= 18) {
        // Workdays have higher intensity
        if (day < 5) { // Mon-Fri
          intensity = 0.3 + Math.random() * 0.6; // 0.3-0.9
        } else { // Weekend
          intensity = 0.1 + Math.random() * 0.3; // 0.1-0.4
        }
      }
      
      // Create cell
      const cell = document.createElement('div');
      cell.className = 'heatmap-cell';
      cell.style.backgroundColor = `rgba(76, 175, 80, ${intensity})`;
      
      // Add tooltip with the day, hour, and value
      const value = Math.round(intensity * 100);
      cell.setAttribute('title', `${days[day]} ${hour}:00 - ${value} phát hiện`);
      
      // Add to grid
      heatmapGrid.appendChild(cell);
    }
  }
}
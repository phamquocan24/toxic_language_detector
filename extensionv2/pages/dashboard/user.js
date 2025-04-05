// scripts/user_dashboard.js
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
      
      // Check if admin trying to access user dashboard
      if (role === 'admin' && !window.location.href.includes('admin_dashboard.html')) {
        window.location.href = 'admin_dashboard.html';
        return;
      }
      
      // Check if user trying to access admin dashboard
      if (role !== 'admin' && window.location.href.includes('admin_dashboard.html')) {
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
    
    // Initialize export functionality
    initializeExport();
    
    // Initialize search functionality
    initializeSearch();
  });
  
  // Export functionality
  function initializeExport() {
    const exportButton = document.querySelector('.export-button');
    if (!exportButton) return;
    
    exportButton.addEventListener('click', () => {
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
        menuItem.addEventListener('click', () => exportData(option.format));
        menu.appendChild(menuItem);
      });
      
      // Remove existing menu if any
      const existingMenu = document.querySelector('.export-menu');
      if (existingMenu) {
        existingMenu.remove();
      }
      
      // Add menu to DOM
      exportButton.parentNode.style.position = 'relative';
      exportButton.parentNode.appendChild(menu);
      
      // Hide menu when clicking outside
      document.addEventListener('click', (event) => {
        if (!menu.contains(event.target) && event.target !== exportButton) {
          menu.remove();
        }
      }, { once: true });
    });
  }
  
  // Export data in different formats
  function exportData(format) {
    // Get data from table
    const table = document.querySelector('.data-table');
    if (!table) return;
    
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
      return Array.from(tr.querySelectorAll('td')).map(td => {
        // Get text content, removing any HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = td.innerHTML;
        return tempDiv.textContent.trim();
      });
    });
    
    // Current date for filename
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10);
    const filename = `toxic-detector-report-${dateStr}`;
    
    // Handle different export formats
    switch (format) {
      case 'excel':
        exportToExcel(headers, rows, filename);
        break;
      case 'csv':
        exportToCSV(headers, rows, filename);
        break;
      case 'pdf':
        exportToPDF(headers, rows, filename);
        break;
      case 'print':
        printTable();
        break;
    }
  }
  
  // Export to Excel
  function exportToExcel(headers, rows, filename) {
    // In a real implementation, you would use a library like SheetJS
    // This is a simplified version just for demonstration
    alert('Tính năng xuất Excel đang được phát triển');
    
    // Example implementation with SheetJS (would require the library)
    /*
    const worksheet = XLSX.utils.aoa_to_sheet([headers, ...rows]);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Report");
    XLSX.writeFile(workbook, `${filename}.xlsx`);
    */
  }
  
  // Export to CSV
  function exportToCSV(headers, rows, filename) {
    // Create CSV content
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.csv`);
    link.style.display = 'none';
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  
  // Export to PDF
  function exportToPDF(headers, rows, filename) {
    // In a real implementation, you would use a library like jsPDF
    // This is a simplified version just for demonstration
    alert('Tính năng xuất PDF đang được phát triển');
  }
  
  // Print table
  function printTable() {
    window.print();
  }
  
  // Search functionality
  function initializeSearch() {
    const searchInput = document.querySelector('.search-box input');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      const tableRows = document.querySelectorAll('.data-table tbody tr');
      
      tableRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
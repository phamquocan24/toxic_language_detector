// scripts/auth.js
document.addEventListener('DOMContentLoaded', () => {
  // Helper function để cập nhật text cho phần tử
  function updateElementText(selector, messageKey) {
    const element = document.querySelector(selector);
    if (element) {
      element.textContent = chrome.i18n.getMessage(messageKey);
    }
  }

  // Cập nhật tất cả các chuỗi văn bản trong giao diện
  updateElementText('#login-button', 'login');
  updateElementText('#register-button', 'register');
  updateElementText('label[for="login-username"]', 'username');
  updateElementText('label[for="login-password"]', 'password');
  updateElementText('label[for="register-email"]', 'email');
  updateElementText('label[for="register-username"]', 'username');
  updateElementText('label[for="register-password"]', 'password');
  updateElementText('label[for="register-confirm-password"]', 'confirmPassword');
  updateElementText('label[for="remember-me"] span', 'rememberMe');
  
  const API_ENDPOINT = chrome.runtime.getURL('config.json')
    .then(response => fetch(response))
    .then(response => response.json())
    .then(config => config.API_ENDPOINT);
  
  // Tab switching
  const loginTab = document.querySelector('[data-tab="login"]');
  const registerTab = document.querySelector('[data-tab="register"]');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  
  loginTab.addEventListener('click', () => {
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    loginForm.classList.add('active');
    registerForm.classList.remove('active');
  });
  
  registerTab.addEventListener('click', () => {
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    registerForm.classList.add('active');
    loginForm.classList.remove('active');
  });
  
  // Login form submission
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const rememberMe = document.getElementById('remember-me').checked;
    const errorElement = document.getElementById('login-error');
    
    try {
      errorElement.textContent = '';
      
      const response = await fetch(`${await API_ENDPOINT}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || chrome.i18n.getMessage("loginFailed"));
      }
      
      const data = await response.json();
      
      // Save auth data
      const authData = {
        token: data.access_token,
        username: username,
        role: data.role,
        expiresAt: rememberMe ? null : Date.now() + (24 * 60 * 60 * 1000) // 24 hours
      };
      
      chrome.storage.sync.set({ authData }, () => {
        // Redirect based on role
        if (data.role === 'admin') {
          window.location.href = 'admin_dashboard.html';
        } else {
          window.location.href = 'popup.html';
        }
      });
      
    } catch (error) {
      errorElement.textContent = error.message;
    }
  });
  
  // Register form submission
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('register-email').value;
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    const errorElement = document.getElementById('register-error');
    
    // Simple validation
    if (password !== confirmPassword) {
      errorElement.textContent = chrome.i18n.getMessage("passwordMismatch");
      return;
    }
    
    try {
      errorElement.textContent = '';
      
      const response = await fetch(`${await API_ENDPOINT}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email,
          username,
          password
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || chrome.i18n.getMessage("registrationFailed"));
      }
      
      // Auto switch to login tab after successful registration
      loginTab.click();
      document.getElementById('login-username').value = username;
      document.getElementById('login-error').textContent = chrome.i18n.getMessage("registrationSuccess");
      
    } catch (error) {
      errorElement.textContent = error.message;
    }
  });
  
  // Check if already logged in
  chrome.storage.sync.get('authData', (data) => {
    if (data.authData) {
      const { token, expiresAt, role } = data.authData;
      
      // Check if token is still valid
      if (!expiresAt || expiresAt > Date.now()) {
        // Redirect based on role
        if (role === 'admin') {
          window.location.href = 'admin_dashboard.html';
        } else {
          window.location.href = 'popup.html';
        }
      }
    }
  });
});
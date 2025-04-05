/**
 * Popup script for the Toxic Language Detector Extension
 * Handles user settings and statistics
 */

// DOM elements
const enableToggle = document.getElementById('enable-toggle');
const thresholdSlider = document.getElementById('threshold');
const thresholdValue = document.getElementById('threshold-value');
const highlightToxic = document.getElementById('highlight-toxic');
const platformFacebook = document.getElementById('platform-facebook');
const platformYoutube = document.getElementById('platform-youtube');
const platformTwitter = document.getElementById('platform-twitter');
const statScanned = document.getElementById('stat-scanned');
const statToxic = document.getElementById('stat-toxic');
const statClean = document.getElementById('stat-clean');
const resetStatsBtn = document.getElementById('reset-stats');

// Load settings from storage
function loadSettings() {
  chrome.storage.sync.get(null, (data) => {
    // Extension enabled state
    enableToggle.checked = data.enabled !== undefined ? data.enabled : true;
    
    // Threshold
    if (data.threshold) {
      thresholdSlider.value = data.threshold;
      thresholdValue.textContent = data.threshold;
    }
    
    // Highlight toxic content
    highlightToxic.checked = data.highlightToxic !== undefined ? data.highlightToxic : true;
    
    // Platform settings
    if (data.platforms) {
      platformFacebook.checked = data.platforms.facebook !== undefined ? data.platforms.facebook : true;
      platformYoutube.checked = data.platforms.youtube !== undefined ? data.platforms.youtube : true;
      platformTwitter.checked = data.platforms.twitter !== undefined ? data.platforms.twitter : true;
    }
    
    // Statistics
    if (data.stats) {
      statScanned.textContent = data.stats.scanned || 0;
      statToxic.textContent = data.stats.toxic || 0;
      statClean.textContent = data.stats.clean || 0;
    }
  });
}

// Save settings to storage
function saveSettings() {
  const settings = {
    enabled: enableToggle.checked,
    threshold: parseFloat(thresholdSlider.value),
    highlightToxic: highlightToxic.checked,
    platforms: {
      facebook: platformFacebook.checked,
      youtube: platformYoutube.checked,
      twitter: platformTwitter.checked
    }
  };
  
  chrome.storage.sync.set(settings);
}

// Update threshold value display
function updateThresholdValue() {
  thresholdValue.textContent = thresholdSlider.value;
}

// Reset statistics
function resetStats() {
  chrome.runtime.sendMessage({ action: "resetStats" }, (response) => {
    if (response && response.success) {
      statScanned.textContent = '0';
      statToxic.textContent = '0';
      statClean.textContent = '0';
    }
  });
}

// Event listeners
document.addEventListener('DOMContentLoaded', loadSettings);
enableToggle.addEventListener('change', saveSettings);
thresholdSlider.addEventListener('input', updateThresholdValue);
thresholdSlider.addEventListener('change', saveSettings);
highlightToxic.addEventListener('change', saveSettings);
platformFacebook.addEventListener('change', saveSettings);
platformYoutube.addEventListener('change', saveSettings);
platformTwitter.addEventListener('change', saveSettings);
resetStatsBtn.addEventListener('click', resetStats);


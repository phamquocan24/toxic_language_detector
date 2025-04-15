/**
 * Background script wrapper
 * Sử dụng ES modules thay vì importScripts
 */

// Import các modules
import '../src/config/constants-worker.js';
import '../src/api/constants-worker.js';
import '../src/utils/storage.js';
import '../src/utils/messaging.js';
import '../src/api/services.js';
import '../src/api/toxicDetection.js';
import '../src/api/auth.js';
import '../src/background/background-main-worker.js';

console.log('Background script loaded successfully'); 
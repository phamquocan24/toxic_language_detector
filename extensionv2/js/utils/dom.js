/**
 * dom.js - DOM utilities for the Toxic Language Detector
 * Provides helper functions for DOM manipulation and interaction
 */

/**
 * Select an element by selector
 * @param {string} selector - CSS selector
 * @param {Element} [context=document] - Context element
 * @returns {Element|null} - Element or null if not found
 */
export function $(selector, context = document) {
    return context.querySelector(selector);
  }
  
  /**
   * Select multiple elements by selector
   * @param {string} selector - CSS selector
   * @param {Element} [context=document] - Context element
   * @returns {Element[]} - Array of elements
   */
  export function $$(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
  }
  
  /**
   * Create an element with attributes and children
   * @param {string} tag - Tag name
   * @param {Object} [attributes={}] - Element attributes
   * @param {(string|Element|Element[])} [children] - Child elements or text
   * @returns {Element} - Created element
   */
  export function createElement(tag, attributes = {}, children) {
    const element = document.createElement(tag);
    
    // Set attributes
    Object.entries(attributes).forEach(([key, value]) => {
      if (key === 'style' && typeof value === 'object') {
        Object.assign(element.style, value);
      } else if (key === 'className') {
        element.className = value;
      } else if (key === 'dataset' && typeof value === 'object') {
        Object.entries(value).forEach(([dataKey, dataValue]) => {
          element.dataset[dataKey] = dataValue;
        });
      } else if (key.startsWith('on') && typeof value === 'function') {
        element.addEventListener(key.slice(2).toLowerCase(), value);
      } else {
        element.setAttribute(key, value);
      }
    });
    
    // Add children
    if (children) {
      if (Array.isArray(children)) {
        children.forEach(child => {
          if (child instanceof Element) {
            element.appendChild(child);
          } else {
            element.appendChild(document.createTextNode(String(child)));
          }
        });
      } else if (children instanceof Element) {
        element.appendChild(children);
      } else {
        element.textContent = String(children);
      }
    }
    
    return element;
  }
  
  /**
   * Add event listener with automatic cleanup
   * @param {Element} element - Element to add listener to
   * @param {string} event - Event name
   * @param {Function} handler - Event handler
   * @param {Object} [options] - Event listener options
   * @returns {Function} - Function to remove the listener
   */
  export function addEvent(element, event, handler, options) {
    element.addEventListener(event, handler, options);
    
    return () => element.removeEventListener(event, handler, options);
  }
  
  /**
   * Add multiple event listeners
   * @param {Element} element - Element to add listeners to
   * @param {Object} events - Object mapping event names to handlers
   * @param {Object} [options] - Event listener options
   * @returns {Function} - Function to remove all listeners
   */
  export function addEvents(element, events, options) {
    const removers = Object.entries(events).map(([event, handler]) => {
      return addEvent(element, event, handler, options);
    });
    
    return () => removers.forEach(remove => remove());
  }
  
  /**
   * Remove all child elements
   * @param {Element} element - Element to clear
   */
  export function clearElement(element) {
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
  }
  
  /**
   * Check if an element is visible
   * @param {Element} element - Element to check
   * @returns {boolean} - Whether the element is visible
   */
  export function isVisible(element) {
    return !!(
      element.offsetWidth || 
      element.offsetHeight || 
      element.getClientRects().length
    );
  }
  
  /**
   * Get element position relative to document
   * @param {Element} element - Element to get position for
   * @returns {Object} - Position object with top and left properties
   */
  export function getOffset(element) {
    const rect = element.getBoundingClientRect();
    
    return {
      top: rect.top + window.scrollY,
      left: rect.left + window.scrollX
    };
  }
  
  /**
   * Add class(es) to an element
   * @param {Element} element - Element to add class to
   * @param {...string} classNames - Class name(s) to add
   */
  export function addClass(element, ...classNames) {
    element.classList.add(...classNames);
  }
  
  /**
   * Remove class(es) from an element
   * @param {Element} element - Element to remove class from
   * @param {...string} classNames - Class name(s) to remove
   */
  export function removeClass(element, ...classNames) {
    element.classList.remove(...classNames);
  }
  
  /**
   * Toggle class on an element
   * @param {Element} element - Element to toggle class on
   * @param {string} className - Class name to toggle
   * @param {boolean} [force] - Force add or remove
   */
  export function toggleClass(element, className, force) {
    element.classList.toggle(className, force);
  }
  
  /**
   * Check if an element has a class
   * @param {Element} element - Element to check
   * @param {string} className - Class name to check
   * @returns {boolean} - Whether the element has the class
   */
  export function hasClass(element, className) {
    return element.classList.contains(className);
  }
  
  /**
   * Get or set element data attributes
   * @param {Element} element - Element to get/set data on
   * @param {string} key - Data key
   * @param {*} [value] - Value to set (if omitted, get value)
   * @returns {*} - Data value (when getting)
   */
  export function data(element, key, value) {
    const dataKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
    
    if (value === undefined) {
      return element.dataset[key];
    }
    
    element.dataset[key] = value;
  }
  
  /**
   * Create a DOM observer to watch for changes
   * @param {Function} callback - Callback function(mutations, observer)
   * @param {Object} [options] - Observer options
   * @param {Element} [target=document.body] - Target element
   * @returns {MutationObserver} - Observer instance
   */
  export function createObserver(callback, options = {}, target = document.body) {
    const defaultOptions = {
      childList: true,
      subtree: true
    };
    
    const observer = new MutationObserver(callback);
    observer.observe(target, { ...defaultOptions, ...options });
    
    return observer;
  }
  
  /**
   * Find the closest ancestor matching a selector
   * @param {Element} element - Starting element
   * @param {string} selector - CSS selector
   * @returns {Element|null} - Matching ancestor or null
   */
  export function closest(element, selector) {
    return element.closest(selector);
  }
  
  /**
   * Wait for an element to appear in the DOM
   * @param {string} selector - CSS selector
   * @param {Object} [options] - Options
   * @param {Element} [options.root=document] - Root element
   * @param {number} [options.timeout=5000] - Timeout in milliseconds
   * @returns {Promise<Element>} - Promise resolving to the element
   */
  export function waitForElement(selector, options = {}) {
    const { root = document, timeout = 5000 } = options;
    
    return new Promise((resolve, reject) => {
      // Check if element already exists
      const element = root.querySelector(selector);
      if (element) {
        resolve(element);
        return;
      }
      
      // Set timeout
      const timeoutId = setTimeout(() => {
        observer.disconnect();
        reject(new Error(`Timeout waiting for element: ${selector}`));
      }, timeout);
      
      // Create observer
      const observer = new MutationObserver((mutations, observer) => {
        const element = root.querySelector(selector);
        if (element) {
          clearTimeout(timeoutId);
          observer.disconnect();
          resolve(element);
        }
      });
      
      observer.observe(root, {
        childList: true,
        subtree: true
      });
    });
  }
  
  /**
   * Insert element after a reference element
   * @param {Element} newElement - Element to insert
   * @param {Element} referenceElement - Element to insert after
   */
  export function insertAfter(newElement, referenceElement) {
    referenceElement.parentNode.insertBefore(newElement, referenceElement.nextSibling);
  }
  
  /**
   * Get element siblings
   * @param {Element} element - Element to get siblings for
   * @returns {Element[]} - Array of sibling elements
   */
  export function getSiblings(element) {
    return Array.from(element.parentNode.children).filter(child => child !== element);
  }
  
  /**
   * Create a document fragment from HTML string
   * @param {string} html - HTML string
   * @returns {DocumentFragment} - Document fragment
   */
  export function createFragment(html) {
    const template = document.createElement('template');
    template.innerHTML = html.trim();
    return template.content;
  }
  
  /**
   * Insert HTML string into an element
   * @param {Element} element - Element to insert into
   * @param {string} position - Position to insert at (beforebegin, afterbegin, beforeend, afterend)
   * @param {string} html - HTML string
   */
  export function insertHTML(element, position, html) {
    element.insertAdjacentHTML(position, html);
  }
  
  /**
   * Wrap an element with another element
   * @param {Element} element - Element to wrap
   * @param {Element|string} wrapper - Wrapper element or HTML string
   */
  export function wrap(element, wrapper) {
    // Get the parent
    const parent = element.parentNode;
    
    // Create wrapper if it's a string
    let wrapperElement;
    if (typeof wrapper === 'string') {
      const div = document.createElement('div');
      div.innerHTML = wrapper;
      wrapperElement = div.firstChild;
    } else {
      wrapperElement = wrapper;
    }
    
    // Insert the wrapper before the element
    parent.insertBefore(wrapperElement, element);
    
    // Move the element into the wrapper
    wrapperElement.appendChild(element);
    
    return wrapperElement;
  }
  
  /**
   * Unwrap an element (remove its parent)
   * @param {Element} element - Element to unwrap
   */
  export function unwrap(element) {
    const parent = element.parentNode;
    
    // Move all children out of the element
    while (element.firstChild) {
      parent.insertBefore(element.firstChild, element);
    }
    
    // Remove the empty element
    parent.removeChild(element);
  }
  
  /**
   * Get the index of an element among its siblings
   * @param {Element} element - Element to get index for
   * @returns {number} - Index of the element
   */
  export function index(element) {
    let index = 0;
    while (element = element.previousElementSibling) {
      index++;
    }
    return index;
  }
  
  /**
   * Get CSS variables computed for an element
   * @param {Element} element - Element to get variables for
   * @param {string} variableName - Variable name (without --)
   * @returns {string} - Variable value
   */
  export function getCSSVariable(element, variableName) {
    return getComputedStyle(element).getPropertyValue(`--${variableName}`).trim();
  }
  
  /**
   * Set CSS variables for an element
   * @param {Element} element - Element to set variables for
   * @param {string} variableName - Variable name (without --)
   * @param {string} value - Variable value
   */
  export function setCSSVariable(element, variableName, value) {
    element.style.setProperty(`--${variableName}`, value);
  }
  
  /**
   * Get scroll position
   * @returns {Object} - Object with x and y scroll position
   */
  export function getScrollPosition() {
    return {
      x: window.pageXOffset || document.documentElement.scrollLeft,
      y: window.pageYOffset || document.documentElement.scrollTop
    };
  }
  
  /**
   * Smooth scroll to element
   * @param {Element} element - Element to scroll to
   * @param {Object} [options] - Scroll options
   */
  export function scrollTo(element, options = {}) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
      ...options
    });
  }
  
  /**
   * Fade in an element
   * @param {Element} element - Element to fade in
   * @param {number} [duration=400] - Duration in milliseconds
   * @returns {Promise<void>} - Promise resolving when animation completes
   */
  export function fadeIn(element, duration = 400) {
    return new Promise(resolve => {
      element.style.opacity = '0';
      element.style.display = 'block';
      element.style.transition = `opacity ${duration}ms`;
      
      // Trigger reflow
      void element.offsetWidth;
      
      element.style.opacity = '1';
      
      setTimeout(resolve, duration);
    });
  }
  
  /**
   * Fade out an element
   * @param {Element} element - Element to fade out
   * @param {number} [duration=400] - Duration in milliseconds
   * @returns {Promise<void>} - Promise resolving when animation completes
   */
  export function fadeOut(element, duration = 400) {
    return new Promise(resolve => {
      element.style.opacity = '1';
      element.style.transition = `opacity ${duration}ms`;
      
      element.style.opacity = '0';
      
      setTimeout(() => {
        element.style.display = 'none';
        resolve();
      }, duration);
    });
  }
  
  // Export all functions as a group
  export default {
    $,
    $$,
    createElement,
    addEvent,
    addEvents,
    clearElement,
    isVisible,
    getOffset,
    addClass,
    removeClass,
    toggleClass,
    hasClass,
    data,
    createObserver,
    closest,
    waitForElement,
    insertAfter,
    getSiblings,
    createFragment,
    insertHTML,
    wrap,
    unwrap,
    index,
    getCSSVariable,
    setCSSVariable,
    getScrollPosition,
    scrollTo,
    fadeIn,
    fadeOut
  };
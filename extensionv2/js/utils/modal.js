// utils/modal.js
import { showNotification } from './notifications.js';

/**
 * Show a modal dialog
 * @param {string} title - Modal title
 * @param {string} content - Modal HTML content
 * @param {Function|null} onConfirm - Confirmation callback
 * @param {boolean} showConfirmButton - Whether to show confirm button
 */
function showModal(title, content, onConfirm = null, showConfirmButton = true) {
  // Remove any existing modal
  const existingModal = document.querySelector('.modal-container');
  if (existingModal) {
    existingModal.remove();
  }
  
  // Create modal container
  const modalContainer = document.createElement('div');
  modalContainer.className = 'modal-container';
  
  // Create modal content
  const modalContent = document.createElement('div');
  modalContent.className = 'modal-content';
  
  // Create modal header
  const modalHeader = document.createElement('div');
  modalHeader.className = 'modal-header';
  
  const modalTitle = document.createElement('h3');
  modalTitle.textContent = title;
  
  const closeButton = document.createElement('button');
  closeButton.className = 'modal-close';
  closeButton.innerHTML = '&times;';
  closeButton.addEventListener('click', () => {
    modalContainer.remove();
  });
  
  modalHeader.appendChild(modalTitle);
  modalHeader.appendChild(closeButton);
  
  // Create modal body
  const modalBody = document.createElement('div');
  modalBody.className = 'modal-body';
  modalBody.innerHTML = content;
  
  // Create modal footer
  const modalFooter = document.createElement('div');
  modalFooter.className = 'modal-footer';
  
  if (showConfirmButton) {
    const confirmButton = document.createElement('button');
    confirmButton.className = 'modal-button confirm';
    confirmButton.textContent = 'Xác nhận';
    confirmButton.addEventListener('click', () => {
      if (onConfirm) {
        onConfirm();
      }
      modalContainer.remove();
    });
    modalFooter.appendChild(confirmButton);
  }
  
  const cancelButton = document.createElement('button');
  cancelButton.className = 'modal-button cancel';
  cancelButton.textContent = showConfirmButton ? 'Hủy' : 'Đóng';
  cancelButton.addEventListener('click', () => {
    modalContainer.remove();
  });
  modalFooter.appendChild(cancelButton);
  
  // Assemble modal
  modalContent.appendChild(modalHeader);
  modalContent.appendChild(modalBody);
  modalContent.appendChild(modalFooter);
  modalContainer.appendChild(modalContent);
  
  // Add to DOM
  document.body.appendChild(modalContainer);
  
  // Click outside to close
  modalContainer.addEventListener('click', (event) => {
    if (event.target === modalContainer) {
      modalContainer.remove();
    }
  });
  
  // Escape key to close
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      modalContainer.remove();
    }
  }, { once: true });
}

/**
 * Show a confirmation dialog
 * @param {string} title - Dialog title
 * @param {string} message - Dialog message
 * @param {Function} onConfirm - Confirmation callback
 * @param {Function} onCancel - Cancel callback (optional)
 */
function showConfirmDialog(title, message, onConfirm, onCancel = null) {
  showModal(
    title,
    `<p>${message}</p>`,
    onConfirm,
    true
  );
}

/**
 * Show an alert dialog
 * @param {string} title - Dialog title
 * @param {string} message - Dialog message
 * @param {Function} onClose - Close callback (optional)
 */
function showAlertDialog(title, message, onClose = null) {
  showModal(
    title,
    `<p>${message}</p>`,
    onClose,
    false
  );
}

/**
 * Show a form dialog
 * @param {string} title - Dialog title
 * @param {string} formHTML - Form HTML
 * @param {Function} onSubmit - Submit callback
 */
function showFormDialog(title, formHTML, onSubmit) {
  showModal(title, formHTML, onSubmit, true);
}

// Export all functions
export { showModal, showConfirmDialog, showAlertDialog, showFormDialog };
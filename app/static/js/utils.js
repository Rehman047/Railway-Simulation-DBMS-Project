/* ============================================================
   Railway DBMS - Utility JavaScript
   Common functions for AJAX, validation, notifications
   ============================================================ */

// API Base URL
const API_BASE = '/api';

// ── AJAX Helper Functions ──────────────────────────────────

/**
 * Perform AJAX GET request
 */
async function apiGet(endpoint) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    return await response.json();
  } catch (error) {
    console.error('API GET Error:', error);
    showNotification('Error fetching data', 'error');
    return null;
  }
}

/**
 * Perform AJAX POST request
 */
async function apiPost(endpoint, data) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    return await response.json();
  } catch (error) {
    console.error('API POST Error:', error);
    showNotification('Error sending data', 'error');
    return null;
  }
}

/**
 * Perform AJAX PUT request
 */
async function apiPut(endpoint, data) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    return await response.json();
  } catch (error) {
    console.error('API PUT Error:', error);
    showNotification('Error updating data', 'error');
    return null;
  }
}

/**
 * Perform AJAX DELETE request
 */
async function apiDelete(endpoint) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    return await response.json();
  } catch (error) {
    console.error('API DELETE Error:', error);
    showNotification('Error deleting data', 'error');
    return null;
  }
}

// ── Form Handling ──────────────────────────────────────────

/**
 * Get form data as object
 */
function getFormData(formId) {
  const form = document.getElementById(formId);
  if (!form) return null;
  
  const formData = new FormData(form);
  const data = {};
  
  formData.forEach((value, key) => {
    if (data[key]) {
      // Handle multiple values
      if (Array.isArray(data[key])) {
        data[key].push(value);
      } else {
        data[key] = [data[key], value];
      }
    } else {
      data[key] = value;
    }
  });
  
  return data;
}

/**
 * Reset form fields
 */
function resetForm(formId) {
  const form = document.getElementById(formId);
  if (form) {
    form.reset();
  }
}

/**
 * Validate email format
 */
function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * Validate phone number (10 digits)
 */
function isValidPhone(phone) {
  const regex = /^\d{10}$/;
  return regex.test(phone.replace(/\D/g, ''));
}

/**
 * Validate required fields
 */
function validateRequired(fields) {
  const errors = [];
  
  fields.forEach(field => {
    const element = document.querySelector(`[name="${field}"]`);
    if (!element || !element.value.trim()) {
      errors.push(`${field} is required`);
    }
  });
  
  return errors;
}

// ── Notification System ────────────────────────────────────

/**
 * Show notification toast
 */
function showNotification(message, type = 'info', duration = 3000) {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => notification.classList.add('show'), 10);
  
  // Auto remove
  if (duration) {
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, duration);
  }
  
  return notification;
}

/**
 * Show success notification
 */
function showSuccess(message) {
  showNotification(message, 'success');
}

/**
 * Show error notification
 */
function showError(message) {
  showNotification(message, 'error');
}

/**
 * Show warning notification
 */
function showWarning(message) {
  showNotification(message, 'warning');
}

/**
 * Show info notification
 */
function showInfo(message) {
  showNotification(message, 'info');
}

// ── Modal Helpers ──────────────────────────────────────────

/**
 * Open modal
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'flex';
    modal.classList.add('active');
  }
}

/**
 * Close modal
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'none';
    modal.classList.remove('active');
  }
}

/**
 * Close all modals
 */
function closeAllModals() {
  const modals = document.querySelectorAll('.modal');
  modals.forEach(modal => {
    modal.style.display = 'none';
    modal.classList.remove('active');
  });
}

/**
 * Show confirmation dialog
 */
function showConfirmation(message) {
  return new Promise((resolve) => {
    if (confirm(message)) {
      resolve(true);
    } else {
      resolve(false);
    }
  });
}

// ── Table Utilities ────────────────────────────────────────

/**
 * Filter table rows based on column text
 */
function filterTable(tableId, searchTerm, columnIndex = null) {
  const table = document.getElementById(tableId);
  if (!table) return;
  
  const rows = table.querySelectorAll('tbody tr');
  const lowerSearchTerm = searchTerm.toLowerCase();
  
  rows.forEach(row => {
    let match = false;
    
    if (columnIndex !== null) {
      // Search specific column
      const cell = row.cells[columnIndex];
      if (cell && cell.textContent.toLowerCase().includes(lowerSearchTerm)) {
        match = true;
      }
    } else {
      // Search all columns
      for (let cell of row.cells) {
        if (cell.textContent.toLowerCase().includes(lowerSearchTerm)) {
          match = true;
          break;
        }
      }
    }
    
    row.style.display = match ? '' : 'none';
  });
}

/**
 * Sort table by column
 */
function sortTable(tableId, columnIndex, ascending = true) {
  const table = document.getElementById(tableId);
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  
  rows.sort((a, b) => {
    const aVal = a.cells[columnIndex].textContent.trim();
    const bVal = b.cells[columnIndex].textContent.trim();
    
    // Try numeric comparison
    const aNum = parseFloat(aVal);
    const bNum = parseFloat(bVal);
    
    if (!isNaN(aNum) && !isNaN(bNum)) {
      return ascending ? aNum - bNum : bNum - aNum;
    }
    
    // String comparison
    return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
  });
  
  rows.forEach(row => tbody.appendChild(row));
}

/**
 * Export table to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
  const table = document.getElementById(tableId);
  if (!table) return;
  
  const csv = [];
  const rows = table.querySelectorAll('tr');
  
  rows.forEach(row => {
    const cols = row.querySelectorAll('td, th');
    const rowData = [];
    
    cols.forEach(col => {
      rowData.push('"' + col.textContent.trim() + '"');
    });
    
    csv.push(rowData.join(','));
  });
  
  // Create blob and download
  const csvContent = csv.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  a.remove();
}

// ── Date/Time Utilities ────────────────────────────────────

/**
 * Format date to readable string
 */
function formatDate(date) {
  if (typeof date === 'string') {
    date = new Date(date);
  }
  
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

/**
 * Format time to readable string
 */
function formatTime(date) {
  if (typeof date === 'string') {
    date = new Date(date);
  }
  
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = '₹') {
  return currency + ' ' + parseFloat(amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

// ── Utility Functions ──────────────────────────────────────

/**
 * Deep clone object
 */
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Check if object is empty
 */
function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

/**
 * Debounce function
 */
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function
 */
function throttle(func, limit = 300) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Get URL parameter
 */
function getUrlParam(paramName) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(paramName);
}

/**
 * Set loading state on element
 */
function setLoading(elementId, isLoading = true) {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  if (isLoading) {
    element.classList.add('loading');
    element.disabled = true;
  } else {
    element.classList.remove('loading');
    element.disabled = false;
  }
}

// ── Event Listeners ────────────────────────────────────────

// Close modal when clicking outside
document.addEventListener('click', function(event) {
  if (event.target.classList.contains('modal')) {
    closeAllModals();
  }
});

// Prevent body scroll when modal is open
function toggleBodyScroll(disable = false) {
  if (disable) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = 'auto';
  }
}

console.log('Utils loaded successfully');

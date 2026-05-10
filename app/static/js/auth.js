/**
 * Authentication Module
 * Handles user login, logout, and authentication status
 */

/**
 * Initialize auth UI on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    // Refresh auth status every 30 seconds
    setInterval(checkAuthStatus, 30000);
});

/**
 * Check current authentication status
 */
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status', {
            method: 'GET',
            credentials: 'include',
        });
        const data = await response.json();
        updateAuthUI(data.authenticated, data.role);
    } catch (error) {
        console.error('Error checking auth status:', error);
    }
}

/**
 * Update UI based on authentication status
 */
function updateAuthUI(isAuthenticated, role) {
    const authButton = document.getElementById('auth-button');
    const authStatusDiv = document.getElementById('auth-status');
    
    if (isAuthenticated && role === 'admin') {
        authButton.textContent = 'Logout (Admin)';
        authButton.className = 'btn-success';
        authButton.onclick = handleLogout;
        authStatusDiv.innerHTML = '<span class="status-dot" style="background-color: #27ae60;"></span> Admin Mode';
    } else {
        authButton.textContent = 'Login (Admin)';
        authButton.className = 'btn-secondary';
        authButton.onclick = handleAuthClick;
        authStatusDiv.innerHTML = '<span class="status-dot"></span> Simple User';
    }
}

/**
 * Handle auth button click
 */
function handleAuthClick() {
    openAuthModal();
}

/**
 * Open authentication modal
 */
function openAuthModal() {
    const modal = document.getElementById('auth-modal');
    const formContainer = document.getElementById('auth-form-container');
    const successContainer = document.getElementById('auth-success-container');
    
    modal.style.display = 'block';
    formContainer.style.display = 'block';
    successContainer.style.display = 'none';
    
    // Clear error message
    const errorDiv = document.getElementById('auth-error');
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
    
    // Clear password field
    document.getElementById('admin-password').value = '';
    document.getElementById('admin-password').focus();
}

/**
 * Close authentication modal
 */
function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    modal.style.display = 'none';
}

/**
 * Handle admin login form submission
 */
async function handleAdminLogin(event) {
    event.preventDefault();
    
    const password = document.getElementById('admin-password').value;
    const errorDiv = document.getElementById('auth-error');
    const formContainer = document.getElementById('auth-form-container');
    const successContainer = document.getElementById('auth-success-container');
    
    // Clear previous error
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
    
    if (!password.trim()) {
        errorDiv.textContent = 'Password is required';
        errorDiv.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ password }),
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Show success message
            formContainer.style.display = 'none';
            successContainer.style.display = 'block';
            
            // Update auth UI
            checkAuthStatus();
            
            // Retry pending request if any
            if (window._pendingAdminRequest) {
                setTimeout(retryPendingAdminRequest, 500);
                setTimeout(closeAuthModal, 1000);
            } else {
                // Close modal after 2 seconds
                setTimeout(closeAuthModal, 2000);
            }
        } else {
            errorDiv.textContent = data.error || 'Authentication failed. Please check the password.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = 'An error occurred. Please try again.';
        errorDiv.style.display = 'block';
    }
}

/**
 * Handle logout
 */
async function handleLogout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include',
        });
        
        if (response.ok) {
            // Update auth UI
            checkAuthStatus();
            alert('Logged out successfully');
            window.location.reload();
        } else {
            alert('Logout failed');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('An error occurred during logout');
    }
}

/**
 * Utility function to check if user is admin before making API calls
 */
async function requireAdminAuth(callback) {
    try {
        const response = await fetch('/api/auth/status', {
            method: 'GET',
            credentials: 'include',
        });
        const data = await response.json();
        
        if (data.authenticated && data.role === 'admin') {
            callback();
        } else {
            openAuthModal();
        }
    } catch (error) {
        console.error('Error checking admin status:', error);
        openAuthModal();
    }
}

/**
 * Wrapper for making admin-protected API calls
 */
async function makeAdminRequest(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            ...options,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });
        
        const data = await response.json();
        
        if (response.status === 403 && data.requires_auth) {
            // Not authenticated as admin - prompt for login
            return new Promise((resolve, reject) => {
                // Store the pending request
                window._pendingAdminRequest = {
                    endpoint,
                    options,
                    resolve,
                    reject
                };
                
                // Show auth modal
                openAuthModal();
                
                // Set a timeout in case user cancels
                setTimeout(() => {
                    if (window._pendingAdminRequest) {
                        window._pendingAdminRequest = null;
                        reject(new Error('Admin authentication required'));
                    }
                }, 60000); // 60 second timeout
            });
        }
        
        return { ok: response.ok, status: response.status, data };
    } catch (error) {
        console.error('Request error:', error);
        throw error;
    }
}

/**
 * Retry pending admin request after successful authentication
 */
async function retryPendingAdminRequest() {
    if (!window._pendingAdminRequest) return;
    
    const { endpoint, options, resolve, reject } = window._pendingAdminRequest;
    window._pendingAdminRequest = null;
    
    try {
        const result = await makeAdminRequest(endpoint, options);
        resolve(result);
    } catch (error) {
        reject(error);
    }
}

// Close modal when clicking outside of it
window.addEventListener('click', function(event) {
    const modal = document.getElementById('auth-modal');
    if (event.target === modal) {
        closeAuthModal();
    }
});

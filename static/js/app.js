/* ============================================================================
   HR Portal - JavaScript Utilities
   ============================================================================ */

/**
 * Check if user is authenticated
 */
function checkAuthStatus() {
    fetch('/api/auth/current', {
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (!data.user && window.location.pathname !== '/') {
            window.location.href = '/';
        }
        if (data.user) {
            document.getElementById('user-name') = data.user.full_name;
            document.getElementById('user-full-name') = data.user.full_name;
        }
    })
    .catch(error => console.error('Auth check error:', error));
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Format datetime to readable string
 */
function formatDateTime(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Get status badge CSS class
 */
function getStatusClass(status) {
    const statusLower = status.toLowerCase().replace(/\s+/g, '');
    if (statusLower.includes('pending')) return 'pending';
    if (statusLower.includes('action')) return 'action';
    if (statusLower.includes('resolved')) return 'resolved';
    return 'pending';
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `notification notification-${type}`;
    notificationDiv.textContent = message;
    notificationDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notificationDiv);
    
    setTimeout(() => {
        notificationDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notificationDiv.remove(), 300);
    }, duration);
}

/**
 * API request helper
 */
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };
    
    const response = await fetch(endpoint, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        if (response.status === 401) {
            window.location.href = '/';
        }
        throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
}

/**
 * Validate email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number (10 digits)
 */
function isValidPhone(phone) {
    return /^\d{10}$/.test(phone);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
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
function throttle(func, limit) {
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
 * Get URL parameters
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Download CSV
 */
function downloadCSV(filename, data) {
    const csv = data.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
}

/**
 * Print page
 */
function printPage() {
    window.print();
}

/* Add slide animation styles */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ HR Portal initialized');
});

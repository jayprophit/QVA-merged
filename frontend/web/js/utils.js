/**
 * Quantum Virtual Assistant (QVA) - Utility Functions
 * Helper functions for the QVA frontend
 */

/**
 * Format a number as a percentage
 * @param {number} value - The value to format
 * @param {number} precision - Decimal precision
 * @returns {string} Formatted percentage
 */
function formatPercent(value, precision = 1) {
    return value.toFixed(precision) + '%';
}

/**
 * Format a number with appropriate units (K, M, G, etc.)
 * @param {number} value - The value to format
 * @param {number} precision - Decimal precision
 * @returns {string} Formatted value with units
 */
function formatNumber(value, precision = 1) {
    const units = ['', 'K', 'M', 'G', 'T'];
    let unitIndex = 0;
    let scaledValue = value;
    
    while (scaledValue >= 1000 && unitIndex < units.length - 1) {
        scaledValue /= 1000;
        unitIndex++;
    }
    
    return scaledValue.toFixed(precision) + units[unitIndex];
}

/**
 * Format date and time
 * @param {Date|string} date - Date object or date string
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
function formatDate(date, includeTime = false) {
    const d = new Date(date);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return d.toLocaleDateString(undefined, options);
}

/**
 * Format a timestamp as relative time (e.g., "2 hours ago")
 * @param {Date|string} date - Date object or date string
 * @returns {string} Relative time string
 */
function formatRelativeTime(date) {
    const d = new Date(date);
    const now = new Date();
    const diff = now - d;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
        return days === 1 ? '1 day ago' : `${days} days ago`;
    } else if (hours > 0) {
        return hours === 1 ? '1 hour ago' : `${hours} hours ago`;
    } else if (minutes > 0) {
        return minutes === 1 ? '1 minute ago' : `${minutes} minutes ago`;
    } else {
        return seconds <= 10 ? 'just now' : `${seconds} seconds ago`;
    }
}

/**
 * Truncate a string to a specified length
 * @param {string} str - String to truncate
 * @param {number} length - Maximum length
 * @param {string} suffix - Suffix to add when truncated
 * @returns {string} Truncated string
 */
function truncateString(str, length = 30, suffix = '...') {
    if (!str) return '';
    if (str.length <= length) return str;
    return str.substring(0, length - suffix.length) + suffix;
}

/**
 * Generate a random ID
 * @param {number} length - Length of the ID
 * @returns {string} Random ID
 */
function generateId(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let id = '';
    
    for (let i = 0; i < length; i++) {
        id += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    return id;
}

/**
 * Debounce a function call
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, delay = 300) {
    let timeoutId;
    
    return function(...args) {
        const context = this;
        
        clearTimeout(timeoutId);
        
        timeoutId = setTimeout(() => {
            func.apply(context, args);
        }, delay);
    };
}

/**
 * Create a throttled function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Throttle limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit = 300) {
    let inThrottle = false;
    
    return function(...args) {
        const context = this;
        
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            
            setTimeout(() => {
                inThrottle = false;
            }, limit);
        }
    };
}

/**
 * Deep clone an object
 * @param {Object} obj - Object to clone
 * @returns {Object} Cloned object
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Check if a value is empty (null, undefined, empty string, empty array, or empty object)
 * @param {*} value - Value to check
 * @returns {boolean} Whether the value is empty
 */
function isEmpty(value) {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string' && value.trim() === '') return true;
    if (Array.isArray(value) && value.length === 0) return true;
    if (typeof value === 'object' && Object.keys(value).length === 0) return true;
    return false;
}

/**
 * Format a blockchain address (truncate the middle)
 * @param {string} address - Blockchain address
 * @returns {string} Formatted address
 */
function formatAddress(address) {
    if (!address || address.length < 10) return address;
    return address.substring(0, 6) + '...' + address.substring(address.length - 4);
}

/**
 * Format an amount of cryptocurrency
 * @param {number} amount - Amount to format
 * @param {number} precision - Decimal precision
 * @returns {string} Formatted amount
 */
function formatCrypto(amount, precision = 4) {
    return amount.toFixed(precision);
}

// Export utilities if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatPercent,
        formatNumber,
        formatDate,
        formatRelativeTime,
        truncateString,
        generateId,
        debounce,
        throttle,
        deepClone,
        isEmpty,
        formatAddress,
        formatCrypto
    };
}

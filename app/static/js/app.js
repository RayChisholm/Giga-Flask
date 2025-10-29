// Zendesk Bulk Operations Tool - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {

    // Initialize dark mode
    initializeDarkMode();

    // Initialize tooltips
    initializeTooltips();

    // Initialize loading spinners
    initializeLoadingStates();

    // Initialize form enhancements
    initializeFormEnhancements();

    // Initialize table enhancements
    initializeTableEnhancements();

    // Initialize smooth scrolling
    initializeSmoothScrolling();
});

/**
 * Initialize dark mode
 */
function initializeDarkMode() {
    // Check localStorage for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Apply theme: saved preference > system preference > light
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    setTheme(theme);

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

/**
 * Set theme
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    // Update toggle button icon if it exists
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.classList.remove('bi-moon-stars');
                icon.classList.add('bi-sun');
            } else {
                icon.classList.remove('bi-sun');
                icon.classList.add('bi-moon-stars');
            }
        }
    }
}

/**
 * Toggle theme
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize loading spinners for forms
 */
function initializeLoadingStates() {
    // Create spinner overlay
    if (!document.getElementById('spinner-overlay')) {
        const spinnerOverlay = document.createElement('div');
        spinnerOverlay.id = 'spinner-overlay';
        spinnerOverlay.className = 'spinner-overlay';
        spinnerOverlay.innerHTML = `
            <div class="spinner-content">
                <div class="spinner-border spinner-border-lg text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 mb-0 text-dark fw-bold">Processing your request...</p>
                <p class="text-muted small">This may take a few moments</p>
            </div>
        `;
        document.body.appendChild(spinnerOverlay);
    }

    // Add submit handlers to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Don't show spinner for search/filter forms
            if (form.classList.contains('no-spinner')) {
                return;
            }

            // Validate form first
            if (form.checkValidity()) {
                showLoadingSpinner();

                // Add loading class to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                }
            }
        });
    });
}

/**
 * Show loading spinner overlay
 */
function showLoadingSpinner() {
    const overlay = document.getElementById('spinner-overlay');
    if (overlay) {
        overlay.classList.add('show');
    }
}

/**
 * Hide loading spinner overlay
 */
function hideLoadingSpinner() {
    const overlay = document.getElementById('spinner-overlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

/**
 * Initialize form enhancements
 */
function initializeFormEnhancements() {
    // Add floating labels effect
    const inputs = document.querySelectorAll('.form-control, .form-select');
    inputs.forEach(input => {
        // Add blur event for validation feedback
        input.addEventListener('blur', function() {
            if (this.value.trim() === '' && this.hasAttribute('required')) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
                if (this.value.trim() !== '') {
                    this.classList.add('is-valid');
                }
            }
        });

        // Remove invalid class on input
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
    });

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea.form-control');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'form-text text-end';
            counter.innerHTML = `<span class="char-count">0</span> / ${maxLength}`;
            textarea.parentNode.appendChild(counter);

            textarea.addEventListener('input', function() {
                const count = this.value.length;
                counter.querySelector('.char-count').textContent = count;

                if (count > maxLength * 0.9) {
                    counter.classList.add('text-warning');
                } else {
                    counter.classList.remove('text-warning');
                }
            });
        }
    });
}

/**
 * Initialize table enhancements
 */
function initializeTableEnhancements() {
    // Add search functionality to tables
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        // Add search box if table has many rows
        if (table.querySelectorAll('tbody tr').length > 10) {
            addTableSearch(table);
        }

        // Make table rows clickable if they have a link
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const link = row.querySelector('a');
            if (link && !row.classList.contains('no-click')) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', function(e) {
                    // Don't trigger if clicking directly on a link or button
                    if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
                        link.click();
                    }
                });
            }
        });
    });
}

/**
 * Add search functionality to a table
 */
function addTableSearch(table) {
    const searchDiv = document.createElement('div');
    searchDiv.className = 'mb-3 search-bar';
    searchDiv.innerHTML = `
        <i class="bi bi-search"></i>
        <input type="text" class="form-control" placeholder="Search table...">
    `;

    table.parentNode.insertBefore(searchDiv, table);

    const searchInput = searchDiv.querySelector('input');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

/**
 * Initialize smooth scrolling
 */
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

/**
 * Show success message with animation
 */
function showSuccessMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3 success-animation';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Confirm dangerous actions
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}, 100);

/**
 * Keyboard shortcuts (macOS optimized)
 */
document.addEventListener('keydown', function(e) {
    // Cmd + K: Go to home/dashboard
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        window.location.href = '/';
    }

    // Cmd + Shift + A: Go to admin (if admin)
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'a') {
        e.preventDefault();
        const adminLink = document.querySelector('a[href="/admin/"]');
        if (adminLink) {
            window.location.href = '/admin/';
        }
    }

    // Cmd + Shift + D: Toggle dark mode
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'd') {
        e.preventDefault();
        toggleTheme();
    }

    // Cmd + /: Toggle search focus (if search exists)
    if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="text"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // ESC: Clear active modals or go back
    if (e.key === 'Escape') {
        const modal = document.querySelector('.modal.show');
        if (!modal) {
            // If no modal is open, clicking ESC goes back
            const cancelBtn = document.querySelector('.btn-outline-secondary[href]');
            if (cancelBtn && window.location.pathname !== '/') {
                window.history.back();
            }
        }
    }

    // Cmd + Enter: Submit active form
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm && !activeForm.classList.contains('no-quick-submit')) {
            e.preventDefault();
            activeForm.requestSubmit();
        }
    }
});

/**
 * Add copy-to-clipboard functionality
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showSuccessMessage('Copied to clipboard!');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}

/**
 * Format numbers with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Debounce function for search inputs
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

// Export functions for use in inline scripts
window.GigaFlask = {
    showLoadingSpinner,
    hideLoadingSpinner,
    showSuccessMessage,
    confirmAction,
    copyToClipboard,
    formatNumber,
    debounce,
    toggleTheme,
    setTheme
};

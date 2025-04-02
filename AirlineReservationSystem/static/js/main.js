// Main JavaScript file for SkyWay Airlines

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Add auto-dismiss for alerts
    const alertList = document.querySelectorAll('.alert:not(.alert-permanent)')
    alertList.forEach(function (alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5 second timeout
    });
    
    // Add event listener to the booking search form
    const bookingSearchForm = document.getElementById('bookingSearchForm');
    if (bookingSearchForm) {
        bookingSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Form validation would go here in a real implementation
            alert('Booking search functionality will be implemented in a future update.');
        });
    }
    
    // Add event listener for date inputs to set min date to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (!input.getAttribute('min')) {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('min', today);
        }
    });
    
    // Add fade-in effect for page content
    const mainContent = document.querySelector('main.container');
    if (mainContent) {
        mainContent.style.opacity = 0;
        mainContent.style.transition = 'opacity 0.4s ease-in-out';
        
        setTimeout(function() {
            mainContent.style.opacity = 1;
        }, 100);
    }
});

// Utility functions
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
}

function showLoadingSpinner() {
    // Create and show a loading spinner
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(spinner);
    
    return spinner;
}

function hideLoadingSpinner(spinner) {
    // Remove the loading spinner
    if (spinner && spinner.parentNode) {
        spinner.parentNode.removeChild(spinner);
    }
}

// Seat Selection JavaScript for SkyWay Airlines

document.addEventListener('DOMContentLoaded', function() {
    // Ensure maxSelections is defined (set by inline script in booking.html)
    if (typeof maxSelections === 'undefined') {
        console.error('maxSelections is not defined. Defaulting to 1.');
        window.maxSelections = 1; // Fallback value
    }

    // Initialize selectedSeats if not already defined
    if (typeof selectedSeats === 'undefined') {
        window.selectedSeats = [];
    }

    // Initialize seat map interactions
    initializeSeatMap();
    
    // Update the pay button state on page load
    updatePayButtonState();
});

/**
 * Initialize the seat map with click handlers and visual indicators
 */
function initializeSeatMap() {
    const availableSeats = document.querySelectorAll('.seat.available');
    
    availableSeats.forEach(seat => {
        // Remove any existing onclick attributes to avoid conflicts
        seat.removeAttribute('onclick');
        
        // Add click handler
        seat.addEventListener('click', function() {
            selectSeat(this);
        });

        // Add hover effects
        seat.addEventListener('mouseenter', function() {
            if (!this.classList.contains('selected')) {
                this.style.backgroundColor = '#6c757d'; // Hover color (gray)
            }
        });
        
        seat.addEventListener('mouseleave', function() {
            if (!this.classList.contains('selected')) {
                this.style.backgroundColor = '#495057'; // Reset to original available color
            }
        });
    });
}

/**
 * Handle seat selection/deselection
 * @param {HTMLElement} seatElement - The seat element to toggle
 */
function selectSeat(seatElement) {
    const seat = seatElement.dataset.seat;

    if (seatElement.classList.contains('selected')) {
        // Deselect seat
        seatElement.classList.remove('selected');
        seatElement.classList.add('available');
        selectedSeats = selectedSeats.filter(s => s !== seat);
    } else {
        // Check if maximum seats are already selected
        if (selectedSeats.length >= maxSelections) {
            showErrorMessage(`You can only select ${maxSelections} seat(s).`);
            return;
        }
        
        // Select seat
        seatElement.classList.remove('available');
        seatElement.classList.add('selected');
        selectedSeats.push(seat);
    }
    
    // Update hidden input and display
    updateSelectedSeatsInput();
    updatePayButtonState();
}

/**
 * Update the hidden input field and display text with the current selected seats
 */
function updateSelectedSeatsInput() {
    const selectedSeatsInput = document.getElementById('selected_seats');
    const selectedSeatsText = document.getElementById('selectedSeatsText');
    
    if (selectedSeatsInput) {
        selectedSeatsInput.value = selectedSeats.join(',');
    } else {
        console.error('Element with ID "selected_seats" not found.');
    }
    
    if (selectedSeatsText) {
        selectedSeatsText.textContent = selectedSeats.length > 0 ? selectedSeats.join(', ') : 'None';
    } else {
        console.error('Element with ID "selectedSeatsText" not found.');
    }
}

/**
 * Update the pay button state based on seat selection
 */
function updatePayButtonState() {
    const payButton = document.getElementById('payButton');
    if (payButton) {
        payButton.disabled = selectedSeats.length !== maxSelections;
        console.log("Selected seats:", selectedSeats, "Pay button enabled:", !payButton.disabled);
    } else {
        console.error('Element with ID "payButton" not found.');
    }
}

/**
 * Display an error message to the user
 * @param {string} message - The error message to display
 */
function showErrorMessage(message) {
    let errorContainer = document.getElementById('seat-selection-error');
    
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'seat-selection-error';
        errorContainer.className = 'alert alert-danger alert-dismissible fade show mt-3';
        errorContainer.role = 'alert';
        
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.setAttribute('data-bs-dismiss', 'alert');
        closeButton.setAttribute('aria-label', 'Close');
        
        errorContainer.appendChild(closeButton);
        
        const seatMapContainer = document.querySelector('.seat-map-container');
        if (seatMapContainer) {
            seatMapContainer.appendChild(errorContainer);
        } else {
            console.error('Seat map container not found. Appending error to body.');
            document.body.appendChild(errorContainer);
        }
    }
    
    // Update the error message while preserving the close button
    errorContainer.innerHTML = message + errorContainer.innerHTML.substring(errorContainer.innerHTML.indexOf('<button'));
    
    // Auto-dismiss after 5 seconds (requires Bootstrap JS)
    setTimeout(() => {
        if (errorContainer && errorContainer.parentNode) {
            new bootstrap.Alert(errorContainer).close();
        }
    }, 5000);
}
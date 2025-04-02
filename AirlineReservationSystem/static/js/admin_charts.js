// Admin Dashboard Charts for SkyWay Airlines

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if we're on the admin dashboard
    if (document.getElementById('flightsChart') && document.getElementById('bookingsChart')) {
        initializeFlightsChart();
        initializeBookingsChart();
        initializeRevenueChart();
    }
});

/**
 * Initialize the flights status chart
 */
function initializeFlightsChart() {
    const flightsCtx = document.getElementById('flightsChart').getContext('2d');
    
    // Get chart data from the data attributes or use defaults
    const chartData = {
        active: parseInt(document.getElementById('flightsChart').dataset.active || 0),
        completed: parseInt(document.getElementById('flightsChart').dataset.completed || 0),
        cancelled: parseInt(document.getElementById('flightsChart').dataset.cancelled || 0)
    };
    
    const flightsChart = new Chart(flightsCtx, {
        type: 'doughnut',
        data: {
            labels: ['Active', 'Completed', 'Cancelled'],
            datasets: [{
                data: [chartData.active, chartData.completed, chartData.cancelled],
                backgroundColor: [
                    '#0d6efd', // Primary (blue)
                    '#198754', // Success (green)
                    '#dc3545'  // Danger (red)
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f8f9fa'
                    }
                },
                tooltip: {
                    backgroundColor: '#343a40',
                    titleColor: '#f8f9fa',
                    bodyColor: '#f8f9fa',
                    borderColor: '#6c757d',
                    borderWidth: 1
                }
            }
        }
    });
}

/**
 * Initialize the bookings status chart
 */
function initializeBookingsChart() {
    const bookingsCtx = document.getElementById('bookingsChart').getContext('2d');
    
    // Get chart data from the data attributes or use defaults
    const chartData = {
        confirmed: parseInt(document.getElementById('bookingsChart').dataset.confirmed || 0),
        cancelled: parseInt(document.getElementById('bookingsChart').dataset.cancelled || 0),
        checkedIn: parseInt(document.getElementById('bookingsChart').dataset.checkedIn || 0)
    };
    
    const bookingsChart = new Chart(bookingsCtx, {
        type: 'doughnut',
        data: {
            labels: ['Confirmed', 'Cancelled', 'Checked-in'],
            datasets: [{
                data: [chartData.confirmed, chartData.cancelled, chartData.checkedIn],
                backgroundColor: [
                    '#198754', // Success (green)
                    '#dc3545', // Danger (red)
                    '#0dcaf0'  // Info (cyan)
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f8f9fa'
                    }
                },
                tooltip: {
                    backgroundColor: '#343a40',
                    titleColor: '#f8f9fa',
                    bodyColor: '#f8f9fa',
                    borderColor: '#6c757d',
                    borderWidth: 1
                }
            }
        }
    });
}

/**
 * Initialize the revenue chart
 */
function initializeRevenueChart() {
    // Check if the revenue chart exists
    const revenueChartElement = document.getElementById('revenueChart');
    if (!revenueChartElement) return;
    
    const revenueCtx = revenueChartElement.getContext('2d');
    
    // Generate some demo data for the last 7 days
    const labels = [];
    const data = [];
    
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        // Generate a random value between 5000 and 15000
        data.push(Math.floor(Math.random() * 10000) + 5000);
    }
    
    const revenueChart = new Chart(revenueCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Revenue',
                data: data,
                backgroundColor: 'rgba(13, 110, 253, 0.2)',
                borderColor: '#0d6efd',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
                pointBackgroundColor: '#0d6efd',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8f9fa'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f8f9fa',
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#f8f9fa'
                    }
                },
                tooltip: {
                    backgroundColor: '#343a40',
                    titleColor: '#f8f9fa',
                    bodyColor: '#f8f9fa',
                    borderColor: '#6c757d',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return 'Revenue: $' + context.raw.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

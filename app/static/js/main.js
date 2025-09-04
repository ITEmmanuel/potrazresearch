// Custom JavaScript for POTRAZ Research
document.addEventListener('DOMContentLoaded', function() {
    console.log('POTRAZ Research application loaded');
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Auto-refresh document status every 30 seconds on dashboard
    if (window.location.pathname.includes('/dashboard')) {
        setInterval(refreshDocumentStatus, 30000);
    }
    
    // File upload handling
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (file.size > maxSize) {
                    alert('File size must be less than 16MB');
                    e.target.value = '';
                    return;
                }
                
                // Show file name
                const fileName = document.querySelector('.file-name');
                if (fileName) {
                    fileName.textContent = file.name;
                }
            }
        });
    }
    
    // Form submission loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
        });
    });
});

// Function to refresh document status
function refreshDocumentStatus() {
    const statusElements = document.querySelectorAll('[data-document-id]');
    statusElements.forEach(element => {
        const documentId = element.dataset.documentId;
        if (documentId) {
            fetch(`/api/document/${documentId}/status`)
                .then(response => response.json())
                .then(data => {
                    if (data.status !== element.textContent.trim()) {
                        // Reload page if status changed
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error checking document status:', error);
                });
        }
    });
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Export for global use
window.POTRAZ = {
    showAlert: showAlert,
    refreshDocumentStatus: refreshDocumentStatus
};

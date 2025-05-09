document.addEventListener('DOMContentLoaded', function() {
    // HTMX Events
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        // Add any global pre-request handling
        console.log('Request starting:', event.detail.requestConfig);
    });
    
    document.body.addEventListener('htmx:afterRequest', function(event) {
        // Add any global post-request handling
        console.log('Request completed:', event.detail.xhr.status);
    });
    
    document.body.addEventListener('htmx:responseError', function(event) {
        // Handle errors
        console.error('Request error:', event.detail.xhr.status, event.detail.xhr.responseText);
        
        // Show error message to user
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.innerHTML = `
            <div class="alert alert-error">
                <p><strong>Chyba:</strong> Nastala chyba při zpracování požadavku.</p>
                <p>Kód: ${event.detail.xhr.status}</p>
                <button class="close-btn">&times;</button>
            </div>
        `;
        
        document.body.appendChild(errorMessage);
        
        // Add event listener to close button
        errorMessage.querySelector('.close-btn').addEventListener('click', function() {
            errorMessage.remove();
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(errorMessage)) {
                errorMessage.remove();
            }
        }, 5000);
    });
    
    // File upload preview
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            if (fileName) {
                // You could add a preview here if needed
                console.log('File selected:', fileName);
            }
        });
    }
    
    // Auto-refresh for processing status
    const resultStatus = document.getElementById('result-status');
    if (resultStatus) {
        // HTMX will handle the polling
        console.log('Monitoring processing status...');
    }
});

// Helper function to format currency
function formatCurrency(amount, currency = 'CZK') {
    if (amount === null || amount === undefined) return 'N/A';
    
    return new Intl.NumberFormat('cs-CZ', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    }).format(amount);
}

// Helper function to format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('cs-CZ').format(date);
}

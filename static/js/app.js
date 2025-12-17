// API endpoints
const API_BASE = '/api';

// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const uploadStatus = document.getElementById('uploadStatus');
const statsDiv = document.getElementById('stats');
const queryInput = document.getElementById('queryInput');
const queryBtn = document.getElementById('queryBtn');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const exampleButtons = document.querySelectorAll('.example-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    setupEventListeners();
});

// Event listeners
function setupEventListeners() {
    uploadBtn.addEventListener('click', uploadCatalog);
    clearBtn.addEventListener('click', clearDatabase);
    queryBtn.addEventListener('click', queryProducts);
    
    // Allow Enter key to submit query (Ctrl+Enter for new line)
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
            e.preventDefault();
            queryProducts();
        }
    });
    
    // Example button clicks
    exampleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            queryInput.value = btn.textContent.replace(/"/g, '');
            queryProducts();
        });
    });
}

// Upload catalog
async function uploadCatalog() {
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('Please select a file first', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';
    showStatus('Uploading and processing catalog...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus(`✅ ${data.message} (${data.products_count} products)`, 'success');
            fileInput.value = '';
            loadStats();
        } else {
            showStatus(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload';
    }
}

// Clear database
async function clearDatabase() {
    if (!confirm('Are you sure you want to clear all products from the database?')) {
        return;
    }
    
    clearBtn.disabled = true;
    clearBtn.textContent = 'Clearing...';
    
    try {
        const response = await fetch(`${API_BASE}/clear`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus(`✅ ${data.message}`, 'success');
            resultsDiv.innerHTML = '';
            loadStats();
        } else {
            showStatus(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        clearBtn.disabled = false;
        clearBtn.textContent = 'Clear Database';
    }
}

// Query products
async function queryProducts() {
    const query = queryInput.value.trim();
    
    if (!query) {
        alert('Please enter a query');
        return;
    }
    
    queryBtn.disabled = true;
    queryBtn.textContent = 'Searching...';
    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            resultsDiv.innerHTML = `<div class="status-message error">❌ Error: ${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="status-message error">❌ Error: ${error.message}</div>`;
    } finally {
        queryBtn.disabled = false;
        queryBtn.textContent = 'Ask';
        loadingDiv.style.display = 'none';
    }
}

// Display results
function displayResults(data) {
    const { answer, products, count } = data;
    
    let html = '';
    
    // Display AI answer
    if (answer) {
        html += `
            <div class="answer-box">
                <h3>💡 Answer</h3>
                <p>${escapeHtml(answer)}</p>
            </div>
        `;
    }
    
    // Display products
    if (products && products.length > 0) {
        html += `
            <div class="products-section">
                <h3>📦 Related Products (${count})</h3>
                <div class="products-grid">
        `;
        
        products.forEach(product => {
            html += createProductCard(product);
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    resultsDiv.innerHTML = html;
}

// Create product card
function createProductCard(product) {
    const name = product.name || product.title || product.product_name || 'Unnamed Product';
    
    let detailsHtml = '';
    for (const [key, value] of Object.entries(product)) {
        if (value !== null && value !== '' && key !== 'id') {
            const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            detailsHtml += `
                <div class="product-detail">
                    <strong>${displayKey}:</strong>
                    <span>${escapeHtml(String(value))}</span>
                </div>
            `;
        }
    }
    
    return `
        <div class="product-card">
            <h4>${escapeHtml(name)}</h4>
            <div class="product-details">
                ${detailsHtml}
            </div>
        </div>
    `;
}

// Load stats
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        if (response.ok) {
            statsDiv.innerHTML = `
                <strong>Database Status:</strong> 
                ${data.total_products} products indexed
            `;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Show status message
function showStatus(message, type) {
    uploadStatus.innerHTML = `<div class="status-message ${type}">${message}</div>`;
    
    setTimeout(() => {
        uploadStatus.innerHTML = '';
    }, 5000);
}

// Utility: Escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

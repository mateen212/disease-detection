// Base API URL
const API_BASE_URL = '/api/v1';

// Global variables
let datasets = [];
let trainingInProgress = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// Initialize application
async function initializeApp() {
    await loadSystemStatus();
    await loadDatasets();
    loadOverviewStats();
}

// Setup event listeners
function setupEventListeners() {
    // Dataset upload form
    document.getElementById('datasetUploadForm').addEventListener('submit', handleDatasetUpload);
    
    // Training form
    document.getElementById('trainingForm').addEventListener('submit', handleTraining);
    
    // File upload preview
    document.getElementById('datasetFile').addEventListener('change', handleFileSelection);
}

// Tab switching functionality
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
    
    // Load tab-specific data
    if (tabName === 'datasets') {
        loadDatasets();
        populateDatasetSelect();
    } else if (tabName === 'system') {
        refreshSystemStatus();
    } else if (tabName === 'overview') {
        loadOverviewStats();
    }
}

// Load system status
async function loadSystemStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        updateSystemHealth(data);
        return data;
    } catch (error) {
        console.error('Failed to load system status:', error);
        showAlert('Failed to load system status', 'error');
    }
}

// Update system health display
function updateSystemHealth(healthData) {
    const systemHealthElement = document.getElementById('systemHealth');
    const healthStatusElement = document.getElementById('healthStatus');
    
    // Update overview stat
    systemHealthElement.textContent = healthData.status;
    
    // Update detailed health status
    const modelsLoaded = Object.values(healthData.models_loaded || {});
    const modelsCount = modelsLoaded.filter(Boolean).length;
    
    document.getElementById('modelsStatus').textContent = `${modelsCount}/${modelsLoaded.length}`;
    
    // Create detailed health status HTML
    let statusHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div class="status-item">
                <strong>Overall Status:</strong>
                <span class="status-badge ${healthData.status === 'healthy' ? 'status-success' : 'status-error'}">
                    ${healthData.status}
                </span>
            </div>
            <div class="status-item">
                <strong>Database:</strong>
                <span class="status-badge ${healthData.database_status === 'healthy' ? 'status-success' : 'status-error'}">
                    ${healthData.database_status}
                </span>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <strong>Models Status:</strong>
            <div style="margin-top: 10px;">
    `;
    
    for (const [modelName, isLoaded] of Object.entries(healthData.models_loaded || {})) {
        statusHTML += `
            <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                <span>${modelName.replace('_', ' ').toUpperCase()}:</span>
                <span class="status-badge ${isLoaded ? 'status-success' : 'status-error'}">
                    ${isLoaded ? 'loaded' : 'not found'}
                </span>
            </div>
        `;
    }
    
    statusHTML += '</div></div>';
    healthStatusElement.innerHTML = statusHTML;
}

// Load datasets
async function loadDatasets() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/datasets`);
        if (response.ok) {
            datasets = await response.json();
            displayDatasets();
            updateDatasetCount();
        } else {
            throw new Error('Failed to load datasets');
        }
    } catch (error) {
        console.error('Failed to load datasets:', error);
        document.getElementById('datasetsList').innerHTML = '<p>Failed to load datasets</p>';
    }
}

// Display datasets
function displayDatasets() {
    const datasetsContainer = document.getElementById('datasetsList');
    
    if (datasets.length === 0) {
        datasetsContainer.innerHTML = '<p>No datasets uploaded yet</p>';
        return;
    }
    
    let html = '';
    datasets.forEach(dataset => {
        const uploadDate = new Date(dataset.uploaded_at).toLocaleString();
        const fileSize = dataset.rows_count ? `${dataset.rows_count} rows, ${dataset.columns_count} columns` : 'Size unknown';
        
        html += `
            <div class="dataset-card">
                <div class="dataset-header">
                    <div>
                        <h4>${dataset.name}</h4>
                        <div class="dataset-info">
                            Type: ${dataset.dataset_type} | ${fileSize} | Uploaded: ${uploadDate}
                        </div>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-danger" onclick="deleteDataset(${dataset.id})">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
                ${dataset.description ? `<p>${dataset.description}</p>` : ''}
            </div>
        `;
    });
    
    datasetsContainer.innerHTML = html;
}

// Update dataset count in overview
function updateDatasetCount() {
    document.getElementById('totalDatasets').textContent = datasets.length;
}

// Handle file selection preview
function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
        const uploadArea = document.querySelector('.file-upload-area');
        uploadArea.innerHTML = `
            <p style="color: #27ae60; font-weight: bold;">📁 ${file.name}</p>
            <p style="color: #666;">Size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            <p style="color: #666; font-size: 14px;">Click to change file</p>
        `;
    }
}

// Handle dataset upload
async function handleDatasetUpload(event) {
    event.preventDefault();
    
    try {
        const formData = new FormData();
        const name = document.getElementById('datasetName').value;
        const type = document.getElementById('datasetType').value;
        const description = document.getElementById('datasetDescription').value;
        const file = document.getElementById('datasetFile').files[0];
        
        if (!file) {
            throw new Error('Please select a file to upload');
        }
        
        // Validate file size
        if (file.size > 10 * 1024 * 1024) {
            throw new Error('File size too large. Maximum 10MB allowed.');
        }
        
        formData.append('name', name);
        formData.append('dataset_type', type);
        formData.append('description', description);
        formData.append('file', file);
        
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/admin/upload-dataset`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Dataset uploaded successfully!', 'success');
            document.getElementById('datasetUploadForm').reset();
            resetFileUploadArea();
            await loadDatasets();
            populateDatasetSelect();
        } else {
            throw new Error(result.detail || 'Upload failed');
        }
        
    } catch (error) {
        showAlert(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Reset file upload area
function resetFileUploadArea() {
    const uploadArea = document.querySelector('.file-upload-area');
    uploadArea.innerHTML = `
        <p style="font-size: 18px; margin-bottom: 10px;">📂 Click to select dataset file</p>
        <p style="color: #666;">Supported: CSV files for symptoms, ZIP files for images (Max 10MB)</p>
    `;
}

// Populate dataset select dropdown
function populateDatasetSelect() {
    const select = document.getElementById('selectedDatasets');
    select.innerHTML = '';
    
    if (datasets.length === 0) {
        select.innerHTML = '<option value="">No datasets available</option>';
        return;
    }
    
    datasets.forEach(dataset => {
        const option = document.createElement('option');
        option.value = dataset.id;
        option.textContent = `${dataset.name} (${dataset.dataset_type})`;
        select.appendChild(option);
    });
}

// Handle training
async function handleTraining(event) {
    event.preventDefault();
    
    try {
        const modelType = document.getElementById('modelType').value;
        const selectedDatasetIds = Array.from(document.getElementById('selectedDatasets').selectedOptions)
            .map(option => parseInt(option.value));
        
        if (selectedDatasetIds.length === 0) {
            throw new Error('Please select at least one dataset');
        }
        
        trainingInProgress = true;
        showTrainingProgress(true);
        updateTrainingLog('Starting model training...\n');
        
        const formData = new FormData();
        formData.append('dataset_ids', JSON.stringify(selectedDatasetIds));
        formData.append('model_type', modelType);
        
        const response = await fetch(`${API_BASE_URL}/admin/train-model`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            updateTrainingLog(`Training completed successfully!\n`);
            updateTrainingLog(`Status: ${result.status}\n`);
            updateTrainingLog(`Training time: ${result.training_time.toFixed(2)} seconds\n`);
            
            if (result.results) {
                for (const [model, modelResult] of Object.entries(result.results)) {
                    updateTrainingLog(`\n${model.toUpperCase()} Results:\n`);
                    updateTrainingLog(`- Accuracy: ${(modelResult.accuracy * 100).toFixed(2)}%\n`);
                }
            }
            
            showAlert('Model training completed successfully!', 'success');
            await loadSystemStatus(); // Refresh system status
            
        } else {
            throw new Error(result.detail || 'Training failed');
        }
        
    } catch (error) {
        updateTrainingLog(`Error: ${error.message}\n`);
        showAlert(error.message, 'error');
    } finally {
        trainingInProgress = false;
        updateProgressBar(100);
        setTimeout(() => showTrainingProgress(false), 3000);
    }
}

// Show/hide training progress
function showTrainingProgress(show) {
    document.getElementById('trainingProgress').style.display = show ? 'block' : 'none';
    if (show) {
        updateProgressBar(0);
        document.getElementById('trainingLog').textContent = '';
    }
}

// Update progress bar
function updateProgressBar(percentage) {
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = percentage + '%';
    progressBar.textContent = percentage + '%';
}

// Update training log
function updateTrainingLog(message) {
    const log = document.getElementById('trainingLog');
    log.textContent += message;
    log.scrollTop = log.scrollHeight;
    
    // Simulate progress for demo
    if (trainingInProgress) {
        const currentProgress = parseInt(document.getElementById('progressBar').style.width) || 0;
        const newProgress = Math.min(currentProgress + Math.random() * 10, 90);
        updateProgressBar(newProgress);
    }
}

// Delete dataset
async function deleteDataset(datasetId) {
    if (!confirm('Are you sure you want to delete this dataset?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/datasets/${datasetId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Dataset deleted successfully', 'success');
            await loadDatasets();
            populateDatasetSelect();
        } else {
            throw new Error('Failed to delete dataset');
        }
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

// Refresh system status
async function refreshSystemStatus() {
    showLoading(true);
    try {
        await loadSystemStatus();
        showAlert('System status refreshed', 'success');
    } catch (error) {
        showAlert('Failed to refresh system status', 'error');
    } finally {
        showLoading(false);
    }
}

// Test API endpoint
async function testEndpoint(endpoint) {
    try {
        showLoading(true);
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`✅ ${endpoint} - Response: ${response.status}`, 'success');
        } else {
            throw new Error(`${response.status}: ${data.detail || 'Unknown error'}`);
        }
    } catch (error) {
        showAlert(`❌ ${endpoint} - Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Load overview statistics
async function loadOverviewStats() {
    try {
        // Load system info
        const infoResponse = await fetch(`${API_BASE_URL}/info`);
        if (infoResponse.ok) {
            const info = await infoResponse.json();
            updateSystemInfo(info);
        }
        
        // Update other stats (these would come from actual data in a real system)
        document.getElementById('totalPredictions').textContent = '0'; // Would be from database
        
    } catch (error) {
        console.error('Failed to load overview stats:', error);
    }
}

// Update system information display
function updateSystemInfo(info) {
    const systemInfoElement = document.getElementById('systemInfo');
    
    systemInfoElement.innerHTML = `
        <p><strong>Version:</strong> ${info.version}</p>
        <p><strong>Features:</strong> ${info.features.length} active</p>
        <p><strong>Supported Diseases:</strong></p>
        <ul>
            <li>Symptom-based: ${info.supported_diseases.symptom_based.join(', ')}</li>
            <li>Image-based: ${info.supported_diseases.image_based.join(', ')}</li>
        </ul>
    `;
}

// Utility functions
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function showAlert(message, type = 'info') {
    const alertId = `alert${type.charAt(0).toUpperCase() + type.slice(1)}`;
    const alertElement = document.getElementById(alertId);
    
    // Hide other alerts
    document.querySelectorAll('.alert').forEach(alert => {
        alert.style.display = 'none';
    });
    
    // Show the appropriate alert
    alertElement.textContent = message;
    alertElement.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertElement.style.display = 'none';
    }, 5000);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}
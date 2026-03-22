// Base API URL
const API_BASE_URL = '/api/v1';

// Global variables
let chart = null;
let currentUserId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    loadUserHistory();
});

// Initialize file upload functionality
function initializeFileUpload() {
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');

    imageUpload.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            // Validate file size (10MB max)
            if (file.size > 10 * 1024 * 1024) {
                showError('File size too large. Please select an image smaller than 10MB.');
                return;
            }

            // Validate file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            if (!validTypes.includes(file.type)) {
                showError('Invalid file type. Please select a JPG or PNG image.');
                return;
            }

            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.style.display = 'none';
        }
    });
}

// Collect selected symptoms
function getSelectedSymptoms() {
    const symptoms = [];
    const checkboxes = document.querySelectorAll('.symptom-checkbox input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
        symptoms.push(checkbox.value);
    });
    return symptoms;
}

// Validate form data
function validateForm() {
    const userName = document.getElementById('userName').value.trim();
    const userAge = document.getElementById('userAge').value;
    const userGender = document.getElementById('userGender').value;
    const symptoms = getSelectedSymptoms();
    const imageFile = document.getElementById('imageUpload').files[0];

    // Check if user info is provided
    if (!userName || !userAge || !userGender) {
        throw new Error('Please fill in all patient information fields.');
    }

    // Check if at least symptoms or image is provided
    if (symptoms.length === 0 && !imageFile) {
        throw new Error('Please select symptoms or upload an image for analysis.');
    }

    return {
        userName,
        userAge: parseInt(userAge),
        userGender,
        symptoms,
        imageFile
    };
}

// Collect lab values
function getLabValues() {
    return {
        platelets: document.getElementById('platelets').value || null,
        oxygen: document.getElementById('oxygen').value || null,
        wbc: document.getElementById('wbc').value || null,
        temperature: document.getElementById('temperature').value || null
    };
}

// Submit diagnosis request
async function submitDiagnosis() {
    try {
        // Validate form
        const formData = validateForm();
        const labValues = getLabValues();

        // Show loading
        showLoading(true);
        hideError();
        hideResults();

        // Prepare form data for API
        const apiFormData = new FormData();
        
        // Add user info
        apiFormData.append('user_name', formData.userName);
        apiFormData.append('user_age', formData.userAge);
        apiFormData.append('user_gender', formData.userGender);

        // Add symptoms
        if (formData.symptoms.length > 0) {
            apiFormData.append('symptoms', JSON.stringify(formData.symptoms));
        }

        // Add lab values
        if (labValues.platelets) apiFormData.append('platelets', parseFloat(labValues.platelets));
        if (labValues.oxygen) apiFormData.append('oxygen', parseFloat(labValues.oxygen));
        if (labValues.wbc) apiFormData.append('wbc', parseFloat(labValues.wbc));
        if (labValues.temperature) apiFormData.append('temperature', parseFloat(labValues.temperature));

        // Add image if provided
        if (formData.imageFile) {
            apiFormData.append('image', formData.imageFile);
        }

        // Make API call
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            body: apiFormData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Prediction failed');
        }

        // Store user ID for history
        currentUserId = result.data.user_id;

        // Display results
        displayResults(result.data);
        
        // Reload history
        loadUserHistory();

    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// Display prediction results
function displayResults(data) {
    // Update prediction card
    const diseaseResult = document.getElementById('diseaseResult');
    const confidenceResult = document.getElementById('confidenceResult');
    const riskResult = document.getElementById('riskResult');
    const predictionCard = document.getElementById('predictionCard');

    diseaseResult.textContent = `Disease: ${data.disease}`;
    confidenceResult.textContent = `Confidence: ${(data.probability * 100).toFixed(1)}%`;
    riskResult.textContent = `Risk Level: ${data.risk_level}`;

    // Update card styling based on risk level
    predictionCard.className = 'prediction-card';
    if (data.risk_level === 'Low') {
        predictionCard.classList.add('risk-low');
    } else if (data.risk_level === 'Moderate') {
        predictionCard.classList.add('risk-moderate');
    } else if (data.risk_level === 'High') {
        predictionCard.classList.add('risk-high');
    }

    // Update chart
    updateProbabilityChart(data.all_probabilities);

    // Update explanation
    const explanationText = document.getElementById('explanationText');
    if (data.explanation) {
        explanationText.innerHTML = formatExplanation(data.explanation);
    } else {
        explanationText.innerHTML = '<p>No detailed explanation available.</p>';
    }

    // Update recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    if (data.recommendations && data.recommendations.length > 0) {
        data.recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.textContent = recommendation;
            recommendationsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Consult with a healthcare professional for proper medical advice.';
        recommendationsList.appendChild(li);
    }

    // Show results
    showResults();
}

// Update probability chart
function updateProbabilityChart(probabilities) {
    const ctx = document.getElementById('probabilityChart').getContext('2d');

    // Destroy existing chart
    if (chart) {
        chart.destroy();
    }

    // Prepare data
    const labels = Object.keys(probabilities);
    const data = Object.values(probabilities).map(p => (p * 100).toFixed(1));
    const colors = [
        '#FF6384',
        '#36A2EB', 
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40'
    ];

    // Create new chart
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Probability (%)',
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y + '%';
                        }
                    }
                }
            }
        }
    });
}

// Format explanation text
function formatExplanation(explanation) {
    if (!explanation) return '<p>No explanation available.</p>';
    
    // Convert markdown-like formatting to HTML
    let formatted = explanation
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic
        .replace(/\n\n/g, '</p><p>')                       // Paragraphs
        .replace(/\n/g, '<br>');                           // Line breaks

    // Wrap in paragraph tags if not already formatted
    if (!formatted.includes('<p>')) {
        formatted = '<p>' + formatted + '</p>';
    }

    return formatted;
}

// Load user history
async function loadUserHistory() {
    if (!currentUserId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/predictions/${currentUserId}`);
        if (response.ok) {
            const history = await response.json();
            displayHistory(history);
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Display user history
function displayHistory(history) {
    const historyContainer = document.getElementById('historyContainer');
    
    if (!history || history.length === 0) {
        historyContainer.innerHTML = '<p>No previous diagnoses found.</p>';
        return;
    }

    historyContainer.innerHTML = '';
    
    // Show recent 5 diagnoses
    const recentHistory = history.slice(0, 5);
    
    recentHistory.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const date = new Date(item.created_at).toLocaleString();
        historyItem.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${item.disease}</strong> (${(item.probability * 100).toFixed(1)}%)
                    <br>
                    <small>Risk: ${item.risk_level} | Model: ${item.model_type}</small>
                </div>
                <div style="text-align: right;">
                    <small>${date}</small>
                </div>
            </div>
        `;
        
        historyContainer.appendChild(historyItem);
    });
}

// Show/hide functions
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 10000);
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function showResults() {
    document.getElementById('results').style.display = 'block';
}

function hideResults() {
    document.getElementById('results').style.display = 'none';
}

// Clear form
function clearForm() {
    // Clear user info
    document.getElementById('userName').value = '';
    document.getElementById('userAge').value = '';
    document.getElementById('userGender').value = '';

    // Clear symptoms
    const checkboxes = document.querySelectorAll('.symptom-checkbox input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    // Clear lab values
    document.getElementById('platelets').value = '';
    document.getElementById('oxygen').value = '';
    document.getElementById('wbc').value = '';
    document.getElementById('temperature').value = '';

    // Clear image
    document.getElementById('imageUpload').value = '';
    document.getElementById('imagePreview').style.display = 'none';

    // Hide results and errors
    hideResults();
    hideError();

    // Destroy chart
    if (chart) {
        chart.destroy();
        chart = null;
    }
}

// Utility function to show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px;
        border-radius: 5px;
        color: white;
        z-index: 1000;
        max-width: 300px;
    `;
    
    if (type === 'success') {
        notification.style.background = '#28a745';
    } else if (type === 'error') {
        notification.style.background = '#dc3545';
    } else {
        notification.style.background = '#17a2b8';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 5000);
}
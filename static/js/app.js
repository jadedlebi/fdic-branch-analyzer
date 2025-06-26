// DOM Elements
const analysisForm = document.getElementById('analysisForm');
const submitBtn = document.getElementById('submitBtn');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const progressText = document.getElementById('progressText');
const downloadBtn = document.getElementById('downloadBtn');
const errorMessage = document.getElementById('errorMessage');

// Progress messages
const progressMessages = [
    'Initializing analysis...',
    'Connecting to database...',
    'Querying branch data...',
    'Processing county information...',
    'Generating AI insights...',
    'Creating Excel report...',
    'Generating PDF report...',
    'Finalizing analysis...'
];

let currentProgress = 0;
let progressInterval;

// Form submission handler
analysisForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(analysisForm);
    const selectedCounties = $('#county-select').val(); // This is an array
    const years = formData.get('years').trim();
    
    if (!selectedCounties || !years) {
        showError('Please fill in both counties and years fields.');
        return;
    }
    
    // Convert to string if needed
    const countiesString = selectedCounties.join(';');
    
    // Show progress and disable form
    showProgress();
    disableForm();
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                counties: countiesString,
                years: years
            })
        });
        
        const result = await response.json();
        const jobId = result.job_id;
        listenForProgress(jobId);
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
        hideProgress();
        enableForm();
    }
});

// Download button handler
downloadBtn.addEventListener('click', function() {
    window.location.href = '/download';
});

// Show progress section
function showProgress() {
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Start progress animation
    startProgressAnimation();
}

// Hide progress section
function hideProgress() {
    progressSection.style.display = 'none';
    clearInterval(progressInterval);
}

// Start progress animation
function startProgressAnimation() {
    currentProgress = 0;
    progressInterval = setInterval(() => {
        currentProgress = (currentProgress + 1) % progressMessages.length;
        progressText.textContent = progressMessages[currentProgress];
    }, 1500);
}

// Show results section
function showResults() {
    resultsSection.style.display = 'block';
    progressSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Show error section
function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

// Disable form
function disableForm() {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Processing...</span>';
    
    // Disable inputs
    const inputs = analysisForm.querySelectorAll('input');
    inputs.forEach(input => input.disabled = true);
}

// Enable form
function enableForm() {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-magic"></i><span>Generate Analysis</span>';
    
    // Enable inputs
    const inputs = analysisForm.querySelectorAll('input');
    inputs.forEach(input => input.disabled = false);
}

// Reset form (for retry button)
function resetForm() {
    analysisForm.reset();
    errorSection.style.display = 'none';
    resultsSection.style.display = 'none';
    progressSection.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Input validation
function validateInput(input, type) {
    const value = input.value.trim();
    
    if (type === 'county-select') {
        const selected = $('#county-select').val();
        if (!selected || selected.length === 0) {
            input.setCustomValidity('Please select at least one county.');
        } else {
            input.setCustomValidity('');
        }
    } else if (type === 'years') {
        if (!value) {
            input.setCustomValidity('Please enter years to analyze.');
        } else if (value.toLowerCase() === 'all') {
            input.setCustomValidity('');
        } else {
            const years = value.split(',').map(y => y.trim()).filter(y => y);
            const validYears = years.every(y => {
                const year = parseInt(y);
                return !isNaN(year) && year >= 2017 && year <= 2024;
            });
            
            if (!validYears) {
                input.setCustomValidity('Please enter valid years between 2017-2024, separated by commas.');
            } else {
                input.setCustomValidity('');
            }
        }
    }
}

// Add input validation listeners
document.getElementById('county-select').addEventListener('change', function() {
    validateInput(this, 'county-select');
});

document.getElementById('years').addEventListener('input', function() {
    validateInput(this, 'years');
});

// Add some nice animations and interactions
$(document).ready(function() {
    // Animate feature cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading state for download button
    downloadBtn.addEventListener('click', function() {
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Preparing download...</span>';
        this.disabled = true;
        
        // Reset after a delay (download should start)
        setTimeout(() => {
            this.innerHTML = originalText;
            this.disabled = false;
        }, 3000);
    });

    // Populate Select2 county dropdown
    if ($('#county-select').length) {
        fetch('/counties')
            .then(response => response.json())
            .then(counties => {
                const $countySelect = $('#county-select');
                $countySelect.empty();
                counties.forEach(county => {
                    $countySelect.append(new Option(county, county));
                });
                $countySelect.select2({
                    placeholder: "Select counties...",
                    allowClear: true
                });
            });
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!submitBtn.disabled) {
            analysisForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to reset form
    if (e.key === 'Escape') {
        resetForm();
    }
});

// Add tooltips for help text
document.querySelectorAll('.help-text').forEach(helpText => {
    helpText.style.cursor = 'help';
    helpText.title = helpText.textContent;
});

// Add success animation for form submission
function addSuccessAnimation() {
    const form = document.querySelector('.analysis-form');
    form.style.transform = 'scale(0.98)';
    form.style.transition = 'transform 0.2s ease';
    
    setTimeout(() => {
        form.style.transform = 'scale(1)';
    }, 200);
}

// Add error shake animation
function addErrorShake() {
    const form = document.querySelector('.analysis-form');
    form.style.animation = 'shake 0.5s ease-in-out';
    
    setTimeout(() => {
        form.style.animation = '';
    }, 500);
}

// Add CSS for shake animation
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Real-time progress bar using SSE
function listenForProgress(jobId) {
    const evtSource = new EventSource(`/progress/${jobId}`);
    evtSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        document.getElementById('progressFill').style.width = data.percent + '%';
        document.getElementById('progressText').textContent = data.step;
        if (data.done || data.error) {
            evtSource.close();
            if (data.error) {
                showError(data.error);
            } else {
                showResults();
            }
            hideProgress();
            enableForm();
        }
    };
} 
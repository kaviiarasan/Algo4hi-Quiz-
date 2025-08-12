// Quiz Timer JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let startTime = Date.now();
    let timerElement = document.getElementById('timer');
    let timeInput = document.getElementById('time_taken');
    let submitBtn = document.getElementById('submit-btn');
    let form = document.getElementById('quiz-form');
    
    // Timer function
    function updateTimer() {
        let elapsed = Math.floor((Date.now() - startTime) / 1000);
        let minutes = Math.floor(elapsed / 60);
        let seconds = elapsed % 60;
        
        // Format time as MM:SS
        let timeStr = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
        timerElement.textContent = timeStr;
        
        // Update hidden input
        timeInput.value = elapsed;
        
        // Change timer color if over 1 minute (no bonus)
        if (elapsed >= 60) {
            timerElement.parentElement.className = 'badge bg-warning fs-6';
        } else {
            timerElement.parentElement.className = 'badge bg-info fs-6';
        }
    }
    
    // Update timer every second
    let timerInterval = setInterval(updateTimer, 1000);
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        // Update time one final time before submission
        updateTimer();
        
        // Stop the timer
        clearInterval(timerInterval);
        
        // Disable the submit button to prevent double submission
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
        
        // Confirm submission
        if (!confirm('Are you sure you want to submit your quiz? You cannot change your answers after submission.')) {
            e.preventDefault();
            // Re-enable button if cancelled
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Submit Quiz';
            // Restart timer
            timerInterval = setInterval(updateTimer, 1000);
        }
    });
    
    // Warn user if they try to leave the page
    window.addEventListener('beforeunload', function(e) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? Your progress will be lost.';
    });
    
    // Initialize timer immediately
    updateTimer();
});

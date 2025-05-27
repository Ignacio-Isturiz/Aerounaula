let seconds = 5;
const countdownElement = document.getElementById('seconds');

const interval = setInterval(function () {
    seconds--;
    countdownElement.textContent = seconds;
    if (seconds <= 0) {
        clearInterval(interval);
        window.location.href = "/login"; 
    }
}, 1000);

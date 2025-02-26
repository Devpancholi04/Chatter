document.addEventListener("DOMContentLoaded", () => {
    const alertDuration = 5000; // 5 seconds
    const progressBar = document.getElementById('progressBar');
    const alertElement = document.getElementById('timedAlert');

    if (progressBar && alertElement) {
        let width = 100;
        const interval = 100; // update every 100ms
        const decrement = (100 / (alertDuration / interval));

        const progressInterval = setInterval(() => {
            width -= decrement;
            progressBar.style.width = width + '%';

            if (width <= 0) {
                clearInterval(progressInterval);
                alertElement.classList.remove('show');
                alertElement.classList.add('fade');
                setTimeout(() => alertElement.remove(), 150);
            }
        }, interval);

        alertElement.querySelector('.btn-close').addEventListener('click', () => {
            clearInterval(progressInterval);
        });
    }
});
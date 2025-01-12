// Wait for the DOM to be loaded before executing the code
document.addEventListener('DOMContentLoaded', () => {
    // Log a message to the console to verify that the JS is loaded
    console.log("Web of Wonders - JavaScript Loaded!");

    // Example of an interactive feature: Change text color after 3 seconds
    const animatedText = document.querySelector('.animated-text');
    setTimeout(() => {
        animatedText.style.color = '#2196F3'; // Change color to blue after animation
    }, 3000);
});

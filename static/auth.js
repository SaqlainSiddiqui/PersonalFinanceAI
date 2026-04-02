// Show/Hide Password
function togglePassword() {
    const passwordInput = document.getElementById("password");
    passwordInput.type =
        passwordInput.type === "password" ? "text" : "password";
}

// Floating Background Particles
for (let i = 0; i < 20; i++) {
    let particle = document.createElement("div");
    particle.classList.add("particle");
    particle.style.width = particle.style.height =
        Math.random() * 10 + 5 + "px";
    particle.style.left = Math.random() * 100 + "vw";
    particle.style.animationDuration =
        Math.random() * 15 + 10 + "s";
    document.body.appendChild(particle);
}


document.querySelectorAll('.flash').forEach(flash => {
    let timeout;

    function startTimer() {
        timeout = setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-20px)';
        }, 4000);
    }

    function stopTimer() {
        clearTimeout(timeout);
    }

    flash.addEventListener('mouseenter', stopTimer);
    flash.addEventListener('mouseleave', startTimer);

    startTimer();
});
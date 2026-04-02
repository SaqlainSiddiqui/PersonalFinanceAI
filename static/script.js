document.addEventListener("DOMContentLoaded", function () {

    const chartDataElement = document.getElementById("chart-data");

    if (chartDataElement) {

        const chartLabels = JSON.parse(chartDataElement.dataset.labels || "[]");
        const chartValues = JSON.parse(chartDataElement.dataset.values || "[]");

        // ✅ NEW LINE
        const totalExpense = JSON.parse(chartDataElement.dataset.total || "0");

        const ctx = document.getElementById("expenseChart");

        if (ctx && chartValues.length > 0) {

            function generateColors(count) {
                const colors = [];

                for (let i = 0; i < count; i++) {
                    const hue = Math.floor((360 / count) * i);
                    colors.push(`hsl(${hue}, 70%, 60%)`);
                }

                return colors;
            }

            const backgroundColors = generateColors(chartLabels.length);

            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: chartLabels,
                    datasets: [{
                        data: chartValues,
                        backgroundColor: backgroundColors
                    }]
                },
                options: {
                    responsive: true,
                    cutout: "70%",
                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    }
                },

                // ✅ ADD THIS PLUGIN
                plugins: [{
                    id: "centerText",
                    beforeDraw(chart) {
                        const { width, height, ctx } = chart;

                        ctx.restore();

                        ctx.font = "bold 16px Arial";
                        ctx.textBaseline = "middle";

                        const textX = width / 2;
                        const textY = height / 2;

                        ctx.textAlign = "center";  // IMPORTANT for proper alignment

                        ctx.fillStyle = "#000000";
                        ctx.fillText("Total", textX, textY - 12);

                        ctx.fillStyle = "#0b3f57";
                        ctx.fillText("₹" + totalExpense, textX, textY + 10);

                        ctx.save();
                    }
                }]
            });
        }
    }

});



// ===== DARK MODE TOGGLE =====
const toggleBtn = document.getElementById("theme-toggle");

if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {

        fetch("/toggle_theme", {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            document.body.className = data.theme + "-mode";
        });

    });
}

// ===== MODAL FUNCTIONS =====
function openModal() {
    document.getElementById("transactionModal").style.display = "block";
}

function closeModal() {
    document.getElementById("transactionModal").style.display = "none";
}

window.addEventListener("click", function(event) {
    const modal = document.getElementById("transactionModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
});

function openEditModal(button) {

    const id = button.dataset.id;
    const category = button.dataset.category;
    const type = button.dataset.type;
    const amount = button.dataset.amount;
    const date = button.dataset.date;
    const description = button.dataset.description;

    const modal = document.getElementById("editTransactionModal");
    const form = document.getElementById("editForm");

    form.action = "/edit_transaction/" + id;

    document.getElementById("editAmount").value = amount;
    document.getElementById("editCategory").value = category;
    document.getElementById("editType").value = type;
    document.getElementById("editDate").value = date;
    document.getElementById("editDescription").value = description;

    modal.style.display = "block";
}

function sendMessage() {

    const input = document.getElementById("chat-input");
    const message = input.value.trim();

    if (!message) return;

    const chatBox = document.getElementById("chat-box");

    // User message
    const userDiv = document.createElement("div");
    userDiv.className = "chat-message user-message";
    userDiv.textContent = message;
    chatBox.appendChild(userDiv);

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"   // ✅ FIXED
        },
        body: JSON.stringify({
            message: message,
            month: selectedMonth   // ✅ SEND MONTH
        })
    })
    .then(response => response.json())
    .then(data => {

        const botDiv = document.createElement("div");
        botDiv.className = "chat-message bot-message";
        botDiv.textContent = data.response;
        chatBox.appendChild(botDiv);

        chatBox.scrollTop = chatBox.scrollHeight;
    });

    input.value = "";
}

document.getElementById("chat-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

/* ================= VOICE RECOGNITION ================= */

function startVoice() {

    const micBtn = document.querySelector(".chat-mic-btn");

    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech recognition not supported in this browser.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    micBtn.classList.add("listening");

    recognition.start();

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;

        document.getElementById("chat-input").value = transcript;

        sendMessage();
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error", event.error);
    };

    recognition.onend = function() {
        micBtn.classList.remove("listening");
    };
}

function toggleTransactions() {
    const list = document.getElementById("transactions-list");
    const icon = document.getElementById("dropdown-icon");

    list.classList.toggle("open");

    icon.innerText = list.classList.contains("open") ? "▲" : "▼";
}

const passwordInput = document.getElementById("password");

if (passwordInput) {
    passwordInput.addEventListener("input", function () {
        const value = passwordInput.value;

        const lengthRule = document.getElementById("length");
        const uppercaseRule = document.getElementById("uppercase");
        const numberRule = document.getElementById("number");
        const specialRule = document.getElementById("special");

        // RULES
        const hasLength = value.length >= 8;
        const hasUpper = /[A-Z]/.test(value);
        const hasNumber = /[0-9]/.test(value);
        const hasSpecial = /[^A-Za-z0-9]/.test(value);

        updateRule(lengthRule, hasLength);
        updateRule(uppercaseRule, hasUpper);
        updateRule(numberRule, hasNumber);
        updateRule(specialRule, hasSpecial);
    });
}

function updateRule(element, isValid) {
    if (isValid) {
        element.classList.add("valid");
        element.innerText = "✔ " + element.innerText.slice(2);
    } else {
        element.classList.remove("valid");
        element.innerText = "❌ " + element.innerText.slice(2);
    }
}

document.querySelector("form")?.addEventListener("submit", function (e) {
    const password = document.getElementById("password").value;

    const isValid =
        password.length >= 8 &&
        /[A-Z]/.test(password) &&
        /[0-9]/.test(password) &&
        /[^A-Za-z0-9]/.test(password);

    if (!isValid) {
        e.preventDefault();
        alert("Password does not meet requirements!");
    }
});
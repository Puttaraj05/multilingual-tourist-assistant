const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatMessages = document.getElementById("chatMessages");

const API_URL = "http://127.0.0.1:8000/api/chat";

// Keep the same session for chat history
let sessionId = localStorage.getItem("travelmate_session");

if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("travelmate_session", sessionId);
}

// Add message to UI
function addMessage(text, sender) {

    const message = document.createElement("div");
    message.className = `message ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = sender === "ai" ? "AI" : "You";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    message.appendChild(avatar);
    message.appendChild(bubble);

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return message;
}

// Format backend response into readable text
function formatAIResponse(data) {

    let response = data;

    // If backend returns JSON as a string, parse it
    if (typeof data.message === "string" && data.message.trim().startsWith("{")) {
        try {
            response = JSON.parse(data.message);
        } catch {
            return data.message;
        }
    }

    let text = response.message || data.message || "";

    if (response.destination) {
        text += `\n\nDestination: ${response.destination}`;
    }

    if (response.attractions?.length) {
        text += "\n\nTop Attractions:";
        response.attractions.forEach(place => {
            text += `\n• ${place.name}`;
        });
    }

    if (response.food?.length) {
        text += "\n\nMust Try Food:";
        response.food.forEach(item => {
            text += `\n• ${item.name}`;
        });
    }

    if (response.transportation?.length) {
        text += "\n\nTransport:";
        response.transportation.forEach(item => {
            text += `\n• ${item.mode}`;
        });
    }

    if (response.tips?.length) {
        text += "\n\nTravel Tips:";
        response.tips.forEach(tip => {
            text += `\n• ${tip}`;
        });
    }

    return text;
}

// Send message to backend
async function sendMessage(text) {

    if (!text.trim()) return;

    addMessage(text, "user");
    userInput.value = "";

    const loading = addMessage("Typing...", "ai");

    try {

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text,
                language: document.getElementById("chatLanguage")?.value || "English",
                session_id: sessionId
            })
        });

        const data = await response.json();

        loading.remove();

        if (!response.ok) {
            addMessage(data.detail || "Something went wrong.", "ai");
            return;
        }

        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem("travelmate_session", sessionId);
        }

        addMessage(formatAIResponse(data), "ai");

    } catch (error) {

        loading.remove();
        addMessage("Unable to connect to the server.", "ai");
        console.error(error);

    }
}

// Form submit
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(userInput.value);
});

// Enter key
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(userInput.value);
    }
});

// Quick prompt buttons
document.querySelectorAll(".quick-btn, .suggestion").forEach(button => {
    button.addEventListener("click", () => {
        sendMessage(button.textContent.trim());
    });
});
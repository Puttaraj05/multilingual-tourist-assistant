// TravelMate AI Chat
// Stores chat history and communicates with the FastAPI backend

const API_ENDPOINT = "/api/chat";
const SESSION_STORAGE_KEY = "travelmate_session_id";

let currentSessionId = null;

let currentChat = {
    id: null,
    title: "New Chat",
    language: "English",
    destination: "",
    messages: []
};

let chatHistory = [];


// Escape text before putting it into HTML

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// Get a value from an object

function fieldText(item, keys) {
    if (item === null || item === undefined) {
        return "";
    }

    if (
        typeof item === "string" ||
        typeof item === "number"
    ) {
        return String(item);
    }

    for (const key of keys) {
        if (
            item[key] !== undefined &&
            item[key] !== null &&
            item[key] !== ""
        ) {
            if (typeof item[key] === "object") {
                return JSON.stringify(item[key]);
            }

            return String(item[key]);
        }
    }

    return "";
}


// Make sure a value is an array

function asArray(value) {
    if (Array.isArray(value)) {
        return value;
    }

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return [];
    }

    return [value];
}


// Images for attraction categories

const CATEGORY_IMAGES = {
    Historical:
        "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=700&q=70",

    Nature:
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=700&q=70",

    Beach:
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=700&q=70",

    Museum:
        "https://images.unsplash.com/photo-1554907984-15263bfd63bd?w=700&q=70",

    Culture:
        "https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?w=700&q=70",

    Entertainment:
        "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=700&q=70",

    default:
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=700&q=70"
};


const HERO_IMAGE =
    "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1000&q=80";


function imgForCategory(category) {
    return (
        CATEGORY_IMAGES[category] ||
        CATEGORY_IMAGES.default
    );
}


// Create a unique chat ID

function generateSessionId() {
    return (
        "session-" +
        Date.now() +
        "-" +
        Math.random()
            .toString(36)
            .substring(2, 8)
    );
}


// Get the currently selected language

function getSelectedLanguage() {
    const select =
        document.getElementById("languageSelect");

    return select?.value || "English";
}


// Create a new chat

function createNewSession() {
    const sessionId =
        generateSessionId();

    currentSessionId = sessionId;

    localStorage.setItem(
        SESSION_STORAGE_KEY,
        sessionId
    );

    const language =
        getSelectedLanguage();

    currentChat = {
        id: sessionId,
        title: "New Chat",
        language: language,
        destination: "",
        messages: []
    };

    const resultArea =
        document.getElementById("resultArea");

    if (resultArea) {
        resultArea.innerHTML = "";
    }

    renderRecentList();
}


// Load an old chat from MongoDB

async function loadChatHistoryFromServer(sessionId) {
    if (!sessionId) {
        return false;
    }

    try {
        const response = await fetch(
            `${API_ENDPOINT}/history/${encodeURIComponent(sessionId)}`
        );

        if (!response.ok) {
            console.error(
                "History request failed:",
                response.status
            );

            return false;
        }

        const data = await response.json();

        if (
            !data.success ||
            !Array.isArray(data.messages)
        ) {
            return false;
        }

        const messages = data.messages;

        if (!messages.length) {
            return false;
        }

        currentSessionId = sessionId;

        localStorage.setItem(
            SESSION_STORAGE_KEY,
            sessionId
        );

        const firstLanguage =
            messages.find(
                message =>
                    message &&
                    message.language
            )?.language || "English";

        currentChat = {
            id: sessionId,
            title: "Travel Chat",
            language: firstLanguage,
            destination: "",
            messages: []
        };

        for (const message of messages) {
            if (
                !message ||
                !message.role
            ) {
                continue;
            }

            if (message.role === "user") {
                currentChat.messages.push({
                    role: "user",
                    content: message.content || "",
                    language:
                        message.language || "English",
                    timestamp:
                        message.created_at ||
                        message.timestamp ||
                        null
                });

                continue;
            }

            if (message.role === "assistant") {
                let content =
                    message.content || "";

                let parsedContent = null;

                if (typeof content === "string") {
                    try {
                        parsedContent =
                            JSON.parse(content);
                    } catch {
                        parsedContent = content;
                    }
                } else {
                    parsedContent = content;
                }

                const assistantData =
                    typeof parsedContent === "object" &&
                    parsedContent !== null
                        ? parsedContent
                        : {
                            message:
                                String(
                                    parsedContent || ""
                                )
                        };

                currentChat.messages.push({
                    role: "assistant",

                    content:
                        assistantData.message || "",

                    data: assistantData,

                    query: "",

                    language:
                        message.language ||
                        "English",

                    timestamp:
                        message.created_at ||
                        message.timestamp ||
                        null
                });
            }
        }

        const firstUserMessage =
            currentChat.messages.find(
                message =>
                    message.role === "user"
            );

        if (firstUserMessage?.content) {
            currentChat.title =
                createChatTitle(
                    firstUserMessage.content
                );
        }

        // Set the language dropdown to the chat language

        const languageSelect =
            document.getElementById(
                "languageSelect"
            );

        if (languageSelect) {
            languageSelect.value =
                currentChat.language;
        }

        updateChatHistory();

        renderConversation();

        return true;

    } catch (error) {
        console.error(
            "Could not load chat history:",
            error
        );

        return false;
    }
}


// Update recent chat information

function updateChatHistory() {
    if (
        !currentChat ||
        !currentChat.id ||
        !currentChat.messages ||
        !currentChat.messages.length
    ) {
        return;
    }

    const existingIndex =
        chatHistory.findIndex(
            chat =>
                chat.id ===
                currentChat.id
        );

    const firstUserMessage =
        currentChat.messages.find(
            message =>
                message.role === "user"
        );

    const chatObject = {
        id: currentChat.id,

        title:
            currentChat.title ||
            (
                firstUserMessage
                    ? createChatTitle(
                        firstUserMessage.content
                    )
                    : "Travel Chat"
            ),

        language:
            currentChat.language ||
            "English",

        destination:
            currentChat.destination ||
            "",

        messages:
            currentChat.messages,

        time: "Saved"
    };

    if (existingIndex >= 0) {
        chatHistory[existingIndex] =
            chatObject;
    } else {
        chatHistory.unshift(
            chatObject
        );
    }

    chatHistory =
        chatHistory.slice(0, 15);

    renderRecentList();
}


// Start a new conversation

function startNewChat() {
    createNewSession();

    showWelcomeScreen();

    document
        .getElementById("chatInput")
        ?.focus();
}


// Save the current chat locally

function saveCurrentChat() {
    updateChatHistory();
}


// Show recent chats

function renderRecentList() {
    const list =
        document.getElementById(
            "recentList"
        );

    if (!list) {
        return;
    }

    if (!chatHistory.length) {
        list.innerHTML = `
            <div class="empty-recent">
                No chats yet
            </div>
        `;

        return;
    }

    list.innerHTML =
        chatHistory
            .map(chat => {
                const active =
                    chat.id ===
                    currentSessionId
                        ? "active"
                        : "";

                return `
                    <button
                        type="button"
                        class="recent-item ${active}"
                        data-chat-id="${escapeHtml(
                            chat.id
                        )}"
                    >
                        <span class="recent-dot"></span>

                        <div class="recent-text">
                            <strong>
                                ${escapeHtml(
                                    chat.title ||
                                    "Travel Chat"
                                )}
                            </strong>

                            <span>
                                ${escapeHtml(
                                    chat.language ||
                                    "English"
                                )}
                                ·
                                ${escapeHtml(
                                    chat.time ||
                                    "Saved"
                                )}
                            </span>
                        </div>
                    </button>
                `;
            })
            .join("");

    list
        .querySelectorAll(
            ".recent-item"
        )
        .forEach(item => {
            item.addEventListener(
                "click",
                async () => {
                    await openChat(
                        item.dataset.chatId
                    );
                }
            );
        });
}


// Open an existing chat

async function openChat(sessionId) {
    if (!sessionId) {
        return;
    }

    const localChat =
        chatHistory.find(
            item =>
                item.id ===
                sessionId
        );

    if (localChat) {
        currentSessionId =
            sessionId;

        localStorage.setItem(
            SESSION_STORAGE_KEY,
            sessionId
        );

        currentChat = {
            id: localChat.id,

            title:
                localChat.title ||
                "Travel Chat",

            language:
                localChat.language ||
                "English",

            destination:
                localChat.destination ||
                "",

            messages:
                localChat.messages || []
        };

        const languageSelect =
            document.getElementById(
                "languageSelect"
            );

        if (languageSelect) {
            languageSelect.value =
                currentChat.language;
        }

        renderConversation();

        renderRecentList();

        return;
    }

    await loadChatHistoryFromServer(
        sessionId
    );
}


// Show the initial welcome message

function showWelcomeScreen() {
    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) {
        return;
    }

    area.innerHTML = `
        <div class="welcome-screen">
            <h2>
                How can I help?
            </h2>

            <p>
                Ask TravelMate about your trip.
            </p>
        </div>
    `;
}


// Render all messages

function renderConversation() {
    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) {
        return;
    }

    area.innerHTML = "";

    if (
        !currentChat.messages ||
        !currentChat.messages.length
    ) {
        showWelcomeScreen();
        return;
    }

    currentChat.messages.forEach(
        message => {
            if (
                message.role === "user"
            ) {
                appendUserMessage(
                    message.content,
                    false
                );

                return;
            }

            if (
                message.role === "assistant"
            ) {
                const assistantData =
                    message.data || {
                        message:
                            message.content ||
                            ""
                    };

                appendAssistantMessage(
                    assistantData,
                    message.query || "",
                    false
                );
            }
        }
    );

    scrollChatToBottom(false);
}


// Render the AI response

function renderAssistantResponse(
    data,
    userQuery
) {
    if (!data) {
        return `
            <div class="error-box">
                No response received.
            </div>
        `;
    }

    const message =
        data.message || "";

    let destination = "";

    if (
        typeof data.destination ===
        "string"
    ) {
        destination =
            data.destination;

    } else if (
        data.destination &&
        typeof data.destination ===
        "object"
    ) {
        destination =
            data.destination.name || "";
    }

    destination =
        destination ||
        currentChat.destination ||
        "";

    if (destination) {
        currentChat.destination =
            destination;
    }

    const attractions =
        asArray(data.attractions);

    const food =
        asArray(data.food);

    const transportation =
        asArray(data.transportation);

    const tips =
        asArray(data.tips);

    const itinerary =
        asArray(data.itinerary);

    const tripOverview =
        data.trip_overview || "";

    const tripDuration =
        data.trip_duration || "";

    const travelStyle =
        data.travel_style || "";

    const bestTime =
        data.best_time_to_visit || "";

    const budget =
        data.estimated_budget || "";

    const hasTripContent =
        attractions.length > 0 ||
        food.length > 0 ||
        transportation.length > 0 ||
        tips.length > 0 ||
        itinerary.length > 0 ||
        tripOverview ||
        tripDuration ||
        travelStyle ||
        bestTime ||
        budget;

    const messageHtml =
        message
            ? `
                <div class="assistant-message">
                    ${formatText(message)}
                </div>
            `
            : "";

    if (!hasTripContent) {
        return `
            <div class="assistant-card">
                ${messageHtml}
            </div>
        `;
    }

    const heroHtml =
        destination
            ? `
                <div class="hero">

                    <div class="hero-img">

                        <img
                            src="${HERO_IMAGE}"
                            alt="${escapeHtml(
                                destination
                            )}"
                        >

                        ${
                            itinerary.length
                                ? `
                                    <div class="badge">
                                        📅
                                        ${itinerary.length}
                                        -Day Plan
                                    </div>
                                `
                                : ""
                        }

                    </div>

                    <div class="hero-body">

                        <h2>
                            ${escapeHtml(
                                destination
                            )}
                            ✨
                        </h2>

                        <p class="tagline">
                            Your AI Travel Plan
                        </p>

                        ${
                            message
                                ? `
                                    <p class="hero-desc">
                                        ${formatText(
                                            message
                                        )}
                                    </p>
                                `
                                : ""
                        }

                        <div class="hero-tags">

                            ${
                                tripDuration
                                    ? `
                                        <span class="hero-tag">
                                            📅
                                            ${escapeHtml(
                                                tripDuration
                                            )}
                                        </span>
                                    `
                                    : ""
                            }

                            ${
                                travelStyle
                                    ? `
                                        <span class="hero-tag">
                                            ✨
                                            ${escapeHtml(
                                                travelStyle
                                            )}
                                        </span>
                                    `
                                    : ""
                            }

                            ${
                                data.language ||
                                currentChat.language
                                    ? `
                                        <span class="hero-tag">
                                            🌍
                                            ${escapeHtml(
                                                data.language ||
                                                currentChat.language
                                            )}
                                        </span>
                                    `
                                    : ""
                            }

                        </div>

                    </div>

                </div>
            `
            : "";

    const overviewHtml =
        tripOverview ||
        tripDuration ||
        travelStyle ||
        bestTime ||
        budget
            ? `
                <div class="panel trip-overview">

                    <h3>
                        🧳 Trip Overview
                    </h3>

                    ${
                        tripOverview
                            ? `
                                <p>
                                    ${formatText(
                                        tripOverview
                                    )}
                                </p>
                            `
                            : ""
                    }

                    <div class="overview-grid">

                        ${
                            tripDuration
                                ? `
                                    <div class="overview-item">
                                        <span>
                                            📅 Duration
                                        </span>

                                        <strong>
                                            ${escapeHtml(
                                                tripDuration
                                            )}
                                        </strong>
                                    </div>
                                `
                                : ""
                        }

                        ${
                            travelStyle
                                ? `
                                    <div class="overview-item">
                                        <span>
                                            ✨ Travel Style
                                        </span>

                                        <strong>
                                            ${escapeHtml(
                                                travelStyle
                                            )}
                                        </strong>
                                    </div>
                                `
                                : ""
                        }

                        ${
                            bestTime
                                ? `
                                    <div class="overview-item">
                                        <span>
                                            🌤️ Best Time
                                        </span>

                                        <strong>
                                            ${escapeHtml(
                                                bestTime
                                            )}
                                        </strong>
                                    </div>
                                `
                                : ""
                        }

                        ${
                            budget
                                ? `
                                    <div class="overview-item">
                                        <span>
                                            💰 Estimated Budget
                                        </span>

                                        <strong>
                                            ${escapeHtml(
                                                budget
                                            )}
                                        </strong>
                                    </div>
                                `
                                : ""
                        }

                    </div>
                </div>
            `
            : "";

    return `
        ${heroHtml}

        ${overviewHtml}

        ${
            attractions.length
                ? renderAttractions(
                    attractions
                )
                : ""
        }

        ${
            food.length
                ? renderFood(food)
                : ""
        }

        ${
            transportation.length
                ? renderTransportation(
                    transportation
                )
                : ""
        }

        ${
            tips.length
                ? renderTips(tips)
                : ""
        }

        ${
            itinerary.length
                ? renderDetailedItinerary(
                    itinerary
                )
                : ""
        }
    `;
}


// Convert text to safe HTML

function formatText(text) {
    if (!text) {
        return "";
    }

    return escapeHtml(text)
        .replace(
            /\n\n/g,
            "</p><p>"
        )
        .replace(
            /\n/g,
            "<br>"
        );
}


// Render attraction cards

function renderAttractions(
    attractions
) {
    return `
        <div class="section-title">
            🏛️ Top Attractions
        </div>

        <div class="attractions-grid">

            ${
                attractions
                    .map(item => {
                        const category =
                            fieldText(
                                item,
                                ["category"]
                            ) ||
                            "Nature";

                        const name =
                            fieldText(
                                item,
                                [
                                    "name",
                                    "title"
                                ]
                            );

                        const description =
                            fieldText(
                                item,
                                [
                                    "description",
                                    "details"
                                ]
                            );

                        const bestTime =
                            fieldText(
                                item,
                                [
                                    "best_time",
                                    "bestTime"
                                ]
                            );

                        const duration =
                            fieldText(
                                item,
                                [
                                    "estimated_time",
                                    "duration"
                                ]
                            );

                        const location =
                            fieldText(
                                item,
                                ["location"]
                            );

                        return `
                            <div class="attraction-card">

                                <img
                                    src="${imgForCategory(
                                        category
                                    )}"
                                    alt="${escapeHtml(
                                        name
                                    )}"
                                    loading="lazy"
                                >

                                <div class="attraction-body">

                                    <h4>
                                        ${escapeHtml(
                                            name
                                        )}
                                    </h4>

                                    <p>
                                        ${escapeHtml(
                                            description
                                        )}
                                    </p>

                                    <span class="tag">
                                        ${escapeHtml(
                                            category
                                        )}
                                    </span>

                                    ${
                                        location
                                            ? `
                                                <div class="meta-line">
                                                    📍
                                                    ${escapeHtml(
                                                        location
                                                    )}
                                                </div>
                                            `
                                            : ""
                                    }

                                    ${
                                        bestTime
                                            ? `
                                                <div class="meta-line">
                                                    🕐 Best:
                                                    ${escapeHtml(
                                                        bestTime
                                                    )}
                                                </div>
                                            `
                                            : ""
                                    }

                                    ${
                                        duration
                                            ? `
                                                <div class="meta-line">
                                                    ⏱️
                                                    ${escapeHtml(
                                                        duration
                                                    )}
                                                </div>
                                            `
                                            : ""
                                    }

                                </div>
                            </div>
                        `;
                    })
                    .join("")
            }

        </div>
    `;
}


// Render food recommendations

function renderFood(food) {
    return `
        <div class="panel">

            <h3>
                🍽️ Food to Try
            </h3>

            ${
                food
                    .map(item => {
                        const name =
                            fieldText(
                                item,
                                [
                                    "name",
                                    "title"
                                ]
                            );

                        const description =
                            fieldText(
                                item,
                                [
                                    "description",
                                    "details"
                                ]
                            );

                        const type =
                            fieldText(
                                item,
                                [
                                    "type",
                                    "category"
                                ]
                            );

                        const mustTry =
                            item.must_try === true;

                        const cost =
                            fieldText(
                                item,
                                [
                                    "approximate_cost",
                                    "estimated_cost",
                                    "cost"
                                ]
                            );

                        return `
                            <div class="food-row">

                                <div class="thumb">
                                    🍛
                                </div>

                                <div class="info">

                                    <strong>
                                        ${escapeHtml(
                                            name
                                        )}
                                    </strong>

                                    <span>
                                        ${escapeHtml(
                                            description
                                        )}
                                    </span>

                                    ${
                                        type
                                            ? `
                                                <span>
                                                    ${escapeHtml(
                                                        type
                                                    )}
                                                </span>
                                            `
                                            : ""
                                    }

                                    <div class="food-meta">

                                        ${
                                            mustTry
                                                ? `
                                                    <span class="must-try">
                                                        ⭐ Must Try
                                                    </span>
                                                `
                                                : ""
                                        }

                                        ${
                                            cost
                                                ? `
                                                    <span>
                                                        💰
                                                        ${escapeHtml(
                                                            cost
                                                        )}
                                                    </span>
                                                `
                                                : ""
                                        }

                                    </div>

                                </div>

                            </div>
                        `;
                    })
                    .join("")
            }

        </div>
    `;
}


// Render transportation options

function renderTransportation(
    transportation
) {
    return `
        <div class="panel">

            <h3>
                🚗 Transportation
            </h3>

            ${
                transportation
                    .map(item => {
                        const mode =
                            fieldText(
                                item,
                                [
                                    "mode",
                                    "name",
                                    "title"
                                ]
                            );

                        const description =
                            fieldText(
                                item,
                                [
                                    "description",
                                    "details"
                                ]
                            );

                        const bestFor =
                            fieldText(
                                item,
                                [
                                    "best_for",
                                    "bestFor"
                                ]
                            );

                        const cost =
                            fieldText(
                                item,
                                [
                                    "approximate_cost",
                                    "estimated_cost",
                                    "cost"
                                ]
                            );

                        const travelTime =
                            fieldText(
                                item,
                                [
                                    "travel_time",
                                    "travelTime"
                                ]
                            );

                        return `
                            <div class="transport-row">

                                <div class="thumb">
                                    🚕
                                </div>

                                <div class="info">

                                    <strong>
                                        ${escapeHtml(
                                            mode
                                        )}
                                    </strong>

                                    <span>
                                        ${escapeHtml(
                                            description
                                        )}
                                    </span>

                                    ${
                                        bestFor
                                            ? `
                                                <span>
                                                    👥 Best for:
                                                    ${escapeHtml(
                                                        bestFor
                                                    )}
                                                </span>
                                            `
                                            : ""
                                    }

                                    ${
                                        cost
                                            ? `
                                                <span>
                                                    💰
                                                    ${escapeHtml(
                                                        cost
                                                    )}
                                                </span>
                                            `
                                            : ""
                                    }

                                    ${
                                        travelTime
                                            ? `
                                                <span>
                                                    ⏱️
                                                    ${escapeHtml(
                                                        travelTime
                                                    )}
                                                </span>
                                            `
                                            : ""
                                    }

                                </div>

                            </div>
                        `;
                    })
                    .join("")
            }

        </div>
    `;
}


// Render travel tips

function renderTips(tips) {
    return `
        <div class="panel">

            <h3>
                💡 Travel Tips
            </h3>

            ${
                tips
                    .map(item => {
                        const title =
                            fieldText(
                                item,
                                [
                                    "title",
                                    "name"
                                ]
                            );

                        const description =
                            fieldText(
                                item,
                                [
                                    "description",
                                    "details"
                                ]
                            );

                        return `
                            <div class="tip-item">

                                <span class="check">
                                    ✔
                                </span>

                                <div>

                                    <strong>
                                        ${escapeHtml(
                                            title
                                        )}
                                    </strong>

                                    <span>
                                        ${escapeHtml(
                                            description
                                        )}
                                    </span>

                                </div>

                            </div>
                        `;
                    })
                    .join("")
            }

        </div>
    `;
}


// Render the itinerary

function renderDetailedItinerary(
    itinerary
) {
    return `
        <div class="panel itinerary-panel">

            <h3>
                🗓️ Detailed Itinerary
            </h3>

            ${
                itinerary
                    .map(day =>
                        renderItineraryDay(
                            day
                        )
                    )
                    .join("")
            }

        </div>
    `;
}


// Render one itinerary day

function renderItineraryDay(day) {
    const dayNumber =
        fieldText(
            day,
            ["day"]
        );

    const title =
        fieldText(
            day,
            [
                "title",
                "name"
            ]
        );

    const summary =
        fieldText(
            day,
            [
                "summary",
                "description"
            ]
        );

    const morning =
        asArray(day.morning);

    const afternoon =
        asArray(day.afternoon);

    const evening =
        asArray(day.evening);

    const night =
        asArray(day.night);

    const activities =
        asArray(day.activities);

    const meals =
        asArray(day.meals);

    const travelNotes =
        fieldText(
            day,
            [
                "travel_notes",
                "travelNotes",
                "transport"
            ]
        );

    const estimatedCost =
        fieldText(
            day,
            [
                "estimated_cost",
                "estimatedCost",
                "cost"
            ]
        );

    const distance =
        fieldText(
            day,
            ["distance"]
        );

    const accommodation =
        fieldText(
            day,
            ["accommodation"]
        );

    return `
        <div class="itinerary-day">

            <div class="day-label">

                📌 Day
                ${escapeHtml(
                    dayNumber
                )}

                ${
                    title
                        ? `
                            — ${escapeHtml(
                                title
                            )}
                        `
                        : ""
                }

            </div>

            ${
                summary
                    ? `
                        <p class="day-summary">
                            ${escapeHtml(
                                summary
                            )}
                        </p>
                    `
                    : ""
            }

            ${renderTimeBlock(
                "🌅 Morning",
                morning
            )}

            ${renderTimeBlock(
                "☀️ Afternoon",
                afternoon
            )}

            ${renderTimeBlock(
                "🌆 Evening",
                evening
            )}

            ${renderTimeBlock(
                "🌙 Night",
                night
            )}

            ${
                activities.length
                    ? renderActivityList(
                        "📍 Activities",
                        activities
                    )
                    : ""
            }

            ${
                meals.length
                    ? renderActivityList(
                        "🍽️ Meals",
                        meals
                    )
                    : ""
            }

            ${
                accommodation
                    ? `
                        <div class="travel-note">
                            🏨
                            <strong>
                                Accommodation:
                            </strong>
                            ${escapeHtml(
                                accommodation
                            )}
                        </div>
                    `
                    : ""
            }

            ${
                travelNotes
                    ? `
                        <div class="travel-note">
                            🚗
                            <strong>
                                Travel:
                            </strong>
                            ${escapeHtml(
                                travelNotes
                            )}
                        </div>
                    `
                    : ""
            }

            <div class="day-footer">

                ${
                    estimatedCost
                        ? `
                            <div class="cost-line">
                                💰
                                ${escapeHtml(
                                    estimatedCost
                                )}
                            </div>
                        `
                        : ""
                }

                ${
                    distance
                        ? `
                            <div class="distance-line">
                                📏
                                ${escapeHtml(
                                    distance
                                )}
                            </div>
                        `
                        : ""
                }

            </div>

        </div>
    `;
}


// Render a morning, afternoon, evening or night block

function renderTimeBlock(
    title,
    items
) {
    if (!items.length) {
        return "";
    }

    return `
        <div class="time-block">

            <div class="time-title">
                ${title}
            </div>

            <div class="timeline">

                ${
                    items
                        .map(item =>
                            renderActivityItem(
                                item
                            )
                        )
                        .join("")
                }

            </div>

        </div>
    `;
}


// Render one activity

function renderActivityItem(
    activity
) {
    if (
        activity === null ||
        activity === undefined
    ) {
        return "";
    }

    if (
        typeof activity === "string" ||
        typeof activity === "number"
    ) {
        return `
            <div class="timeline-item">

                <div class="timeline-content">
                    ${escapeHtml(
                        activity
                    )}
                </div>

            </div>
        `;
    }

    const time =
        fieldText(
            activity,
            ["time"]
        );

    const activityName =
        fieldText(
            activity,
            [
                "activity",
                "name",
                "title"
            ]
        );

    const location =
        fieldText(
            activity,
            ["location"]
        );

    const duration =
        fieldText(
            activity,
            ["duration"]
        );

    const description =
        fieldText(
            activity,
            ["description"]
        );

    const cost =
        fieldText(
            activity,
            [
                "estimated_cost",
                "estimatedCost",
                "cost"
            ]
        );

    return `
        <div class="timeline-item">

            ${
                time
                    ? `
                        <div class="activity-time">
                            ${escapeHtml(
                                time
                            )}
                        </div>
                    `
                    : ""
            }

            <div class="timeline-content">

                <strong>
                    ${escapeHtml(
                        activityName
                    )}
                </strong>

                ${
                    location
                        ? `
                            <div class="activity-meta">
                                📍
                                ${escapeHtml(
                                    location
                                )}
                            </div>
                        `
                        : ""
                }

                ${
                    duration
                        ? `
                            <div class="activity-meta">
                                ⏱️
                                ${escapeHtml(
                                    duration
                                )}
                            </div>
                        `
                        : ""
                }

                ${
                    description
                        ? `
                            <p class="activity-description">
                                ${escapeHtml(
                                    description
                                )}
                            </p>
                        `
                        : ""
                }

                ${
                    cost
                        ? `
                            <div class="activity-cost">
                                💰
                                ${escapeHtml(
                                    cost
                                )}
                            </div>
                        `
                        : ""
                }

            </div>

        </div>
    `;
}


// Render a simple activity list

function renderActivityList(
    title,
    items
) {
    return `
        <div class="activity-list">

            <div class="activity-title">
                ${title}
            </div>

            <ul>

                ${
                    items
                        .map(
                            item => `
                                <li>
                                    ${escapeHtml(
                                        activityText(
                                            item
                                        )
                                    )}
                                </li>
                            `
                        )
                        .join("")
                }

            </ul>

        </div>
    `;
}


// Convert an activity into readable text

function activityText(activity) {
    if (
        activity === null ||
        activity === undefined
    ) {
        return "";
    }

    if (
        typeof activity === "string" ||
        typeof activity === "number"
    ) {
        return String(activity);
    }

    const time =
        fieldText(
            activity,
            ["time"]
        );

    const name =
        fieldText(
            activity,
            [
                "activity",
                "name",
                "title"
            ]
        );

    const location =
        fieldText(
            activity,
            ["location"]
        );

    return [
        time,
        name,
        location
    ]
        .filter(Boolean)
        .join(" — ");
}


// Build a clear language instruction for Gemini

function buildLanguageInstruction(
    language
) {
    return `
IMPORTANT LANGUAGE RULE:

The selected target language is: ${language}.

You MUST write the complete response in ${language}.

Do not translate the user's input into another language.

Do not answer in English unless the selected target language is English.

All text fields must use ${language}, including:
- message
- destination
- trip duration
- travel style
- best time
- budget
- attractions
- food
- transportation
- tips
- itinerary
- activity names
- descriptions
- locations
- accommodation
- travel notes

Keep numbers, dates and currency values natural for ${language}.

Return valid JSON only.
`;
}


// Send the request to FastAPI

async function fetchTripPlan(
    query,
    language
) {
    // Create an explicit instruction so the AI knows
    // which language must be used for the answer.

    const languageInstruction =
        buildLanguageInstruction(
            language
        );

    const response =
        await fetch(
            API_ENDPOINT,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    "Accept":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        message:
                            `${languageInstruction}\n\nUSER REQUEST:\n${query}`,

                        language:
                            language,

                        session_id:
                            currentSessionId
                    })
            }
        );

    if (!response.ok) {
        let errorText =
            `HTTP ${response.status}`;

        try {
            const errorData =
                await response.json();

            if (errorData.detail) {
                errorText =
                    errorData.detail;
            }
        } catch {
            // The server did not return JSON
        }

        throw new Error(
            errorText
        );
    }

    const data =
        await response.json();

    if (!data) {
        throw new Error(
            "Empty response received from server."
        );
    }

    // Save the session ID returned by FastAPI

    if (data.session_id) {
        currentSessionId =
            data.session_id;

        currentChat.id =
            data.session_id;

        localStorage.setItem(
            SESSION_STORAGE_KEY,
            data.session_id
        );
    }

    // Keep the selected language in the frontend

    data.language =
        data.language ||
        language;

    return data;
}


// Send a user message

async function sendMessage() {
    const input =
        document.getElementById(
            "chatInput"
        );

    if (!input) {
        return;
    }

    const query =
        input.value.trim();

    if (!query) {
        return;
    }

    // Read the language at the exact moment
    // the user clicks Send.

    const language =
        getSelectedLanguage();

    // Create a session if needed

    if (!currentSessionId) {
        createNewSession();
    }

    // Always use the currently selected language

    currentChat.language =
        language;

    if (
        currentChat.messages.length ===
        0
    ) {
        currentChat.title =
            createChatTitle(query);
    }

    // Add the user message

    currentChat.messages.push({
        role: "user",

        content:
            query,

        language:
            language,

        timestamp:
            new Date().toISOString()
    });

    appendUserMessage(
        query,
        true
    );

    input.value = "";

    appendLoading();

    scrollChatToBottom(true);

    let data;

    try {
        data =
            await fetchTripPlan(
                query,
                language
            );

    } catch (error) {
        console.error(
            "TravelMate API error:",
            error
        );

        removeLoading();

        // Show the real error instead of
        // making the page appear to refresh.

        appendAssistantMessage(
            {
                message:
                    `TravelMate could not generate a response.\n\nError: ${error.message}`
            },
            query,
            true
        );

        input.focus();

        return;
    }

    removeLoading();

    // Save the assistant response

    currentChat.messages.push({
        role: "assistant",

        content:
            data.message || "",

        data:
            data,

        query:
            query,

        language:
            data.language ||
            language,

        timestamp:
            new Date().toISOString()
    });

    // Update destination

    let destination = "";

    if (
        typeof data.destination ===
        "string"
    ) {
        destination =
            data.destination;

    } else if (
        data.destination &&
        typeof data.destination ===
        "object"
    ) {
        destination =
            data.destination.name ||
            "";
    }

    if (destination) {
        currentChat.destination =
            destination;
    }

    // Show the AI response

    appendAssistantMessage(
        data,
        query,
        true
    );

    // Update recent chats

    saveCurrentChat();

    scrollChatToBottom(true);

    input.focus();
}


// Add a user message

function appendUserMessage(
    query,
    shouldScroll = true
) {
    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) {
        return;
    }

    const div =
        document.createElement(
            "div"
        );

    div.className =
        "user-msg";

    div.innerHTML =
        escapeHtml(query);

    area.appendChild(div);

    if (shouldScroll) {
        scrollChatToBottom();
    }
}


// Add an AI message

function appendAssistantMessage(
    data,
    query,
    shouldScroll = true
) {
    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) {
        return;
    }

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        "assistant-response";

    wrapper.innerHTML =
        renderAssistantResponse(
            data,
            query
        );

    area.appendChild(wrapper);

    if (shouldScroll) {
        scrollChatToBottom();
    }
}


// Show loading message

function appendLoading() {
    removeLoading();

    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) {
        return;
    }

    const loading =
        document.createElement(
            "div"
        );

    loading.id =
        "chatLoading";

    loading.className =
        "loading";

    loading.innerHTML = `
        <div>
            ✈️ Planning your trip...
        </div>
    `;

    area.appendChild(loading);
}


// Remove loading message

function removeLoading() {
    const loading =
        document.getElementById(
            "chatLoading"
        );

    if (loading) {
        loading.remove();
    }
}


// Scroll to the latest message

function scrollChatToBottom(
    smooth = true
) {
    const scrollArea =
        document.getElementById(
            "chatScrollArea"
        );

    if (!scrollArea) {
        return;
    }

    setTimeout(() => {
        scrollArea.scrollTo({
            top:
                scrollArea.scrollHeight,

            behavior:
                smooth
                    ? "smooth"
                    : "auto"
        });
    }, 50);
}


// Create a short chat title

function createChatTitle(query) {
    let title =
        String(
            query || ""
        ).trim();

    if (title.length > 36) {
        title =
            title.substring(0, 36) +
            "...";
    }

    return (
        title ||
        "Travel Chat"
    );
}


// Watch for target language changes

function initializeLanguageListener() {
    const languageSelect =
        document.getElementById(
            "languageSelect"
        );

    if (!languageSelect) {
        return;
    }

    languageSelect.addEventListener(
        "change",
        function () {
            // Change the current chat language immediately

            currentChat.language =
                this.value;

            // Save the new language for this chat

            saveCurrentChat();

            console.log(
                "Target language changed to:",
                this.value
            );
        }
    );
}


// Allow Enter to send

function initializeInputListener() {
    const input =
        document.getElementById(
            "chatInput"
        );

    if (!input) {
        return;
    }

    input.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();

                sendMessage();
            }
        }
    );
}


// Connect New Chat button

function initializeNewChatButton() {
    const button =
        document.getElementById(
            "newChatBtn"
        );

    if (!button) {
        return;
    }

    button.addEventListener(
        "click",
        startNewChat
    );
}


// Initialize the chat page

async function initializeChat() {
    console.log(
        "Initializing TravelMate chat..."
    );

    const savedSessionId =
        localStorage.getItem(
            SESSION_STORAGE_KEY
        );

    if (savedSessionId) {
        const restored =
            await loadChatHistoryFromServer(
                savedSessionId
            );

        if (restored) {
            console.log(
                "Existing conversation restored."
            );
        } else {
            currentSessionId =
                savedSessionId;

            currentChat = {
                id:
                    savedSessionId,

                title:
                    "New Chat",

                language:
                    getSelectedLanguage(),

                destination:
                    "",

                messages:
                    []
            };

            showWelcomeScreen();

            renderRecentList();
        }

    } else {
        createNewSession();

        showWelcomeScreen();
    }

    initializeLanguageListener();

    initializeInputListener();

    initializeNewChatButton();

    renderRecentList();

    document
        .getElementById(
            "chatInput"
        )
        ?.focus();
}


// Start when the page is ready

document.addEventListener(
    "DOMContentLoaded",
    initializeChat
);
/* =========================================================
   TRAVELMATE AI CHAT
   Updated for current FastAPI response structure
========================================================= */

const API_ENDPOINT = "/api/chat";

let currentSessionId = null;

let currentChat = {
    id: null,
    title: "New Chat",
    language: "English",
    destination: "",
    messages: []
};

let chatHistory = [];


/* =========================================================
   HTML ESCAPING
========================================================= */

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* =========================================================
   TEXT HELPER
========================================================= */

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


/* =========================================================
   ARRAY HELPER
========================================================= */

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


/* =========================================================
   IMAGES
========================================================= */

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

    return CATEGORY_IMAGES[category] ||
        CATEGORY_IMAGES.default;
}


/* =========================================================
   CREATE SESSION
========================================================= */

function createNewSession() {

    const sessionId =
        "session-" +
        Date.now() +
        "-" +
        Math.random()
            .toString(36)
            .substring(2, 8);

    currentSessionId = sessionId;

    const language =
        document.getElementById("languageSelect")?.value ||
        "English";

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


/* =========================================================
   NEW CHAT
========================================================= */

function startNewChat() {

    saveCurrentChat();

    createNewSession();

    showWelcomeScreen();

    document
        .getElementById("chatInput")
        ?.focus();
}


/* =========================================================
   SAVE CHAT
========================================================= */

function saveCurrentChat() {

    if (
        !currentChat ||
        !currentChat.messages ||
        currentChat.messages.length === 0
    ) {
        return;
    }

    const existingIndex =
        chatHistory.findIndex(
            chat => chat.id === currentChat.id
        );

    const chatObject = {

        id: currentChat.id,

        title:
            currentChat.title ||
            "Travel Chat",

        language:
            currentChat.language ||
            "English",

        destination:
            currentChat.destination ||
            "",

        messages:
            currentChat.messages,

        time: "Just now"
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


/* =========================================================
   RECENT CHATS
========================================================= */

function renderRecentList() {

    const list =
        document.getElementById(
            "recentList"
        );

    if (!list) return;

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
                    chat.id === currentSessionId
                        ? "active"
                        : "";

                return `
                    <button
                        type="button"
                        class="recent-item ${active}"
                        data-chat-id="${escapeHtml(chat.id)}"
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
                                    "Recent"
                                )}
                            </span>

                        </div>

                    </button>
                `;
            })
            .join("");

    list
        .querySelectorAll(".recent-item")
        .forEach(item => {

            item.addEventListener(
                "click",
                () => {
                    openChat(
                        item.dataset.chatId
                    );
                }
            );

        });
}


/* =========================================================
   OPEN CHAT
========================================================= */

function openChat(sessionId) {

    const chat =
        chatHistory.find(
            item => item.id === sessionId
        );

    if (!chat) return;

    currentSessionId =
        chat.id;

    currentChat = {
        id: chat.id,

        title:
            chat.title ||
            "Travel Chat",

        language:
            chat.language ||
            "English",

        destination:
            chat.destination ||
            "",

        messages:
            chat.messages ||
            []
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
}


/* =========================================================
   WELCOME
========================================================= */

function showWelcomeScreen() {

    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) return;

    area.innerHTML = `

        <div class="welcome-screen">

            <div class="welcome-icon">
                🌍
            </div>

            <h2>
                Where do you want to go?
            </h2>

            <p>
                Ask me about destinations,
                detailed itineraries, local food,
                transportation, budgets,
                attractions, safety and travel tips.
            </p>

        </div>

    `;
}


/* =========================================================
   RENDER CONVERSATION
========================================================= */

function renderConversation() {

    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) return;

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

            if (message.role === "user") {

                appendUserMessage(
                    message.content,
                    false
                );
            }

            if (message.role === "assistant") {

                appendAssistantMessage(
                    message.data,
                    message.query,
                    false
                );
            }
        }
    );

    scrollChatToBottom(false);
}


/* =========================================================
   ASSISTANT RESPONSE
========================================================= */

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


    /* =====================================================
       BASIC DATA
    ===================================================== */

    const message =
        data.message || "";

    let destination = "";

    if (typeof data.destination === "string") {

        destination =
            data.destination;

    } else if (
        data.destination &&
        typeof data.destination === "object"
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


    /* =====================================================
       ARRAYS
    ===================================================== */

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


    /* =====================================================
       TRIP METADATA
    ===================================================== */

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


    /* =====================================================
       CHECK CONTENT
    ===================================================== */

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


    /* =====================================================
       SIMPLE RESPONSE
    ===================================================== */

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


    /* =====================================================
       HERO
    ===================================================== */

    const heroHtml =
        destination
            ? `
                <div class="hero">

                    <div class="hero-img">

                        <img
                            src="${HERO_IMAGE}"
                            alt="${escapeHtml(destination)}"
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
                            ${escapeHtml(destination)}
                            ✨
                        </h2>

                        <p class="tagline">
                            Your AI Travel Plan
                        </p>

                        ${
                            message
                                ? `
                                    <p class="hero-desc">
                                        ${formatText(message)}
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


    /* =====================================================
       TRIP OVERVIEW
    ===================================================== */

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
                                        <span>📅 Duration</span>
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
                                        <span>✨ Travel Style</span>
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
                                        <span>🌤️ Best Time</span>
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
                                        <span>💰 Estimated Budget</span>
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
                ? renderAttractions(attractions)
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


/* =========================================================
   FORMAT TEXT
========================================================= */

function formatText(text) {

    if (!text) return "";

    return escapeHtml(text)
        .replace(/\n\n/g, "</p><p>")
        .replace(/\n/g, "<br>");
}


/* =========================================================
   ATTRACTIONS
========================================================= */

function renderAttractions(attractions) {

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
                            ) || "Nature";

                        const name =
                            fieldText(
                                item,
                                ["name", "title"]
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
                                    src="${imgForCategory(category)}"
                                    alt="${escapeHtml(name)}"
                                    loading="lazy"
                                >

                                <div class="attraction-body">

                                    <h4>
                                        ${escapeHtml(name)}
                                    </h4>

                                    <p>
                                        ${escapeHtml(
                                            description
                                        )}
                                    </p>

                                    <span class="tag">
                                        ${escapeHtml(category)}
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


/* =========================================================
   FOOD
========================================================= */

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
                                ["name", "title"]
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
                                        ${escapeHtml(name)}
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
                                                    ${escapeHtml(type)}
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


/* =========================================================
   TRANSPORTATION
========================================================= */

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
                                        ${escapeHtml(mode)}
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


/* =========================================================
   TIPS
========================================================= */

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
                                        ${escapeHtml(title)}
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


/* =========================================================
   DETAILED ITINERARY
========================================================= */

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
                        renderItineraryDay(day)
                    )
                    .join("")
            }

        </div>
    `;
}


/* =========================================================
   ITINERARY DAY
========================================================= */

function renderItineraryDay(day) {

    const dayNumber =
        fieldText(
            day,
            ["day"]
        );

    const title =
        fieldText(
            day,
            ["title", "name"]
        );

    const summary =
        fieldText(
            day,
            ["summary", "description"]
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
                ${escapeHtml(dayNumber)}

                ${
                    title
                        ? `
                            — ${escapeHtml(title)}
                        `
                        : ""
                }

            </div>

            ${
                summary
                    ? `
                        <p class="day-summary">
                            ${escapeHtml(summary)}
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
                            <strong>Accommodation:</strong>
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
                            <strong>Travel:</strong>
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


/* =========================================================
   TIME BLOCK
========================================================= */

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
                        .map(
                            item =>
                                renderActivityItem(item)
                        )
                        .join("")
                }

            </div>

        </div>
    `;
}


/* =========================================================
   ACTIVITY ITEM
========================================================= */

function renderActivityItem(activity) {

    if (
        activity === null ||
        activity === undefined
    ) {
        return "";
    }


    /* Old backend/string compatibility */

    if (
        typeof activity === "string" ||
        typeof activity === "number"
    ) {

        return `
            <div class="timeline-item">

                <div class="timeline-content">

                    ${escapeHtml(activity)}

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
                            ${escapeHtml(time)}
                        </div>
                    `
                    : ""
            }

            <div class="timeline-content">

                <strong>
                    ${escapeHtml(activityName)}
                </strong>

                ${
                    location
                        ? `
                            <div class="activity-meta">
                                📍
                                ${escapeHtml(location)}
                            </div>
                        `
                        : ""
                }

                ${
                    duration
                        ? `
                            <div class="activity-meta">
                                ⏱️
                                ${escapeHtml(duration)}
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
                                ${escapeHtml(cost)}
                            </div>
                        `
                        : ""
                }

            </div>

        </div>
    `;
}


/* =========================================================
   ACTIVITY LIST
========================================================= */

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
                                        activityText(item)
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
        fieldText(activity, ["time"]);

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


/* =========================================================
   API REQUEST
========================================================= */

async function fetchTripPlan(
    query,
    language
) {

    const response =
        await fetch(
            API_ENDPOINT,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        message: query,
                        language: language,
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
            // Ignore JSON parsing error.
        }

        throw new Error(errorText);
    }


    const data =
        await response.json();


    if (data.session_id) {

        currentSessionId =
            data.session_id;

        currentChat.id =
            data.session_id;
    }


    return data;
}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    const input =
        document.getElementById(
            "chatInput"
        );

    if (!input) return;

    const query =
        input.value.trim();

    if (!query) return;


    const language =
        document.getElementById(
            "languageSelect"
        )?.value ||
        "English";


    if (!currentSessionId) {
        createNewSession();
    }


    currentChat.language =
        language;


    if (
        currentChat.messages.length === 0
    ) {

        currentChat.title =
            createChatTitle(query);
    }


    /* USER */

    currentChat.messages.push({

        role: "user",

        content: query,

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


    /* API */

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

        appendAssistantMessage(
            {
                message:
                    "Sorry, TravelMate is temporarily unavailable. Please try again in a few seconds."
            },
            query,
            true
        );

        input.focus();

        return;
    }


    removeLoading();


    /* ASSISTANT */

    currentChat.messages.push({

        role: "assistant",

        content:
            data.message || "",

        data: data,

        query: query,

        timestamp:
            new Date().toISOString()

    });


    /* Destination */

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


    if (destination) {

        currentChat.destination =
            destination;
    }


    appendAssistantMessage(
        data,
        query,
        true
    );


    saveCurrentChat();

    scrollChatToBottom(true);

    input.focus();
}


/* =========================================================
   USER MESSAGE
========================================================= */

function appendUserMessage(
    query,
    shouldScroll = true
) {

    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) return;


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


/* =========================================================
   ASSISTANT MESSAGE
========================================================= */

function appendAssistantMessage(
    data,
    query,
    shouldScroll = true
) {

    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) return;


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


/* =========================================================
   LOADING
========================================================= */

function appendLoading() {

    removeLoading();


    const area =
        document.getElementById(
            "resultArea"
        );

    if (!area) return;


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


function removeLoading() {

    const loading =
        document.getElementById(
            "chatLoading"
        );

    if (loading) {
        loading.remove();
    }
}


/* =========================================================
   SCROLL
========================================================= */

function scrollChatToBottom(
    smooth = true
) {

    const scrollArea =
        document.getElementById(
            "chatScrollArea"
        );

    if (!scrollArea) return;


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


/* =========================================================
   CHAT TITLE
========================================================= */

function createChatTitle(query) {

    let title =
        query.trim();


    if (title.length > 36) {

        title =
            title.substring(0, 36) +
            "...";
    }


    return title;
}


/* =========================================================
   LANGUAGE
========================================================= */

function initializeLanguageListener() {

    const languageSelect =
        document.getElementById(
            "languageSelect"
        );


    if (!languageSelect) return;


    languageSelect.addEventListener(
        "change",
        function () {

            currentChat.language =
                this.value;

            saveCurrentChat();

        }
    );
}


/* =========================================================
   ENTER KEY
========================================================= */

function initializeInputListener() {

    const input =
        document.getElementById(
            "chatInput"
        );


    if (!input) return;


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


/* =========================================================
   NEW CHAT BUTTON
========================================================= */

function initializeNewChatButton() {

    const button =
        document.getElementById(
            "newChatBtn"
        );

    if (!button) return;

    button.addEventListener(
        "click",
        startNewChat
    );
}


/* =========================================================
   INITIALIZE
========================================================= */

function initializeChat() {

    createNewSession();

    showWelcomeScreen();

    renderRecentList();

    initializeLanguageListener();

    initializeInputListener();

    initializeNewChatButton();

    document
        .getElementById("chatInput")
        ?.focus();
}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initializeChat
);
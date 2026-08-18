/*
 * =========================================================
 * TRAVELAI — AI CHAT ASSISTANT
 * =========================================================
 *
 * Backend:
 *
 * POST /api/chat
 * GET  /api/chat/history/{session_id}
 *
 * The backend returns:
 *
 * {
 *   success,
 *   session_id,
 *   language,
 *   message,
 *   destination,
 *   attractions,
 *   food,
 *   transportation,
 *   tips,
 *   itinerary
 * }
 */


const state = {

    sessionId:
        localStorage.getItem(
            "travelaiChatSessionId"
        ) || null,

    language:
        localStorage.getItem(
            "travelaiChatLanguage"
        ) || "English",

    sending: false

};


const languageCodes = {

    English: "en",

    Hindi: "hi",

    Telugu: "te",

    Tamil: "ta"

};


function $(id) {
    return document.getElementById(id);
}


function escapeHtml(value) {

    return String(value ?? "")
        .replace(
            /[&<>"']/g,
            character => ({

                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"

            })[character]
        );

}


/* =========================================================
   SESSION
========================================================= */

function saveSessionId(sessionId) {

    state.sessionId =
        sessionId;

    if (sessionId) {

        localStorage.setItem(
            "travelaiChatSessionId",
            sessionId
        );

    }

    updateSessionDisplay();

}


function updateSessionDisplay() {

    const element =
        $("sessionId");

    if (!element) return;

    element.textContent =
        state.sessionId
        ||
        "New conversation";

}


/* =========================================================
   NEW CHAT
========================================================= */

function newChat() {

    state.sessionId = null;

    localStorage.removeItem(
        "travelaiChatSessionId"
    );

    $("messages").innerHTML = `
        ${welcomeMarkup()}
    `;

    updateSessionDisplay();

    bindSuggestionButtons();

    $("messageInput").focus();

}


function welcomeMarkup() {

    return `

        <div class="welcome">

            <div class="welcome-icon">
                ✦
            </div>

            <h1>
                Where do you want to go?
            </h1>

            <p>
                Ask me anything about destinations, attractions,
                food, transportation, itineraries and travel tips.
            </p>

            <div class="welcome-suggestions">

                <button data-message="Plan a 3 day trip to Hyderabad">
                    🗺️ Plan a 3-day Hyderabad trip
                </button>

                <button data-message="What food should I try in Hyderabad?">
                    🍛 What food should I try?
                </button>

                <button data-message="What are the best places to visit in Hyderabad?">
                    📍 Best places to visit
                </button>

            </div>

        </div>

    `;

}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage(message) {

    message =
        String(message || "")
            .trim();

    if (!message || state.sending) {
        return;
    }


    const welcome =
        document.querySelector(
            ".welcome"
        );

    if (welcome) {
        welcome.remove();
    }


    addUserMessage(
        message
    );


    $("messageInput").value = "";

    autoResizeTextarea();


    state.sending = true;

    $("sendButton").disabled =
        true;

    showTyping();


    try {

        const payload = {

            message:
                message,

            language:
                state.language

        };


        if (state.sessionId) {

            payload.session_id =
                state.sessionId;

        }


        const response =
            await fetch(
                "/api/chat",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            payload
                        )

                }
            );


        if (!response.ok) {

            let errorText =
                `Chat request failed (${response.status})`;

            try {

                const errorData =
                    await response.json();

                errorText =
                    errorData.detail
                    ||
                    errorText;

            }

            catch (_) {}

            throw new Error(
                errorText
            );

        }


        const data =
            await response.json();


        if (data.session_id) {

            saveSessionId(
                data.session_id
            );

        }


        addAssistantResponse(
            data
        );

    }

    catch (error) {

        console.error(
            "Chat error:",
            error
        );


        addErrorMessage(
            error.message
        );

    }

    finally {

        hideTyping();

        state.sending =
            false;

        $("sendButton").disabled =
            false;

        $("messageInput").focus();

    }

}


/* =========================================================
   USER MESSAGE
========================================================= */

function addUserMessage(
    message
) {

    const container =
        $("messages");


    const row =
        document.createElement(
            "div"
        );

    row.className =
        "message-row user";


    row.innerHTML = `

        <div class="message-content">

            <div class="message-bubble">
                ${escapeHtml(message)}
            </div>

            <div class="message-meta">
                You
            </div>

        </div>

        <div class="avatar user-avatar">
            You
        </div>

    `;


    container.appendChild(
        row
    );


    scrollToBottom();

}


/* =========================================================
   ASSISTANT RESPONSE
========================================================= */

function addAssistantResponse(
    data
) {

    const container =
        $("messages");


    const row =
        document.createElement(
            "div"
        );

    row.className =
        "message-row ai";


    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";


    let html = "";


    if (data.message) {

        html += `

            <div class="message-bubble">
                ${formatText(data.message)}
            </div>

        `;

    }


    if (data.destination) {

        html += `

            <div class="response-card">

                <div class="response-title">
                    📍 ${escapeHtml(
                        data.destination
                    )}
                </div>

            </div>

        `;

    }


    html += renderAttractions(
        data.attractions
    );


    html += renderFood(
        data.food
    );


    html += renderTransportation(
        data.transportation
    );


    html += renderTips(
        data.tips
    );


    html += renderItinerary(
        data.itinerary
    );


    content.innerHTML =
        html;


    row.innerHTML = `

        <div class="avatar ai-avatar">
            ✦
        </div>

    `;

    row.appendChild(
        content
    );


    container.appendChild(
        row
    );


    scrollToBottom();

}


/* =========================================================
   TEXT
========================================================= */

function formatText(
    text
) {

    return escapeHtml(
        text
    )
    .replace(
        /\n/g,
        "<br>"
    );

}


/* =========================================================
   ATTRACTIONS
========================================================= */

function renderAttractions(
    attractions
) {

    if (
        !Array.isArray(attractions)
        ||
        attractions.length === 0
    ) {

        return "";

    }


    return `

        <div class="response-card">

            <div class="response-title">
                📍 Attractions
            </div>

            <div class="response-items">

                ${attractions
                    .map(
                        item => `

                            <div class="response-item">

                                <strong>
                                    ${escapeHtml(
                                        item.name
                                    )}
                                </strong>

                                <p>
                                    ${escapeHtml(
                                        item.description
                                    )}
                                </p>

                                ${
                                    item.category
                                    ?

                                    `
                                        <span class="badge">
                                            ${escapeHtml(
                                                item.category
                                            )}
                                        </span>
                                    `

                                    :

                                    ""
                                }

                            </div>

                        `
                    )
                    .join("")}

            </div>

        </div>

    `;

}


/* =========================================================
   FOOD
========================================================= */

function renderFood(
    food
) {

    if (
        !Array.isArray(food)
        ||
        food.length === 0
    ) {

        return "";

    }


    return `

        <div class="response-card">

            <div class="response-title">
                🍛 Food
            </div>

            <div class="response-items">

                ${food
                    .map(
                        item => `

                            <div class="response-item">

                                <strong>
                                    ${escapeHtml(
                                        item.name
                                    )}
                                </strong>

                                <p>
                                    ${escapeHtml(
                                        item.description
                                    )}
                                </p>

                                ${
                                    item.type
                                    ?

                                    `
                                        <span class="badge">
                                            ${escapeHtml(
                                                item.type
                                            )}
                                        </span>
                                    `

                                    :

                                    ""
                                }

                            </div>

                        `
                    )
                    .join("")}

            </div>

        </div>

    `;

}


/* =========================================================
   TRANSPORTATION
========================================================= */

function renderTransportation(
    transportation
) {

    if (
        !Array.isArray(transportation)
        ||
        transportation.length === 0
    ) {

        return "";

    }


    return `

        <div class="response-card">

            <div class="response-title">
                🚕 Transportation
            </div>

            <div class="response-items">

                ${transportation
                    .map(
                        item => `

                            <div class="response-item">

                                <strong>
                                    ${escapeHtml(
                                        item.mode
                                    )}
                                </strong>

                                <p>
                                    ${escapeHtml(
                                        item.description
                                    )}
                                </p>

                            </div>

                        `
                    )
                    .join("")}

            </div>

        </div>

    `;

}


/* =========================================================
   TIPS
========================================================= */

function renderTips(
    tips
) {

    if (
        !Array.isArray(tips)
        ||
        tips.length === 0
    ) {

        return "";

    }


    return `

        <div class="response-card">

            <div class="response-title">
                💡 Travel Tips
            </div>

            <div class="response-items">

                ${tips
                    .map(
                        item => `

                            <div class="response-item">

                                <strong>
                                    ${escapeHtml(
                                        item.title
                                    )}
                                </strong>

                                <p>
                                    ${escapeHtml(
                                        item.description
                                    )}
                                </p>

                            </div>

                        `
                    )
                    .join("")}

            </div>

        </div>

    `;

}


/* =========================================================
   ITINERARY
========================================================= */

function renderItinerary(
    itinerary
) {

    if (
        !Array.isArray(itinerary)
        ||
        itinerary.length === 0
    ) {

        return "";

    }


    return `

        <div class="itinerary">

            ${itinerary
                .map(
                    day => `

                        <div class="day-card">

                            <div class="day-header">

                                <div class="day-number">
                                    ${escapeHtml(
                                        day.day
                                    )}
                                </div>

                                <div class="day-title">
                                    ${escapeHtml(
                                        day.title
                                    )}
                                </div>

                            </div>

                            <ul class="activities">

                                ${
                                    Array.isArray(
                                        day.activities
                                    )

                                    ?

                                    day.activities
                                        .map(
                                            activity => `
                                                <li>
                                                    ${escapeHtml(
                                                        activity
                                                    )}
                                                </li>
                                            `
                                        )
                                        .join("")

                                    :

                                    ""
                                }

                            </ul>

                        </div>

                    `
                )
                .join("")}

        </div>

    `;

}


/* =========================================================
   ERROR
========================================================= */

function addErrorMessage(
    message
) {

    const container =
        $("messages");


    const row =
        document.createElement(
            "div"
        );

    row.className =
        "message-row ai";


    row.innerHTML = `

        <div class="avatar ai-avatar">
            ✦
        </div>

        <div class="message-content">

            <div class="message-bubble">

                ⚠️ Sorry, I couldn't process that request.

                <br><br>

                <small>
                    ${escapeHtml(
                        message
                    )}
                </small>

            </div>

        </div>

    `;


    container.appendChild(
        row
    );


    scrollToBottom();

}


/* =========================================================
   TYPING
========================================================= */

function showTyping() {

    $("typing")
        .classList
        .remove("hidden");

    scrollToBottom();

}


function hideTyping() {

    $("typing")
        .classList
        .add("hidden");

}


/* =========================================================
   SCROLL
========================================================= */

function scrollToBottom() {

    const container =
        $("messages");


    requestAnimationFrame(
        () => {

            container.scrollTop =
                container.scrollHeight;

        }
    );

}


/* =========================================================
   HISTORY
========================================================= */

async function loadHistory() {

    if (!state.sessionId) {
        return;
    }


    try {

        const response =
            await fetch(
                `/api/chat/history/${encodeURIComponent(
                    state.sessionId
                )}`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load chat history."
            );

        }


        const data =
            await response.json();


        if (
            !Array.isArray(
                data.messages
            )
        ) {

            return;

        }


        const container =
            $("messages");


        container.innerHTML = "";


        for (
            const item of data.messages
        ) {

            if (
                item.role === "user"
            ) {

                addUserMessage(
                    item.content
                );

            }

            else if (
                item.role === "assistant"
            ) {

                let parsed;


                try {

                    parsed =
                        JSON.parse(
                            item.content
                        );

                }

                catch (_) {

                    parsed = {

                        message:
                            item.content

                    };

                }


                addAssistantResponse(
                    parsed
                );

            }

        }


        scrollToBottom();

    }

    catch (error) {

        console.error(
            "History error:",
            error
        );

    }

}


/* =========================================================
   LANGUAGE
========================================================= */

function changeLanguage(
    language
) {

    state.language =
        language;

    localStorage.setItem(
        "travelaiChatLanguage",
        language
    );

}


/* =========================================================
   TEXTAREA
========================================================= */

function autoResizeTextarea() {

    const textarea =
        $("messageInput");


    textarea.style.height =
        "auto";


    textarea.style.height =
        Math.min(
            textarea.scrollHeight,
            150
        ) + "px";

}


/* =========================================================
   SUGGESTIONS
========================================================= */

function bindSuggestionButtons() {

    document
        .querySelectorAll(
            "[data-message]"
        )
        .forEach(
            button => {

                button.onclick =
                    () => {

                        sendMessage(
                            button.dataset.message
                        );

                    };

            }
        );

}


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        $("language").value =
            state.language;


        $("language")
            .addEventListener(
                "change",
                event => {

                    changeLanguage(
                        event.target.value
                    );

                }
            );


        $("newChat")
            .addEventListener(
                "click",
                newChat
            );


        $("chatForm")
            .addEventListener(
                "submit",
                event => {

                    event.preventDefault();

                    sendMessage(
                        $("messageInput").value
                    );

                }
            );


        $("messageInput")
            .addEventListener(
                "input",
                autoResizeTextarea
            );


        $("messageInput")
            .addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter"
                        &&
                        !event.shiftKey
                    ) {

                        event.preventDefault();

                        sendMessage(
                            $("messageInput").value
                        );

                    }

                }
            );


        bindSuggestionButtons();

        updateSessionDisplay();


        if (state.sessionId) {

            await loadHistory();

        }

    }
);

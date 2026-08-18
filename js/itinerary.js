document.addEventListener("DOMContentLoaded", function () {

    console.log("=================================");
    console.log("TRAVELMATE ITINERARY PAGE LOADED");
    console.log("=================================");

    const container =
        document.getElementById("itineraryContainer");

    const loading =
        document.getElementById("loading");

    const errorBox =
        document.getElementById("error");

    console.log("Container:", container);
    console.log("Loading:", loading);
    console.log("Error:", errorBox);

    if (!container) {
        console.error("ERROR: itineraryContainer not found.");
        return;
    }

    // ---------------------------------------------
    // GET ITINERARY
    // ---------------------------------------------

    const saved =
        localStorage.getItem("itinerary");

    console.log("Saved itinerary:", saved);

    if (!saved) {

        showError(
            "No itinerary found. Please generate your itinerary again."
        );

        return;
    }

    let itinerary;

    try {

        itinerary = JSON.parse(saved);

    } catch (error) {

        console.error(
            "Failed to parse itinerary:",
            error
        );

        showError(
            "The itinerary data is invalid. Please generate it again."
        );

        return;
    }

    console.log("Parsed itinerary:", itinerary);

    // ---------------------------------------------
    // HIDE LOADING
    // ---------------------------------------------

    if (loading) {
        loading.style.display = "none";
    }

    // ---------------------------------------------
    // RENDER
    // ---------------------------------------------

    try {

        renderItinerary(
            itinerary,
            container
        );

        console.log(
            "Itinerary rendered successfully."
        );

    } catch (error) {

        console.error(
            "Rendering error:",
            error
        );

        showError(
            "Unable to display the itinerary."
        );

        return;
    }

    // ---------------------------------------------
    // BUTTONS
    // ---------------------------------------------

    const backButton =
        document.getElementById("backToPlanner");

    const printButton =
        document.getElementById("printItinerary");

    const downloadButton =
        document.getElementById("downloadItinerary");

    if (backButton) {

        backButton.addEventListener(
            "click",
            function () {

                window.location.href =
                    "/planner.html";

            }
        );

    }

    if (printButton) {

        printButton.addEventListener(
            "click",
            function () {

                window.print();

            }
        );

    }

    if (downloadButton) {

        downloadButton.addEventListener(
            "click",
            function () {

                downloadJSON(itinerary);

            }
        );

    }

});


/* =========================================================
   RENDER ITINERARY
   ========================================================= */

function renderItinerary(
    itinerary,
    container
) {

    const currency =
        itinerary.currencySymbol || "₹";

    const destination =
        itinerary.destination ||
        "Your Destination";

    const overview =
        itinerary.destination_overview ||
        "Your personalized travel itinerary.";

    const duration =
        itinerary.duration ||
        0;

    const budget =
        itinerary.budget ||
        itinerary.estimated_total_cost ||
        0;

    const travelStyle =
        itinerary.tripStyle ||
        "Balanced";

    const travelType =
        itinerary.travelType ||
        "Solo";

    const interests =
        Array.isArray(itinerary.interests)
            ? itinerary.interests.join(", ")
            : "Not specified";


    container.innerHTML = `

        <!-- =========================================
             HERO
             ========================================= -->

        <section class="itinerary-hero">

            <div class="hero-content">

                <span class="hero-label">
                    YOUR PERSONALIZED JOURNEY
                </span>

                <h1>
                    ${escapeHtml(destination)}
                </h1>

                <p>
                    ${escapeHtml(overview)}
                </p>


                <div class="trip-summary">

                    <div class="summary-item">

                        <span class="summary-icon">
                            📅
                        </span>

                        <div>

                            <small>
                                Duration
                            </small>

                            <strong>
                                ${escapeHtml(duration)}
                                Days
                            </strong>

                        </div>

                    </div>


                    <div class="summary-item">

                        <span class="summary-icon">
                            🗓️
                        </span>

                        <div>

                            <small>
                                Travel Date
                            </small>

                            <strong>
                                ${
                                    itinerary.travel_date
                                        ? formatDate(
                                            itinerary.travel_date
                                        )
                                        : "Not specified"
                                }
                            </strong>

                        </div>

                    </div>


                    <div class="summary-item">

                        <span class="summary-icon">
                            💰
                        </span>

                        <div>

                            <small>
                                Budget
                            </small>

                            <strong>
                                ${escapeHtml(currency)}
                                ${formatNumber(budget)}
                            </strong>

                        </div>

                    </div>


                    <div class="summary-item">

                        <span class="summary-icon">
                            ✈️
                        </span>

                        <div>

                            <small>
                                Travel Style
                            </small>

                            <strong>
                                ${escapeHtml(travelStyle)}
                            </strong>

                        </div>

                    </div>

                </div>

            </div>

        </section>


        <!-- =========================================
             ACTIONS
             ========================================= -->

        <div class="itinerary-actions">

            <button
                id="backToPlanner"
                class="action-button secondary"
            >
                ← Plan Again
            </button>

            <button
                id="printItinerary"
                class="action-button"
            >
                🖨 Print
            </button>

            <button
                id="downloadItinerary"
                class="action-button"
            >
                ↓ Download
            </button>

        </div>


        <!-- =========================================
             OVERVIEW
             ========================================= -->

        <section class="overview-card">

            <div class="section-heading">

                <span class="section-icon">
                    🌍
                </span>

                <div>

                    <h2>
                        About ${escapeHtml(destination)}
                    </h2>

                    <p>
                        Your destination overview
                    </p>

                </div>

            </div>


            <p class="overview-text">
                ${escapeHtml(overview)}
            </p>

        </section>


        <!-- =========================================
             DAYS
             ========================================= -->

        <section class="days-section">

            <div class="section-title">

                <span>
                    🗺️
                </span>

                <div>

                    <h2>
                        Your Day-by-Day Plan
                    </h2>

                    <p>
                        Explore your personalized itinerary
                    </p>

                </div>

            </div>


            <div class="days-container">

                ${renderDays(
                    itinerary.days || [],
                    currency
                )}

            </div>

        </section>

    `;
}


/* =========================================================
   RENDER DAYS
   ========================================================= */

function renderDays(
    days,
    currency
) {

    if (
        !Array.isArray(days) ||
        days.length === 0
    ) {

        return `

            <div class="empty-state">

                <div>
                    🗺️
                </div>

                <h3>
                    No itinerary days available
                </h3>

                <p>
                    Please generate your itinerary again.
                </p>

            </div>

        `;
    }


    return days.map(
        function (day, index) {

            return `

                <article class="day-card">

                    <div class="day-header">

                        <div class="day-number">

                            <span>
                                DAY
                            </span>

                            <strong>
                                ${escapeHtml(
                                    day.day ||
                                    index + 1
                                )}
                            </strong>

                        </div>


                        <div class="day-title">

                            <h3>
                                ${escapeHtml(
                                    day.title ||
                                    `Day ${index + 1}`
                                )}
                            </h3>

                            ${
                                day.introduction
                                    ? `
                                        <p>
                                            ${escapeHtml(
                                                day.introduction
                                            )}
                                        </p>
                                    `
                                    : ""
                            }

                        </div>

                    </div>


                    <div class="activities">

                        ${renderActivities(
                            day.activities || [],
                            currency
                        )}

                    </div>

                </article>

            `;

        }
    ).join("");
}


/* =========================================================
   RENDER ACTIVITIES
   ========================================================= */

function renderActivities(
    activities,
    currency
) {

    if (
        !Array.isArray(activities) ||
        activities.length === 0
    ) {

        return `

            <div class="empty-activities">

                No activities available
                for this day.

            </div>

        `;
    }


    return activities.map(
        function (activity, index) {

            return `

                <div class="activity-card">

                    <div class="activity-time">

                        <span class="time-dot"></span>

                        <strong>
                            ${escapeHtml(
                                activity.time ||
                                `Activity ${index + 1}`
                            )}
                        </strong>

                    </div>


                    <div class="activity-content">

                        <div class="activity-top">

                            <div>

                                <span class="category">

                                    ${escapeHtml(
                                        activity.category ||
                                        "Activity"
                                    )}

                                </span>


                                <h4>

                                    ${escapeHtml(
                                        activity.place ||
                                        "Place"
                                    )}

                                </h4>

                            </div>


                            <div class="activity-cost">

                                ${escapeHtml(currency)}
                                ${formatNumber(
                                    activity.cost || 0
                                )}

                            </div>

                        </div>


                        <p class="activity-description">

                            ${escapeHtml(
                                activity.description ||
                                "A memorable stop during your journey."
                            )}

                        </p>


                        <div class="activity-meta">

                            ${
                                activity.duration
                                    ? `
                                        <span>
                                            ⏱
                                            ${escapeHtml(
                                                activity.duration
                                            )}
                                        </span>
                                    `
                                    : ""
                            }


                            ${
                                activity.best_time
                                    ? `
                                        <span>
                                            🌤
                                            Best:
                                            ${escapeHtml(
                                                activity.best_time
                                            )}
                                        </span>
                                    `
                                    : ""
                            }


                            ${
                                activity.popularity
                                    ? `
                                        <span>
                                            ⭐
                                            ${escapeHtml(
                                                activity.popularity
                                            )}
                                        </span>
                                    `
                                    : ""
                            }

                        </div>


                        ${
                            activity.tip
                                ? `
                                    <div class="tip-box">

                                        <span>
                                            💡
                                        </span>

                                        <div>

                                            <strong>
                                                Travel Tip
                                            </strong>

                                            <p>
                                                ${escapeHtml(
                                                    activity.tip
                                                )}
                                            </p>

                                        </div>

                                    </div>
                                `
                                : ""
                        }


                        ${
                            activity.nearby_food
                                ? `
                                    <div class="food-box">

                                        <span>
                                            🍴
                                        </span>

                                        <div>

                                            <strong>
                                                Nearby Food
                                            </strong>

                                            <p>
                                                ${escapeHtml(
                                                    activity.nearby_food
                                                )}
                                            </p>

                                        </div>

                                    </div>
                                `
                                : ""
                        }

                    </div>

                </div>

            `;

        }
    ).join("");
}


/* =========================================================
   FORMAT DATE
   ========================================================= */

function formatDate(dateString) {

    if (!dateString) {
        return "";
    }

    const date =
        new Date(dateString);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return dateString;

    }

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "numeric",
            month: "short",
            year: "numeric"
        }
    );
}


/* =========================================================
   FORMAT NUMBER
   ========================================================= */

function formatNumber(value) {

    const number =
        Number(value);

    if (
        Number.isNaN(number)
    ) {

        return "0";

    }

    return number.toLocaleString(
        "en-IN"
    );
}


/* =========================================================
   DOWNLOAD JSON
   ========================================================= */

function downloadJSON(itinerary) {

    const json =
        JSON.stringify(
            itinerary,
            null,
            2
        );

    const blob =
        new Blob(
            [json],
            {
                type: "application/json"
            }
        );

    const url =
        URL.createObjectURL(
            blob
        );

    const link =
        document.createElement("a");

    link.href = url;

    link.download =
        `${itinerary.destination || "travelmate"}-itinerary.json`;

    document.body.appendChild(link);

    link.click();

    link.remove();

    URL.revokeObjectURL(url);
}


/* =========================================================
   ERROR
   ========================================================= */

function showError(message) {

    const loading =
        document.getElementById("loading");

    const errorBox =
        document.getElementById("error");

    if (loading) {

        loading.style.display =
            "none";

    }

    if (errorBox) {

        errorBox.classList.remove(
            "hidden"
        );

        errorBox.innerHTML = `

            <div class="error-icon">
                ⚠️
            </div>

            <h2>
                Something went wrong
            </h2>

            <p>
                ${escapeHtml(message)}
            </p>

            <button
                onclick="window.location.href='/planner.html'"
                class="action-button"
            >
                ← Back to Planner
            </button>

        `;

    }
}


/* =========================================================
   HTML ESCAPE
   ========================================================= */

function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,
        function (character) {

            return {

                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"

            }[character];

        }
    );
}
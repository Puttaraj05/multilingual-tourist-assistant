document.addEventListener("DOMContentLoaded", () => {

    console.log("=================================");
    console.log("TRAVELMATE ITINERARY LOADED");
    console.log("=================================");


    // =====================================================
    // LOAD ITINERARY
    // =====================================================

    const saved =
        localStorage.getItem("itinerary");


    if (!saved) {

        alert(
            "No itinerary found. Please generate your itinerary again."
        );

        window.location.href =
            "/planner.html";

        return;
    }


    let itinerary;


    try {

        itinerary =
            JSON.parse(saved);

    } catch (error) {

        console.error(
            "Invalid itinerary:",
            error
        );

        alert(
            "Invalid itinerary data. Please generate it again."
        );

        window.location.href =
            "/planner.html";

        return;
    }


    console.log(
        "Loaded itinerary:",
        itinerary
    );


    // =====================================================
    // RENDER
    // =====================================================

    renderItinerary(itinerary);


    // =====================================================
    // SAVE BUTTON
    // =====================================================

    const saveButton =
        document.getElementById("saveButton");


    if (saveButton) {

        saveButton.addEventListener(
            "click",
            () => {

                localStorage.setItem(
                    "savedItinerary",
                    JSON.stringify(itinerary)
                );

                saveButton.textContent =
                    "✓ Itinerary Saved";

                setTimeout(() => {

                    saveButton.textContent =
                        "Save Itinerary";

                }, 2000);

            }
        );

    }

});


// =========================================================
// MAIN RENDER FUNCTION
// =========================================================

function renderItinerary(itinerary) {

    console.log(
        "Rendering itinerary..."
    );


    // =====================================================
    // DESTINATION
    // =====================================================

    const destination =
        itinerary.destination ||
        "Your Destination";


    document.getElementById(
        "destinationTitle"
    ).textContent =
        destination;


    document.getElementById(
        "destinationSubtitle"
    ).textContent =
        `${itinerary.duration || 0}-Day Personalized Travel Plan`;


    // =====================================================
    // TRIP SUMMARY
    // =====================================================

    document.getElementById(
        "summaryDestination"
    ).textContent =
        destination;


    document.getElementById(
        "summaryDuration"
    ).textContent =
        `${itinerary.duration || 0} Days`;


    document.getElementById(
        "summaryDate"
    ).textContent =
        formatDate(
            itinerary.travel_date
        );


    const currency =
        itinerary.currencySymbol ||
        "₹";


    const budget =
        itinerary.budget;


    document.getElementById(
        "summaryBudget"
    ).textContent =
        budget
            ? `${currency}${Number(budget).toLocaleString()}`
            : "Not specified";


    document.getElementById(
        "summaryTravelType"
    ).textContent =
        itinerary.travelType ||
        "Solo";


    document.getElementById(
        "summaryTripStyle"
    ).textContent =
        itinerary.tripStyle ||
        "Balanced";


    // =====================================================
    // DESTINATION OVERVIEW
    // =====================================================

    document.getElementById(
        "destinationOverview"
    ).textContent =
        itinerary.destination_overview ||
        "No destination overview was provided.";


    // =====================================================
    // DAYS
    // =====================================================

    renderDays(
        itinerary.days || [],
        currency
    );


    // =====================================================
    // TOTAL COST
    // =====================================================

    const totalCost =
        itinerary.estimated_total_cost;


    document.getElementById(
        "totalCost"
    ).textContent =
        totalCost !== undefined
            ? `${currency}${Number(totalCost).toLocaleString()}`
            : "Not available";

}


// =========================================================
// RENDER DAYS
// =========================================================

function renderDays(days, currency) {

    const container =
        document.getElementById(
            "daysContainer"
        );


    container.innerHTML = "";


    if (!days.length) {

        container.innerHTML = `
            <div class="empty-itinerary">
                <h3>No daily itinerary available</h3>
                <p>Please generate your itinerary again.</p>
            </div>
        `;

        return;
    }


    days.forEach(
        (day, index) => {

            const dayNumber =
                day.day ||
                index + 1;


            const daySection =
                document.createElement("section");


            daySection.className =
                "day-section";


            daySection.innerHTML = `

                <div class="day-header">

                    <div class="day-number">

                        <span>DAY</span>

                        <strong>
                            ${dayNumber}
                        </strong>

                    </div>


                    <div class="day-heading">

                        <h3>
                            ${escapeHTML(
                                day.title ||
                                `Day ${dayNumber}`
                            )}
                        </h3>

                        <p>
                            ${escapeHTML(
                                day.introduction ||
                                ""
                            )}
                        </p>

                    </div>

                </div>


                <div class="activities-container">

                    ${
                        renderActivities(
                            day.activities || [],
                            currency
                        )
                    }

                </div>

            `;


            container.appendChild(
                daySection
            );

        }
    );

}


// =========================================================
// RENDER ACTIVITIES
// =========================================================

function renderActivities(
    activities,
    currency
) {

    if (!activities.length) {

        return `
            <div class="empty-activities">
                No activities available for this day.
            </div>
        `;

    }


    return activities.map(
        activity => {

            const cost =
                activity.cost !== undefined
                    ? `${currency}${Number(
                        activity.cost
                    ).toLocaleString()}`
                    : "Free";


            return `

                <article class="activity-card">

                    <div class="activity-time">

                        <strong>
                            ${escapeHTML(
                                activity.time ||
                                ""
                            )}
                        </strong>

                    </div>


                    <div class="activity-content">

                        <div class="activity-top">

                            <div>

                                <span class="activity-category">

                                    ${escapeHTML(
                                        activity.category ||
                                        "Activity"
                                    )}

                                </span>


                                <h4>

                                    ${escapeHTML(
                                        activity.place ||
                                        "Tourist Attraction"
                                    )}

                                </h4>

                            </div>


                            <div class="activity-cost">

                                ${cost}

                            </div>

                        </div>


                        <p class="activity-description">

                            ${escapeHTML(
                                activity.description ||
                                ""
                            )}

                        </p>


                        <div class="activity-details">

                            ${
                                activity.duration
                                    ? `
                                    <span>
                                        ⏱ ${escapeHTML(
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
                                        🌤 ${escapeHTML(
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
                                        ⭐ ${escapeHTML(
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
                                <div class="activity-tip">

                                    <strong>
                                        💡 Tip
                                    </strong>

                                    <span>
                                        ${escapeHTML(
                                            activity.tip
                                        )}
                                    </span>

                                </div>
                                `
                                : ""
                        }


                        ${
                            activity.nearby_food
                                ? `
                                <div class="activity-food">

                                    <strong>
                                        🍴 Nearby Food
                                    </strong>

                                    <span>
                                        ${escapeHTML(
                                            activity.nearby_food
                                        )}
                                    </span>

                                </div>
                                `
                                : ""
                        }

                    </div>

                </article>

            `;

        }
    ).join("");

}


// =========================================================
// DATE FORMAT
// =========================================================

function formatDate(dateString) {

    if (!dateString) {
        return "Not specified";
    }


    const date =
        new Date(dateString);


    if (isNaN(date.getTime())) {
        return dateString;
    }


    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );

}


// =========================================================
// HTML SAFETY
// =========================================================

function escapeHTML(value) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}
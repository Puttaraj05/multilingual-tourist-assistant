const saved = localStorage.getItem("itinerary");

if (!saved) {
    window.location.href = "planner.html";
}

const itinerary = JSON.parse(saved);

// -----------------------------
// Helper
// -----------------------------

const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
};

// -----------------------------
// UI Labels
// -----------------------------

const labels = {
    English: {
        plan: "YOUR PERSONALIZED PLAN",
        duration: "Duration",
        budget: "Budget",
        interests: "Interests",
        travelType: "Travel Type",
        tripStyle: "Trip Style",
        kids: "Child Under 12",
        modify: "Modify Trip",
        save: "Save Itinerary"
    }
};

const language = itinerary.language || "English";
const ui = labels[language] || labels.English;

// -----------------------------
// Static Labels
// -----------------------------

setText("planLabel", ui.plan);
setText("durationLabel", ui.duration);
setText("budgetLabel", ui.budget);
setText("interestsLabel", ui.interests);
setText("travelTypeLabel", ui.travelType);
setText("tripStyleLabel", ui.tripStyle);
setText("kidsLabel", ui.kids);
setText("modifyLabel", ui.modify);
setText("saveButton", ui.save);

// -----------------------------
// Hero
// -----------------------------

setText("destinationTitle", itinerary.destination || "Your Destination");

setText(
    "destinationOverview",
    itinerary.destination_overview ||
        `Discover the best of ${itinerary.destination} with a personalized AI-powered itinerary.`
);

// -----------------------------
// Summary
// -----------------------------

setText("summaryDuration", `${itinerary.duration} Days`);

setText(
    "summaryBudget",
    `${itinerary.currencySymbol || "$"}${Number(
        itinerary.budget || 0
    ).toLocaleString()}`
);

setText("summaryTravelType", itinerary.travelType || "Solo");
setText("summaryTripStyle", itinerary.tripStyle || "Balanced");
setText("summaryKids", itinerary.kidsUnder12 ? "Yes" : "No");

setText(
    "summaryInterests",
    (itinerary.interests || []).join(", ")
);

// -----------------------------
// Build Itinerary
// -----------------------------

const container = document.getElementById("itineraryContent");
container.innerHTML = "";

(itinerary.days || []).forEach(day => {

    const section = document.createElement("section");
    section.className = "day-section";

    let activitiesHTML = "";

    (day.activities || []).forEach(activity => {

        const mapUrl =
            `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                activity.place + " " + itinerary.destination
            )}`;

        activitiesHTML += `

        <div class="activity-card">

            <div class="activity-top">

                <div>
                    <p class="activity-time">${activity.time || "Flexible"}</p>
                    <h3>${activity.place || "Destination"}</h3>
                </div>

                <span class="popularity-badge">
                    ${activity.popularity || "Recommended"}
                </span>

            </div>

            <p class="activity-description">
                ${activity.description || "A must-visit stop during your journey."}
            </p>

            <div class="activity-meta">

                <span>${activity.category || "Sightseeing"}</span>

                <span>•</span>

                <span>${activity.duration || "1-2 hrs"}</span>

                <span>•</span>

                <span>${itinerary.currencySymbol || "$"}${activity.cost ?? "-"}</span>

            </div>

            <div class="activity-extra">

                <div class="activity-info">
                    <strong>Best Time:</strong>
                    ${activity.best_time || "Morning or Evening"}
                </div>

                <div class="activity-info">
                    <strong>Travel Tip:</strong>
                    ${activity.tip || "Arrive early to avoid crowds."}
                </div>

                ${
                    activity.nearby_food
                        ? `
                        <div class="activity-info">
                            <strong>Nearby Food:</strong>
                            ${activity.nearby_food}
                        </div>
                        `
                        : ""
                }

            </div>

            <a
                href="${mapUrl}"
                target="_blank"
                rel="noopener noreferrer"
                class="map-button"
            >
                View on Map
            </a>

        </div>

        `;
    });

    section.innerHTML = `

        <div class="day-header">

            <div class="day-circle">
                ${String(day.day).padStart(2, "0")}
            </div>

            <div>
                <p class="day-label">DAY ${day.day}</p>
                <h2>${day.title || `Day ${day.day}`}</h2>
            </div>

        </div>

        <p class="day-introduction">
            ${
                day.introduction ||
                `Enjoy a memorable day exploring ${itinerary.destination}.`
            }
        </p>

        <div class="activities-container">
            ${activitiesHTML}
        </div>

    `;

    container.appendChild(section);
});

// -----------------------------
// Save Itinerary
// -----------------------------

const saveButton = document.getElementById("saveButton");

if (saveButton) {

    saveButton.addEventListener("click", () => {

        const blob = new Blob(
            [JSON.stringify(itinerary, null, 2)],
            { type: "application/json" }
        );

        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `${itinerary.destination}-itinerary.json`;

        a.click();

        URL.revokeObjectURL(url);

    });

}
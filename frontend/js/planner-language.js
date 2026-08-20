const defaultLabels = {
    title: "PLAN YOUR JOURNEY",
    subtitle: "Tell us a little about your trip",
    languageLabel: "Language",
    destination: "Destination",
    duration: "Trip Duration",
    date: "Travel Date",
    budget: "Budget",
    interests: "Interests",
    continue: "Generate My Itinerary",

    travelType: "Who's Travelling?",
    kids: "Travelling with a Child Under 12?",
    tripStyle: "Trip Style",

    relaxed: "Relaxed",
    balanced: "Balanced",
    packed: "Packed"
};

const languageInput = document.getElementById("language");

// -----------------------------
// Apply Labels
// -----------------------------

function applyLabels(labels) {

    document.querySelectorAll("[data-key]").forEach(el => {

        const key = el.dataset.key;

        if (labels[key]) {
            el.textContent = labels[key];
        }

    });

    document.body.dir =
        languageInput.value.toLowerCase() === "arabic"
            ? "rtl"
            : "ltr";
}

// -----------------------------
// Translate UI
// -----------------------------

async function translateUI(language) {

    if (!language || language.toLowerCase() === "english") {
        applyLabels(defaultLabels);
        return;
    }

    try {

        const response = await fetch(
            "/api/ui-translate",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    language,
                    labels: defaultLabels
                })
            }
        );

        const translated = await response.json();

        applyLabels(translated);

    } catch (err) {

        console.error("Translation failed:", err);

        applyLabels(defaultLabels);

    }

}

// -----------------------------
// Listen for Language Changes
// -----------------------------

languageInput.addEventListener("change", () => {
    translateUI(languageInput.value);
});

// Initial Load
translateUI("English");
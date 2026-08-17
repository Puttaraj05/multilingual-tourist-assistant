const defaultText = {

    title: "PLAN YOUR JOURNEY",

    subtitle: "Tell us a little about your trip",

    languageLabel: "Language",

    destination: "Destination",

    duration: "Trip Duration",

    date: "Travel Date",

    budget: "Budget (INR)",

    interests: "Interests",

    continue: "Generate My Itinerary"

};

const languageInput = document.getElementById("language");

async function changeLanguage(lang) {

    let translated = defaultText;

    if (lang.toLowerCase() !== "english") {

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/api/ui-translate",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        language: lang,
                        labels: defaultText
                    })
                }
            );

            translated = await response.json();

        } catch (error) {

            console.error("Translation failed:", error);

            translated = defaultText;
        }

    }

    document.querySelectorAll("[data-key]").forEach(el => {

        const key = el.dataset.key;

        if (translated[key]) {
            el.textContent = translated[key];
        }

    });

    document.body.dir =
        lang.toLowerCase() === "arabic"
            ? "rtl"
            : "ltr";

}

languageInput.addEventListener("change", e => {

    changeLanguage(e.target.value);

});

changeLanguage("English");
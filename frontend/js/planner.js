const form = document.getElementById("plannerForm");

const durationInput = document.getElementById("duration");
const decreaseButton = document.getElementById("decreaseDays");
const increaseButton = document.getElementById("increaseDays");

// =============================================
// DURATION BUTTONS
// =============================================

decreaseButton.addEventListener("click", () => {
    let days = parseInt(durationInput.value);

    if (days > 1) {
        durationInput.value = days - 1;
    }
});

increaseButton.addEventListener("click", () => {
    let days = parseInt(durationInput.value);

    if (days < 30) {
        durationInput.value = days + 1;
    }
});


// =============================================
// FORM SUBMIT
// =============================================

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const destination =
        document.getElementById("destination").value.trim();

    const duration =
        parseInt(durationInput.value);

    const travelDate =
        document.getElementById("travelDate").value;

    const budget =
        Number(document.getElementById("budget").value);

    const currencySymbol =
        document.getElementById("currency").value;

    const language =
        document.getElementById("language").value.trim();

    const travelType =
        document.querySelector(
            'input[name="travelType"]:checked'
        )?.value || "Solo";

    const tripStyle =
        document.querySelector(
            'input[name="tripStyle"]:checked'
        )?.value || "Balanced";

    const kidsUnder12 =
        document.getElementById("kidsUnder12").checked;

    const interests = [];

    document
        .querySelectorAll('input[name="interest"]:checked')
        .forEach((item) => {
            interests.push(item.value);
        });


    // =============================================
    // VALIDATION
    // =============================================

    if (!destination) {
        alert("Please enter a destination.");
        return;
    }

    if (!travelDate) {
        alert("Please select a travel date.");
        return;
    }

    if (budget <= 0) {
        alert("Please enter a valid budget.");
        return;
    }

    if (interests.length === 0) {
        alert("Please select at least one interest.");
        return;
    }


    // =============================================
    // REQUEST DATA
    // =============================================

    const tripData = {
        destination: destination,
        duration: duration,
        travelDate: travelDate,
        budget: budget,
        currencySymbol: currencySymbol,
        language: language,
        travelType: travelType,
        tripStyle: tripStyle,
        kidsUnder12: kidsUnder12,
        interests: interests
    };


    console.log("Sending itinerary request:", tripData);


    const button =
        document.querySelector(".generate-button");

    button.disabled = true;
    button.textContent =
        "Generating your itinerary...";


    // =============================================
    // CALL FASTAPI
    // =============================================

    try {

        const response = await fetch(
            "/api/itinerary",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(tripData)
            }
        );


        const result =
            await response.json();


        console.log(
            "Itinerary API response:",
            result
        );


        if (!response.ok) {

            throw new Error(
                result.detail ||
                result.error ||
                "Unable to generate itinerary."
            );

        }


        // =============================================
        // PRESERVE USER INPUTS
        // =============================================

        result.destination =
            destination;

        result.currencySymbol =
            currencySymbol;

        result.travelType =
            travelType;

        result.tripStyle =
            tripStyle;

        result.kidsUnder12 =
            kidsUnder12;

        result.interests =
            interests;

        result.duration =
            duration;

        result.travel_date =
            travelDate;

        result.budget =
            result.budget || budget;


        // =============================================
        // SAVE ITINERARY
        // =============================================

        localStorage.setItem(
            "itinerary",
            JSON.stringify(result)
        );


        // =============================================
        // OPEN ITINERARY PAGE
        // =============================================

        window.location.href =
            "/itinerary.html";


    } catch (error) {

        console.error(
            "Itinerary error:",
            error
        );

        alert(
            error.message ||
            "Unable to generate itinerary."
        );

        button.disabled = false;

        button.textContent =
            "Generate My Itinerary";

    }

});
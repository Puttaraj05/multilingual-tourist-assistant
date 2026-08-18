const form = document.getElementById("plannerForm");

const durationInput = document.getElementById("duration");
const decreaseButton = document.getElementById("decreaseDays");
const increaseButton = document.getElementById("increaseDays");

// -----------------------------
// Duration Buttons
// -----------------------------

decreaseButton.addEventListener("click", () => {
    let days = parseInt(durationInput.value);
    if (days > 1) durationInput.value = days - 1;
});

increaseButton.addEventListener("click", () => {
    let days = parseInt(durationInput.value);
    if (days < 30) durationInput.value = days + 1;
});

// -----------------------------
// Form Submit
// -----------------------------

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const destination = document.getElementById("destination").value.trim();
    const duration = parseInt(durationInput.value);
    const travelDate = document.getElementById("travelDate").value;

    const budget = Number(document.getElementById("budget").value);
    const currencySymbol = document.getElementById("currency").value;

    const language = document.getElementById("language").value;

    const travelType =
        document.querySelector('input[name="travelType"]:checked').value;

    const tripStyle =
        document.querySelector('input[name="tripStyle"]:checked').value;

    const kidsUnder12 =
        document.getElementById("kidsUnder12").checked;

    const interests = [];

    document
        .querySelectorAll('input[name="interest"]:checked')
        .forEach(item => interests.push(item.value));

    // Basic validation

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

    const tripData = {

        destination,
        duration,
        travelDate,

        budget,
        currencySymbol,

        language,

        travelType,
        tripStyle,
        kidsUnder12,

        interests

    };

    const button = document.querySelector(".generate-button");

    button.disabled = true;
    button.innerHTML = "Generating your itinerary...";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/itinerary",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(tripData)
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Something went wrong.");
        }

        // Preserve frontend values

        result.destination = destination;
        result.currencySymbol = currencySymbol;
        result.travelType = travelType;
        result.tripStyle = tripStyle;
        result.kidsUnder12 = kidsUnder12;

        localStorage.setItem(
            "itinerary",
            JSON.stringify(result)
        );

        window.location.href = "itinerary.html";

    } catch (err) {

        console.error(err);

        alert(err.message || "Unable to generate itinerary.");

        button.disabled = false;

        button.innerHTML =
            '<span data-key="continue">Generate My Itinerary</span>';

    }

});
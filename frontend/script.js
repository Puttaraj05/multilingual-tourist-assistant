const API_URL =
    "http://127.0.0.1:8000/api/recommendations";


const nearMeBtn =
    document.getElementById("nearMeBtn");

const searchLocationBtn =
    document.getElementById("searchLocationBtn");

const categorySelect =
    document.getElementById("category");

const radiusSelect =
    document.getElementById("radius");

const locationInput =
    document.getElementById("locationInput");

const statusText =
    document.getElementById("status");

const coordinatesDiv =
    document.getElementById("coordinates");

const resultsDiv =
    document.getElementById("results");


// ==========================================
// OPTION 1: NEAR ME
// ==========================================

nearMeBtn.addEventListener(
    "click",
    getNearMe
);


function getNearMe() {

    if (!navigator.geolocation) {

        statusText.textContent =
            "Geolocation is not supported by your browser.";

        return;
    }


    statusText.textContent =
        "Getting your current location...";

    clearResults();


    navigator.geolocation.getCurrentPosition(

        locationSuccess,

        locationError,

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}


function locationSuccess(position) {

    const latitude =
        position.coords.latitude;

    const longitude =
        position.coords.longitude;


    coordinatesDiv.innerHTML = `
        <strong>📍 Your Current Location</strong><br>
        Latitude: ${latitude}<br>
        Longitude: ${longitude}
    `;


    const requestData = {
        latitude: latitude,
        longitude: longitude,
        category: categorySelect.value,
        radius: Number(radiusSelect.value),
        max_results: 5
    };


    getRecommendations(
        requestData,
        "Finding nearby places..."
    );
}


function locationError(error) {

    const errors = {
        1: "Location permission was denied.",
        2: "Location information is unavailable.",
        3: "Location request timed out."
    };


    statusText.textContent =
        errors[error.code]
        || "Unable to get your location.";
}


// ==========================================
// OPTION 2: SEARCH NEAR A PLACE
// ==========================================

searchLocationBtn.addEventListener(
    "click",
    searchNearLocation
);


function searchNearLocation() {

    const location =
        locationInput.value.trim();


    if (!location) {

        statusText.textContent =
            "Please enter a location such as Hyderabad, Charminar or Kompally.";

        return;
    }


    clearResults();


    const requestData = {
        location: location,
        category: categorySelect.value,
        radius: Number(radiusSelect.value),
        max_results: 5
    };


    getRecommendations(
        requestData,
        "Searching near " + location + "..."
    );
}


// ==========================================
// CALL BACKEND API
// ==========================================

async function getRecommendations(
    requestData,
    loadingMessage
) {

    statusText.textContent =
        loadingMessage;


    try {

        const response =
            await fetch(
                API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        requestData
                    )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            statusText.textContent =
                "Error: "
                + (
                    data.detail
                    || "Unable to get recommendations."
                );

            return;
        }


        coordinatesDiv.innerHTML = `
            <strong>📍 Search Location</strong><br>
            ${data.search_location || "Near Me"}<br>
            Latitude: ${data.search_latitude}<br>
            Longitude: ${data.search_longitude}
        `;


        statusText.textContent =
            `Found ${data.count} nearby places.`;


        displayResults(
            data.recommendations
        );

    }
    catch (error) {

        console.error(error);

        statusText.textContent =
            "Cannot connect to the backend server.";
    }
}


// ==========================================
// DISPLAY RESULTS
// ==========================================

function displayResults(recommendations) {

    resultsDiv.innerHTML = "";


    if (
        !recommendations
        || recommendations.length === 0
    ) {

        resultsDiv.innerHTML =
            "<p>No matching places found nearby.</p>";

        return;
    }


    recommendations.forEach(
        (place) => {

            const placeDiv =
                document.createElement("div");

            placeDiv.className =
                "place";


            placeDiv.innerHTML = `

                <h3>${place.name}</h3>

                <p>
                    <strong>Category:</strong>
                    ${place.category}
                </p>

                <p>
                    <strong>Distance:</strong>
                    ${place.distance_km} km
                </p>

                <p>
                    <strong>Address:</strong>
                    ${place.address || "Not available"}
                </p>

                ${
                    place.rating
                    ? `
                    <p>
                        <strong>Rating:</strong>
                        ${place.rating}
                    </p>
                    `
                    : ""
                }

                <a
                    href="${place.navigation_url}"
                    target="_blank"
                    class="navigate-btn"
                >
                    🗺 Navigate with Google Maps
                </a>

            `;


            resultsDiv.appendChild(
                placeDiv
            );
        }
    );
}


// ==========================================
// CLEAR OLD RESULTS
// ==========================================

function clearResults() {

    resultsDiv.innerHTML = "";
    coordinatesDiv.innerHTML = "";
}
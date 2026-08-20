const resultsGrid = document.getElementById("resultsGrid");
const resultCount = document.getElementById("resultCount");

const searchLocation = document.getElementById("searchLocation");
const nearMeBtn = document.getElementById("nearMeBtn");
const searchBtn = document.getElementById("searchBtn");

const categoryFilter = document.getElementById("categoryFilter");
const distanceFilter = document.getElementById("distanceFilter");

const API_URL = "/api/recommendations";


// =====================================================
// CONFIGURATION
// =====================================================

const MAX_RESULTS = 10;


// =====================================================
// CATEGORY ICONS
// =====================================================

const categoryIcons = {

    restaurant: "fa-utensils",

    hotel: "fa-hotel",

    cafe: "fa-mug-hot",

    attraction: "fa-landmark",

    shopping: "fa-bag-shopping",

    museum: "fa-building-columns",

    park: "fa-tree",

    hostel: "fa-bed",

    supermarket: "fa-cart-shopping",

    hospital: "fa-hospital",

    pharmacy: "fa-pills",

    bank: "fa-building-columns",

    atm: "fa-credit-card",

    fuel: "fa-gas-pump",

    parking: "fa-square-parking",

    fast_food: "fa-burger",

    guest_house: "fa-house",

    all: "fa-location-dot"

};


// =====================================================
// LOAD RECOMMENDATIONS
// =====================================================

async function loadRecommendations(options = {}) {

    // -------------------------------------------------
    // LOADING STATE
    // -------------------------------------------------

    resultsGrid.innerHTML = `

        <div class="recommend-loading">

            <div class="loading-icon">

                <i class="fa-solid fa-spinner fa-spin"></i>

            </div>

            <h3>
                Finding places for you...
            </h3>

            <p>
                Searching nearby recommendations.
            </p>

        </div>

    `;

    resultCount.textContent = "Searching...";


    // -------------------------------------------------
    // CATEGORY
    // -------------------------------------------------

    const selectedCategory =
        categoryFilter.value === "all"
            ? "all"
            : categoryFilter.value;


    // -------------------------------------------------
    // RADIUS
    // -------------------------------------------------

    const radius =
        Number(distanceFilter.value);


    // -------------------------------------------------
    // LOCATION
    // -------------------------------------------------

    const typedLocation =
        searchLocation.value.trim();


    let locationValue = null;


    if (
        options.location !== undefined
    ) {

        locationValue =
            options.location;

    } else {

        locationValue =
            typedLocation || null;

    }


    // -------------------------------------------------
    // PAYLOAD
    // -------------------------------------------------

    const payload = {

        latitude:
            options.latitude ?? null,

        longitude:
            options.longitude ?? null,

        location:
            locationValue,

        category:
            selectedCategory,

        radius:
            radius,

        max_results:
            MAX_RESULTS

    };


    console.log(
        "Recommendation request:",
        payload
    );


    // -------------------------------------------------
    // API REQUEST
    // -------------------------------------------------

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

                    body:
                        JSON.stringify(payload)
                }
            );


        // -------------------------------------------------
        // RESPONSE
        // -------------------------------------------------

        let data;


        try {

            data =
                await response.json();

        } catch {

            throw new Error(
                "Invalid response received from server."
            );

        }


        // -------------------------------------------------
        // API ERROR
        // -------------------------------------------------

        if (!response.ok) {

            let errorMessage =
                "Unable to fetch recommendations.";


            if (data.detail) {

                if (
                    Array.isArray(
                        data.detail
                    )
                ) {

                    errorMessage =
                        data.detail
                            .map(
                                error =>
                                    error.msg ||
                                    String(error)
                            )
                            .join(", ");

                } else {

                    errorMessage =
                        String(
                            data.detail
                        );

                }

            }


            throw new Error(
                errorMessage
            );

        }


        console.log(
            "Recommendation response:",
            data
        );


        // -------------------------------------------------
        // RENDER RESULTS
        // -------------------------------------------------

        renderRecommendations(
            data
        );


    } catch (error) {

        console.error(
            "Recommendation error:",
            error
        );


        resultCount.textContent =
            "Unable to load";


        resultsGrid.innerHTML = `

            <div class="recommend-error">

                <div class="error-icon">

                    <i class="fa-solid fa-circle-exclamation"></i>

                </div>

                <h3>
                    Could not load recommendations
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

                <button
                    class="retry-btn"
                    onclick="loadRecommendations()"
                >

                    <i class="fa-solid fa-rotate-right"></i>

                    Try Again

                </button>

            </div>

        `;

    }

}


// =====================================================
// RENDER RESULTS
// =====================================================

function renderRecommendations(data) {

    let places =
        data.recommendations ||
        data.results ||
        data.places ||
        [];


    // -------------------------------------------------
    // MAXIMUM 10 RESULTS
    // -------------------------------------------------

    places =
        Array.isArray(places)
            ? places.slice(
                0,
                MAX_RESULTS
            )
            : [];


    // -------------------------------------------------
    // RESULT COUNT
    // -------------------------------------------------

    resultCount.textContent =
        `${places.length} places found`;


    // -------------------------------------------------
    // EMPTY RESULTS
    // -------------------------------------------------

    if (!places.length) {

        resultsGrid.innerHTML = `

            <div class="recommend-empty">

                <div class="empty-icon">

                    <i class="fa-solid fa-map-location-dot"></i>

                </div>

                <h3>
                    No places found
                </h3>

                <p>
                    Try increasing the search radius
                    or selecting another category.
                </p>

            </div>

        `;

        return;

    }


    // -------------------------------------------------
    // CLEAR OLD RESULTS
    // -------------------------------------------------

    resultsGrid.innerHTML = "";


    // -------------------------------------------------
    // CREATE CARDS
    // -------------------------------------------------

    places.forEach(
        (place, index) => {

            resultsGrid.insertAdjacentHTML(
                "beforeend",

                createRecommendationCard(
                    place,
                    index
                )
            );

        }
    );

}


// =====================================================
// CREATE RECOMMENDATION CARD
// =====================================================

function createRecommendationCard(
    place,
    index
) {

    const name =
        place.name ||
        place.title ||
        "Unnamed Place";


    const category =
        place.category ||
        place.type ||
        "place";


    const normalizedCategory =
        String(category)
            .toLowerCase()
            .replaceAll(
                " ",
                "_"
            );


    const rating =
        place.rating ??
        place.score ??
        null;


    const distance =
        place.distance_km ??
        place.distance ??
        null;


    const address =
        place.address ||
        place.location ||
        "Address unavailable";


    const description =
        place.description ||
        "A recommended place worth exploring.";


    // -------------------------------------------------
    // ICON
    // -------------------------------------------------

    const icon =
        categoryIcons[
            normalizedCategory
        ] ||
        "fa-location-dot";


    // -------------------------------------------------
    // MAP / NAVIGATION URL
    // -------------------------------------------------

    const navigationUrl =
        place.navigation_url ||
        place.maps_url ||
        place.google_maps_url ||
        createMapsUrl(
            name,
            address
        );


    // -------------------------------------------------
    // RATING
    // -------------------------------------------------

    let ratingHtml = "";


    if (
        rating !== null &&
        rating !== undefined &&
        rating !== ""
    ) {

        ratingHtml = `

            <div class="recommend-rating">

                <i class="fa-solid fa-star"></i>

                <strong>
                    ${escapeHtml(
                        String(rating)
                    )}
                </strong>

            </div>

        `;

    }


    // -------------------------------------------------
    // DISTANCE
    // -------------------------------------------------

    let distanceHtml = "";


    if (
        distance !== null &&
        distance !== undefined &&
        distance !== ""
    ) {

        distanceHtml = `

            <div class="recommend-distance">

                <i class="fa-solid fa-route"></i>

                <span>
                    ${formatDistance(
                        distance
                    )}
                </span>

            </div>

        `;

    }


    // -------------------------------------------------
    // OPENING HOURS
    // -------------------------------------------------

    let openingHoursHtml = "";


    if (
        place.opening_time ||
        place.closing_time
    ) {

        const opening =
            place.opening_time ||
            "--";


        const closing =
            place.closing_time ||
            "--";


        openingHoursHtml = `

            <div class="recommend-hours">

                <i class="fa-regular fa-clock"></i>

                <span>

                    ${escapeHtml(
                        opening
                    )}

                    -

                    ${escapeHtml(
                        closing
                    )}

                </span>

            </div>

        `;

    }


    // -------------------------------------------------
    // SOURCE / DETAILS
    // -------------------------------------------------

    let sourceHtml = "";


    if (
        place.source_url
    ) {

        sourceHtml = `

            <a
                href="${escapeAttribute(
                    place.source_url
                )}"
                target="_blank"
                rel="noopener noreferrer"
                class="source-link"
            >

                <i class="fa-solid fa-arrow-up-right-from-square"></i>

                Details

            </a>

        `;

    }


    // -------------------------------------------------
    // CARD
    // -------------------------------------------------

    return `

        <article
            class="recommend-card"
            data-category="${escapeAttribute(
                normalizedCategory
            )}"
        >

            <!-- CARD TOP -->

            <div class="recommend-card-top">

                <div class="recommend-icon">

                    <i
                        class="fa-solid ${icon}"
                    ></i>

                </div>


                <span class="recommend-badge">

                    ${escapeHtml(
                        formatCategory(
                            category
                        )
                    )}

                </span>


                <span class="recommend-number">

                    #${index + 1}

                </span>

            </div>


            <!-- CARD CONTENT -->

            <div class="recommend-content">

                <div class="recommend-title-row">

                    <h3 class="recommend-title">

                        ${escapeHtml(
                            name
                        )}

                    </h3>

                    ${ratingHtml}

                </div>


                <!-- ADDRESS -->

                <div class="recommend-address">

                    <i class="fa-solid fa-location-dot"></i>

                    <span>

                        ${escapeHtml(
                            address
                        )}

                    </span>

                </div>


                <!-- DESCRIPTION -->

                <p class="recommend-description">

                    ${escapeHtml(
                        description
                    )}

                </p>


                <!-- META -->

                <div class="recommend-meta">

                    ${distanceHtml}

                    ${openingHoursHtml}

                </div>


                <!-- ACTIONS -->

                <div class="recommend-actions">

                    <a
                        href="${escapeAttribute(
                            navigationUrl
                        )}"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="map-btn"
                    >

                        <i class="fa-solid fa-map-location-dot"></i>

                        View Map

                    </a>


                    ${sourceHtml}

                </div>

            </div>

        </article>

    `;

}


// =====================================================
// SEARCH BY LOCATION
// =====================================================

searchBtn.addEventListener(
    "click",

    async () => {

        const location =
            searchLocation.value.trim();


        if (!location) {

            alert(
                "Please enter a city or destination."
            );


            searchLocation.focus();


            return;

        }


        await loadRecommendations({

            location:
                location,

            latitude:
                null,

            longitude:
                null

        });

    }
);


// =====================================================
// ENTER KEY SEARCH
// =====================================================

searchLocation.addEventListener(
    "keydown",

    event => {

        if (
            event.key === "Enter"
        ) {

            event.preventDefault();

            searchBtn.click();

        }

    }
);

// =====================================================
// CATEGORY FILTER
// =====================================================

categoryFilter.addEventListener(
    "change",
    () => {

        console.log(
            "Category changed:",
            categoryFilter.value
        );

        const location =
            searchLocation.value.trim();

        // All Places means all categories,
        // NOT "no location".
        if (categoryFilter.value === "all") {

            if (!location) {

                showInitialMessage();

                return;
            }

            loadRecommendations();

            return;
        }

        if (!location) {

            showInitialMessage();

            return;
        }

        loadRecommendations();

    }
);


// =====================================================
// DISTANCE FILTER
// =====================================================

distanceFilter.addEventListener(
    "change",

    () => {

        const location =
            searchLocation.value.trim();


        if (!location) {

            showInitialMessage();

            return;

        }


        loadRecommendations();

    }
);


// =====================================================
// NEAR ME
// =====================================================

nearMeBtn.addEventListener(
    "click",

    () => {

        if (
            !navigator.geolocation
        ) {

            alert(
                "Geolocation is not supported by your browser."
            );

            return;

        }


        nearMeBtn.disabled = true;


        nearMeBtn.innerHTML = `

            <i class="fa-solid fa-spinner fa-spin"></i>

            Locating...

        `;


        navigator.geolocation.getCurrentPosition(

            async position => {

                const latitude =
                    position.coords.latitude;


                const longitude =
                    position.coords.longitude;


                searchLocation.value =
                    "Current Location";


                await loadRecommendations({

                    latitude:
                        latitude,

                    longitude:
                        longitude,

                    location:
                        null

                });


                nearMeBtn.disabled =
                    false;


                nearMeBtn.innerHTML = `

                    <i class="fa-solid fa-location-crosshairs"></i>

                    Near Me

                `;

            },


            error => {

                console.error(
                    "Geolocation error:",
                    error
                );


                let message =
                    "Unable to access your location.";


                if (
                    error.code ===
                    error.PERMISSION_DENIED
                ) {

                    message =
                        "Location permission was denied. Please allow location access and try again.";

                } else if (
                    error.code ===
                    error.POSITION_UNAVAILABLE
                ) {

                    message =
                        "Your current location could not be determined.";

                } else if (
                    error.code ===
                    error.TIMEOUT
                ) {

                    message =
                        "Location request timed out. Please try again.";

                }


                alert(message);


                nearMeBtn.disabled =
                    false;


                nearMeBtn.innerHTML = `

                    <i class="fa-solid fa-location-crosshairs"></i>

                    Near Me

                `;

            },


            {
                enableHighAccuracy:
                    true,

                timeout:
                    15000,

                maximumAge:
                    0
            }

        );

    }
);


// =====================================================
// INITIAL MESSAGE
// =====================================================

function showInitialMessage() {

    resultsGrid.innerHTML = `

        <div class="recommend-empty">

            <div class="empty-icon">

                <i class="fa-solid fa-compass"></i>

            </div>

            <h3>
                Discover places around you
            </h3>

            <p>
                Search for a destination or
                click "Near Me" to get recommendations.
            </p>

        </div>

    `;


    resultCount.textContent =
        "Ready to search";

}


// =====================================================
// FORMAT CATEGORY
// =====================================================

function formatCategory(category) {

    if (!category) {

        return "Place";

    }


    return String(category)

        .replaceAll(
            "_",
            " "
        )

        .replace(
            /\b\w/g,

            char =>
                char.toUpperCase()
        );

}


// =====================================================
// FORMAT DISTANCE
// =====================================================

function formatDistance(distance) {

    const value =
        Number(distance);


    if (
        Number.isNaN(value)
    ) {

        return `${escapeHtml(
            String(distance)
        )} away`;

    }


    return `${value.toFixed(1)} km away`;

}


// =====================================================
// GOOGLE MAPS URL
// =====================================================

function createMapsUrl(
    name,
    address
) {

    const query =
        encodeURIComponent(
            `${name}, ${address}`
        );


    return (
        "https://www.google.com/maps/search/?api=1&query="
        + query
    );

}


// =====================================================
// HTML ESCAPE
// =====================================================

function escapeHtml(value) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


// =====================================================
// ATTRIBUTE ESCAPE
// =====================================================

function escapeAttribute(value) {

    return escapeHtml(
        String(value)
    );

}


// =====================================================
// INITIALIZE
// =====================================================

document.addEventListener(
    "DOMContentLoaded",

    () => {

        showInitialMessage();

    }
);
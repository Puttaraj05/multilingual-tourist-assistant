const API_BASE = "";


// =========================================================
// ELEMENTS
// =========================================================

const form = document.getElementById("emergencyForm");

const locationInput = document.getElementById("location");

const emergencyType = document.getElementById("type");

const resultsContainer = document.getElementById("results");

const resultsStatus = document.getElementById("resultsStatus");

const countrySelect = document.getElementById("country");

const countryContacts = document.getElementById("countryContacts");

const useLocationBtn = document.getElementById("useLocationBtn");

const incidentForm = document.getElementById("incidentForm");

const incidentType = document.getElementById("incidentType");

const incidentCountry = document.getElementById("incidentCountry");

const incidentDescription =
    document.getElementById("incidentDescription");

const incidentLocation =
    document.getElementById("incidentLocation");

const incidentMessage =
    document.getElementById("incidentMessage");

const incidentResults =
    document.getElementById("incidentResults");

const refreshIncidentsBtn =
    document.getElementById("refreshIncidentsBtn");


// =========================================================
// GPS STATE
// =========================================================

let currentLatitude = null;
let currentLongitude = null;
let currentAccuracy = null;


// =========================================================
// API RESPONSE HELPER
// =========================================================

async function getJsonResponse(response) {

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            `Server returned HTTP ${response.status}`
        );
    }

    if (!response.ok) {

        throw new Error(
            data.detail ||
            data.error ||
            data.message ||
            `Request failed (${response.status})`
        );
    }

    return data;
}


// =========================================================
// COUNTRY EMERGENCY CONTACTS
// =========================================================

async function loadEmergencyContacts(countryCode) {

    if (!countryContacts) {
        return;
    }

    countryContacts.innerHTML = `
        <div class="placeholder-box">
            <i class="fa-solid fa-spinner fa-spin"></i>

            <h3>
                Loading emergency contacts...
            </h3>
        </div>
    `;

    try {

        const response = await fetch(
            `${API_BASE}/api/emergency-contacts?country=${encodeURIComponent(
                countryCode || "IN"
            )}`
        );

        const data = await getJsonResponse(response);

        displayCountryContacts(
            data.contacts || []
        );

    } catch (error) {

        console.error(
            "Emergency contacts error:",
            error
        );

        countryContacts.innerHTML = `
            <div class="placeholder-box">

                <i class="fa-solid fa-triangle-exclamation"></i>

                <h3>
                    Unable to load contacts
                </h3>

                <p>
                    ${escapeHtml(error.message)}
                </p>

            </div>
        `;
    }
}


// =========================================================
// DISPLAY COUNTRY CONTACTS
// =========================================================

function displayCountryContacts(contacts) {

    countryContacts.innerHTML = "";

    if (!contacts.length) {

        countryContacts.innerHTML = `
            <div class="placeholder-box">

                <i class="fa-solid fa-phone-slash"></i>

                <h3>
                    No emergency contacts found
                </h3>

                <p>
                    No emergency numbers are available
                    for this country.
                </p>

            </div>
        `;

        return;
    }

    contacts.forEach(contact => {

        const card = document.createElement("div");

        card.className = "emergency-contact-card";

        card.innerHTML = `
            <div class="emergency-contact-icon">
                <i class="fa-solid fa-phone"></i>
            </div>

            <div class="emergency-contact-info">

                <h3>
                    ${escapeHtml(
                        contact.service ||
                        "Emergency Service"
                    )}
                </h3>

                <p>
                    ${escapeHtml(
                        contact.description || ""
                    )}
                </p>

            </div>

            <div class="emergency-contact-action">

                <a
                    href="tel:${escapeHtml(
                        contact.number || ""
                    )}"
                    class="call-btn"
                >
                    <i class="fa-solid fa-phone"></i>

                    ${escapeHtml(
                        contact.number ||
                        "Unavailable"
                    )}
                </a>

            </div>
        `;

        countryContacts.appendChild(card);

    });
}


// =========================================================
// COUNTRY CHANGE
// =========================================================

if (countrySelect) {

    countrySelect.addEventListener(
        "change",
        () => {

            loadEmergencyContacts(
                countrySelect.value
            );

        }
    );

}


// =========================================================
// GET GPS LOCATION
// =========================================================

function getCurrentLocation() {

    return new Promise(
        (resolve, reject) => {

            if (!navigator.geolocation) {

                reject(
                    new Error(
                        "Geolocation is not supported by this browser."
                    )
                );

                return;
            }

            navigator.geolocation.getCurrentPosition(

                position => {

                    currentLatitude =
                        position.coords.latitude;

                    currentLongitude =
                        position.coords.longitude;

                    currentAccuracy =
                        position.coords.accuracy;

                    resolve(position);

                },

                error => {

                    let message =
                        "Unable to get your location.";

                    if (
                        error.code ===
                        error.PERMISSION_DENIED
                    ) {

                        message =
                            "Location permission was denied. Please allow location access.";

                    } else if (
                        error.code ===
                        error.POSITION_UNAVAILABLE
                    ) {

                        message =
                            "Your current location is unavailable.";

                    } else if (
                        error.code ===
                        error.TIMEOUT
                    ) {

                        message =
                            "Location request timed out.";

                    }

                    reject(
                        new Error(message)
                    );

                },

                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                }
            );

        }
    );
}


// =========================================================
// USE MY LOCATION
// =========================================================

if (useLocationBtn) {

    useLocationBtn.addEventListener(
        "click",
        async () => {

            useLocationBtn.disabled = true;

            useLocationBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Getting Location...
            `;

            try {

                await getCurrentLocation();

                if (locationInput) {

                    locationInput.value =
                        `${currentLatitude.toFixed(6)}, ${currentLongitude.toFixed(6)}`;

                }

                await saveLocation();

                useLocationBtn.innerHTML = `
                    <i class="fa-solid fa-check"></i>
                    Location Found
                `;

            } catch (error) {

                console.error(
                    "Location error:",
                    error
                );

                alert(error.message);

                useLocationBtn.innerHTML = `
                    <i class="fa-solid fa-location-crosshairs"></i>
                    Use My Current Location
                `;

            } finally {

                useLocationBtn.disabled = false;

            }

        }
    );

}


// =========================================================
// SAVE GPS LOCATION
// =========================================================

async function saveLocation() {

    if (
        currentLatitude === null ||
        currentLongitude === null
    ) {

        return;

    }

    try {

        const response = await fetch(
            `${API_BASE}/api/location`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    latitude: currentLatitude,

                    longitude: currentLongitude,

                    accuracy: currentAccuracy,

                    countryCode:
                        countrySelect?.value || "IN"

                })
            }
        );

        const data =
            await getJsonResponse(response);

        console.log(
            "Location saved:",
            data
        );

    } catch (error) {

        console.warn(
            "Could not save location:",
            error
        );

    }
}


// =========================================================
// FIND NEARBY SERVICES
// =========================================================

async function findNearbyServices() {

    if (
        currentLatitude === null ||
        currentLongitude === null
    ) {

        await getCurrentLocation();

    }

    const type =
        emergencyType.value;

    /*
     * Backend expects radius in METERS.
     * 5 km = 5000 meters.
     */
    const radius = 5000;

    resultsStatus.textContent =
        "Searching";

    resultsContainer.innerHTML = `
        <div class="placeholder-box">

            <i class="fa-solid fa-spinner fa-spin"></i>

            <h3>
                Finding nearby
                ${escapeHtml(type)}
                services...
            </h3>

            <p>
                Searching around your current GPS location.
            </p>

        </div>
    `;

    const url =
        `${API_BASE}/api/nearby-emergency` +
        `?latitude=${encodeURIComponent(currentLatitude)}` +
        `&longitude=${encodeURIComponent(currentLongitude)}` +
        `&type=${encodeURIComponent(type)}` +
        `&radius=${encodeURIComponent(radius)}`;

    console.log(
        "Nearby emergency request:",
        url
    );

    const response =
        await fetch(url);

    const data =
        await getJsonResponse(response);

    displayNearbyResults(
        data.results || [],
        type
    );
}


// =========================================================
// NEARBY SERVICES FORM
// =========================================================

if (form) {

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            try {

                await findNearbyServices();

            } catch (error) {

                console.error(
                    "Nearby emergency error:",
                    error
                );

                if (resultsStatus) {
                    resultsStatus.textContent =
                        "Error";
                }

                if (resultsContainer) {

                    resultsContainer.innerHTML = `
                        <div class="placeholder-box">

                            <i class="fa-solid fa-triangle-exclamation"></i>

                            <h3>
                                Unable to find nearby services
                            </h3>

                            <p>
                                ${escapeHtml(
                                    error.message
                                )}
                            </p>

                            <button
                                type="button"
                                class="secondary-action"
                                onclick="location.reload()"
                            >
                                Try Again
                            </button>

                        </div>
                    `;

                }

            }

        }
    );

}


// =========================================================
// DISPLAY NEARBY SERVICES
// =========================================================

function displayNearbyResults(results, type) {

    resultsContainer.innerHTML = "";

    const limitedResults = results.slice(0, 10);

    resultsStatus.textContent =
        `${limitedResults.length} found`;

    if (!limitedResults.length) {

        resultsContainer.innerHTML = `
            <div class="placeholder-box">
                <i class="fa-solid fa-location-dot"></i>

                <h3>
                    No nearby services found
                </h3>

                <p>
                    Try using your current location again.
                </p>
            </div>
        `;

        return;
    }

    limitedResults.forEach((place, index) => {

        const card = document.createElement("div");

        card.className = "emergency-card";

        const distance = Number(place.distance_km);

        const safeDistance =
            Number.isFinite(distance)
                ? `${distance.toFixed(2)} km`
                : "Distance unavailable";

        const latitude = Number(place.latitude);
        const longitude = Number(place.longitude);

        let mapUrl = place.maps_url;

        if (
            !mapUrl &&
            Number.isFinite(latitude) &&
            Number.isFinite(longitude)
        ) {
            mapUrl =
                `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
        }

        const phoneHtml = place.phone
            ? `
                <a
                    href="tel:${escapeHtml(place.phone)}"
                    class="emergency-call-btn"
                >
                    <i class="fa-solid fa-phone"></i>
                    Call
                </a>
            `
            : "";

        const directionsHtml = mapUrl
            ? `
                <a
                    href="${escapeHtml(mapUrl)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="emergency-directions-btn"
                >
                    <i class="fa-solid fa-diamond-turn-right"></i>
                    Directions
                </a>
            `
            : "";

        card.innerHTML = `

            <div class="emergency-card-top">

                <div class="emergency-rank">
                    ${index + 1}
                </div>

                <div class="emergency-card-title">

                    <h3>
                        ${escapeHtml(
                            place.name ||
                            "Emergency Service"
                        )}
                    </h3>

                    <span class="emergency-distance">
                        <i class="fa-solid fa-location-dot"></i>
                        ${safeDistance} away
                    </span>

                </div>

            </div>


            <div class="emergency-card-details">

                ${
                    place.address
                        ? `
                            <div class="emergency-detail">
                                <i class="fa-solid fa-map-pin"></i>
                                <span>
                                    ${escapeHtml(place.address)}
                                </span>
                            </div>
                        `
                        : ""
                }

                ${
                    place.phone
                        ? `
                            <div class="emergency-detail">
                                <i class="fa-solid fa-phone"></i>
                                <span>
                                    ${escapeHtml(place.phone)}
                                </span>
                            </div>
                        `
                        : ""
                }

            </div>


            <div class="emergency-card-actions">

                ${phoneHtml}

                ${directionsHtml}

            </div>

        `;

        resultsContainer.appendChild(card);
    });
}


// =========================================================
// REPORT INCIDENT
// =========================================================

if (incidentForm) {

    incidentForm.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const type =
                incidentType.value.trim();

            const description =
                incidentDescription.value.trim();

            const countryCode =
                incidentCountry?.value || "IN";

            const locationText =
                incidentLocation?.value.trim() || "";

            if (!description) {

                alert(
                    "Please describe what happened."
                );

                incidentDescription.focus();

                return;
            }

            let latitude =
                currentLatitude;

            let longitude =
                currentLongitude;

            let accuracy =
                currentAccuracy;


            // ---------------------------------------------
            // Try GPS
            // ---------------------------------------------

            if (
                latitude === null ||
                longitude === null
            ) {

                try {

                    await getCurrentLocation();

                    latitude =
                        currentLatitude;

                    longitude =
                        currentLongitude;

                    accuracy =
                        currentAccuracy;

                } catch (error) {

                    console.warn(
                        "GPS unavailable for incident:",
                        error
                    );

                }

            }


            const reportButton =
                document.getElementById(
                    "reportIncidentBtn"
                );


            if (reportButton) {

                reportButton.disabled = true;

                reportButton.innerHTML = `
                    <i class="fa-solid fa-spinner fa-spin"></i>
                    Saving Report...
                `;

            }


            incidentMessage.innerHTML = "";


            try {

                /*
                 * IMPORTANT:
                 *
                 * Your FastAPI backend uses:
                 *
                 * POST /api/incidents
                 *
                 * NOT:
                 *
                 * /api/emergency/report
                 */

                const response =
                    await fetch(
                        `${API_BASE}/api/incidents`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                type: type,

                                description:
                                    locationText
                                        ? `Location: ${locationText}\n\n${description}`
                                        : description,

                                latitude:
                                    latitude,

                                longitude:
                                    longitude,

                                accuracy:
                                    accuracy,

                                countryCode:
                                    countryCode

                            })
                        }
                    );


                const data =
                    await getJsonResponse(response);


                console.log(
                    "Incident saved successfully:",
                    data
                );


                incidentMessage.innerHTML = `
                    <div class="success-message">

                        <i class="fa-solid fa-circle-check"></i>

                        <div>

                            <strong>
                                Report submitted successfully
                            </strong>

                            <p>
                                Your ${escapeHtml(type)}
                                report has been saved to TravelMate.
                            </p>

                        </div>

                    </div>
                `;


                /*
                 * Clear form.
                 */
                incidentForm.reset();


                /*
                 * IMPORTANT:
                 * Reload reports from MongoDB.
                 */
                await loadIncidents();


            } catch (error) {

                console.error(
                    "Incident save error:",
                    error
                );


                incidentMessage.innerHTML = `
                    <div class="error-message">

                        <i class="fa-solid fa-circle-exclamation"></i>

                        <div>

                            <strong>
                                Unable to submit report
                            </strong>

                            <p>
                                ${escapeHtml(
                                    error.message
                                )}
                            </p>

                        </div>

                    </div>
                `;

            } finally {

                if (reportButton) {

                    reportButton.disabled =
                        false;

                    reportButton.innerHTML = `
                        <i class="fa-solid fa-file-circle-exclamation"></i>
                        Report Incident
                    `;

                }

            }

        }
    );

}


// =========================================================
// LOAD INCIDENTS
// =========================================================

async function loadIncidents() {

    if (!incidentResults) {
        return;
    }

    incidentResults.innerHTML = `
        <div class="placeholder-box">

            <i class="fa-solid fa-spinner fa-spin"></i>

            <h3>
                Loading reports...
            </h3>

        </div>
    `;

    try {

        /*
         * Backend:
         *
         * GET /api/incidents
         */

        const response =
            await fetch(
                `${API_BASE}/api/incidents`
            );


        const data =
            await getJsonResponse(response);


        /*
         * Your current backend returns:
         *
         * [
         *   {...},
         *   {...}
         * ]
         *
         * So handle that format.
         */

        const incidents =
            Array.isArray(data)
                ? data
                : (
                    data.incidents ||
                    []
                );


        console.log(
            "Incidents loaded:",
            incidents
        );


        displayIncidents(
            incidents
        );


    } catch (error) {

        console.error(
            "Incident history error:",
            error
        );


        incidentResults.innerHTML = `
            <div class="placeholder-box">

                <i class="fa-solid fa-triangle-exclamation"></i>

                <h3>
                    Unable to load reports
                </h3>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

                <button
                    type="button"
                    class="secondary-action"
                    onclick="loadIncidents()"
                >
                    Retry
                </button>

            </div>
        `;

    }

}


// =========================================================
// DISPLAY INCIDENTS
// =========================================================

function displayIncidents(
    incidents
) {

    incidentResults.innerHTML = "";

    if (!incidents.length) {

        incidentResults.innerHTML = `
            <div class="placeholder-box">

                <i class="fa-solid fa-shield-halved"></i>

                <h3>
                    No travel incidents
                </h3>

                <p>
                    Your submitted lost, theft and safety
                    reports will appear here.
                </p>

            </div>
        `;

        return;
    }


    incidents.forEach(
        incident => {

            const card =
                document.createElement("div");

            card.className =
                "incident-card";


            const date =
                incident.created_at
                    ? new Date(
                        incident.created_at
                    ).toLocaleString()
                    : "Unknown date";


            const typeLabel =
                formatIncidentType(
                    incident.type
                );


            let gpsHtml = "";


            if (
                incident.latitude !== null &&
                incident.latitude !== undefined &&
                incident.longitude !== null &&
                incident.longitude !== undefined
            ) {

                const lat =
                    Number(incident.latitude);

                const lon =
                    Number(incident.longitude);


                if (
                    Number.isFinite(lat) &&
                    Number.isFinite(lon)
                ) {

                    gpsHtml = `
                        <p>
                            <i class="fa-solid fa-location-dot"></i>

                            GPS:
                            ${lat.toFixed(5)},
                            ${lon.toFixed(5)}
                        </p>
                    `;

                }

            }


            card.innerHTML = `
                <div class="incident-card-header">

                    <span class="incident-type">
                        ${escapeHtml(typeLabel)}
                    </span>

                    <span class="incident-date">
                        ${escapeHtml(date)}
                    </span>

                </div>

                <p class="incident-description">
                    ${escapeHtml(
                        incident.description ||
                        "No description provided."
                    )}
                </p>

                ${gpsHtml}

            `;


            incidentResults.appendChild(
                card
            );

        }
    );

}


// =========================================================
// INCIDENT TYPE LABEL
// =========================================================

function formatIncidentType(type) {

    const labels = {

        lost:
            "Lost Item",

        theft:
            "Theft / Stolen",

        unsafe:
            "Unsafe Situation",

        document:
            "Lost Document",

        medical:
            "Medical Emergency",

        other:
            "Other"

    };


    return (
        labels[type] ||
        "Travel Incident"
    );

}


// =========================================================
// ESCAPE HTML
// =========================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// =========================================================
// REFRESH REPORTS
// =========================================================

if (refreshIncidentsBtn) {

    refreshIncidentsBtn.addEventListener(
        "click",
        async () => {

            refreshIncidentsBtn.disabled = true;

            const originalText =
                refreshIncidentsBtn.innerHTML;

            refreshIncidentsBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Refreshing...
            `;

            try {

                await loadIncidents();

            } finally {

                refreshIncidentsBtn.disabled =
                    false;

                refreshIncidentsBtn.innerHTML =
                    originalText;

            }

        }
    );

}


// =========================================================
// INITIAL LOAD
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        /*
         * Load emergency contacts.
         */

        if (countrySelect) {

            await loadEmergencyContacts(
                countrySelect.value || "IN"
            );

        }


        /*
         * Load existing reports from MongoDB.
         */

        await loadIncidents();

    }
);
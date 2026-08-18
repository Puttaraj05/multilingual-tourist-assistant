/* =========================================================
   TRAVELMATE — PLANNER
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    console.log("=================================");
    console.log("PLANNER JS LOADED");
    console.log("=================================");


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const form =
        document.getElementById("plannerForm");

    const durationInput =
        document.getElementById("duration");

    const decreaseButton =
        document.getElementById("decreaseDays");

    const increaseButton =
        document.getElementById("increaseDays");

    const destinationInput =
        document.getElementById("destination");

    const destinationError =
        document.getElementById("destinationError");

    const travelDate =
        document.getElementById("travelDate");

    const budgetInput =
        document.getElementById("budget");

    const languageInput =
        document.getElementById("language");

    const currencyInput =
        document.getElementById("currency");


    /* =====================================================
       CHECK FORM
       ===================================================== */

    if (!form) {

        console.error(
            "ERROR: plannerForm was not found."
        );

        return;
    }


    /* =====================================================
       DURATION — DECREASE
       ===================================================== */

    decreaseButton?.addEventListener(
        "click",
        () => {

            let value =
                parseInt(
                    durationInput?.value
                ) || 1;


            if (value > 1) {

                value--;

                if (durationInput) {

                    durationInput.value =
                        value;

                }

            }

        }
    );


    /* =====================================================
       DURATION — INCREASE
       ===================================================== */

    increaseButton?.addEventListener(
        "click",
        () => {

            let value =
                parseInt(
                    durationInput?.value
                ) || 1;


            if (value < 30) {

                value++;

                if (durationInput) {

                    durationInput.value =
                        value;

                }

            }

        }
    );


    /* =====================================================
       SET MINIMUM TRAVEL DATE
       ===================================================== */

    if (travelDate) {

        const today =
            new Date();

        const year =
            today.getFullYear();

        const month =
            String(
                today.getMonth() + 1
            ).padStart(2, "0");

        const day =
            String(
                today.getDate()
            ).padStart(2, "0");


        travelDate.min =
            `${year}-${month}-${day}`;

    }


    /* =====================================================
       FORM SUBMIT
       ===================================================== */

    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            console.log(
                "Generate itinerary clicked."
            );


            /* =============================================
               CLEAR OLD ERROR
               ============================================= */

            if (destinationError) {

                destinationError.textContent =
                    "";

            }


            /* =============================================
               GET FORM VALUES
               ============================================= */

            const destination =
                destinationInput?.value
                    ?.trim() || "";


            const duration =
                parseInt(
                    durationInput?.value
                ) || 0;


            const travelDateValue =
                travelDate?.value || "";


            const budget =
                parseInt(
                    budgetInput?.value
                ) || 0;


            const language =
                languageInput?.value ||
                "English";


            const currency =
                currencyInput?.value ||
                "₹";


            /* =============================================
               TRAVEL TYPE
               ============================================= */

            const travelTypeElement =
                document.querySelector(
                    'input[name="travelType"]:checked'
                );


            const travelType =
                travelTypeElement?.value ||
                "Solo";


            /* =============================================
               TRIP STYLE
               ============================================= */

            const tripStyleElement =
                document.querySelector(
                    'input[name="tripStyle"]:checked'
                );


            const tripStyle =
                tripStyleElement?.value ||
                "Balanced";


            /* =============================================
               CHILDREN
               ============================================= */

            const kidsUnder12 =
                document.getElementById(
                    "kidsUnder12"
                )?.checked || false;


            /* =============================================
               INTERESTS
               ============================================= */

            const interests =
                Array.from(
                    document.querySelectorAll(
                        'input[name="interest"]:checked'
                    )
                ).map(
                    checkbox =>
                        checkbox.value
                );


            /* =============================================
               VALIDATION — DESTINATION
               ============================================= */

            if (!destination) {

                if (destinationError) {

                    destinationError.textContent =
                        "Please enter a destination.";

                }

                destinationInput?.focus();

                return;
            }


            /* =============================================
               VALIDATION — DURATION
               ============================================= */

            if (
                duration < 1 ||
                duration > 30
            ) {

                alert(
                    "Trip duration must be between 1 and 30 days."
                );

                durationInput?.focus();

                return;
            }


            /* =============================================
               VALIDATION — DATE
               ============================================= */

            if (!travelDateValue) {

                alert(
                    "Please select your travel date."
                );

                travelDate?.focus();

                return;
            }


            /* =============================================
               VALIDATION — BUDGET
               ============================================= */

            if (
                budget <= 0
            ) {

                alert(
                    "Please enter a valid budget."
                );

                budgetInput?.focus();

                return;
            }


            /* =============================================
               SUBMIT BUTTON
               ============================================= */

            const submitButton =
                form.querySelector(
                    ".generate-button"
                );


            const originalText =
                submitButton?.innerHTML;


            if (submitButton) {

                submitButton.disabled =
                    true;

                submitButton.innerHTML = `
                    <span>
                        Generating your itinerary...
                    </span>
                `;

            }


            /* =============================================
               REQUEST DATA
               ============================================= */

            const requestData = {

                destination:
                    destination,

                duration:
                    duration,

                travelDate:
                    travelDateValue,

                budget:
                    budget,

                currencySymbol:
                    currency,

                interests:
                    interests,

                language:
                    language,

                travelType:
                    travelType,

                tripStyle:
                    tripStyle,

                kidsUnder12:
                    kidsUnder12

            };


            console.log(
                "Sending itinerary request:"
            );

            console.log(
                requestData
            );


            /* =============================================
               SEND REQUEST
               ============================================= */

            try {

                const response =
                    await fetch(
                        "/api/itinerary",
                        {

                            method:
                                "POST",

                            headers: {

                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"

                            },

                            body:
                                JSON.stringify(
                                    requestData
                                )

                        }
                    );


                console.log(
                    "Backend response status:",
                    response.status
                );


                /* =========================================
                   READ RESPONSE
                   ========================================= */

                let data;


                try {

                    data =
                        await response.json();

                }

                catch (jsonError) {

                    console.error(
                        "Could not parse backend response:",
                        jsonError
                    );

                    throw new Error(
                        "The server returned an invalid response."
                    );

                }


                console.log(
                    "Backend itinerary response:",
                    data
                );


                /* =========================================
                   BACKEND ERROR
                   ========================================= */

                if (!response.ok) {

                    const message =
                        data?.detail ||
                        data?.message ||
                        `Server error (${response.status})`;


                    throw new Error(
                        message
                    );

                }


                /* =========================================
                   VALIDATE ITINERARY
                   ========================================= */

                if (
                    !data ||
                    typeof data !== "object"
                ) {

                    throw new Error(
                        "The server returned empty itinerary data."
                    );

                }


                if (
                    !Array.isArray(
                        data.days
                    )
                ) {

                    console.error(
                        "Invalid itinerary:",
                        data
                    );

                    throw new Error(
                        "The generated itinerary has no day-by-day plan."
                    );

                }


                if (
                    data.days.length === 0
                ) {

                    throw new Error(
                        "The generated itinerary contains no days."
                    );

                }


                /* =========================================
                   SAVE TO SESSION STORAGE
                   ========================================= */

                try {

                    localStorage.setItem(
                        "itinerary",
                        JSON.stringify(data)
                    );

                }

                catch (storageError) {

                    console.error(
                        "SessionStorage error:",
                        storageError
                    );

                    throw new Error(
                        "Unable to save your itinerary in the browser."
                    );

                }


                /* =========================================
                   VERIFY STORAGE
                   ========================================= */

                const saved =
                    localStorage.getItem(
                        "itinerary"
                    );


                if (!saved) {

                    throw new Error(
                        "Itinerary could not be saved."
                    );

                }


                console.log(
                    "================================="
                );

                console.log(
                    "ITINERARY SAVED SUCCESSFULLY"
                );

                console.log(
                    "Destination:",
                    data.destination
                );

                console.log(
                    "Days:",
                    data.days.length
                );

                console.log(
                    "================================="
                );


                /* =========================================
                   REDIRECT
                   ========================================= */

                window.location.assign(
                    "/itinerary.html"
                );

            }


            /* =============================================
               ERROR
               ============================================= */

            catch (error) {

                console.error(
                    "================================="
                );

                console.error(
                    "ITINERARY GENERATION ERROR"
                );

                console.error(
                    error
                );

                console.error(
                    "================================="
                );


                alert(
                    error?.message ||
                    "Something went wrong while generating your itinerary."
                );

            }


            /* =============================================
               RESTORE BUTTON
               ============================================= */

            finally {

                if (submitButton) {

                    submitButton.disabled =
                        false;


                    submitButton.innerHTML =
                        originalText ||
                        `
                        <span>
                            Generate My Itinerary
                        </span>
                        `;

                }

            }

        }
    );

});
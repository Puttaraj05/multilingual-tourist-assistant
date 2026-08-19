/* =========================================================
   TRAVELMATE AUTHENTICATION
========================================================= */

const API_AUTH = "/api/auth";

const TOKEN_KEY = "travelmate_token";
const USER_KEY = "travelmate_user";


/* =========================================================
   ELEMENTS
========================================================= */

const tabs = document.querySelectorAll(".tab");

const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");


/* =========================================================
   TABS
========================================================= */

tabs.forEach(tab => {

    tab.addEventListener("click", () => {

        tabs.forEach(t => {
            t.classList.remove("active");
        });

        tab.classList.add("active");

        if (tab.dataset.tab === "login") {

            loginForm?.classList.remove("hidden");
            signupForm?.classList.add("hidden");

        } else {

            signupForm?.classList.remove("hidden");
            loginForm?.classList.add("hidden");

        }

    });

});


/* =========================================================
   SAVE AUTH DATA
========================================================= */

function saveAuth(data) {

    if (!data || !data.token || !data.user) {

        throw new Error(
            "Invalid authentication response from server."
        );
    }

    localStorage.setItem(
        TOKEN_KEY,
        data.token
    );

    localStorage.setItem(
        USER_KEY,
        JSON.stringify(data.user)
    );
}


/* =========================================================
   API RESPONSE HANDLER
========================================================= */

async function parseResponse(response) {

    const contentType =
        response.headers.get("content-type") || "";

    /*
     * Normal FastAPI JSON response
     */

    if (contentType.includes("application/json")) {

        return await response.json();

    }

    /*
     * Prevent:
     * Unexpected token 'I', "Internal S..."
     */

    const text = await response.text();

    throw new Error(
        text || `Server returned HTTP ${response.status}`
    );
}


/* =========================================================
   LOGIN
========================================================= */

loginForm?.addEventListener(
    "submit",
    async event => {

        event.preventDefault();

        const inputs =
            loginForm.querySelectorAll("input");

        const email =
            inputs[0].value.trim().toLowerCase();

        const password =
            inputs[1].value;

        if (!email || !password) {

            alert("Please enter email and password.");

            return;
        }


        const button =
            loginForm.querySelector(
                "button[type='submit']"
            );

        const originalText =
            button.textContent;


        try {

            button.disabled = true;
            button.textContent = "Logging in...";


            const response =
                await fetch(
                    `${API_AUTH}/login`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body: JSON.stringify({
                            email,
                            password
                        })
                    }
                );


            const data =
                await parseResponse(response);


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    data.message ||
                    "Login failed."
                );
            }


            saveAuth(data);


            /*
             * Successful login
             */

            window.location.href =
                "/dashboard.html";


        } catch (error) {

            console.error(
                "Login error:",
                error
            );

            alert(
                error.message ||
                "Unable to login. Please try again."
            );

        } finally {

            button.disabled = false;
            button.textContent = originalText;

        }

    }
);


/* =========================================================
   SIGN UP
========================================================= */

signupForm?.addEventListener(
    "submit",
    async event => {

        event.preventDefault();


        const inputs =
            signupForm.querySelectorAll("input");


        const name =
            inputs[0].value.trim();

        const email =
            inputs[1].value.trim().toLowerCase();

        const password =
            inputs[2].value;

        const confirmPassword =
            inputs[3].value;


        /* =================================================
           VALIDATION
        ================================================= */

        if (name.length < 2) {

            alert(
                "Name must contain at least 2 characters."
            );

            return;
        }


        if (password.length < 6) {

            alert(
                "Password must contain at least 6 characters."
            );

            return;
        }


        if (password !== confirmPassword) {

            alert(
                "Passwords do not match."
            );

            return;
        }


        /*
         * bcrypt supports maximum 72 bytes
         */

        if (
            new TextEncoder()
                .encode(password)
                .length > 72
        ) {

            alert(
                "Password must be 72 bytes or fewer."
            );

            return;
        }


        const button =
            signupForm.querySelector(
                "button[type='submit']"
            );

        const originalText =
            button.textContent;


        try {

            button.disabled = true;

            button.textContent =
                "Creating account...";


            const response =
                await fetch(
                    `${API_AUTH}/signup`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body: JSON.stringify({
                            name,
                            email,
                            password
                        })
                    }
                );


            const data =
                await parseResponse(response);


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    data.message ||
                    "Signup failed."
                );
            }


            saveAuth(data);


            /*
             * Successful signup
             */

            window.location.href =
                "/dashboard.html";


        } catch (error) {

            console.error(
                "Signup error:",
                error
            );

            alert(
                error.message ||
                "Unable to create account. Please try again."
            );

        } finally {

            button.disabled = false;

            button.textContent =
                originalText;

        }

    }
);
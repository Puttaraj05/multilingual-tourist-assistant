// Handle login, signup, and authentication data for TravelMate.

const API_AUTH = "/api/auth";

const TOKEN_KEY = "travelmate_token";
const USER_KEY = "travelmate_user";

// Get the authentication forms and tab controls from the page.

const tabs = document.querySelectorAll(".tab");

const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");

// Switch between the login and signup forms.

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

// Save the token and user information returned by the authentication API.

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

// Convert the API response into JSON and provide a useful error for non-JSON responses.

async function parseResponse(response) {

    const contentType =
        response.headers.get("content-type") || "";

    // FastAPI normally returns authentication responses as JSON.

    if (contentType.includes("application/json")) {

        return await response.json();

    }

    // If the server returns plain text or an HTML error page, show that response instead.

    const text = await response.text();

    throw new Error(
        text || `Server returned HTTP ${response.status}`
    );
}

// Handle the login form submission.

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

            // Send the user to the dashboard after a successful login.

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

// Handle the account creation form.

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


        // Check the basic signup requirements before sending the request.

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


        // bcrypt supports passwords up to a maximum of 72 bytes.

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

            // Send the new user to the dashboard after signup.

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
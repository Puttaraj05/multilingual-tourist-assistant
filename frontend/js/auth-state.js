// Manage the logged-in user's authentication state across all pages.

const AUTH_TOKEN_KEY = "travelmate_token";
const AUTH_USER_KEY = "travelmate_user";

const AUTH_ME_ENDPOINT = "/api/auth/me";

// Get the authentication token saved in localStorage.

function getAuthToken() {

    return localStorage.getItem(
        AUTH_TOKEN_KEY
    );
}

// Retrieve the previously saved user information.

function getSavedUser() {

    try {

        const user =
            localStorage.getItem(
                AUTH_USER_KEY
            );

        return user
            ? JSON.parse(user)
            : null;

    } catch {

        return null;
    }
}

// Generate initials from the user's name for the profile avatar.

function getUserInitials(name) {

    if (!name) {
        return "TM";
    }

    return name
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map(
            word =>
                word
                    .charAt(0)
                    .toUpperCase()
        )
        .join("");
}

// Clear the saved authentication details and return to the login page.

function logoutUser() {

    localStorage.removeItem(
        AUTH_TOKEN_KEY
    );

    localStorage.removeItem(
        AUTH_USER_KEY
    );

    window.location.href =
        "/auth.html";
}

// Show login and sign-up links when there is no active session.

function renderLoggedOut() {

    const container =
        document.getElementById(
            "authSection"
        );

    if (!container) {
        return;
    }

    container.innerHTML = `
        <a href="/auth.html">
            Login
        </a>

        <a
            href="/auth.html"
            class="nav-signup"
        >
            Sign Up
        </a>
    `;
}

// Display the user's profile menu when they are logged in.

function renderLoggedIn(user) {

    const container =
        document.getElementById(
            "authSection"
        );

    if (!container) {
        return;
    }

    const name =
        user.name || "Traveler";

    const email =
        user.email || "";

    const initials =
        getUserInitials(name);


    container.innerHTML = `

        <div class="user-menu">

            <button
                type="button"
                class="user-menu-button"
                id="userMenuButton"
            >

                <span class="user-avatar">
                    ${initials}
                </span>

                <span class="user-menu-name">
                    ${escapeAuthHtml(name)}
                </span>

                <i
                    class="fa-solid fa-chevron-down user-menu-arrow"
                ></i>

            </button>


            <div
                class="user-dropdown"
                id="userDropdown"
            >

                <div class="user-dropdown-header">

                    <strong>
                        ${escapeAuthHtml(name)}
                    </strong>

                    <span>
                        ${escapeAuthHtml(email)}
                    </span>

                </div>


                <a href="/dashboard.html">

                    <i class="fa-solid fa-gauge"></i>

                    Dashboard

                </a>


                <a href="/chat.html">

                    <i class="fa-solid fa-comments"></i>

                    AI Assistant

                </a>


                <a href="/planner.html">

                    <i class="fa-solid fa-map"></i>

                    Plan a Trip

                </a>


                <button
                    type="button"
                    class="logout-item"
                    id="globalLogoutButton"
                >

                    <i class="fa-solid fa-right-from-bracket"></i>

                    Logout

                </button>

            </div>

        </div>
    `;


    const menuButton =
        document.getElementById(
            "userMenuButton"
        );

    const dropdown =
        document.getElementById(
            "userDropdown"
        );

    const logoutButton =
        document.getElementById(
            "globalLogoutButton"
        );


    menuButton?.addEventListener(
        "click",
        event => {

            event.stopPropagation();

            dropdown?.classList.toggle(
                "show"
            );

        }
    );


    logoutButton?.addEventListener(
        "click",
        logoutUser
    );


    document.addEventListener(
        "click",
        event => {

            if (
                !event.target.closest(
                    ".user-menu"
                )
            ) {

                dropdown?.classList.remove(
                    "show"
                );

            }

        }
    );
}

// Escape special characters before inserting user data into HTML.

function escapeAuthHtml(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Check the current authentication token and update the page accordingly.

async function initializeAuthState() {

    const token =
        getAuthToken();

    // If there is no saved token, show the logged-out navigation.

    if (!token) {

        renderLoggedOut();

        return;
    }

    // Show the cached user immediately while the backend verifies the token.

    const cachedUser =
        getSavedUser();

    if (cachedUser) {

        renderLoggedIn(
            cachedUser
        );
    }

    // Verify the saved token with the backend.

    try {

        const response =
            await fetch(
                AUTH_ME_ENDPOINT,
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            localStorage.removeItem(
                AUTH_TOKEN_KEY
            );

            localStorage.removeItem(
                AUTH_USER_KEY
            );

            renderLoggedOut();

            return;
        }


        const data =
            await response.json();


        if (
            !data.success ||
            !data.user
        ) {

            renderLoggedOut();

            return;
        }

        // Save the latest user information for future page loads.

        localStorage.setItem(
            AUTH_USER_KEY,
            JSON.stringify(
                data.user
            )
        );


        renderLoggedIn(
            data.user
        );


    } catch (error) {

        console.error(
            "Auth state error:",
            error
        );

        // Keep the cached user visible if the backend is temporarily unavailable.

        if (!cachedUser) {

            renderLoggedOut();

        }

    }
}

// Initialize authentication handling after the page has loaded.

document.addEventListener(
    "DOMContentLoaded",
    initializeAuthState
);
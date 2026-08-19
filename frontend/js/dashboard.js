/* =========================================================
   TRAVELMATE DASHBOARD
========================================================= */

const AUTH_API = "/api/auth";

const TOKEN_KEY = "travelmate_token";
const USER_KEY = "travelmate_user";


/* =========================================================
   ELEMENTS
========================================================= */

const userName =
    document.getElementById("userName");

const userEmail =
    document.getElementById("userEmail");

const logoutBtn =
    document.getElementById("logoutBtn");


/* =========================================================
   GET TOKEN
========================================================= */

function getToken() {

    return localStorage.getItem(
        TOKEN_KEY
    );
}


/* =========================================================
   LOAD USER
========================================================= */

async function loadUser() {

    const token = getToken();


    /*
     * No token → not logged in
     */

    if (!token) {

        window.location.href =
            "/auth.html";

        return;
    }


    try {

        const response =
            await fetch(
                `${AUTH_API}/me`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        /*
         * Token expired/invalid
         */

        if (!response.ok) {

            logout();

            return;
        }


        const data =
            await response.json();


        if (
            !data.success ||
            !data.user
        ) {

            logout();

            return;
        }


        /*
         * Update local user
         */

        localStorage.setItem(
            USER_KEY,
            JSON.stringify(data.user)
        );


        displayUser(
            data.user
        );


    } catch (error) {

        console.error(
            "Dashboard authentication error:",
            error
        );

        alert(
            "Unable to load your account."
        );

    }

}


/* =========================================================
   DISPLAY USER
========================================================= */

function displayUser(user) {

    if (userName) {

        userName.textContent =
            user.name || "Traveler";

    }


    if (userEmail) {

        userEmail.textContent =
            user.email || "";

    }


    const initials =
        document.getElementById(
            "userInitials"
        );


    if (initials) {

        initials.textContent =
            getInitials(
                user.name
            );

    }

}


/* =========================================================
   INITIALS
========================================================= */

function getInitials(name) {

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


/* =========================================================
   LOGOUT
========================================================= */

function logout() {

    localStorage.removeItem(
        TOKEN_KEY
    );

    localStorage.removeItem(
        USER_KEY
    );

    window.location.href =
        "/auth.html";
}


/* =========================================================
   LOGOUT BUTTON
========================================================= */

logoutBtn?.addEventListener(
    "click",
    () => {

        if (
            confirm(
                "Are you sure you want to logout?"
            )
        ) {

            logout();

        }

    }
);


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    loadUser
);
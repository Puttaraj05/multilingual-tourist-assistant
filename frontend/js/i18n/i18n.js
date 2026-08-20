(function () {

    "use strict";

    const STORAGE_KEY = "travelmate_language";

    const DEFAULT_LANGUAGE = "en";

    const SUPPORTED_LANGUAGES = [
        "en",
        "hi",
        "te"
    ];

    // =====================================================
    // GET CURRENT LANGUAGE
    // =====================================================

    function getCurrentLanguage() {

        const savedLanguage =
            localStorage.getItem(STORAGE_KEY);

        if (
            savedLanguage &&
            SUPPORTED_LANGUAGES.includes(savedLanguage)
        ) {
            return savedLanguage;
        }

        return DEFAULT_LANGUAGE;
    }


    // =====================================================
    // SET LANGUAGE
    // =====================================================

    function setLanguage(language) {

        if (
            !SUPPORTED_LANGUAGES.includes(language)
        ) {
            console.warn(
                "Unsupported TravelMate language:",
                language
            );

            return;
        }

        localStorage.setItem(
            STORAGE_KEY,
            language
        );

        applyTranslations(language);
    }


    // =====================================================
    // GET TRANSLATION
    // =====================================================

    function getTranslation(
        dictionary,
        key
    ) {

        return key
            .split(".")
            .reduce(
                (object, property) =>
                    object &&
                    object[property],
                dictionary
            );
    }


    // =====================================================
    // APPLY TRANSLATIONS
    // =====================================================

    function applyTranslations(language) {

        const dictionary =
            window.TRANSLATIONS &&
            window.TRANSLATIONS[language];

        if (!dictionary) {

            console.warn(
                "Translation dictionary not found:",
                language
            );

            return;
        }


        // -------------------------------------------------
        // TEXT CONTENT
        // -------------------------------------------------

        document
            .querySelectorAll(
                "[data-i18n]"
            )
            .forEach(element => {

                const key =
                    element.dataset.i18n;

                const translated =
                    getTranslation(
                        dictionary,
                        key
                    );

                if (
                    translated !== undefined
                ) {
                    element.textContent =
                        translated;
                }
            });


        // -------------------------------------------------
        // PLACEHOLDERS
        // -------------------------------------------------

        document
            .querySelectorAll(
                "[data-i18n-placeholder]"
            )
            .forEach(element => {

                const key =
                    element.dataset
                        .i18nPlaceholder;

                const translated =
                    getTranslation(
                        dictionary,
                        key
                    );

                if (
                    translated !== undefined
                ) {
                    element.placeholder =
                        translated;
                }
            });


        // -------------------------------------------------
        // TITLE ATTRIBUTES
        // -------------------------------------------------

        document
            .querySelectorAll(
                "[data-i18n-title]"
            )
            .forEach(element => {

                const key =
                    element.dataset.i18nTitle;

                const translated =
                    getTranslation(
                        dictionary,
                        key
                    );

                if (
                    translated !== undefined
                ) {
                    element.title =
                        translated;
                }
            });


        // -------------------------------------------------
        // HTML LANGUAGE ATTRIBUTE
        // -------------------------------------------------

        document.documentElement.lang =
            language;


        // -------------------------------------------------
        // UPDATE LANGUAGE SELECTOR
        // -------------------------------------------------

        const selector =
            document.getElementById(
                "globalLanguageSelector"
            );

        if (selector) {
            selector.value =
                language;
        }


        console.log(
            `TravelMate language: ${language}`
        );
    }


    // =====================================================
    // INITIALIZE
    // =====================================================

    function initialize() {

        const language =
            getCurrentLanguage();

        applyTranslations(language);


        const selector =
            document.getElementById(
                "globalLanguageSelector"
            );

        if (selector) {

            selector.value =
                language;

            selector.addEventListener(
                "change",
                function () {

                    setLanguage(
                        this.value
                    );
                }
            );
        }
    }


    // =====================================================
    // PUBLIC API
    // =====================================================

    window.TravelMateI18n = {

        getLanguage:
            getCurrentLanguage,

        setLanguage:
            setLanguage,

        applyTranslations:
            applyTranslations,

        getTranslation:
            getTranslation,

        supportedLanguages:
            SUPPORTED_LANGUAGES
    };


    // =====================================================
    // DOM READY
    // =====================================================

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initialize
        );

    } else {

        initialize();
    }

})();
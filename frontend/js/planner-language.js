/* =========================================================
   TRAVELMATE — PLANNER LANGUAGE
   Changes planner UI text when language is selected
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const languageInput =
        document.getElementById("language");

    if (!languageInput) {
        console.error("Language input not found.");
        return;
    }


    /* =====================================================
       TRANSLATIONS
       ===================================================== */

    const translations = {

        English: {
            title: "PLAN YOUR JOURNEY",
            subtitle: "Tell us a little about your trip",
            languageLabel: "Language",
            destination: "Destination",
            destinationPlaceholder: "Country or city...",
            duration: "Trip Duration",
            date: "Travel Date",
            budget: "Budget",
            budgetPlaceholder: "Enter amount",
            travelType: "Who's Travelling?",
            child: "Travelling with a Child Under 12?",
            yes: "Yes",
            tripStyle: "Trip Style",
            interests: "Interests",
            continue: "Generate My Itinerary",

            solo: "Solo",
            couple: "Couple",
            family: "Family",
            friends: "Friends",

            relaxed: "Relaxed",
            relaxedDesc:
                "Fewer places with more time at each stop.",

            balanced: "Balanced",
            balancedDesc:
                "A mix of sightseeing and breaks.",

            packed: "Packed",
            packedDesc:
                "Fit in as many attractions as possible.",

            food: "Food",
            history: "History",
            culture: "Culture",
            shopping: "Shopping",
            nature: "Nature",
            adventure: "Adventure",
            nightlife: "Nightlife",
            photography: "Photography"
        },


        Hindi: {
            title: "अपनी यात्रा की योजना बनाएं",
            subtitle: "अपनी यात्रा के बारे में कुछ जानकारी दें",
            languageLabel: "भाषा",
            destination: "गंतव्य",
            destinationPlaceholder: "देश या शहर...",
            duration: "यात्रा की अवधि",
            date: "यात्रा की तारीख",
            budget: "बजट",
            budgetPlaceholder: "राशि दर्ज करें",
            travelType: "कौन यात्रा कर रहा है?",
            child: "क्या 12 साल से कम उम्र का बच्चा साथ है?",
            yes: "हाँ",
            tripStyle: "यात्रा शैली",
            interests: "रुचियाँ",
            continue: "मेरी यात्रा योजना बनाएं",

            solo: "अकेले",
            couple: "जोड़ा",
            family: "परिवार",
            friends: "दोस्त",

            relaxed: "आरामदायक",
            relaxedDesc:
                "कम स्थानों पर जाएं और प्रत्येक स्थान पर अधिक समय बिताएं।",

            balanced: "संतुलित",
            balancedDesc:
                "दर्शनीय स्थलों और आराम का संतुलित मिश्रण।",

            packed: "व्यस्त",
            packedDesc:
                "जितने संभव हों उतने आकर्षण शामिल करें।",

            food: "भोजन",
            history: "इतिहास",
            culture: "संस्कृति",
            shopping: "खरीदारी",
            nature: "प्रकृति",
            adventure: "साहसिक गतिविधियाँ",
            nightlife: "नाइटलाइफ़",
            photography: "फोटोग्राफी"
        },


        Telugu: {
            title: "మీ ప్రయాణాన్ని ప్లాన్ చేసుకోండి",
            subtitle: "మీ ప్రయాణం గురించి కొంత సమాచారం ఇవ్వండి",
            languageLabel: "భాష",
            destination: "గమ్యస్థానం",
            destinationPlaceholder: "దేశం లేదా నగరం...",
            duration: "ప్రయాణ వ్యవధి",
            date: "ప్రయాణ తేదీ",
            budget: "బడ్జెట్",
            budgetPlaceholder: "మొత్తాన్ని నమోదు చేయండి",
            travelType: "ఎవరు ప్రయాణిస్తున్నారు?",
            child: "12 సంవత్సరాల లోపు పిల్లలు ఉన్నారా?",
            yes: "అవును",
            tripStyle: "ప్రయాణ శైలి",
            interests: "ఆసక్తులు",
            continue: "నా ప్రయాణ ప్రణాళికను రూపొందించండి",

            solo: "ఒంటరిగా",
            couple: "జంట",
            family: "కుటుంబం",
            friends: "స్నేహితులు",

            relaxed: "ప్రశాంతమైన",
            relaxedDesc:
                "తక్కువ ప్రదేశాలను సందర్శించి ప్రతి ప్రదేశంలో ఎక్కువ సమయం గడపండి.",

            balanced: "సమతుల్య",
            balancedDesc:
                "సందర్శనా స్థలాలు మరియు విశ్రాంతి కలయిక.",

            packed: "వేగవంతమైన",
            packedDesc:
                "సాధ్యమైనన్ని ఎక్కువ ఆకర్షణలను సందర్శించండి.",

            food: "ఆహారం",
            history: "చరిత్ర",
            culture: "సంస్కృతి",
            shopping: "షాపింగ్",
            nature: "ప్రకృతి",
            adventure: "సాహసం",
            nightlife: "నైట్‌లైఫ్",
            photography: "ఫోటోగ్రఫీ"
        },


        Kannada: {
            title: "ನಿಮ್ಮ ಪ್ರಯಾಣವನ್ನು ಯೋಜಿಸಿ",
            subtitle: "ನಿಮ್ಮ ಪ್ರಯಾಣದ ಬಗ್ಗೆ ಸ್ವಲ್ಪ ಮಾಹಿತಿ ನೀಡಿ",
            languageLabel: "ಭಾಷೆ",
            destination: "ಗಮ್ಯಸ್ಥಾನ",
            destinationPlaceholder: "ದೇಶ ಅಥವಾ ನಗರ...",
            duration: "ಪ್ರಯಾಣದ ಅವಧಿ",
            date: "ಪ್ರಯಾಣದ ದಿನಾಂಕ",
            budget: "ಬಜೆಟ್",
            budgetPlaceholder: "ಮೊತ್ತವನ್ನು ನಮೂದಿಸಿ",
            travelType: "ಯಾರು ಪ್ರಯಾಣಿಸುತ್ತಿದ್ದಾರೆ?",
            child: "12 ವರ್ಷದೊಳಗಿನ ಮಗು ಜೊತೆಯಲ್ಲಿದೆಯೇ?",
            yes: "ಹೌದು",
            tripStyle: "ಪ್ರಯಾಣ ಶೈಲಿ",
            interests: "ಆಸಕ್ತಿಗಳು",
            continue: "ನನ್ನ ಪ್ರಯಾಣ ಯೋಜನೆಯನ್ನು ರಚಿಸಿ",

            solo: "ಏಕಾಂಗಿಯಾಗಿ",
            couple: "ಜೋಡಿ",
            family: "ಕುಟುಂಬ",
            friends: "ಸ್ನೇಹಿತರು",

            relaxed: "ವಿಶ್ರಾಂತಿಯ",
            relaxedDesc:
                "ಕಡಿಮೆ ಸ್ಥಳಗಳನ್ನು ಭೇಟಿ ಮಾಡಿ ಪ್ರತಿ ಸ್ಥಳದಲ್ಲಿ ಹೆಚ್ಚು ಸಮಯ ಕಳೆಯಿರಿ.",

            balanced: "ಸಮತೋಲನ",
            balancedDesc:
                "ಸಂದರ್ಶನ ಮತ್ತು ವಿಶ್ರಾಂತಿಯ ಸಮತೋಲನ.",

            packed: "ತುಂಬಿದ",
            packedDesc:
                "ಸಾಧ್ಯವಾದಷ್ಟು ಹೆಚ್ಚು ಆಕರ್ಷಣೆಗಳನ್ನು ಸೇರಿಸಿ.",

            food: "ಆಹಾರ",
            history: "ಇತಿಹಾಸ",
            culture: "ಸಂಸ್ಕೃತಿ",
            shopping: "ಶಾಪಿಂಗ್",
            nature: "ಪ್ರಕೃತಿ",
            adventure: "ಸಾಹಸ",
            nightlife: "ರಾತ್ರಿಜೀವನ",
            photography: "ಛಾಯಾಗ್ರಹಣ"
        }

    };


    /* =====================================================
       APPLY TRANSLATION
       ===================================================== */

    function applyLanguage(language) {

        const selected =
            translations[language];

        if (!selected) {
            return;
        }


        /* -----------------------------------------------
           Elements with data-key
           IMPORTANT:
           Use textContent =
           NEVER use +=
           ----------------------------------------------- */

        document
            .querySelectorAll("[data-key]")
            .forEach(element => {

                const key =
                    element.dataset.key;

                if (
                    selected[key] !== undefined
                ) {

                    element.textContent =
                        selected[key];

                }

            });


        /* -----------------------------------------------
           Placeholders
           ----------------------------------------------- */

        const destination =
            document.getElementById(
                "destination"
            );

        if (destination) {

            destination.placeholder =
                selected.destinationPlaceholder
                || "Country or city...";

        }


        const budget =
            document.getElementById(
                "budget"
            );

        if (budget) {

            budget.placeholder =
                selected.budgetPlaceholder
                || "Enter amount";

        }


        /* -----------------------------------------------
           Travel type
           ----------------------------------------------- */

        const travelCards =
            document.querySelectorAll(
                'input[name="travelType"]'
            );

        travelCards.forEach(input => {

            const key =
                input.value.toLowerCase();

            const span =
                input.parentElement
                    ?.querySelector("span");

            if (
                span &&
                selected[key]
            ) {

                span.textContent =
                    selected[key];

            }

        });


        /* -----------------------------------------------
           Trip style
           ----------------------------------------------- */

        const tripStyles = {

            Relaxed: "relaxed",
            Balanced: "balanced",
            Packed: "packed"

        };

        document
            .querySelectorAll(
                'input[name="tripStyle"]'
            )
            .forEach(input => {

                const key =
                    tripStyles[input.value];

                const span =
                    input.parentElement
                        ?.querySelector("span");

                if (!span || !key) {
                    return;
                }


                const small =
                    span.querySelector("small");


                /* Remove only existing text nodes
                   but preserve <small> */

                Array.from(
                    span.childNodes
                )
                .filter(
                    node =>
                        node.nodeType ===
                        Node.TEXT_NODE
                )
                .forEach(
                    node =>
                        node.remove()
                );


                span.insertBefore(
                    document.createTextNode(
                        ` ${selected[key]} `
                    ),
                    small
                );


                if (small) {

                    small.textContent =
                        selected[
                            `${key}Desc`
                        ] || "";

                }

            });


        /* -----------------------------------------------
           Interests
           ----------------------------------------------- */

        document
            .querySelectorAll(
                'input[name="interest"]'
            )
            .forEach(input => {

                const key =
                    input.value.toLowerCase();

                const label =
                    input.parentElement;

                if (
                    label &&
                    selected[key]
                ) {

                    /* Keep checkbox */

                    const checkbox =
                        label.querySelector(
                            "input"
                        );


                    /* Remove text nodes */

                    Array.from(
                        label.childNodes
                    )
                    .filter(
                        node =>
                            node.nodeType ===
                            Node.TEXT_NODE
                    )
                    .forEach(
                        node =>
                            node.remove()
                    );


                    label.appendChild(
                        document.createTextNode(
                            ` ${selected[key]}`
                        )
                    );

                }

            });


        /* -----------------------------------------------
           HTML language attribute
           ----------------------------------------------- */

        document.documentElement.lang =
            language.toLowerCase();

    }


    /* =====================================================
       LANGUAGE CHANGE
       ===================================================== */

    languageInput.addEventListener(
        "change",
        () => {

            const language =
                languageInput.value.trim();

            applyLanguage(language);

        }
    );


    languageInput.addEventListener(
        "input",
        () => {

            const language =
                languageInput.value.trim();

            if (
                translations[language]
            ) {

                applyLanguage(language);

            }

        }
    );


    /* =====================================================
       INITIAL LANGUAGE
       ===================================================== */

    applyLanguage(
        languageInput.value || "English"
    );

});
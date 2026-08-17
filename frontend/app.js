/* =========================================================
   TRAVELAI — FASTAPI + MONGODB FRONTEND
   ========================================================= */


/* =========================================================
   STATE
   ========================================================= */

const state = {

    language:
        localStorage.getItem(
            "travelaiLanguage"
        ) || "en",

    country:
        localStorage.getItem(
            "travelaiCountry"
        ) || "IN",

    location: null,

    contacts: []

};


/* =========================================================
   HELPER
   ========================================================= */

function $(id) {

    return document.getElementById(id);

}


function t(key) {

    return (
        translations[
            state.language
        ]?.[key]

        ||

        translations.en[key]

        ||

        key
    );

}


function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,

        character => ({

            "&":
                "&amp;",

            "<":
                "&lt;",

            ">":
                "&gt;",

            '"':
                "&quot;",

            "'":
                "&#039;"

        })[character]
    );

}


function toast(message) {

    const element =
        $("toast");

    if (!element) return;


    element.textContent =
        message;


    element.classList.add(
        "show"
    );


    setTimeout(
        () => {

            element.classList.remove(
                "show"
            );

        },
        3000
    );

}


/* =========================================================
   TRANSLATIONS
   ========================================================= */

const translations = {

    en: {

        title:
            "TravelAI — Emergency Support",

        eyebrow:
            "EMERGENCY TRAVEL SUPPORT",

        heroLine1:
            "Help when you",

        heroLine2:
            "need it most.",

        heroDesc:
            "Quick access to local emergency services, location sharing, incident logging and multilingual emergency phrases.",

        sos:
            "🚨 SOS — GET HELP",

        shareLocation:
            "📍 Share My Location",

        prototypeNote:
            "This prototype does not dispatch emergency services automatically. In a real emergency, call the local emergency number shown below.",

        safetyStatus:
            "Safety status",

        locationNotShared:
            "Location not shared",

        locationShared:
            "Location captured",

        locationPrivacy:
            "Your location stays in this browser unless you submit an SOS or incident.",

        emergencyContacts:
            "Emergency contacts",

        chooseCountry:
            "Choose your current country.",

        refresh:
            "Refresh",

        emergencyActions:
            "Emergency actions",

        oneTap:
            "One-tap tools for common situations.",

        medicalHelp:
            "Medical help",

        openAmbulance:
            "Open ambulance contact",

        unsafe:
            "I'm unsafe",

        openPolice:
            "Open police contact",

        lost:
            "I'm lost",

        shareCurrentLocation:
            "Share current location",

        lostDocuments:
            "Lost documents",

        recordIncident:
            "Record an incident",

        phrasesTitle:
            "Multilingual emergency phrases",

        phrasesDesc:
            "Click a phrase to hear it.",

        reportIncident:
            "Report an incident",

        saveDetails:
            "Save details to your support log.",

        incidentType:
            "Type",

        medical:
            "Medical",

        lostStranded:
            "Lost / stranded",

        theft:
            "Theft",

        unsafeSituation:
            "Unsafe situation",

        lostDocument:
            "Lost document",

        other:
            "Other",

        description:
            "Description",

        descriptionPlaceholder:
            "What happened?",

        saveIncident:
            "Save incident",

        recentLog:
            "Recent support log",

        recentLogDesc:
            "Incidents recorded by this demo application.",

        sosActivated:
            "SOS activated",

        sosLogged:
            "SOS was logged. Call the local emergency service now.",

        understand:
            "I understand",

        noContacts:
            "No contacts configured for this country.",

        noLogs:
            "No incidents recorded yet.",

        locationDenied:
            "Location permission was not granted.",

        locationReady:
            "Location captured and ready to share.",

        locationRequired:
            "Please allow location access first.",

        saved:
            "Incident saved successfully.",

        mapsOpened:
            "Your location has been opened in Google Maps.",

        browserSpeech:
            "Speech is not supported by this browser.",

        databaseError:
            "Unable to connect to the backend database.",

        emergencyNumber:
            "Emergency number",

        call:
            "Call",

        open:
            "Open",

        incident:
            "Incident",

        noLocation:
            "No location attached"

    },


    hi: {

        title:
            "TravelAI — आपातकालीन सहायता",

        eyebrow:
            "फीचर 5 · आपातकालीन यात्रा सहायता",

        heroLine1:
            "जब आपको",

        heroLine2:
            "सबसे अधिक मदद चाहिए।",

        heroDesc:
            "स्थानीय आपातकालीन सेवाओं, लोकेशन साझा करने, घटना दर्ज करने और बहुभाषी आपातकालीन वाक्यों तक तुरंत पहुँच।",

        sos:
            "🚨 SOS — मदद लें",

        shareLocation:
            "📍 मेरी लोकेशन साझा करें",

        prototypeNote:
            "यह प्रोटोटाइप अपने आप आपातकालीन सेवाओं को नहीं बुलाता। वास्तविक आपातकाल में नीचे दिए स्थानीय नंबर पर कॉल करें।",

        safetyStatus:
            "सुरक्षा स्थिति",

        locationNotShared:
            "लोकेशन साझा नहीं की गई",

        locationShared:
            "लोकेशन प्राप्त हो गई",

        locationPrivacy:
            "आपकी लोकेशन इसी ब्राउज़र में रहती है जब तक आप SOS या घटना सबमिट नहीं करते।",

        emergencyContacts:
            "आपातकालीन संपर्क",

        chooseCountry:
            "अपना वर्तमान देश चुनें।",

        refresh:
            "रीफ्रेश",

        emergencyActions:
            "आपातकालीन कार्य",

        oneTap:
            "सामान्य स्थितियों के लिए एक-टैप टूल।",

        medicalHelp:
            "चिकित्सा सहायता",

        openAmbulance:
            "एम्बुलेंस संपर्क खोलें",

        unsafe:
            "मैं सुरक्षित नहीं हूँ",

        openPolice:
            "पुलिस संपर्क खोलें",

        lost:
            "मैं रास्ता भटक गया हूँ",

        shareCurrentLocation:
            "वर्तमान लोकेशन साझा करें",

        lostDocuments:
            "दस्तावेज़ खो गए",

        recordIncident:
            "घटना दर्ज करें",

        phrasesTitle:
            "बहुभाषी आपातकालीन वाक्य",

        phrasesDesc:
            "वाक्य सुनने के लिए क्लिक करें।",

        reportIncident:
            "घटना की रिपोर्ट करें",

        saveDetails:
            "अपनी सहायता लॉग में विवरण सहेजें।",

        incidentType:
            "प्रकार",

        medical:
            "चिकित्सा",

        lostStranded:
            "खोया / फँसा हुआ",

        theft:
            "चोरी",

        unsafeSituation:
            "असुरक्षित स्थिति",

        lostDocument:
            "खोया दस्तावेज़",

        other:
            "अन्य",

        description:
            "विवरण",

        descriptionPlaceholder:
            "क्या हुआ?",

        saveIncident:
            "घटना सहेजें",

        recentLog:
            "हाल की सहायता लॉग",

        recentLogDesc:
            "इस डेमो एप्लिकेशन द्वारा दर्ज घटनाएँ।",

        sosActivated:
            "SOS सक्रिय",

        sosLogged:
            "SOS दर्ज किया गया है। अभी स्थानीय आपातकालीन सेवा को कॉल करें।",

        understand:
            "मैं समझता हूँ",

        noContacts:
            "इस देश के लिए कोई संपर्क उपलब्ध नहीं है।",

        noLogs:
            "अभी कोई घटना दर्ज नहीं है।",

        locationDenied:
            "लोकेशन की अनुमति नहीं मिली।",

        locationReady:
            "लोकेशन प्राप्त हो गई और साझा करने के लिए तैयार है।",

        locationRequired:
            "कृपया पहले लोकेशन की अनुमति दें।",

        saved:
            "घटना सफलतापूर्वक सहेजी गई।",

        mapsOpened:
            "आपकी लोकेशन Google Maps में खोली गई है।",

        browserSpeech:
            "इस ब्राउज़र में आवाज़ समर्थित नहीं है।",

        databaseError:
            "बैकएंड डेटाबेस से कनेक्ट नहीं हो सका।",

        emergencyNumber:
            "आपातकालीन नंबर",

        call:
            "कॉल",

        open:
            "खोलें",

        incident:
            "घटना",

        noLocation:
            "कोई लोकेशन संलग्न नहीं है"

    },


    te: {

        title:
            "TravelAI — అత్యవసర సహాయం",

        eyebrow:
            "ఫీచర్ 5 · అత్యవసర ప్రయాణ సహాయం",

        heroLine1:
            "మీకు",

        heroLine2:
            "అత్యంత అవసరమైనప్పుడు సహాయం.",

        heroDesc:
            "స్థానిక అత్యవసర సేవలు, లొకేషన్ షేరింగ్, సంఘటన నమోదు మరియు బహుభాషా అత్యవసర వాక్యాలకు త్వరిత ప్రాప్యత.",

        sos:
            "🚨 SOS — సహాయం పొందండి",

        shareLocation:
            "📍 నా లొకేషన్ షేర్ చేయండి",

        prototypeNote:
            "ఈ ప్రోటోటైప్ స్వయంచాలకంగా అత్యవసర సేవలకు కాల్ చేయదు. నిజమైన అత్యవసర పరిస్థితిలో క్రింద ఉన్న స్థానిక నంబర్‌కు కాల్ చేయండి.",

        safetyStatus:
            "భద్రత స్థితి",

        locationNotShared:
            "లొకేషన్ షేర్ కాలేదు",

        locationShared:
            "లొకేషన్ పొందబడింది",

        locationPrivacy:
            "మీరు SOS లేదా సంఘటనను పంపే వరకు మీ లొకేషన్ ఈ బ్రౌజర్‌లోనే ఉంటుంది.",

        emergencyContacts:
            "అత్యవసర సంప్రదింపులు",

        chooseCountry:
            "మీ ప్రస్తుత దేశాన్ని ఎంచుకోండి.",

        refresh:
            "రిఫ్రెష్",

        emergencyActions:
            "అత్యవసర చర్యలు",

        oneTap:
            "సాధారణ పరిస్థితుల కోసం వన్-ట్యాప్ టూల్స్.",

        medicalHelp:
            "వైద్య సహాయం",

        openAmbulance:
            "అంబులెన్స్ సంప్రదింపు తెరవండి",

        unsafe:
            "నేను సురక్షితంగా లేను",

        openPolice:
            "పోలీస్ సంప్రదింపు తెరవండి",

        lost:
            "నేను దారి తప్పాను",

        shareCurrentLocation:
            "ప్రస్తుత లొకేషన్ షేర్ చేయండి",

        lostDocuments:
            "పత్రాలు పోయాయి",

        recordIncident:
            "సంఘటన నమోదు చేయండి",

        phrasesTitle:
            "బహుభాషా అత్యవసర వాక్యాలు",

        phrasesDesc:
            "వాక్యం వినడానికి క్లిక్ చేయండి.",

        reportIncident:
            "సంఘటనను నివేదించండి",

        saveDetails:
            "మీ సహాయ లాగ్‌లో వివరాలను సేవ్ చేయండి.",

        incidentType:
            "రకం",

        medical:
            "వైద్యం",

        lostStranded:
            "దారి తప్పడం / చిక్కుకుపోవడం",

        theft:
            "దొంగతనం",

        unsafeSituation:
            "అసురక్షిత పరిస్థితి",

        lostDocument:
            "పత్రం పోయింది",

        other:
            "ఇతర",

        description:
            "వివరణ",

        descriptionPlaceholder:
            "ఏం జరిగింది?",

        saveIncident:
            "సంఘటనను సేవ్ చేయండి",

        recentLog:
            "ఇటీవలి సహాయ లాగ్",

        recentLogDesc:
            "ఈ డెమో అప్లికేషన్‌లో నమోదు చేసిన సంఘటనలు.",

        sosActivated:
            "SOS యాక్టివేట్ అయింది",

        sosLogged:
            "SOS నమోదు అయింది. ఇప్పుడు స్థానిక అత్యవసర సేవకు కాల్ చేయండి.",

        understand:
            "నాకు అర్థమైంది",

        noContacts:
            "ఈ దేశానికి సంప్రదింపులు అందుబాటులో లేవు.",

        noLogs:
            "ఇంకా సంఘటనలు నమోదు కాలేదు.",

        locationDenied:
            "లొకేషన్ అనుమతి ఇవ్వలేదు.",

        locationReady:
            "లొకేషన్ పొందబడింది మరియు షేర్ చేయడానికి సిద్ధంగా ఉంది.",

        locationRequired:
            "ముందుగా లొకేషన్ అనుమతించండి.",

        saved:
            "సంఘటన విజయవంతంగా సేవ్ అయింది.",

        mapsOpened:
            "మీ లొకేషన్ Google Mapsలో తెరవబడింది.",

        browserSpeech:
            "ఈ బ్రౌజర్‌లో వాయిస్ సపోర్ట్ లేదు.",

        databaseError:
            "బ్యాకెండ్ డేటాబేస్‌కు కనెక్ట్ కాలేకపోయింది.",

        emergencyNumber:
            "అత్యవసర నంబర్",

        call:
            "కాల్",

        open:
            "తెరవండి",

        incident:
            "సంఘటన",

        noLocation:
            "లొకేషన్ జోడించలేదు"

    },


    ta: {

        title:
            "TravelAI — அவசர உதவி",

        eyebrow:
            "அம்சம் 5 · அவசர பயண உதவி",

        heroLine1:
            "உங்களுக்கு",

        heroLine2:
            "மிகவும் தேவைப்படும் போது உதவி.",

        heroDesc:
            "உள்ளூர் அவசர சேவைகள், இருப்பிடப் பகிர்வு, சம்பவப் பதிவு மற்றும் பலமொழி அவசர சொற்றொடர்களை விரைவாக அணுகலாம்.",

        sos:
            "🚨 SOS — உதவி பெறுங்கள்",

        shareLocation:
            "📍 எனது இருப்பிடத்தைப் பகிரவும்",

        prototypeNote:
            "இந்த முன்மாதிரி தானாக அவசர சேவைகளை அழைக்காது. உண்மையான அவசரநிலையில் கீழே காட்டப்படும் உள்ளூர் எண்ணை அழைக்கவும்.",

        safetyStatus:
            "பாதுகாப்பு நிலை",

        locationNotShared:
            "இருப்பிடம் பகிரப்படவில்லை",

        locationShared:
            "இருப்பிடம் பெறப்பட்டது",

        locationPrivacy:
            "SOS அல்லது சம்பவத்தை சமர்ப்பிக்கும் வரை உங்கள் இருப்பிடம் இந்த உலாவியில் மட்டுமே இருக்கும்.",

        emergencyContacts:
            "அவசர தொடர்புகள்",

        chooseCountry:
            "உங்கள் தற்போதைய நாட்டைத் தேர்ந்தெடுக்கவும்.",

        refresh:
            "புதுப்பிக்கவும்",

        emergencyActions:
            "அவசர நடவடிக்கைகள்",

        oneTap:
            "பொதுவான சூழ்நிலைகளுக்கான ஒரே-தொடுதல் கருவிகள்.",

        medicalHelp:
            "மருத்துவ உதவி",

        openAmbulance:
            "ஆம்புலன்ஸ் தொடர்பைத் திறக்கவும்",

        unsafe:
            "நான் பாதுகாப்பாக இல்லை",

        openPolice:
            "காவல்துறை தொடர்பைத் திறக்கவும்",

        lost:
            "நான் வழி தவறிவிட்டேன்",

        shareCurrentLocation:
            "தற்போதைய இருப்பிடத்தைப் பகிரவும்",

        lostDocuments:
            "ஆவணங்கள் தொலைந்துவிட்டன",

        recordIncident:
            "சம்பவத்தைப் பதிவு செய்யவும்",

        phrasesTitle:
            "பலமொழி அவசர சொற்றொடர்கள்",

        phrasesDesc:
            "சொற்றொடரை கேட்க கிளிக் செய்யவும்.",

        reportIncident:
            "சம்பவத்தைப் புகாரளிக்கவும்",

        saveDetails:
            "உங்கள் உதவி பதிவில் விவரங்களைச் சேமிக்கவும்.",

        incidentType:
            "வகை",

        medical:
            "மருத்துவம்",

        lostStranded:
            "வழி தவறியது / சிக்கியது",

        theft:
            "திருட்டு",

        unsafeSituation:
            "பாதுகாப்பற்ற நிலை",

        lostDocument:
            "ஆவணம் தொலைந்தது",

        other:
            "மற்றவை",

        description:
            "விளக்கம்",

        descriptionPlaceholder:
            "என்ன நடந்தது?",

        saveIncident:
            "சம்பவத்தைச் சேமிக்கவும்",

        recentLog:
            "சமீபத்திய உதவி பதிவு",

        recentLogDesc:
            "இந்த முன்மாதிரி பயன்பாட்டில் பதிவு செய்யப்பட்ட சம்பவங்கள்.",

        sosActivated:
            "SOS செயல்படுத்தப்பட்டது",

        sosLogged:
            "SOS பதிவு செய்யப்பட்டது. இப்போது உள்ளூர் அவசர சேவையை அழைக்கவும்.",

        understand:
            "எனக்கு புரிந்தது",

        noContacts:
            "இந்த நாட்டிற்கு தொடர்புகள் இல்லை.",

        noLogs:
            "இதுவரை சம்பவங்கள் பதிவு செய்யப்படவில்லை.",

        locationDenied:
            "இருப்பிட அனுமதி வழங்கப்படவில்லை.",

        locationReady:
            "இருப்பிடம் பெறப்பட்டது; பகிர தயாராக உள்ளது.",

        locationRequired:
            "முதலில் இருப்பிட அனுமதியை வழங்கவும்.",

        saved:
            "சம்பவம் வெற்றிகரமாகச் சேமிக்கப்பட்டது.",

        mapsOpened:
            "உங்கள் இருப்பிடம் Google Mapsல் திறக்கப்பட்டது.",

        browserSpeech:
            "இந்த உலாவியில் குரல் ஆதரவு இல்லை.",

        databaseError:
            "பின்தள தரவுத்தளத்துடன் இணைக்க முடியவில்லை.",

        emergencyNumber:
            "அவசர எண்",

        call:
            "அழைக்கவும்",

        open:
            "திறக்கவும்",

        incident:
            "சம்பவம்",

        noLocation:
            "இருப்பிடம் இணைக்கப்படவில்லை"

    }

};


/* =========================================================
   COUNTRY NAMES
   ========================================================= */

const countryNames = {

    en: {

        IN:
            "India",

        AE:
            "United Arab Emirates",

        US:
            "United States",

        GB:
            "United Kingdom"

    },

    hi: {

        IN:
            "भारत",

        AE:
            "संयुक्त अरब अमीरात",

        US:
            "संयुक्त राज्य अमेरिका",

        GB:
            "यूनाइटेड किंगडम"

    },

    te: {

        IN:
            "భారతదేశం",

        AE:
            "యునైటెడ్ అరబ్ ఎమిరేట్స్",

        US:
            "యునైటెడ్ స్టేట్స్",

        GB:
            "యునైటెడ్ కింగ్‌డమ్"

    },

    ta: {

        IN:
            "இந்தியா",

        AE:
            "ஐக்கிய அரபு அமீரகம்",

        US:
            "அமெரிக்கா",

        GB:
            "ஐக்கிய இராச்சியம்"

    }

};


/* =========================================================
   PHRASES
   ========================================================= */

const phrases = {

    en: [

        "I need help.",

        "Please call an ambulance.",

        "Please call the police.",

        "I am lost."

    ],

    hi: [

        "मुझे मदद चाहिए।",

        "कृपया एम्बुलेंस बुलाइए।",

        "कृपया पुलिस को बुलाइए।",

        "मैं रास्ता भटक गया हूँ।"

    ],

    te: [

        "నాకు సహాయం కావాలి.",

        "దయచేసి అంబులెన్స్‌కు కాల్ చేయండి.",

        "దయచేసి పోలీసులకు కాల్ చేయండి.",

        "నేను దారి తప్పిపోయాను."

    ],

    ta: [

        "எனக்கு உதவி தேவை.",

        "தயவுசெய்து ஆம்புலன்ஸை அழைக்கவும்.",

        "தயவுசெய்து காவல்துறையை அழைக்கவும்.",

        "நான் வழி தவறிவிட்டேன்."

    ]

};


/* =========================================================
   APPLY LANGUAGE
   ========================================================= */

function applyLanguage() {

    document.documentElement.lang =
        state.language;


    document.title =
        t("title");


    document
        .querySelectorAll(
            "[data-i18n]"
        )
        .forEach(
            element => {

                element.textContent =
                    t(
                        element.dataset.i18n
                    );

            }
        );


    document
        .querySelectorAll(
            "[data-i18n-placeholder]"
        )
        .forEach(
            element => {

                element.placeholder =
                    t(
                        element.dataset
                            .i18nPlaceholder
                    );

            }
        );


    if ($("language")) {

        $("language").value =
            state.language;

    }


    if ($("phraseLanguage")) {

        $("phraseLanguage").value =
            state.language;

    }


    renderCountryOptions();

    renderPhrases();

    renderContacts();

    loadLogs();

}


/* =========================================================
   LANGUAGE CHANGE
   ========================================================= */

function changeLanguage(
    language
) {

    if (
        !translations[language]
    ) {

        language = "en";

    }


    state.language =
        language;


    localStorage.setItem(
        "travelaiLanguage",
        language
    );


    applyLanguage();

}


/* =========================================================
   COUNTRY OPTIONS
   ========================================================= */

function renderCountryOptions() {

    const select =
        $("country");


    if (!select) return;


    select.innerHTML =
        Object.keys(
            countryNames.en
        )
        .map(
            code => `

                <option value="${code}">
                    ${escapeHtml(
                        countryNames[
                            state.language
                        ][code]
                    )}
                </option>

            `
        )
        .join("");


    select.value =
        state.country;

}


/* =========================================================
   LOAD COUNTRIES FROM MONGODB THROUGH FASTAPI
   ========================================================= */

async function loadCountries() {

    try {

        const response =
            await fetch(
                "/api/countries"
            );


        if (!response.ok) {

            throw new Error(
                "Countries API failed."
            );

        }


        const countries =
            await response.json();


        const select =
            $("country");


        if (!select) return;


        select.innerHTML = "";


        countries.forEach(
            country => {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    country.code;


                option.textContent =
                    countryNames[
                        state.language
                    ]?.[
                        country.code
                    ]
                    ||
                    country.name;


                select.appendChild(
                    option
                );

            }
        );


        select.value =
            state.country;

    }

    catch (error) {

        console.error(
            error
        );

        renderCountryOptions();

    }

}


/* =========================================================
   LOAD CONTACTS
   ========================================================= */

async function loadContacts() {

    try {

        const response =
            await fetch(
                `/api/emergency-contacts?country=${encodeURIComponent(
                    state.country
                )}`
            );


        if (!response.ok) {

            throw new Error(
                "Contacts API failed."
            );

        }


        const data =
            await response.json();


        state.contacts =
            data.contacts || [];


        renderContacts();

    }

    catch (error) {

        console.error(
            error
        );


        state.contacts =
            [];


        renderContacts();


        toast(
            t("databaseError")
        );

    }

}


/* =========================================================
   RENDER CONTACTS
   ========================================================= */

function renderContacts() {

    const container =
        $("contacts");


    if (!container) return;


    if (
        !state.contacts.length
    ) {

        container.innerHTML = `

            <div class="empty">
                ${t("noContacts")}
            </div>

        `;

        return;

    }


    container.innerHTML =
        state.contacts
            .map(
                contact => `

                    <div class="contact">

                        <div>

                            <b>
                                ${escapeHtml(
                                    translateService(
                                        contact.service
                                    )
                                )}
                            </b>

                            <small>
                                ${escapeHtml(
                                    contact.description
                                )}
                            </small>

                        </div>


                        <a
                            class="call"
                            href="tel:${escapeHtml(
                                contact.number
                            )}"
                        >

                            ☎
                            ${escapeHtml(
                                contact.number
                            )}

                        </a>

                    </div>

                `
            )
            .join("");

}


/* =========================================================
   TRANSLATE SERVICE NAMES
   ========================================================= */

function translateService(
    service
) {

    const map = {

        en: {

            "Unified Emergency":
                "Unified Emergency",

            Police:
                "Police",

            Ambulance:
                "Ambulance",

            Fire:
                "Fire",

            "Alternative Emergency":
                "Alternative Emergency"

        },

        hi: {

            "Unified Emergency":
                "एकीकृत आपातकालीन सेवा",

            Police:
                "पुलिस",

            Ambulance:
                "एम्बुलेंस",

            Fire:
                "फायर सेवा",

            "Alternative Emergency":
                "वैकल्पिक आपातकालीन सेवा"

        },

        te: {

            "Unified Emergency":
                "ఏకీకృత అత్యవసర సేవ",

            Police:
                "పోలీస్",

            Ambulance:
                "అంబులెన్స్",

            Fire:
                "అగ్నిమాపక సేవ",

            "Alternative Emergency":
                "ప్రత్యామ్నాయ అత్యవసర సేవ"

        },

        ta: {

            "Unified Emergency":
                "ஒருங்கிணைந்த அவசர சேவை",

            Police:
                "காவல்துறை",

            Ambulance:
                "ஆம்புலன்ஸ்",

            Fire:
                "தீயணைப்பு சேவை",

            "Alternative Emergency":
                "மாற்று அவசர சேவை"

        }

    };


    return (
        map[
            state.language
        ]?.[service]

        ||

        service
    );

}


/* =========================================================
   PHRASES
   ========================================================= */

function renderPhrases() {

    const container =
        $("phrases");


    if (!container) return;


    const list =
        phrases[
            state.language
        ] || phrases.en;


    container.innerHTML = "";


    list.forEach(
        phrase => {

            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.className =
                "phrase";


            button.innerHTML = `

                <span>
                    🔊
                </span>

                <b>
                    ${escapeHtml(
                        phrase
                    )}
                </b>

            `;


            button.addEventListener(
                "click",
                () => {

                    speak(
                        phrase,
                        state.language
                    );

                }
            );


            container.appendChild(
                button
            );

        }
    );

}


/* =========================================================
   SPEECH
   ========================================================= */

function getSpeechLanguage(
    language
) {

    return {

        en:
            "en-US",

        hi:
            "hi-IN",

        te:
            "te-IN",

        ta:
            "ta-IN"

    }[
        language
    ] || "en-US";

}


function speak(
    text,
    language
) {

    if (
        !window.speechSynthesis
    ) {

        toast(
            t("browserSpeech")
        );

        return;

    }


    window.speechSynthesis.cancel();


    const utterance =
        new SpeechSynthesisUtterance(
            text
        );


    utterance.lang =
        getSpeechLanguage(
            language
        );


    utterance.rate =
        0.85;


    const voices =
        window.speechSynthesis
            .getVoices();


    const matchingVoice =
        voices.find(
            voice =>
                voice.lang
                    .toLowerCase()
                    .startsWith(
                        language
                    )
        );


    if (
        matchingVoice
    ) {

        utterance.voice =
            matchingVoice;

    }


    window.speechSynthesis.speak(
        utterance
    );

}


/* =========================================================
   GET LOCATION
   ========================================================= */

function getLocation() {

    return new Promise(
        (
            resolve,
            reject
        ) => {

            if (
                !navigator.geolocation
            ) {

                reject(
                    new Error(
                        "Geolocation is not supported."
                    )
                );

                return;

            }


            navigator.geolocation
                .getCurrentPosition(

                    position => {

                        state.location = {

                            latitude:
                                position
                                    .coords
                                    .latitude,

                            longitude:
                                position
                                    .coords
                                    .longitude,

                            accuracy:
                                position
                                    .coords
                                    .accuracy

                        };


                        resolve(
                            state.location
                        );

                    },


                    error => {

                        console.error(
                            error
                        );


                        reject(
                            new Error(
                                t(
                                    "locationDenied"
                                )
                            )
                        );

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

}


/* =========================================================
   SAVE LOCATION TO MONGODB
   ========================================================= */

async function saveLocation(
    location
) {

    const response =
        await fetch(
            "/api/location",
            {

                method:
                    "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify({

                        latitude:
                            location.latitude,

                        longitude:
                            location.longitude,

                        accuracy:
                            location.accuracy,

                        countryCode:
                            state.country

                    })

            }
        );


    if (!response.ok) {

        throw new Error(
            "Unable to save location."
        );

    }


    return response.json();

}


/* =========================================================
   SHARE LOCATION
   ========================================================= */

async function shareLocation() {

    try {

        const location =
            await getLocation();


        await saveLocation(
            location
        );


        $("status").textContent =
            t(
                "locationShared"
            );


        toast(
            `${location.latitude.toFixed(
                6
            )}, ${location.longitude.toFixed(
                6
            )}`
        );

    }

    catch (error) {

        toast(
            error.message
        );

    }

}


/* =========================================================
   SOS
   ========================================================= */

async function activateSOS() {

    const confirmed =
        window.confirm(
            "Activate SOS?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const location =
            state.location
            ||
            await getLocation();


        const response =
            await fetch(
                "/api/sos",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            latitude:
                                location.latitude,

                            longitude:
                                location.longitude,

                            accuracy:
                                location.accuracy,

                            countryCode:
                                state.country

                        })

                }
            );


        if (!response.ok) {

            throw new Error(
                "SOS request failed."
            );

        }


        const data =
            await response.json();


        showSOSModal(
            data.contacts || []
        );

    }

    catch (error) {

        console.error(
            error
        );


        toast(
            error.message
        );

    }

}


/* =========================================================
   SOS MODAL
   ========================================================= */

function showSOSModal(
    contacts
) {

    const modal =
        $("modal");


    const container =
        $("sosContacts");


    if (!modal) return;


    container.innerHTML = "";


    contacts.forEach(
        contact => {

            container.innerHTML += `

                <a
                    class="call full"
                    href="tel:${escapeHtml(
                        contact.number
                    )}"
                >

                    ☎

                    ${escapeHtml(
                        translateService(
                            contact.service
                        )
                    )}

                    -

                    ${escapeHtml(
                        contact.number
                    )}

                </a>

            `;

        }
    );


    modal.classList.remove(
        "hidden"
    );

}


function closeModal() {

    $("modal")
        ?.classList.add(
            "hidden"
        );

}


/* =========================================================
   EMERGENCY ACTIONS
   ========================================================= */

async function action(
    type
) {


    if (
        type === "medical"
    ) {

        const ambulance =
            state.contacts.find(
                contact =>
                    contact.service
                    === "Ambulance"
            );


        if (ambulance) {

            window.location.href =
                `tel:${ambulance.number}`;

        }

        else {

            toast(
                t("openAmbulance")
            );

        }


        return;

    }


    if (
        type === "unsafe"
    ) {

        const police =
            state.contacts.find(
                contact =>
                    contact.service
                    === "Police"
            )
            ||
            state.contacts.find(
                contact =>
                    contact.service
                    === "Unified Emergency"
            );


        if (police) {

            window.location.href =
                `tel:${police.number}`;

        }

        else {

            toast(
                t("openPolice")
            );

        }


        return;

    }


    if (
        type === "lost"
    ) {

        try {

            const location =
                state.location
                ||
                await getLocation();


            await saveLocation(
                location
            );


            const mapsURL =
                `https://www.google.com/maps?q=${location.latitude},${location.longitude}`;


            window.open(
                mapsURL,
                "_blank"
            );


            toast(
                t("mapsOpened")
            );

        }

        catch (error) {

            toast(
                error.message
            );

        }


        return;

    }


    if (
        type === "document"
    ) {

        $("type").value =
            "document";


        $("desc").focus();


        toast(
            t("recordIncident")
        );

    }

}


/* =========================================================
   SAVE INCIDENT
   ========================================================= */

async function saveIncident(
    event
) {

    event.preventDefault();


    const type =
        $("type").value;


    const description =
        $("desc")
            .value
            .trim();


    let location =
        state.location;


    /*
       Try to capture location,
       but incident saving should still
       work if location permission is denied.
    */

    if (!location) {

        try {

            location =
                await getLocation();

        }

        catch (_) {

            location =
                null;

        }

    }


    try {

        const response =
            await fetch(
                "/api/incidents",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            type:

                                type,

                            description:

                                description,

                            latitude:

                                location
                                ?.latitude
                                ?? null,

                            longitude:

                                location
                                ?.longitude
                                ?? null,

                            accuracy:

                                location
                                ?.accuracy
                                ?? null,

                            countryCode:

                                state.country

                        })

                }
            );


        if (!response.ok) {

            throw new Error(
                "Unable to save incident."
            );

        }


        $("desc").value =
            "";


        $("result").innerHTML = `

            <div class="success">

                ✓ ${escapeHtml(
                    t("saved")
                )}

            </div>

        `;


        await loadLogs();


        toast(
            t("saved")
        );

    }

    catch (error) {

        console.error(
            error
        );


        toast(
            error.message
        );

    }

}


/* =========================================================
   LOAD LOGS
   ========================================================= */

async function loadLogs() {

    const container =
        $("logs");


    if (!container) return;


    try {

        const response =
            await fetch(
                "/api/incidents"
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load logs."
            );

        }


        const logs =
            await response.json();


        renderLogs(
            logs
        );

    }

    catch (error) {

        console.error(
            error
        );


        container.innerHTML = `

            <div class="empty">

                ${t("noLogs")}

            </div>

        `;

    }

}


/* =========================================================
   RENDER LOGS
   ========================================================= */

function renderLogs(
    logs
) {

    const container =
        $("logs");


    if (!container) return;


    if (
        !logs.length
    ) {

        container.innerHTML = `

            <div class="empty">

                ${t("noLogs")}

            </div>

        `;

        return;

    }


    const typeMap = {

        medical:
            "medical",

        lost:
            "lostStranded",

        theft:
            "theft",

        unsafe:
            "unsafeSituation",

        document:
            "lostDocument",

        other:
            "other"

    };


    container.innerHTML =
        logs
            .map(
                log => {

                    const date =
                        new Date(
                            log.created_at
                        );


                    const typeName =
                        t(
                            typeMap[
                                log.type
                            ]
                            ||
                            "incident"
                        );


                    const mapLink =
                        log.latitude !== null
                        &&
                        log.longitude !== null

                        ?

                        `

                            <a
                                href="https://www.google.com/maps?q=${log.latitude},${log.longitude}"
                                target="_blank"
                            >

                                📍
                                ${escapeHtml(
                                    t("open")
                                )}

                            </a>

                        `

                        :

                        `<small>
                            ${escapeHtml(
                                t("noLocation")
                            )}
                         </small>`;


                    return `

                        <div class="log">

                            <div>

                                <strong>
                                    ${escapeHtml(
                                        typeName
                                    )}
                                </strong>


                                <p>
                                    ${escapeHtml(
                                        log.description
                                    )}
                                </p>


                                <small>
                                    ${escapeHtml(
                                        date.toLocaleString()
                                    )}
                                </small>

                            </div>


                            <div>

                                ${mapLink}

                            </div>

                        </div>

                    `;

                }
            )
            .join("");

}


/* =========================================================
   COUNTRY CHANGE
   ========================================================= */

async function changeCountry() {

    state.country =
        $("country").value;


    localStorage.setItem(
        "travelaiCountry",
        state.country
    );


    await loadContacts();

}


/* =========================================================
   LANGUAGE EVENTS
   ========================================================= */

function setupLanguageEvents() {


    $("language")
        ?.addEventListener(
            "change",
            event => {

                changeLanguage(
                    event.target.value
                );

            }
        );


    /*
       Phrase language selector
       changes the ENTIRE WEBSITE.
    */

    $("phraseLanguage")
        ?.addEventListener(
            "change",
            event => {

                changeLanguage(
                    event.target.value
                );

            }
        );

}


/* =========================================================
   INITIALIZATION
   ========================================================= */

async function init() {

    setupLanguageEvents();


    applyLanguage();


    await loadCountries();


    await loadContacts();


    await loadLogs();


    applyLanguage();

}


/* =========================================================
   DOM EVENTS
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {


        $("sos")
            ?.addEventListener(
                "click",
                activateSOS
            );


        $("loc")
            ?.addEventListener(
                "click",
                shareLocation
            );


        $("country")
            ?.addEventListener(
                "change",
                changeCountry
            );


        $("refresh")
            ?.addEventListener(
                "click",
                loadContacts
            );


        $("logsBtn")
            ?.addEventListener(
                "click",
                loadLogs
            );


        $("form")
            ?.addEventListener(
                "submit",
                saveIncident
            );


        init();

    }
);
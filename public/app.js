/* =========================================================
   TRAVELAI — EMERGENCY SUPPORT
   Multilingual Frontend
   ========================================================= */

const API = "";


/* =========================================================
   APPLICATION STATE
   ========================================================= */

const state = {

  language:
    localStorage.getItem("travelaiLanguage") || "en",

  country:
    localStorage.getItem("travelaiCountry") || "IN",

  location: null,

  contacts: []

};


/* =========================================================
   TRANSLATIONS
   ========================================================= */

const translations = {

  /* ================= ENGLISH ================= */

  en: {

    title: "TravelAI — Emergency Support",

    eyebrow:
      "FEATURE 5 · EMERGENCY TRAVEL SUPPORT",

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

    locationDenied:
      "Location permission was not granted.",

    locationReady:
      "Location captured and ready to share.",

    locationRequired:
      "Please allow location access first.",

    noContacts:
      "No contacts configured for this country.",

    saved:
      "Incident saved successfully.",

    noLogs:
      "No incidents recorded yet.",

    incident:
      "Incident",

    open:
      "Open",

    call:
      "Call",

    location:
      "Location",

    noLocation:
      "No location attached",

    browserSpeech:
      "Speech is not supported by this browser.",

    medicalAction:
      "Use the ambulance number shown above.",

    policeAction:
      "Use the police number shown above.",

    mapsOpened:
      "Your location has been opened in Google Maps.",

    savedLocally:
      "Saved locally because the backend is unavailable.",

    apiError:
      "Backend unavailable; using local demo storage."

  },


  /* ================= HINDI ================= */

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

    locationDenied:
      "लोकेशन की अनुमति नहीं मिली।",

    locationReady:
      "लोकेशन प्राप्त हो गई और साझा करने के लिए तैयार है।",

    locationRequired:
      "कृपया पहले लोकेशन की अनुमति दें।",

    noContacts:
      "इस देश के लिए कोई संपर्क उपलब्ध नहीं है।",

    saved:
      "घटना सफलतापूर्वक सहेजी गई।",

    noLogs:
      "अभी कोई घटना दर्ज नहीं है।",

    incident:
      "घटना",

    open:
      "खोलें",

    call:
      "कॉल",

    location:
      "लोकेशन",

    noLocation:
      "कोई लोकेशन संलग्न नहीं है",

    browserSpeech:
      "इस ब्राउज़र में आवाज़ समर्थित नहीं है।",

    medicalAction:
      "ऊपर दिया गया एम्बुलेंस नंबर इस्तेमाल करें।",

    policeAction:
      "ऊपर दिया गया पुलिस नंबर इस्तेमाल करें।",

    mapsOpened:
      "आपकी लोकेशन Google Maps में खोली गई है।",

    savedLocally:
      "बैकएंड उपलब्ध नहीं था, इसलिए स्थानीय रूप से सहेजा गया।",

    apiError:
      "बैकएंड उपलब्ध नहीं है; स्थानीय डेमो स्टोरेज का उपयोग हो रहा है।"

  },


  /* ================= TELUGU ================= */

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

    locationDenied:
      "లొకేషన్ అనుమతి ఇవ్వలేదు.",

    locationReady:
      "లొకేషన్ పొందబడింది మరియు షేర్ చేయడానికి సిద్ధంగా ఉంది.",

    locationRequired:
      "ముందుగా లొకేషన్ అనుమతించండి.",

    noContacts:
      "ఈ దేశానికి సంప్రదింపులు అందుబాటులో లేవు.",

    saved:
      "సంఘటన విజయవంతంగా సేవ్ అయింది.",

    noLogs:
      "ఇంకా సంఘటనలు నమోదు కాలేదు.",

    incident:
      "సంఘటన",

    open:
      "తెరవండి",

    call:
      "కాల్",

    location:
      "లొకేషన్",

    noLocation:
      "లొకేషన్ జోడించలేదు",

    browserSpeech:
      "ఈ బ్రౌజర్‌లో వాయిస్ సపోర్ట్ లేదు.",

    medicalAction:
      "పైన ఉన్న అంబులెన్స్ నంబర్‌ను ఉపయోగించండి.",

    policeAction:
      "పైన ఉన్న పోలీస్ నంబర్‌ను ఉపయోగించండి.",

    mapsOpened:
      "మీ లొకేషన్ Google Mapsలో తెరవబడింది.",

    savedLocally:
      "బ్యాకెండ్ అందుబాటులో లేకపోవడంతో స్థానికంగా సేవ్ చేశాము.",

    apiError:
      "బ్యాకెండ్ అందుబాటులో లేదు; స్థానిక డెమో స్టోరేజ్ ఉపయోగిస్తున్నాము."

  },


  /* ================= TAMIL ================= */

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

    locationDenied:
      "இருப்பிட அனுமதி வழங்கப்படவில்லை.",

    locationReady:
      "இருப்பிடம் பெறப்பட்டது; பகிர தயாராக உள்ளது.",

    locationRequired:
      "முதலில் இருப்பிட அனுமதியை வழங்கவும்.",

    noContacts:
      "இந்த நாட்டிற்கு தொடர்புகள் இல்லை.",

    saved:
      "சம்பவம் வெற்றிகரமாகச் சேமிக்கப்பட்டது.",

    noLogs:
      "இதுவரை சம்பவங்கள் பதிவு செய்யப்படவில்லை.",

    incident:
      "சம்பவம்",

    open:
      "திறக்கவும்",

    call:
      "அழைக்கவும்",

    location:
      "இருப்பிடம்",

    noLocation:
      "இருப்பிடம் இணைக்கப்படவில்லை",

    browserSpeech:
      "இந்த உலாவியில் குரல் ஆதரவு இல்லை.",

    medicalAction:
      "மேலே உள்ள ஆம்புலன்ஸ் எண்ணைப் பயன்படுத்தவும்.",

    policeAction:
      "மேலே உள்ள காவல்துறை எண்ணைப் பயன்படுத்தவும்.",

    mapsOpened:
      "உங்கள் இருப்பிடம் Google Mapsல் திறக்கப்பட்டது.",

    savedLocally:
      "பின்புற சேவை கிடைக்காததால் உள்ளூரில் சேமிக்கப்பட்டது.",

    apiError:
      "பின்புற சேவை கிடைக்கவில்லை; உள்ளூர் டெமோ சேமிப்பகம் பயன்படுத்தப்படுகிறது."

  }

};


/* =========================================================
   COUNTRY NAMES
   ========================================================= */

const countryNames = {

  en: {
    IN: "India",
    AE: "United Arab Emirates",
    US: "United States",
    GB: "United Kingdom"
  },

  hi: {
    IN: "भारत",
    AE: "संयुक्त अरब अमीरात",
    US: "संयुक्त राज्य अमेरिका",
    GB: "यूनाइटेड किंगडम"
  },

  te: {
    IN: "భారతదేశం",
    AE: "యునైటెడ్ అరబ్ ఎమిరేట్స్",
    US: "యునైటెడ్ స్టేట్స్",
    GB: "యునైటెడ్ కింగ్‌డమ్"
  },

  ta: {
    IN: "இந்தியா",
    AE: "ஐக்கிய அரபு அமீரகம்",
    US: "அமெரிக்கா",
    GB: "ஐக்கிய இராச்சியம்"
  }

};


/* =========================================================
   SERVICE NAMES
   ========================================================= */

const serviceNames = {

  en: {
    Police: "Police",
    Ambulance: "Ambulance",
    Fire: "Fire",
    "Unified Emergency": "Unified Emergency",
    "Alternative Emergency": "Alternative Emergency"
  },

  hi: {
    Police: "पुलिस",
    Ambulance: "एम्बुलेंस",
    Fire: "फायर सेवा",
    "Unified Emergency": "एकीकृत आपातकालीन सेवा",
    "Alternative Emergency": "वैकल्पिक आपातकालीन सेवा"
  },

  te: {
    Police: "పోలీస్",
    Ambulance: "అంబులెన్స్",
    Fire: "అగ్నిమాపక సేవ",
    "Unified Emergency": "ఏకీకృత అత్యవసర సేవ",
    "Alternative Emergency": "ప్రత్యామ్నాయ అత్యవసర సేవ"
  },

  ta: {
    Police: "காவல்துறை",
    Ambulance: "ஆம்புலன்ஸ்",
    Fire: "தீயணைப்பு சேவை",
    "Unified Emergency": "ஒருங்கிணைந்த அவசர சேவை",
    "Alternative Emergency": "மாற்று அவசர சேவை"
  }

};


/* =========================================================
   LOCAL EMERGENCY CONTACTS
   ========================================================= */

const localContacts = {

  IN: [
    [
      "Unified Emergency",
      "112",
      "India's pan-India emergency number."
    ],

    [
      "Police",
      "100",
      "Police emergency number."
    ],

    [
      "Ambulance",
      "108",
      "Emergency medical response in many Indian states."
    ],

    [
      "Fire",
      "101",
      "Fire emergency number."
    ]
  ],

  AE: [

    [
      "Police",
      "999",
      "Police emergency."
    ],

    [
      "Ambulance",
      "998",
      "Ambulance emergency."
    ],

    [
      "Fire",
      "997",
      "Civil Defence / fire emergency."
    ]

  ],

  US: [

    [
      "Unified Emergency",
      "911",
      "Police, fire and medical emergency."
    ]

  ],

  GB: [

    [
      "Unified Emergency",
      "999",
      "Police, fire and ambulance emergency."
    ],

    [
      "Alternative Emergency",
      "112",
      "Alternative emergency number."
    ]

  ]

};


/* =========================================================
   EMERGENCY PHRASES
   ========================================================= */

const phrases = {

  en: [

    [
      "I need help.",
      "I need help."
    ],

    [
      "Please call an ambulance.",
      "Please call an ambulance."
    ],

    [
      "Please call the police.",
      "Please call the police."
    ],

    [
      "I am lost.",
      "I am lost."
    ]

  ],


  hi: [

    [
      "मुझे मदद चाहिए।",
      "Mujhe madad chahiye."
    ],

    [
      "कृपया एम्बुलेंस बुलाइए।",
      "Kripya ambulance bulaiye."
    ],

    [
      "कृपया पुलिस को बुलाइए।",
      "Kripya police ko bulaiye."
    ],

    [
      "मैं रास्ता भटक गया हूँ।",
      "Main raasta bhatak gaya hoon."
    ]

  ],


  te: [

    [
      "నాకు సహాయం కావాలి.",
      "Naaku sahaayam kaavaali."
    ],

    [
      "దయచేసి అంబులెన్స్‌కు కాల్ చేయండి.",
      "Dayachesi ambulance-ku call cheyandi."
    ],

    [
      "దయచేసి పోలీసులకు కాల్ చేయండి.",
      "Dayachesi police-laku call cheyandi."
    ],

    [
      "నేను దారి తప్పిపోయాను.",
      "Nenu daari tappipoyaanu."
    ]

  ],


  ta: [

    [
      "எனக்கு உதவி தேவை.",
      "Enakku uthavi thevai."
    ],

    [
      "தயவுசெய்து ஆம்புலன்ஸை அழைக்கவும்.",
      "Dayavuseythu ambulance-ai azhaikkavum."
    ],

    [
      "தயவுசெய்து காவல்துறையை அழைக்கவும்.",
      "Dayavuseythu kaavalthuraiyai azhaikkavum."
    ],

    [
      "நான் வழி தவறிவிட்டேன்.",
      "Naan vazhi thavarivitten."
    ]

  ]

};


/* =========================================================
   HELPER FUNCTIONS
   ========================================================= */

const $ = id => document.getElementById(id);


function t(key) {

  return (

    translations[state.language] &&
    translations[state.language][key]

  ) ||

    translations.en[key] ||

    key;

}


function escapeHtml(value) {

  return String(value ?? "")
    .replace(
      /[&<>"']/g,
      c => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[c])
    );

}


/* =========================================================
   APPLY LANGUAGE TO ENTIRE PAGE
   ========================================================= */

function applyLanguage() {

  document.documentElement.lang =
    state.language;

  document.title =
    t("title");


  /* Text elements */

  document
    .querySelectorAll("[data-i18n]")
    .forEach(element => {

      element.textContent =
        t(element.dataset.i18n);

    });


  /* Placeholder */

  document
    .querySelectorAll("[data-i18n-placeholder]")
    .forEach(element => {

      element.placeholder =
        t(element.dataset.i18nPlaceholder);

    });


  $("language").value =
    state.language;

  $("phraseLanguage").value =
    state.language;


  /* Incident types */

  const typeMap = {

    medical: "medical",

    lost: "lostStranded",

    theft: "theft",

    unsafe: "unsafeSituation",

    document: "lostDocument",

    other: "other"

  };


  const selectedType =
    $("type").value;


  [
    ...$("type").options
  ].forEach(option => {

    if (typeMap[option.value]) {

      option.textContent =
        t(typeMap[option.value]);

    }

  });


  $("type").value =
    selectedType;


  renderCountryOptions();

  renderPhrases();

  renderContacts();

  renderLogs();

}


/* =========================================================
   COUNTRY SELECT
   ========================================================= */

function renderCountryOptions() {

  $("country").innerHTML =

    Object.keys(countryNames.en)

      .map(code =>

        `<option value="${code}">
          ${escapeHtml(countryNames[state.language][code])}
        </option>`

      )
      .join("");


  $("country").value =
    state.country;

}


/* =========================================================
   CONTACT DISPLAY
   ========================================================= */

function renderContacts() {

  const data =
    state.contacts;


  if (!data.length) {

    $("contacts").innerHTML =
      `<div class="empty">
        ${t("noContacts")}
      </div>`;

    return;

  }


  $("contacts").innerHTML =

    data.map(contact => `

      <div class="contact">

        <div>

          <b>
            ${escapeHtml(
              serviceNames[state.language][contact.service]
              || contact.service
            )}
          </b>

          <small>
            ${escapeHtml(contact.description)}
          </small>

        </div>


        <a
          class="call"
          href="tel:${encodeURIComponent(contact.number)}">

          ☎ ${escapeHtml(contact.number)}

        </a>

      </div>

    `).join("");

}


/* =========================================================
   PHRASES
   ========================================================= */

function renderPhrases() {

  const list =
    phrases[state.language];


  $("phrases").innerHTML =

    list.map((phrase, index) => `

      <button
        class="phrase"
        data-index="${index}">

        <b>
          ${escapeHtml(phrase[0])}
        </b>

        <span>
          ${escapeHtml(phrase[1])}
        </span>

      </button>

    `).join("");


  document
    .querySelectorAll(".phrase")
    .forEach(button => {

      button.addEventListener(
        "click",
        () => {

          const phrase =
            list[
              Number(button.dataset.index)
            ];

          speak(
            phrase[0],
            state.language
          );

        }
      );

    });

}


/* =========================================================
   TEXT TO SPEECH
   ========================================================= */

function speechLang(language) {

  return {

    en: "en-US",

    hi: "hi-IN",

    te: "te-IN",

    ta: "ta-IN"

  }[language] || "en-US";

}


function speak(text, language) {

  if (!("speechSynthesis" in window)) {

    toast(t("browserSpeech"));

    return;

  }


  speechSynthesis.cancel();


  const utterance =
    new SpeechSynthesisUtterance(text);


  utterance.lang =
    speechLang(language);

  utterance.rate =
    0.9;


  speechSynthesis.speak(
    utterance
  );

}


/* =========================================================
   TOAST
   ========================================================= */

function toast(message) {

  $("toast").textContent =
    message;

  $("toast").classList.add(
    "show"
  );


  clearTimeout(
    window.__toastTimer
  );


  window.__toastTimer =

    setTimeout(() => {

      $("toast").classList.remove(
        "show"
      );

    }, 3200);

}


/* =========================================================
   GEOLOCATION
   ========================================================= */

async function getLocation() {

  if (!navigator.geolocation) {

    throw new Error(
      "Geolocation not supported"
    );

  }


  return new Promise(
    (resolve, reject) => {

      navigator.geolocation.getCurrentPosition(

        position => {

          state.location = {

            latitude:
              position.coords.latitude,

            longitude:
              position.coords.longitude,

            accuracy:
              position.coords.accuracy

          };


          $("status").textContent =

            `${t("locationShared")}: ` +

            `${state.location.latitude.toFixed(5)}, ` +

            `${state.location.longitude.toFixed(5)}`;


          resolve(
            state.location
          );

        },


        error => {

          reject(error);

        },


        {

          enableHighAccuracy: true,

          timeout: 10000,

          maximumAge: 30000

        }

      );

    }

  );

}


/* =========================================================
   LOAD EMERGENCY CONTACTS
   ========================================================= */

async function loadContacts() {

  try {

    const response =

      await fetch(
        `${API}/api/emergency-contacts?country=${encodeURIComponent(state.country)}`
      );


    if (!response.ok) {

      throw new Error(
        "API error"
      );

    }


    const data =
      await response.json();


    state.contacts =
      data.contacts;


  } catch (error) {

    state.contacts =

      (localContacts[state.country] || [])
        .map(contact => ({

          service:
            contact[0],

          number:
            contact[1],

          description:
            contact[2]

        }));


    toast(
      t("apiError")
    );

  }


  renderContacts();

}


/* =========================================================
   SOS BUTTON
   ========================================================= */

$("sos").addEventListener(
  "click",
  async () => {

    const confirmation =

      confirm(
        state.language === "en"

          ? "Activate SOS logging? This prototype does not automatically contact authorities."

          : t("sosActivated")
      );


    if (!confirmation) {

      return;

    }


    /* Try to get location */

    if (!state.location) {

      try {

        await getLocation();

      } catch {

        // Continue even if location denied

      }

    }


    const payload = {

      ...(state.location || {}),

      countryCode:
        state.country

    };


    try {

      const response =

        await fetch(
          `${API}/api/sos`,
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


      if (!response.ok) {

        throw new Error(
          "API error"
        );

      }


      const data =
        await response.json();


      showSOS(
        data.contacts ||
        state.contacts
      );


    } catch {

      const sosData = {

        id:
          Date.now(),

        type:
          "SOS",

        description:
          t("sosLogged"),

        created_at:
          new Date().toLocaleString(),

        ...(state.location || {})

      };


      saveLocal(
        "travelai_sos",
        [
          sosData,
          ...getLocal(
            "travelai_sos",
            []
          )
        ]
      );


      showSOS(
        state.contacts
      );

    }


    loadLogs();

  }
);


/* =========================================================
   SOS MODAL
   ========================================================= */

function showSOS(contacts) {

  $("sosContacts").innerHTML =

    contacts.map(contact => `

      <div class="modal-contact">

        <span>

          <b>
            ${
              escapeHtml(
                serviceNames[state.language][contact.service]
                || contact.service
              )
            }
          </b>

          <br>

          <small>
            ${escapeHtml(
              contact.description || ""
            )}
          </small>

        </span>


        <a
          class="call"
          href="tel:${encodeURIComponent(contact.number)}">

          ☎ ${escapeHtml(contact.number)}

        </a>

      </div>

    `).join("");


  $("modal")
    .classList
    .remove("hidden");

}


function closeModal() {

  $("modal")
    .classList
    .add("hidden");

}


window.closeModal =
  closeModal;


/* =========================================================
   LOCATION SHARE BUTTON
   ========================================================= */

$("loc").addEventListener(
  "click",
  async () => {

    try {

      await getLocation();

      toast(
        t("locationReady")
      );

    } catch {

      toast(
        t("locationDenied")
      );

    }

  }
);


/* =========================================================
   EMERGENCY ACTIONS
   ========================================================= */

async function action(type) {


  /* Medical */

  if (type === "medical") {

    const contact =

      state.contacts.find(
        c =>
          c.service === "Ambulance"
      );


    if (contact) {

      window.location.href =
        `tel:${contact.number}`;

      return;

    }


    toast(
      t("medicalAction")
    );

    return;

  }


  /* Unsafe */

  if (type === "unsafe") {

    const contact =

      state.contacts.find(
        c =>
          c.service === "Police"
      ) ||

      state.contacts.find(
        c =>
          c.service === "Unified Emergency"
      );


    if (contact) {

      window.location.href =
        `tel:${contact.number}`;

      return;

    }


    toast(
      t("policeAction")
    );

    return;

  }


  /* Lost */

  if (type === "lost") {

    try {

      const location =
        await getLocation();


      const mapsURL =

        `https://www.google.com/maps/search/?api=1&query=` +

        `${location.latitude},${location.longitude}`;


      window.open(
        mapsURL,
        "_blank"
      );


      toast(
        t("mapsOpened")
      );

    } catch {

      toast(
        t("locationRequired")
      );

    }


    return;

  }


  /* Lost Documents */

  if (type === "document") {

    $("type").value =
      "document";


    $("desc").focus();


    $("form")
      .scrollIntoView({
        behavior: "smooth",
        block: "center"
      });


    return;

  }

}


window.action =
  action;


/* =========================================================
   COUNTRY CHANGE
   ========================================================= */

$("country").addEventListener(
  "change",
  async event => {

    state.country =
      event.target.value;


    localStorage.setItem(
      "travelaiCountry",
      state.country
    );


    await loadContacts();

  }
);


/* =========================================================
   REFRESH CONTACTS
   ========================================================= */

$("refresh").addEventListener(
  "click",
  loadContacts
);


/* =========================================================
   LANGUAGE CHANGE
   ========================================================= */

$("language").addEventListener(
  "change",
  event => {

    state.language =
      event.target.value;


    localStorage.setItem(
      "travelaiLanguage",
      state.language
    );


    applyLanguage();

  }
);


/* =========================================================
   PHRASE LANGUAGE CHANGE
   ========================================================= */

$("phraseLanguage").addEventListener(
  "change",
  event => {

    /*
      IMPORTANT:
      This changes the ENTIRE page language.
    */

    state.language =
      event.target.value;


    localStorage.setItem(
      "travelaiLanguage",
      state.language
    );


    applyLanguage();

  }
);


/* =========================================================
   INCIDENT FORM
   ========================================================= */

$("form").addEventListener(
  "submit",
  async event => {

    event.preventDefault();


    /* Try location */

    if (!state.location) {

      try {

        await getLocation();

      } catch {

        // Location is optional

      }

    }


    const payload = {

      type:
        $("type").value,

      description:
        $("desc").value.trim(),

      ...(state.location || {}),

      countryCode:
        state.country

    };


    try {

      const response =

        await fetch(
          `${API}/api/incidents`,
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


      if (!response.ok) {

        throw new Error(
          "API error"
        );

      }


      const data =
        await response.json();


      $("result").textContent =

        `✓ ${t("saved")} #${data.incidentId}`;


    } catch {

      const logs =

        getLocal(
          "travelai_incidents",
          []
        );


      logs.unshift({

        id:
          Date.now(),

        ...payload,

        created_at:
          new Date().toLocaleString()

      });


      saveLocal(
        "travelai_incidents",
        logs
      );


      $("result").textContent =

        `✓ ${t("saved")} — ${t("savedLocally")}`;

    }


    $("desc").value = "";


    loadLogs();

  }
);


/* =========================================================
   LOCAL STORAGE
   ========================================================= */

function saveLocal(
  key,
  value
) {

  localStorage.setItem(
    key,
    JSON.stringify(value)
  );

}


function getLocal(
  key,
  fallback = []
) {

  try {

    return (
      JSON.parse(
        localStorage.getItem(key)
      ) ?? fallback
    );

  } catch {

    return fallback;

  }

}


/* =========================================================
   LOAD SUPPORT LOGS
   ========================================================= */

async function loadLogs() {

  let logs = [];


  try {

    const response =
      await fetch(
        `${API}/api/incidents`
      );


    if (!response.ok) {

      throw new Error();

    }


    logs =
      await response.json();


  } catch {

    logs =
      getLocal(
        "travelai_incidents",
        []
      );


    const sos =
      getLocal(
        "travelai_sos",
        []
      );


    logs =
      [
        ...sos,
        ...logs
      ];

  }


  if (!logs.length) {

    $("logs").innerHTML =

      `<div class="empty">
        ${t("noLogs")}
      </div>`;

    return;

  }


  $("logs").innerHTML =

    logs.map(log => {

      const typeKey = {

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

      }[log.type] || log.type;


      return `

        <div class="log">

          <div class="log-top">

            <b>

              ${
                escapeHtml(
                  log.type === "SOS"

                    ? "🚨 SOS"

                    : t(typeKey)
                )
              }

            </b>

            <small>
              ${escapeHtml(
                log.created_at || ""
              )}
            </small>

          </div>


          <div>

            ${escapeHtml(
              log.description ||
              t("incident")
            )}

          </div>


          <small>

            ${
              log.latitude != null

                ?

                `${t("location")}: ` +

                `${Number(log.latitude).toFixed(5)}, ` +

                `${Number(log.longitude).toFixed(5)}`

                :

                t("noLocation")
            }

          </small>

        </div>

      `;

    }).join("");

}

$("logsBtn").addEventListener(
  "click",
  loadLogs
);

(async function init() {

  renderCountryOptions();

  await loadContacts();

  applyLanguage();

  await loadLogs();

})();
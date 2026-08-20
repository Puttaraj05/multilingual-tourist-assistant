document.addEventListener("DOMContentLoaded", () => {

    console.log("=================================");
    console.log("TRAVELMATE TRANSLATOR LOADED");
    console.log("=================================");

    const API_BASE = "";

    // =====================================================
    // LANGUAGE MAP
    // =====================================================

    const languageCodes = {
        "English": "en",
        "Hindi": "hi",
        "Telugu": "te",
        "Tamil": "ta",
        "Kannada": "kn",
        "Malayalam": "ml",
        "Bengali": "bn",
        "Marathi": "mr",
        "Gujarati": "gu",
        "Punjabi": "pa",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Japanese": "ja",
        "Korean": "ko",
        "Arabic": "ar",
        "Chinese": "zh-CN",
        "Russian": "ru"
    };

    const languageNames = {
        auto: "Auto Detect",
        en: "English",
        hi: "Hindi",
        te: "Telugu",
        ta: "Tamil",
        kn: "Kannada",
        ml: "Malayalam",
        bn: "Bengali",
        mr: "Marathi",
        gu: "Gujarati",
        pa: "Punjabi",
        es: "Spanish",
        fr: "French",
        de: "German",
        it: "Italian",
        ja: "Japanese",
        ko: "Korean",
        ar: "Arabic",
        "zh-CN": "Chinese",
        ru: "Russian"
    };

    function getLanguageCode(value) {

        if (!value) {
            return "auto";
        }

        if (value === "auto") {
            return "auto";
        }

        return languageCodes[value] || value;
    }

    function getLanguageName(code) {

        return languageNames[code] || code || "Unknown";
    }

    // =====================================================
    // STATUS
    // =====================================================

    function showStatus(element, message, type = "") {

        if (!element) {
            return;
        }

        element.textContent = message;

        element.className =
            `translation-status ${type}`;
    }

    // =====================================================
    // RESPONSE HANDLER
    // =====================================================

    async function parseResponse(response) {

        let result;

        try {

            result = await response.json();

        } catch {

            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }

        if (!response.ok) {

            throw new Error(
                result.detail ||
                result.error ||
                `Request failed (${response.status})`
            );
        }

        if (result.success === false) {

            throw new Error(
                result.error ||
                "Request failed."
            );
        }

        return result;
    }

    // =====================================================
    // TEXT TRANSLATION ELEMENTS
    // =====================================================

    const sourceLanguage =
        document.getElementById("sourceLanguage");

    const targetLanguage =
        document.getElementById("targetLanguage");

    const inputText =
        document.getElementById("inputText");

    const translatedText =
        document.getElementById("translatedText");

    const translateTextBtn =
        document.getElementById("translateTextBtn");

    const detectedLanguage =
        document.getElementById("detectedLanguage");

    const translationStatus =
        document.getElementById("translationStatus");

    const inputCounter =
        document.getElementById("inputCounter");

    // =====================================================
    // TEXT COUNTER
    // =====================================================

    if (inputText) {

        inputText.addEventListener("input", () => {

            if (inputCounter) {

                inputCounter.textContent =
                    `${inputText.value.length} / 5000`;
            }
        });
    }

    // =====================================================
    // TEXT TRANSLATION
    // =====================================================

    if (translateTextBtn) {

        translateTextBtn.addEventListener(
            "click",
            async () => {

                const text =
                    inputText.value.trim();

                if (!text) {

                    alert(
                        "Enter some text first."
                    );

                    inputText.focus();

                    return;
                }

                if (
                    sourceLanguage.value !== "auto" &&
                    sourceLanguage.value === targetLanguage.value
                ) {

                    translatedText.value = text;

                    showStatus(
                        translationStatus,
                        "Source and target languages are the same.",
                        "success"
                    );

                    return;
                }

                translateTextBtn.disabled = true;

                translateTextBtn.innerHTML =
                    `<i class="fa-solid fa-spinner fa-spin"></i>
                     Translating...`;

                translatedText.value = "";

                showStatus(
                    translationStatus,
                    "Translating your text...",
                    "loading"
                );

                try {

                    const response =
                        await fetch(
                            `${API_BASE}/api/translate`,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({

                                    text: text,

                                    source:
                                        sourceLanguage.value,

                                    target:
                                        targetLanguage.value
                                })
                            }
                        );

                    const result =
                        await parseResponse(response);

                    translatedText.value =
                        result.translated_text || "";

                    const detected =
                        result.source_language ||
                        sourceLanguage.value;

                    if (
                        sourceLanguage.value === "auto"
                    ) {

                        detectedLanguage.textContent =
                            `Detected language: ${
                                getLanguageName(detected)
                            }`;

                        detectedLanguage.style.display =
                            "block";
                    }

                    showStatus(
                        translationStatus,
                        "Translation completed successfully.",
                        "success"
                    );

                } catch (error) {

                    console.error(
                        "Translation error:",
                        error
                    );

                    showStatus(
                        translationStatus,
                        error.message ||
                        "Unable to translate text.",
                        "error"
                    );

                } finally {

                    translateTextBtn.disabled =
                        false;

                    translateTextBtn.innerHTML =
                        `<i class="fa-solid fa-language"></i>
                         Translate Text`;
                }
            }
        );
    }

    // =====================================================
    // IMAGE TRANSLATION ELEMENTS
    // =====================================================

    const imageInput =
        document.getElementById("imageInput");

    const imagePreview =
        document.getElementById("imagePreview");

    const imagePreviewContainer =
        document.getElementById(
            "imagePreviewContainer"
        );

    const originalImageText =
        document.getElementById(
            "originalImageText"
        );

    const imageTranslation =
        document.getElementById(
            "imageTranslation"
        );

    const imageTargetLanguage =
        document.getElementById(
            "imageTargetLanguage"
        );

    const translateImageBtn =
        document.getElementById(
            "translateImageBtn"
        );

    const imageTranslationStatus =
        document.getElementById(
            "imageTranslationStatus"
        );

    // =====================================================
    // IMAGE PREVIEW
    // =====================================================

    if (imageInput) {

        imageInput.addEventListener(
            "change",
            () => {

                const file =
                    imageInput.files[0];

                if (!file) {

                    imagePreviewContainer.style.display =
                        "none";

                    return;
                }

                if (
                    !file.type.startsWith("image/")
                ) {

                    alert(
                        "Please select a valid image."
                    );

                    imageInput.value = "";

                    return;
                }

                if (
                    file.size >
                    10 * 1024 * 1024
                ) {

                    alert(
                        "Image size must be less than 10 MB."
                    );

                    imageInput.value = "";

                    return;
                }

                imagePreview.src =
                    URL.createObjectURL(file);

                imagePreviewContainer.style.display =
                    "block";

                originalImageText.value = "";

                imageTranslation.value = "";

                showStatus(
                    imageTranslationStatus,
                    ""
                );
            }
        );
    }

    // =====================================================
    // IMAGE TRANSLATION
    // =====================================================

    if (translateImageBtn) {

        translateImageBtn.addEventListener(
            "click",
            async () => {

                const file =
                    imageInput.files[0];

                // -----------------------------------------
                // CHECK IMAGE
                // -----------------------------------------

                if (!file) {

                    alert(
                        "Upload an image first."
                    );

                    return;
                }

                // -----------------------------------------
                // CHECK TARGET LANGUAGE
                // -----------------------------------------

                const targetCode =
                    imageTargetLanguage
                        ? imageTargetLanguage.value
                        : "en";

                if (
                    !targetCode ||
                    targetCode === "auto"
                ) {

                    alert(
                        "Please select a target language."
                    );

                    return;
                }

                // -----------------------------------------
                // DISABLE BUTTON
                // -----------------------------------------

                translateImageBtn.disabled =
                    true;

                translateImageBtn.innerHTML =
                    `<i class="fa-solid fa-spinner fa-spin"></i>
                     Processing Image...`;

                // -----------------------------------------
                // CLEAR OLD RESULTS
                // -----------------------------------------

                originalImageText.value = "";

                imageTranslation.value = "";

                showStatus(
                    imageTranslationStatus,
                    "Reading and translating image...",
                    "loading"
                );

                try {

                    // -------------------------------------
                    // FORM DATA
                    // -------------------------------------

                    const formData =
                        new FormData();

                    formData.append(
                        "image",
                        file
                    );

                    formData.append(
                        "target",
                        targetCode
                    );

                    console.log(
                        "Image translation target:",
                        targetCode
                    );

                    // -------------------------------------
                    // API REQUEST
                    // -------------------------------------

                    const response =
                        await fetch(
                            `${API_BASE}/api/image-translate`,
                            {
                                method: "POST",
                                body: formData
                            }
                        );

                    const result =
                        await parseResponse(
                            response
                        );

                    console.log(
                        "Image translation response:",
                        result
                    );

                    // -------------------------------------
                    // ORIGINAL TEXT
                    // -------------------------------------

                    originalImageText.value =
                        result.original_text || "";

                    // -------------------------------------
                    // TRANSLATED TEXT
                    // -------------------------------------

                    imageTranslation.value =
                        result.translated_text || "";

                    // -------------------------------------
                    // DETECTED SOURCE LANGUAGE
                    // -------------------------------------

                    const source =
                        result.source_language ||
                        "Unknown";

                    const sourceName =
                        getLanguageName(source);

                    // -------------------------------------
                    // TARGET LANGUAGE NAME
                    // -------------------------------------

                    const targetName =
                        getLanguageName(targetCode);

                    // -------------------------------------
                    // SUCCESS
                    // -------------------------------------

                    showStatus(
                        imageTranslationStatus,

                        `Image translated successfully. Detected: ${sourceName} → Translated to: ${targetName}`,

                        "success"
                    );

                } catch (error) {

                    console.error(
                        "Image translation error:",
                        error
                    );

                    showStatus(
                        imageTranslationStatus,

                        error.message ||
                        "Unable to translate image.",

                        "error"
                    );

                } finally {

                    translateImageBtn.disabled =
                        false;

                    translateImageBtn.innerHTML =
                        `<i class="fa-solid fa-wand-magic-sparkles"></i>
                         Translate Image`;
                }
            }
        );
    }

    // =====================================================
    // VOICE ELEMENTS
    // =====================================================

    const voiceSourceLanguage =
        document.getElementById(
            "voiceSourceLanguage"
        );

    const voiceTargetLanguage =
        document.getElementById(
            "voiceTargetLanguage"
        );

    const recordVoiceBtn =
        document.getElementById(
            "recordVoiceBtn"
        );

    const voiceOriginalText =
        document.getElementById(
            "voiceOriginalText"
        );

    const voiceTranslatedText =
        document.getElementById(
            "voiceTranslatedText"
        );

    const voiceStatus =
        document.getElementById(
            "voiceStatus"
        );

    const voiceTranslationStatus =
        document.getElementById(
            "voiceTranslationStatus"
        );

    const recordingTimer =
        document.getElementById(
            "recordingTimer"
        );

    const playTranslationBtn =
        document.getElementById(
            "playTranslationBtn"
        );

    const voiceCircle =
        document.getElementById(
            "voiceCircle"
        );

    // =====================================================
    // RECORDING VARIABLES
    // =====================================================

    let mediaRecorder = null;
    let audioChunks = [];
    let recordingStartTime = null;
    let recordingInterval = null;
    let translatedAudio = null;

    // =====================================================
    // MIME TYPE
    // =====================================================

    function getAudioMimeType() {

        const types = [
            "audio/webm;codecs=opus",
            "audio/webm",
            "audio/mp4",
            "audio/ogg;codecs=opus"
        ];

        if (!window.MediaRecorder) {
            return "";
        }

        for (const type of types) {

            if (
                MediaRecorder.isTypeSupported(type)
            ) {
                return type;
            }
        }

        return "";
    }

    // =====================================================
    // TIMER
    // =====================================================

    function startTimer() {

        if (!recordingTimer) {
            return;
        }

        recordingStartTime =
            Date.now();

        recordingTimer.style.display =
            "inline-flex";

        recordingInterval =
            setInterval(() => {

                const elapsed =
                    Math.floor(
                        (
                            Date.now() -
                            recordingStartTime
                        ) / 1000
                    );

                const minutes =
                    String(
                        Math.floor(
                            elapsed / 60
                        )
                    ).padStart(2, "0");

                const seconds =
                    String(
                        elapsed % 60
                    ).padStart(2, "0");

                recordingTimer.innerHTML =
                    `<span class="recording-dot"></span>
                     <span>Recording: ${minutes}:${seconds}</span>`;

            }, 1000);
    }

    function stopTimer() {

        clearInterval(
            recordingInterval
        );

        recordingInterval = null;

        if (recordingTimer) {

            recordingTimer.style.display =
                "none";
        }
    }

    // =====================================================
    // START RECORDING
    // =====================================================

    async function startRecording() {

        try {

            if (
                !navigator.mediaDevices ||
                !navigator.mediaDevices.getUserMedia
            ) {

                throw new Error(
                    "Your browser does not support microphone access."
                );
            }

            if (
                !voiceTargetLanguage ||
                !voiceSourceLanguage
            ) {

                throw new Error(
                    "Voice language controls are missing from the page."
                );
            }

            const targetCode =
                getLanguageCode(
                    voiceTargetLanguage.value
                );

            if (
                !targetCode ||
                targetCode === "auto"
            ) {

                throw new Error(
                    "Please select a target language."
                );
            }

            const stream =
                await navigator.mediaDevices.getUserMedia({
                    audio: true
                });

            const mimeType =
                getAudioMimeType();

            mediaRecorder =
                mimeType
                    ? new MediaRecorder(
                        stream,
                        {
                            mimeType
                        }
                    )
                    : new MediaRecorder(stream);

            audioChunks = [];

            mediaRecorder.addEventListener(
                "dataavailable",
                event => {

                    if (
                        event.data &&
                        event.data.size > 0
                    ) {

                        audioChunks.push(
                            event.data
                        );
                    }
                }
            );

            mediaRecorder.addEventListener(
                "stop",
                async () => {

                    stream
                        .getTracks()
                        .forEach(
                            track =>
                                track.stop()
                        );

                    await processRecordedAudio(
                        mimeType ||
                        "audio/webm"
                    );
                }
            );

            mediaRecorder.start();

            startTimer();

            if (recordVoiceBtn) {

                recordVoiceBtn.innerHTML =
                    `<i class="fa-solid fa-stop"></i>
                     <span>Stop Recording</span>`;

                recordVoiceBtn.classList.add(
                    "recording"
                );
            }

            if (voiceCircle) {

                voiceCircle.classList.add(
                    "recording"
                );
            }

            if (voiceStatus) {

                voiceStatus.textContent =
                    "Listening... speak now.";
            }

            showStatus(
                voiceTranslationStatus,
                "Recording your voice...",
                "loading"
            );

        } catch (error) {

            console.error(
                "Microphone error:",
                error
            );

            showStatus(
                voiceTranslationStatus,
                error.message ||
                "Unable to access microphone.",
                "error"
            );
        }
    }

    // =====================================================
    // STOP RECORDING
    // =====================================================

    function stopRecording() {

        if (
            mediaRecorder &&
            mediaRecorder.state === "recording"
        ) {

            mediaRecorder.stop();
        }

        stopTimer();

        if (recordVoiceBtn) {

            recordVoiceBtn.innerHTML =
                `<i class="fa-solid fa-spinner fa-spin"></i>
                 <span>Processing...</span>`;

            recordVoiceBtn.disabled =
                true;

            recordVoiceBtn.classList.remove(
                "recording"
            );
        }

        if (voiceCircle) {

            voiceCircle.classList.remove(
                "recording"
            );
        }

        if (voiceStatus) {

            voiceStatus.textContent =
                "Processing your speech...";
        }
    }

    // =====================================================
    // PROCESS RECORDED AUDIO
    // =====================================================

    async function processRecordedAudio(
        mimeType
    ) {

        try {

            if (!audioChunks.length) {

                throw new Error(
                    "No audio was recorded."
                );
            }

            const audioBlob =
                new Blob(
                    audioChunks,
                    {
                        type: mimeType
                    }
                );

            console.log(
                "Recorded audio:",
                audioBlob.size,
                audioBlob.type
            );

            const sourceCode =
                getLanguageCode(
                    voiceSourceLanguage.value
                );

            const targetCode =
                getLanguageCode(
                    voiceTargetLanguage.value
                );

            const formData =
                new FormData();

            formData.append(
                "audio",
                audioBlob,
                "recording.webm"
            );

            formData.append(
                "source",
                sourceCode
            );

            formData.append(
                "target",
                targetCode
            );

            showStatus(
                voiceTranslationStatus,
                "Converting speech → text → translation → speech...",
                "loading"
            );

            const response =
                await fetch(
                    `${API_BASE}/api/voice-translate`,
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const result =
                await parseResponse(response);

            console.log(
                "Voice translation response:",
                result
            );

            if (voiceOriginalText) {

                voiceOriginalText.value =
                    result.original_text || "";
            }

            if (voiceTranslatedText) {

                voiceTranslatedText.value =
                    result.translated_text || "";
            }

            const detected =
                result.source_language ||
                sourceCode;

            const detectedName =
                getLanguageName(detected);

            translatedAudio = null;

            if (result.audio_base64) {

                translatedAudio =
                    new Audio(
                        `data:audio/mpeg;base64,${result.audio_base64}`
                    );

                if (playTranslationBtn) {

                    playTranslationBtn.disabled =
                        false;
                }
            }

            showStatus(
                voiceTranslationStatus,
                `Voice translation completed. Detected language: ${detectedName}`,
                "success"
            );

            if (voiceStatus) {

                voiceStatus.textContent =
                    "Translation ready. Press Play Translation.";
            }

        } catch (error) {

            console.error(
                "Voice translation error:",
                error
            );

            if (voiceOriginalText) {
                voiceOriginalText.value = "";
            }

            if (voiceTranslatedText) {
                voiceTranslatedText.value = "";
            }

            translatedAudio = null;

            if (playTranslationBtn) {

                playTranslationBtn.disabled =
                    true;
            }

            showStatus(
                voiceTranslationStatus,
                error.message ||
                "Unable to translate voice.",
                "error"
            );

            if (voiceStatus) {

                voiceStatus.textContent =
                    "Something went wrong. Please try again.";
            }

        } finally {

            if (recordVoiceBtn) {

                recordVoiceBtn.disabled =
                    false;

                recordVoiceBtn.innerHTML =
                    `<i class="fa-solid fa-microphone"></i>
                     <span>Start Recording</span>`;
            }

            mediaRecorder = null;
            audioChunks = [];
        }
    }

    // =====================================================
    // RECORD BUTTON
    // =====================================================

    if (recordVoiceBtn) {

        recordVoiceBtn.addEventListener(
            "click",
            async () => {

                if (
                    mediaRecorder &&
                    mediaRecorder.state === "recording"
                ) {

                    stopRecording();

                } else {

                    await startRecording();
                }
            }
        );
    }

    // =====================================================
    // PLAY TRANSLATED AUDIO
    // =====================================================

    if (playTranslationBtn) {

        playTranslationBtn.disabled = true;

        playTranslationBtn.addEventListener(
            "click",
            async () => {

                if (!translatedAudio) {
                    return;
                }

                try {

                    translatedAudio.currentTime =
                        0;

                    await translatedAudio.play();

                    showStatus(
                        voiceTranslationStatus,
                        "Playing translated speech...",
                        "success"
                    );

                } catch (error) {

                    console.error(
                        "Audio playback error:",
                        error
                    );

                    showStatus(
                        voiceTranslationStatus,
                        "Unable to play translated audio.",
                        "error"
                    );
                }
            }
        );
    }

    // =====================================================
    // SWAP TEXT LANGUAGES
    // =====================================================

    const swapBtn =
        document.getElementById(
            "swapLanguages"
        );

    if (swapBtn) {

        swapBtn.addEventListener(
            "click",
            () => {

                if (
                    sourceLanguage.value === "auto"
                ) {

                    alert(
                        "Select a source language before swapping."
                    );

                    return;
                }

                const oldSource =
                    sourceLanguage.value;

                const oldTarget =
                    targetLanguage.value;

                sourceLanguage.value =
                    oldTarget;

                targetLanguage.value =
                    oldSource;

                const oldText =
                    inputText.value;

                inputText.value =
                    translatedText.value;

                translatedText.value =
                    oldText;

                if (detectedLanguage) {

                    detectedLanguage.style.display =
                        "none";
                }

                showStatus(
                    translationStatus,
                    ""
                );
            }
        );
    }

    // =====================================================
    // INITIAL LOG
    // =====================================================

    console.log(
        "Text API:",
        `${API_BASE}/api/translate`
    );

    console.log(
        "Image API:",
        `${API_BASE}/api/image-translate`
    );

    console.log(
        "Voice Translation API:",
        `${API_BASE}/api/voice-translate`
    );

    console.log(
        "TTS API:",
        `${API_BASE}/api/text-to-speech`
    );

});
const API_BASE = "http://127.0.0.1:8000/api";

// ====================== TABS ======================
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));

    tab.classList.add("active");
    document.getElementById(`panel-${tab.dataset.tab}`).classList.add("active");
  });
});

// ====================== TEXT TRANSLATION ======================
document.getElementById("text-translate-btn").addEventListener("click", async () => {
  const text = document.getElementById("text-input").value.trim();
  const target = document.getElementById("text-target").value;
  const source = document.getElementById("text-source").value;

  if (!text) {
    showStatus("text", "Please enter some text", "error");
    return;
  }

  showStatus("text", "Translating...", "info");
  document.getElementById("text-result").classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE}/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, target, source }),
    });

    const data = await res.json();

    if (!data.success) {
      showStatus("text", data.error || "Translation failed", "error");
      return;
    }

    document.getElementById("text-output").textContent = data.translated_text;
    document.getElementById("text-result").classList.remove("hidden");
    showStatus("text", `Success • ${data.source_language} → ${data.target_language}`, "success");
  } catch (err) {
    showStatus("text", "Network error: " + err.message, "error");
  }
});

// Speak translated text
document.getElementById("text-speak-btn").addEventListener("click", async () => {
  const text = document.getElementById("text-output").textContent;
  const lang = document.getElementById("text-target").value;

  if (!text) {
    showStatus("text", "No translation to speak", "error");
    return;
  }

  showStatus("text", "Generating speech...", "info");

  const formData = new FormData();
  formData.append("text", text);
  formData.append("language", lang);

  try {
    const res = await fetch(`${API_BASE}/text-to-speech`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      showStatus("text", err.error || "TTS failed", "error");
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
    showStatus("text", "Playing translation...", "success");
  } catch (err) {
    showStatus("text", "Network error: " + err.message, "error");
  }
});

// ====================== IMAGE TRANSLATION ======================
const dropzone = document.getElementById("image-dropzone");
const imageFileInput = document.getElementById("image-file");
let selectedImage = null;
let lastImageData = null; // store response for drawing boxes

dropzone.addEventListener("click", () => imageFileInput.click());

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    handleImageSelect(e.dataTransfer.files[0]);
  }
});

imageFileInput.addEventListener("change", (e) => {
  if (e.target.files.length) {
    handleImageSelect(e.target.files[0]);
  }
});

function handleImageSelect(file) {
  selectedImage = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = document.getElementById("image-preview-img");
    img.src = e.target.result;
    document.getElementById("image-preview").classList.remove("hidden");
    document.getElementById("image-translate-btn").disabled = false;

    // Clear previous canvas
    const canvas = document.getElementById("image-canvas");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };
  reader.readAsDataURL(file);
}

document.getElementById("image-translate-btn").addEventListener("click", async () => {
  if (!selectedImage) return;

  const target = document.getElementById("image-target").value;

  showStatus("image", "Processing image...", "info");
  document.getElementById("image-result").classList.add("hidden");

  const formData = new FormData();
  formData.append("image", selectedImage);
  formData.append("target", target);

  try {
    const res = await fetch(`${API_BASE}/image-translate`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!data.success) {
      showStatus("image", data.error || "Image translation failed", "error");
      return;
    }

    lastImageData = data;

    document.getElementById("image-original").textContent = data.original_text;
    document.getElementById("image-translated").textContent = data.translated_text;

    // Draw bounding boxes
    drawBoundingBoxes(data);

    // Show regions list
    renderRegionsList(data.positioned_items || []);

    document.getElementById("image-result").classList.remove("hidden");
    showStatus("image", `Success • ${data.source_language} → ${data.target_language}`, "success");
  } catch (err) {
    showStatus("image", "Network error: " + err.message, "error");
  }
});

function drawBoundingBoxes(data) {
  const img = document.getElementById("image-preview-img");
  const canvas = document.getElementById("image-canvas");
  const ctx = canvas.getContext("2d");

  // Wait for image to load dimensions
  const draw = () => {
    const displayWidth = img.clientWidth;
    const displayHeight = img.clientHeight;

    canvas.width = displayWidth;
    canvas.height = displayHeight;
    canvas.style.width = displayWidth + "px";
    canvas.style.height = displayHeight + "px";

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const originalWidth = data.image?.width || img.naturalWidth;
    const originalHeight = data.image?.height || img.naturalHeight;

    const scaleX = displayWidth / originalWidth;
    const scaleY = displayHeight / originalHeight;

    const items = data.positioned_items || [];

    items.forEach((item, index) => {
      if (!item.box || item.box.length < 4) return;

      const points = item.box.map((p) => ({
        x: p[0] * scaleX,
        y: p[1] * scaleY,
      }));

      // Draw polygon
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
      }
      ctx.closePath();

      // Color based on confidence
      if (item.low_confidence) {
        ctx.strokeStyle = "#f59e0b"; // orange
        ctx.fillStyle = "rgba(245, 158, 11, 0.15)";
      } else {
        ctx.strokeStyle = "#22c55e"; // green
        ctx.fillStyle = "rgba(34, 197, 94, 0.12)";
      }

      ctx.lineWidth = 2;
      ctx.fill();
      ctx.stroke();

      // Draw index number
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 12px sans-serif";
      ctx.fillText(String(index + 1), points[0].x + 4, points[0].y + 14);
    });
  };

  if (img.complete) {
    draw();
  } else {
    img.onload = draw;
  }
}

function renderRegionsList(items) {
  const container = document.getElementById("image-regions");
  container.innerHTML = "";

  if (!items.length) {
    container.innerHTML = `<div class="region-item">No text regions detected</div>`;
    return;
  }

  items.forEach((item, index) => {
    const div = document.createElement("div");
    div.className = "region-item" + (item.low_confidence ? " low-confidence" : "");
    div.innerHTML = `
      <div>
        <strong>#${index + 1}</strong>
        <span class="original"> ${item.text}</span>
      </div>
      <div class="translated">${item.translated_text}</div>
    `;
    container.appendChild(div);
  });
}

// ====================== VOICE TRANSLATION ======================
let mediaRecorder = null;
let audioChunks = [];
let lastVoiceAudioBase64 = null;

document.getElementById("voice-record-btn").addEventListener("click", toggleRecording);
document.getElementById("voice-upload-btn").addEventListener("click", () => {
  document.getElementById("voice-file").click();
});
document.getElementById("voice-file").addEventListener("change", (e) => {
  if (e.target.files.length) {
    runVoiceTranslate(e.target.files[0]);
  }
});

document.getElementById("voice-download-btn").addEventListener("click", () => {
  if (!lastVoiceAudioBase64) return;
  downloadBase64Audio(lastVoiceAudioBase64, "translated-audio.mp3");
});

async function toggleRecording() {
  const btn = document.getElementById("voice-record-btn");

  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    btn.textContent = "🎤 Start Recording";
    btn.classList.remove("recording", "btn-danger");
    btn.classList.add("btn-primary");
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: "audio/webm" });
      stream.getTracks().forEach((t) => t.stop());
      await runVoiceTranslate(blob);
    };

    mediaRecorder.start();
    btn.textContent = "⏹ Stop Recording";
    btn.classList.remove("btn-primary");
    btn.classList.add("btn-danger", "recording");
    showStatus("voice", "Recording... Speak now", "info");
  } catch (err) {
    showStatus("voice", "Microphone access denied", "error");
  }
}

async function runVoiceTranslate(audioBlob) {
  showStatus("voice", "Processing voice translation...", "info");
  document.getElementById("voice-result").classList.add("hidden");

  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  formData.append("target", document.getElementById("voice-target").value);
  formData.append("source", document.getElementById("voice-source").value);

  try {
    const res = await fetch(`${API_BASE}/voice-translate`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!data.success) {
      showStatus("voice", data.error || "Voice translation failed", "error");
      return;
    }

    document.getElementById("voice-original").textContent = data.original_text;
    document.getElementById("voice-translated").textContent = data.translated_text;

    lastVoiceAudioBase64 = data.audio_base64;
    const audioSrc = `data:audio/mp3;base64,${data.audio_base64}`;
    const audioEl = document.getElementById("voice-audio");
    audioEl.src = audioSrc;
    audioEl.play().catch(() => {});

    document.getElementById("voice-result").classList.remove("hidden");
    showStatus("voice", `Success • ${data.source_language} → ${data.target_language}`, "success");
  } catch (err) {
    showStatus("voice", "Network error: " + err.message, "error");
  }
}

// ====================== TEXT TO SPEECH ======================
let lastTtsBlobUrl = null;

document.getElementById("tts-btn").addEventListener("click", async () => {
  const text = document.getElementById("tts-text").value.trim();
  const lang = document.getElementById("tts-lang").value;

  if (!text) {
    showStatus("tts", "Please enter some text", "error");
    return;
  }

  showStatus("tts", "Generating speech...", "info");
  document.getElementById("tts-result").classList.add("hidden");
  document.getElementById("tts-download-btn").classList.add("hidden");

  const formData = new FormData();
  formData.append("text", text);
  formData.append("language", lang);

  try {
    const res = await fetch(`${API_BASE}/text-to-speech`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      showStatus("tts", err.error || "TTS failed", "error");
      return;
    }

    const blob = await res.blob();
    if (lastTtsBlobUrl) URL.revokeObjectURL(lastTtsBlobUrl);
    lastTtsBlobUrl = URL.createObjectURL(blob);

    const audioEl = document.getElementById("tts-audio");
    audioEl.src = lastTtsBlobUrl;
    audioEl.play().catch(() => {});

    document.getElementById("tts-result").classList.remove("hidden");
    document.getElementById("tts-download-btn").classList.remove("hidden");
    showStatus("tts", "Speech generated", "success");
  } catch (err) {
    showStatus("tts", "Network error: " + err.message, "error");
  }
});

document.getElementById("tts-download-btn").addEventListener("click", () => {
  if (!lastTtsBlobUrl) return;
  const a = document.createElement("a");
  a.href = lastTtsBlobUrl;
  a.download = "speech.mp3";
  a.click();
});

// ====================== HELPERS ======================
function showStatus(mode, message, type) {
  const el = document.getElementById(`${mode}-status`);
  if (!el) return;
  el.textContent = message;
  el.className = `status show ${type}`;
}

function downloadBase64Audio(base64, filename) {
  const a = document.createElement("a");
  a.href = `data:audio/mp3;base64,${base64}`;
  a.download = filename;
  a.click();
}
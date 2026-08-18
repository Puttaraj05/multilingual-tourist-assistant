const form = document.getElementById("helpForm");
const locationInput = document.getElementById("location");
const emergencyType = document.getElementById("emergencyType");
const resultsContainer = document.getElementById("results");

const sampleData = {
  Hospital: [
    {
      name: "City Care Hospital",
      distance: "1.2 km",
      phone: "+91 98765 43210",
      address: "Main Road"
    },
    {
      name: "Apollo Emergency Center",
      distance: "3.8 km",
      phone: "+91 91234 56789",
      address: "MG Road"
    }
  ],

  Police: [
    {
      name: "Central Police Station",
      distance: "900 m",
      phone: "100",
      address: "Station Road"
    },
    {
      name: "Tourist Police Help Desk",
      distance: "2.5 km",
      phone: "+91 99887 77665",
      address: "City Square"
    }
  ],

  Ambulance: [
    {
      name: "108 Emergency Ambulance",
      distance: "Available",
      phone: "108",
      address: "Nationwide"
    }
  ],

  Embassy: [
    {
      name: "Indian Embassy Help Desk",
      distance: "5 km",
      phone: "+91 1800 111 363",
      address: "Embassy District"
    }
  ]
};

form.addEventListener("submit", (e) => {
  e.preventDefault();

  const location = locationInput.value.trim();
  const type = emergencyType.value;

  resultsContainer.innerHTML = "";

  const title = document.createElement("h3");
  title.textContent = `${type} near ${location || "your location"}`;
  resultsContainer.appendChild(title);

  sampleData[type].forEach((place) => {
    const card = document.createElement("div");
    card.className = "emergency-card";

    card.innerHTML = `
      <div class="emergency-info">
        <h4>${place.name}</h4>
        <p>📍 ${place.address}</p>
        <p>📏 ${place.distance}</p>
      </div>

      <div class="emergency-actions">
        <a href="tel:${place.phone.replace(/\s+/g, "")}" class="call-btn">
          📞 ${place.phone}
        </a>

        <a href="https://www.google.com/maps/search/${encodeURIComponent(
          place.name + " " + place.address
        )}" target="_blank" class="map-btn">
          🗺 View Map
        </a>
      </div>
    `;

    resultsContainer.appendChild(card);
  });
});
const resultsGrid = document.getElementById("resultsGrid");
const resultCount = document.getElementById("resultCount");

const places = [
{
name:"Blue Tokai Café",
type:"cafe",
distance:2,
rating:4.8,
description:"Specialty coffee with a cozy atmosphere.",
icon:"fa-mug-hot"
},
{
name:"Taj Palace Hotel",
type:"hotel",
distance:4,
rating:4.9,
description:"Luxury stay with premium amenities.",
icon:"fa-hotel"
},
{
name:"Paradise Biryani",
type:"restaurant",
distance:6,
rating:4.7,
description:"Popular local restaurant famous for biryani.",
icon:"fa-utensils"
},
{
name:"City Heritage Museum",
type:"attraction",
distance:8,
rating:4.6,
description:"Discover local history and culture.",
icon:"fa-landmark"
},
{
name:"Central Mall",
type:"shopping",
distance:12,
rating:4.5,
description:"Shopping, food court and entertainment.",
icon:"fa-bag-shopping"
},
{
name:"Sunset View Point",
type:"attraction",
distance:5,
rating:4.9,
description:"Beautiful sunset spot loved by travelers.",
icon:"fa-mountain-sun"
}
];

function renderPlaces(){

const category=document.getElementById("categoryFilter").value;
const maxDistance=Number(document.getElementById("distanceFilter").value);
const location=document.getElementById("searchLocation").value.trim() || "your location";

const filtered=places.filter(place=>{

const categoryMatch=category==="all" || place.type===category;
const distanceMatch=place.distance<=maxDistance;

return categoryMatch && distanceMatch;

});

resultCount.textContent=`${filtered.length} places found`;

resultsGrid.innerHTML="";

filtered.forEach(place=>{

resultsGrid.innerHTML+=`

<div class="place-card">

<div class="place-top">

<div class="place-icon">
<i class="fa-solid ${place.icon}"></i>
</div>

<div class="place-rating">
⭐ ${place.rating}
</div>

</div>

<h3>${place.name}</h3>

<p>${place.description}</p>

<div class="place-meta">

<span>${place.distance} km away</span>

<span>${place.type}</span>

</div>

<div class="place-actions">

<a
class="map-btn"
target="_blank"
href="https://www.google.com/maps/search/${encodeURIComponent(place.name+" "+location)}">

View Map

</a>

<a
class="dir-btn"
target="_blank"
href="https://www.google.com/maps/search/${encodeURIComponent(place.name+" "+location)}">

Directions

</a>

</div>

</div>

`;

});

}

document.getElementById("searchBtn").onclick=renderPlaces;
document.getElementById("categoryFilter").onchange=renderPlaces;
document.getElementById("distanceFilter").onchange=renderPlaces;

document.getElementById("nearMeBtn").onclick=()=>{

document.getElementById("searchLocation").value="Current Location";

renderPlaces();

};

renderPlaces();
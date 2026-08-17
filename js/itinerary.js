const saved=localStorage.getItem("itinerary");

if(!saved){
window.location.href="planner.html";
}

const itinerary=JSON.parse(saved);

const currency=itinerary.currencySymbol||"₹";

const labels={

English:{
plan:"YOUR PERSONALIZED PLAN",
duration:"Duration",
budget:"Budget",
interests:"Interests",
modify:"Modify Trip",
save:"Save Itinerary"
}

};

const ui=labels[itinerary.language]||labels.English;

document.getElementById("planLabel").textContent=ui.plan;
document.getElementById("durationLabel").textContent=ui.duration;
document.getElementById("budgetLabel").textContent=ui.budget;
document.getElementById("interestsLabel").textContent=ui.interests;
document.getElementById("modifyLabel").textContent=ui.modify;
document.getElementById("saveLabel").textContent=ui.save;

document.getElementById("destinationTitle").textContent=itinerary.destination;

document.getElementById("summaryDuration").textContent=
itinerary.duration+" Days";

document.getElementById("summaryBudget").textContent=
currency+Number(itinerary.budget).toLocaleString();

document.getElementById("summaryInterests").textContent=
itinerary.interests.join(", ");

const container=document.getElementById("itineraryContent");

container.innerHTML="";

itinerary.days.forEach(day=>{

const section=document.createElement("section");

section.className="day-section";

let activities="";

day.activities.forEach(activity=>{

activities+=`

<div class="activity">

<div class="activity-time">
${activity.time}
</div>

<div class="activity-content">

<h3>${activity.place}</h3>

<p>${activity.description}</p>

<div class="activity-meta">

${activity.category}

<span>•</span>

${currency}${Number(activity.cost).toLocaleString()}

<span>•</span>

${activity.duration}

</div>

</div>

</div>

`;

});

section.innerHTML=`

<div class="day-heading">

<span class="day-number">

${String(day.day).padStart(2,"0")}

</span>

<div>

<p>DAY ${day.day}</p>

<h2>${day.title}</h2>

</div>

</div>

<div class="timeline">

${activities}

</div>

`;

container.appendChild(section);

});
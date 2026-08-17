const form = document.getElementById("plannerForm");

const durationInput = document.getElementById("duration");
const decreaseButton = document.getElementById("decreaseDays");
const increaseButton = document.getElementById("increaseDays");

decreaseButton.addEventListener("click",()=>{

let days=parseInt(durationInput.value);

if(days>1) durationInput.value=days-1;

});

increaseButton.addEventListener("click",()=>{

let days=parseInt(durationInput.value);

if(days<30) durationInput.value=days+1;

});

form.addEventListener("submit",async(e)=>{

e.preventDefault();

const destination=document.getElementById("destination").value.trim();

const duration=parseInt(document.getElementById("duration").value);

const travelDate=document.getElementById("travelDate").value;

const budget=Number(document.getElementById("budget").value);

const language=document.getElementById("language").value;

const interests=[];

document.querySelectorAll('input[name="interest"]:checked').forEach(i=>{

interests.push(i.value);

});

const tripData={

destination,

duration,

travelDate,

budget,

language,

interests

};

const button=document.querySelector(".generate-button");

button.disabled=true;

button.innerHTML="Generating...";

try{

const response=await fetch(
"http://127.0.0.1:8000/api/itinerary",
{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(tripData)
}
);

const result=await response.json();

if(!response.ok){
throw new Error(result.error||"Something went wrong.");
}

result.destination=destination;

localStorage.setItem(
"itinerary",
JSON.stringify(result)
);

window.location.href="itinerary.html";

}catch(err){

alert(err.message);

button.disabled=false;

button.innerHTML='<span data-key="continue">Generate My Itinerary</span>';

}

});
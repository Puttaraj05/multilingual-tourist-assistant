const tabs = document.querySelectorAll(".tab");
const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");

tabs.forEach(tab => {
tab.addEventListener("click", () => {

tabs.forEach(t => t.classList.remove("active"));
tab.classList.add("active");

if(tab.dataset.tab === "login"){
loginForm.classList.remove("hidden");
signupForm.classList.add("hidden");
}else{
signupForm.classList.remove("hidden");
loginForm.classList.add("hidden");
}

});
});

// Demo only

loginForm.addEventListener("submit",(e)=>{
e.preventDefault();
alert("Login integration will be connected later.");
});

signupForm.addEventListener("submit",(e)=>{
e.preventDefault();
alert("Signup integration will be connected later.");
});
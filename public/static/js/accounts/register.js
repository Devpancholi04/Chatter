// creating validation requirements
const namePattern = /^[a-zA-Z\s]+$/;
const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const mobilePattern = /^[0-9]{10}$/;
const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
const usernamePattern = /^[a-zA-Z0-9._@]+$/;


// getting the element using their ID
const username = document.getElementById('username');
const fname = document.getElementById('fname');
const lname = document.getElementById('lname');
const dob = document.getElementById('dob');
const gender = document.getElementById('gender');
const email = document.getElementById('email');
const mobile = document.getElementById('mobile');
const password = document.getElementById('password');
const repassword = document.getElementById('re-password');

// getting button using their ID
const NextButton = document.getElementById('nextButton');
const submitButton = document.getElementById('submitButton');


// validate field function
function validateField(field, pattern, errorId){
    const isValid = pattern.test(field.value);
    document.getElementById(errorId).style.display = isValid || !field.value ? "none" : "block";
    return isValid;
}

// password matching function to validate
function validatePasswordMatch(){
    const isValid = password.value === repassword.value;
    document.getElementById('repasswordError').style.display = isValid ? "none" : "block";
    return isValid;
}


// validate gender function
function validateGender(){
    const GenderValue = gender.value;

    if(GenderValue === ""){
        document.getElementById('genderError').style.display = "block";
        return false
    }
    else{
        document.getElementById('genderError').style.display = "none";
        return true;
    }
}


// validate Dob function
function validateDob() {
    const dobValue = dob.value.trim();

    if(dobValue === ""){
        document.getElementById('dobError').style.display = "block";
        return false
    }
    const selectedDate = new Date(dobValue);
    const today = new Date();

    today.setHours(0,0,0,0);
    if(selectedDate > today){
        document.getElementById('dobError').textContent = "Date of Birth cannot be in Future.";
        document.getElementById('dobError').style.display = "block";
        return false
    }

    document.getElementById('dobError').style.display = "none";
    return true;
}

// move to next page function before validatation checking function
function NextPage(){
    const isUsernameValid = validateField(username, usernamePattern, "usernameError");
    const isFnameValid = validateField(fname, namePattern, "fnameError");
    const isLnameValid = validateField(lname, namePattern, "lnameError");
    const isDobValid = validateDob();
    const isGenderValid = validateGender();

    if (isUsernameValid && isFnameValid && isLnameValid && isDobValid && isGenderValid){
        NextButton.disabled = false;
    }
}

// activating the button to be called on the click
NextButton.addEventListener('click', function(){
    if(!this.disabled){
        document.getElementById('page1').style.display = 'none';
        document.getElementById('page2').style.display = 'block'
    }
})
 

// go to pervious page function
function prevStep() {
    document.getElementById('page2').style.display = 'none';
    document.getElementById('page1').style.display = 'block';
}


// checking the validate for the page 2 and updating the submit button function
function UpdateSubmitButtonState(){
    const isEmailValid = validateField(email, emailPattern, "emailError");
    const isMobileValid = validateField(mobile, mobilePattern, "mobileError");
    const isPasswordValid = validateField(password, passwordPattern, "passwordError");
    const isrePasswordValid = validatePasswordMatch();

    if(isEmailValid && isMobileValid && isPasswordValid && isrePasswordValid){
        submitButton.disabled = false;
    }

}

// applying the eventlistner on the field and required function on the fields
username.addEventListener("input", NextPage);
fname.addEventListener("input", NextPage);
lname.addEventListener("input", NextPage);
dob.addEventListener("input", NextPage);
gender.addEventListener("change", NextPage);

email.addEventListener("input", UpdateSubmitButtonState);
mobile.addEventListener("input", UpdateSubmitButtonState);
password.addEventListener("input", UpdateSubmitButtonState);
repassword.addEventListener("input", UpdateSubmitButtonState);


// add the eventlistner on the feild make the on focus and off focus on the field and showing or hidding the error message 
username.addEventListener("blur", () => {if (!username.value) document.getElementById('usernameError').style.display = "none";});
fname.addEventListener("blur", () => {if (!fname.value) document.getElementById('fnameError').style.display = "none";});
lname.addEventListener("blur", () => {if (!lname.value) document.getElementById('lnameError').style.display = "none";});
dob.addEventListener("blur", () => {if (!dob.value) document.getElementById('dobError').style.display = "none";});
gender.addEventListener("blur", () => {if (!gender.value) document.getElementById('genderError').style.display = "none";});

email.addEventListener("blur", () => {if (!email.value) document.getElementById('emailError').style.display = "none";});
mobile.addEventListener("blur", () => {if (!mobile.value) document.getElementById('mobileError').style.display = "none";});
password.addEventListener("blur", () => {if (!password.value) document.getElementById('passwordError').style.display = "none";});
repassword.addEventListener("blur", () => {if (!repassword.value) document.getElementById('repasswordError').style.display = "none";});
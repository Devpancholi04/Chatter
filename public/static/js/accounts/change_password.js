const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

const password = document.getElementById('password');
const repassword = document.getElementById('repassword');

const ChangeBtn = document.getElementById('change-btn')

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

function SubmitBtn(){
    const isPasswordValid = validateField(password, passwordPattern, "passwordError");
    const isrePasswordValid = validatePasswordMatch();

    if(isPasswordValid && isrePasswordValid){
        ChangeBtn.disabled = false;
    }
}

password.addEventListener("input", SubmitBtn);
repassword.addEventListener("input", SubmitBtn);

password.addEventListener("blur", () => {if (!password.value) document.getElementById('passwordError').style.display = "none";});
repassword.addEventListener("blur", () => {if (!repassword.value) document.getElementById('repasswordError').style.display = "none";});

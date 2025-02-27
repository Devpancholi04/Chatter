
document.querySelector('form').addEventListener('submit', function(event){
    const submitButton = document.getElementById('submitButton');
    const spinner = document.getElementById('spinner')

    spinner.style.display = 'inline-block'
    submitButton.disabled = true
})


document.querySelector('form').addEventListener('button', function(event){
    const resendbutton = document.getElementById('resendbutton');
    const spinner = document.getElementById('spinner')

    spinner.style.display = 'inline-block'
    resendbutton.disabled = true
})
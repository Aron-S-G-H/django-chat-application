"use strict";

// LOGIN FORM
const loginForm = document.getElementById('loginForm');
const loginUsernameInput = loginForm.querySelector('#loginUsername');
const loginPasswordInput = loginForm.querySelector('#loginPass');
const loginSubmitBtn = loginForm.querySelector('#loginBtn');
const changeToForgotPass = loginForm.querySelector('#forgotPass');
const changeToRegister = loginForm.querySelector('.changeToRegister');
// REGISTER FORM
const registerForm = document.getElementById('registerForm');
const registerUsernameInput = registerForm.querySelector('#R-Username');
const registerEmailInput = registerForm.querySelector('#R-Email');
const registerFirstnameInput = registerForm.querySelector('#R-FirstName');
const registerLastnameInput = registerForm.querySelector('#R-LastName');
const registerPasswordInput = registerForm.querySelector('#R-Pass');
const registerConfirmPasswordInput = registerForm.querySelector('#R-ConfirmPass');
const registerSubmitBtn = registerForm.querySelector('#registerBtn');
const changeToLogin = registerForm.querySelector('.changeToLogin');
// OTP FORM
const otpForm = document.getElementById('otpForm');
const otpCodeInput = otpForm.querySelector('#otpCode');
const otpSubmitBtn = otpForm.querySelector('#otpBtn');
const OTPtoLogin = otpForm.querySelector('.OTPtoLogin');
// FORGOT PASSWORD FORM
const forgotPassForm = document.getElementById('forgotPassForm');
const emailSection = forgotPassForm.querySelector('#email-section');
const codeSection = forgotPassForm.querySelector('#code-section');
const forgotPassEmailInput = emailSection.querySelector('#forgotPassEmail');
const forgotPassEmailSubmit = emailSection.querySelector('#submitEmail');
const forgotPassCodeInput = codeSection.querySelector('#forgotPassCodeInput')
const forgotPassCodeSubmit = codeSection.querySelector('#submitCode');
const FPtoLogin = forgotPassForm.querySelector('.FPtoLogin')


function checkInputsValue(formType){
    let inputs;

    if (formType === 'loginForm'){
        inputs = loginForm.querySelectorAll('.wrap-input100 input');
    } else if (formType === 'registerForm'){
        inputs = registerForm.querySelectorAll('.wrap-input100 input');
    } else if (formType === 'otpForm'){
        inputs = otpForm.querySelectorAll('.wrap-input100 input');
    } else if (formType === 'forgotPass_emailSection'){
        inputs = emailSection.querySelectorAll('.wrap-input100 input');
    } else if (formType === 'forgotPass_codeSection'){
        inputs = codeSection.querySelectorAll('.wrap-input100 input');
    }

    let inputsNumber = inputs.length;
    let filledInputs = 0;

    for (let input of inputs){
        if (!input.value){
            let parentElement = input.parentElement;
            if (parentElement.firstElementChild.tagName !== 'SPAN'){
                parentElement.insertAdjacentHTML('afterbegin',
                    `<span class="d-block text-center bg-danger text-light" style="border-radius: 10px 10px 0px 0px">
                    This field is required
                    </span>`
                )
            }
        }else{
            filledInputs += 1;
        }
    }

    if (filledInputs !== inputsNumber) {
        return false
    } else {
        return true
    }
}

loginSubmitBtn.addEventListener('click', () => {
    let checkInputs = checkInputsValue('loginForm');
    if (checkInputs){
        let formData = new FormData;
        formData.append('username', loginUsernameInput.value);
        formData.append('password', loginPasswordInput.value);
        formData.append('csrfmiddlewaretoken', loginForm.dataset.csrf);

        axios.post('/account/login', formData)
            .then(response => {
                if (response.data.status === 200){
                    Swal.fire({
                        position: 'top-start',
                        icon: 'success',
                        title: `Wellcome back ${response.data.username}`,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.replace('/chat/lobby');
                    })
                }
                else if (response.data.status === 401){
                    Swal.fire({
                        icon: 'error',
                        title: 'Authentication Error',
                        text: 'No user found with this information',
                        confirmButtonColor: '#3085d6',
                    })
                }
                else if (response.data.status === 400){
                    Swal.fire({
                        icon: 'error',
                        title: 'Error 400',
                        text: 'Some required information was not sent',
                        confirmButtonColor: '#3085d6',
                    })
                }
            })
            .catch(err => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error 500',
                    text: 'An error has occurred! Check your internet connection and try again. If the problem persists, contact support.',
                    confirmButtonColor: '#3085d6',
                })
                console.log(err)
            })
    }
})

function showError(parentElement, message){
    if (parentElement.firstElementChild.tagName !== 'SPAN'){
        parentElement.insertAdjacentHTML('afterbegin',
            `<span class="d-block text-center bg-danger text-light" style="border-radius: 10px 10px 0px 0px">
             ${message}
            </span>`
        )
    }else {
        parentElement.firstElementChild.innerHTML = message
    }
}

registerSubmitBtn.addEventListener('click', () => {
    let checkInputs = checkInputsValue('registerForm');
    if (checkInputs){
        if (registerPasswordInput.value !== registerConfirmPasswordInput.value){
            showError(registerPasswordInput.parentElement, 'Passwords are not the Same');
        }
        else{
            let formData = new FormData;
            formData.append('username', registerUsernameInput.value);
            formData.append('email', registerEmailInput.value);
            formData.append('first_name', registerFirstnameInput.value);
            formData.append('last_name', registerLastnameInput.value);
            formData.append('password', registerPasswordInput.value);
            formData.append('confirm_pass', registerConfirmPasswordInput.value);
            formData.append('csrfmiddlewaretoken', registerForm.dataset.csrf);

            axios.post('/account/register', formData)
                .then(response => {
                    if (response.data.status === 200){
                        let token = response.data.token;
                        otpSubmitBtn.addEventListener('click', () => {
                            submitOtpCode(token)
                        })
                        registerForm.classList.add('d-none');
                        otpForm.classList.remove('d-none');
                    }
                    else if (response.data.status === 400){
                        if (response.data.message === 'passwords conflict'){
                            showError(registerPasswordInput.parentElement, 'Passwords are not the Same');
                        }else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error 400',
                                text: 'Some required information was not sent',
                                confirmButtonColor: '#3085d6',
                            })
                        }
                    }
                    else if (response.data.status === 409){
                        Swal.fire({
                            icon: 'error',
                            title: 'Authentication Error',
                            text: 'User with this information exist. sign in or use forgot password',
                            footer: `<a href="/account/login">Sign in</a>`,
                            confirmButtonColor: '#3085d6',
                        });
                    }
                    else if (response.data.status === 500){
                        Swal.fire({
                            icon: 'error',
                            title: 'Error 500',
                            text: response.data.message,
                            confirmButtonColor: '#3085d6',
                        })
                    }
                })
        }
    }
})

function submitOtpCode (token) {
    let checkInputs = checkInputsValue('otpForm');
    if (checkInputs){
        let formData = new FormData;
        formData.append('code', otpCodeInput.value);
        formData.append('token', token);
        formData.append('csrfmiddlewaretoken', otpForm.dataset.csrf);
        axios.post('/account/checkotp', formData)
            .then(response => {
                if (response.data.status === 200){
                    Swal.fire({
                        position: 'top-start',
                        icon: 'success',
                        title: `Wellcome ${response.data.username}`,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.replace('/chat/lobby');
                    })
                }
                else if (response.data.status === 400){
                    if (response.data.message === 'Invalid code'){
                        showError(otpCodeInput.parentElement, response.data.message);
                    }else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error 400',
                            text: 'Some required information was not sent',
                            confirmButtonColor: '#3085d6',
                        })
                    }
                }
            })
    }
}

forgotPassEmailSubmit.addEventListener('click', () => {
    let checkInputs = checkInputsValue('forgotPass_emailSection');
    if (checkInputs){
        let email = forgotPassEmailInput.value;
        axios.get(`/account/forgot-password?email=${email}`)
            .then(response => {
                if (response.data.status === 200){
                    let token = response.data.token;

                    forgotPassCodeSubmit.addEventListener('click', () => {
                        submitCode(token);
                    })
                    emailSection.classList.add('d-none');
                    codeSection.classList.remove('d-none');
                }
                else if (response.data.status === 400){
                    if (response.data.message === 'Data not sent'){
                        showError(forgotPassEmailInput.parentElement, response.data.message);
                    }else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error 400',
                            text: 'User not found, try to sign up',
                            confirmButtonColor: '#3085d6',
                        })
                    }
                }
                else if (response.data.status === 500){
                    Swal.fire({
                        icon: 'error',
                        title: 'Error 500',
                        text: response.data.message,
                        confirmButtonColor: '#3085d6',
                    })
                }
            })
    }
})

function submitCode(token){
    let checkInputs = checkInputsValue('forgotPass_codeSection');
    if (checkInputs){
        let formData = new FormData;
        formData.append('code', forgotPassCodeInput.value);
        formData.append('token', token);
        formData.append('csrfmiddlewaretoken', forgotPassForm.dataset.csrf);
        axios.post('/account/forgot-password', formData)
            .then(response => {
                if (response.data.status === 200){
                    Swal.fire({
                        position: 'top-start',
                        icon: 'success',
                        title: `Wellcome back ${response.data.username}`,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.replace('/chat/lobby');
                    })
                }
                else if (response.data.status === 400){
                    if (response.data.message === 'Code is wrong'){
                        showError(forgotPassCodeInput.parentElement, response.data.message);
                    }else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error 400',
                            text: response.data.message,
                            confirmButtonColor: '#3085d6',
                        })
                    }
                }
            })
    }
}

changeToRegister.addEventListener('click', event => {
    event.preventDefault();
    loginForm.classList.add('d-none');
    registerForm.classList.remove('d-none');
})
changeToLogin.addEventListener('click', event => {
    event.preventDefault();
    loginForm.classList.remove('d-none');
    registerForm.classList.add('d-none');
})
OTPtoLogin.addEventListener('click', event => {
    event.preventDefault();
    otpForm.classList.add('d-none');
    loginForm.classList.remove('d-none');
})
changeToForgotPass.addEventListener('click', event => {
    event.preventDefault();
    loginForm.classList.add('d-none');
    forgotPassForm.classList.remove('d-none');
})
FPtoLogin.addEventListener('click', event => {
    event.preventDefault();
    forgotPassForm.classList.add('d-none');
    loginForm.classList.remove('d-none');
})
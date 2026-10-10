document.addEventListener('DOMContentLoaded', function() {
    const inputEmail = document.getElementById('email');
    const inputPassword = document.getElementById('password');
    const button = document.getElementById('send');

    button.addEventListener('click', function() {
        const email = inputEmail.value;
        const password = inputPassword.value;

        fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Неверный email или пароль');
            }
        })
        .then(data => {
            localStorage.setItem('token', data.access_token);
            window.location.href = '/static/index.html';
        })
        .catch(error => {
            alert(error.message);
        });
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            if (response.ok) {
                // Регистрация прошла → логинимся
                const loginResponse = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                if (loginResponse.ok) {
                    const data = await loginResponse.json();
                    localStorage.setItem('token', data.access_token);
                    window.location.href = '/static/index.html';
                } else {
                    alert('Регистрация прошла, но войти не удалось. Войдите вручную.');
                    window.location.href = '/static/login.html';
                }
            } else {
                // ← Добавь обработку ошибок регистрации
                const errorData = await response.json();
                alert('Ошибка регистрации: ' + (errorData.detail || 'Попробуйте ещё раз'));
            }
        } catch (error) {
            alert('Ошибка сети: ' + error.message);
        }
    });
});
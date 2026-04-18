document.getElementById('signupForm').addEventListener('submit', function(e) {
    const email = this.email.value.trim();
    const name = this.name.value.trim();
    const password1 = this.password1.value;
    const password2 = this.password2.value;

    const errorBox = document.getElementById('signupError');

    errorBox.hidden = true;
    errorBox.textContent = '';

    if (email.length > 254) {
        e.preventDefault();
        showError("Email слишком длинный (макс 254)");
        return;
    }

    if (name.length > 25) {
        e.preventDefault();
        showError("Имя слишком длинное (макс 25)");
        return;
    }

    if (password1 !== password2) {
        e.preventDefault();
        showError("Пароли не совпадают");
        return;
    }

    function showError(text) {
        errorBox.textContent = text;
        errorBox.hidden = false;
    }
});
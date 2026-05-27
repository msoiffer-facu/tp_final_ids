const form = document.querySelector(".login-form");

form.addEventListener("submit", (event) => {

    const email = document.querySelector("#email").value.trim();
    const password = document.querySelector("#password").value.trim();

    if (!email || !password) {

        event.preventDefault();

        alert("Completa todos los campos");
    }

    if (!email.includes("@")) {

        event.preventDefault();

        alert("Ingresá un correo válido");

    }

});
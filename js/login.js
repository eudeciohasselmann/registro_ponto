const loginForm = document.querySelector(".login-form");
const registerForm = document.querySelector(".register-form");
const wrapper = document.querySelector(".wrapper");
const loginTitle = document.querySelector(".title-login");
const registerTitle = document.querySelector(".title-register");

document.addEventListener("DOMContentLoaded", () => {
  const inputFields = document.querySelectorAll(".input-field");

  inputFields.forEach((inputField) => {
    inputField.value = "";
    const label = inputField.nextElementSibling;
    label.style.top = "50%";
    label.style.fontSize = "16px";

    inputField.addEventListener("input", function () {
      if (this.value) {
        this.classList.add("has-value");
        label.style.top = "0";
        label.style.fontSize = "14px";
      } else {
        this.classList.remove("has-value");
        label.style.top = "50%";
        label.style.fontSize = "16px";
      }
    });
  });
});

function loginFunction() {
  loginForm.style.left = "50%";
  loginForm.style.opacity = 1;
  registerForm.style.left = "150%";
  registerForm.style.opacity = 0;
  wrapper.style.height = "500px";
  loginTitle.style.top = "50%";
  loginTitle.style.opacity = 1;
  registerTitle.style.top = "50px";
  registerTitle.style.opacity = 0;
}

function registerFunction() {
  loginForm.style.left = "-50%";
  loginForm.style.opacity = 0;
  registerForm.style.left = "50%";
  registerForm.style.opacity = 1;
  wrapper.style.height = "580px";
  loginTitle.style.top = "-60px";
  loginTitle.style.opacity = 0;
  registerTitle.style.top = "50%";
  registerTitle.style.opacity = 1;
}

function recoverPassword() {
  window.location.href = "forgot-password.html";
}

async function login(event) {
  event.preventDefault();
  const nome = document.getElementById("log-user").value.trim();
  const senha = document.getElementById("log-pass").value;

  try {
    const response = await apiRequest("LOGIN", {
      method: "POST",
      body: JSON.stringify({ nome, senha }),
    });

    const data = await response.json();

    if (response.ok) {
      sessionStorage.setItem("usuarioAtual", data.user.nome);
      window.location.href = "ponto.html";
    } else {
      alert(data.error || "Erro ao fazer login.");
    }
  } catch (error) {
    console.error("Erro na requisição:", error);
    alert("Não foi possível conectar ao servidor.");
  }
}

async function cadastrar(event) {
  event.preventDefault();
  const nome = document.getElementById("reg-name").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const senha = document.getElementById("reg-pass").value;
  const horas = document.getElementById("reg-time").value;
  const termsAccepted = document.getElementById("agree").checked;

  if (!nome || !email || !senha || !horas) {
    alert("Por favor, preencha todos os campos.");
    return;
  }

  if (!termsAccepted) {
    alert("Você deve aceitar os termos e condições para se cadastrar.");
    return;
  }

  try {
    const response = await apiRequest("USERS", {
      method: "POST",
      body: JSON.stringify({ nome, email, senha, horas, termsAccepted }),
    });

    const data = await response.json();

    if (response.status === 201) {
      alert("Usuário cadastrado com sucesso!");
      loginFunction();
    } else {
      alert(data.error || "Erro ao cadastrar usuário.");
    }
  } catch (error) {
    console.error("Erro na requisição:", error);
    alert("Não foi possível conectar ao servidor.");
  }
}

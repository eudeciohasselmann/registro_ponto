document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("reset-password-form");
  const inputFields = document.querySelectorAll(".input-field");

  // Configurar labels para todos os campos
  inputFields.forEach((inputField) => {
    const label = inputField.nextElementSibling;

    // Inicializar estado
    inputField.value = "";
    if (label && label.classList.contains("label")) {
      label.style.top = "50%";
      label.style.fontSize = "16px";
    }

    inputField.addEventListener("input", function () {
      if (label && label.classList.contains("label")) {
        if (this.value) {
          this.classList.add("has-value");
          label.style.top = "0";
          label.style.fontSize = "14px";
        } else {
          this.classList.remove("has-value");
          label.style.top = "50%";
          label.style.fontSize = "16px";
        }
      }
    });
  });

  // Verificar se há token na URL e preencher o campo automaticamente
  const urlParams = new URLSearchParams(window.location.search);
  const urlToken = urlParams.get("token");
  const tokenField = document.getElementById("token");

  if (urlToken && tokenField) {
    tokenField.value = urlToken;
    tokenField.dispatchEvent(new Event("input")); // Trigger label animation
    // Ajustar altura do textarea se necessário
    tokenField.style.height = "auto";
    tokenField.style.height = tokenField.scrollHeight + "px";
  }

  // Adicionar evento para ajustar altura do textarea automaticamente
  if (tokenField && tokenField.tagName === "TEXTAREA") {
    tokenField.addEventListener("input", function () {
      this.style.height = "auto";
      this.style.height = this.scrollHeight + "px";
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const tokenInput = document.getElementById("token").value.trim();
    const newPassword = document.getElementById("new-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    // Validações
    if (!tokenInput) {
      alert("Por favor, digite o código de redefinição.");
      return;
    }

    if (!newPassword) {
      alert("Por favor, digite a nova senha.");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("As senhas não coincidem.");
      return;
    }

    if (newPassword.length < 6) {
      alert("A senha deve ter pelo menos 6 caracteres.");
      return;
    }

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: tokenInput, new_password: newPassword }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(
          "Senha redefinida com sucesso! Você será redirecionado para a página de login."
        );
        // Redireciona para a página de login após o sucesso
        window.location.href = "index.html";
      } else {
        alert(data.error || "Ocorreu um erro ao redefinir a senha.");
      }
    } catch (error) {
      console.error("Erro na requisição:", error);
      alert(
        "Não foi possível conectar ao servidor. Verifique se o servidor está rodando."
      );
    }
  });
});

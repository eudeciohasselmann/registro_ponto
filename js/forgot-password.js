document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("forgot-password-form");
  const inputField = document.querySelector(".input-field");
  const label = inputField.nextElementSibling;

  // Configurar labels
  inputField.value = "";
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

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();

    if (!email) {
      alert("Por favor, digite seu e-mail.");
      return;
    }

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(
          "Se um usuário com este e-mail existir, um link de recuperação será enviado."
        );
        window.location.href = "index.html";
      } else {
        alert(data.error || "Ocorreu um erro ao processar sua solicitação.");
      }
    } catch (error) {
      console.error("Erro na requisição:", error);
      alert("Não foi possível conectar ao servidor.");
    }
  });
});

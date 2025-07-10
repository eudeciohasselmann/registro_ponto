// Configuração da API
const API_CONFIG = {
  // URL base da API - será diferente em desenvolvimento e produção
  BASE_URL:
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
      ? "http://127.0.0.1:5000" // Desenvolvimento
      : "https://registro-ponto-api.onrender.com", // Produção

  // Endpoints da API
  ENDPOINTS: {
    LOGIN: "/login",
    USERS: "/users",
    RECORDS: "/records",
    FORGOT_PASSWORD: "/forgot-password",
    RESET_PASSWORD: "/reset-password",
  },
};

// Função helper para construir URLs completas
function getApiUrl(endpoint) {
  return API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS[endpoint];
}

// Função helper para fazer requisições à API
async function apiRequest(endpoint, options = {}) {
  const url =
    typeof endpoint === "string" && endpoint.startsWith("http")
      ? endpoint
      : getApiUrl(endpoint);

  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, finalOptions);
    return response;
  } catch (error) {
    console.error("Erro na requisição:", error);
    throw error;
  }
}

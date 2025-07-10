const API_URL = "http://127.0.0.1:5000";

// Variável para armazenar o mês atual do filtro
let currentFilterMonth = "";

const usuario = sessionStorage.getItem("usuarioAtual");
if (!usuario) {
  window.location.href = "index.html";
} else {
  document.getElementById("nomeUsuario").textContent = usuario;
}

// Função de logout
function logout() {
  sessionStorage.removeItem("usuarioAtual");
  window.location.href = "index.html";
}

// Função para buscar registros da API
async function fetchRecords() {
  if (!currentFilterMonth) return [];
  try {
    const response = await fetch(
      `${API_URL}/records/${usuario}?month=${currentFilterMonth}`
    );
    if (!response.ok) {
      throw new Error("Falha ao buscar registros");
    }
    return await response.json();
  } catch (error) {
    console.error("Erro:", error);
    alert("Não foi possível carregar os registros do servidor.");
    return [];
  }
}

// Função para calcular diferença entre horários
function calculateTimeDifference(start, end) {
  const startTime = new Date(`2000-01-01 ${start}`);
  const endTime = new Date(`2000-01-01 ${end}`);
  const diff = endTime - startTime;

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  return `${hours.toString().padStart(2, "0")}:${minutes
    .toString()
    .padStart(2, "0")}`;
}

// Função para calcular total parcial
function updatePartialTotal() {
  let totalMinutes = 0;
  document.querySelectorAll(".form-grid").forEach((row, index) => {
    const entryTimeInput = row.querySelector(`.entry-time-${index}`);
    const exitTimeInput = row.querySelector(`.exit-time-${index}`);
    const entryTime = entryTimeInput ? entryTimeInput.value : "";
    const exitTime = exitTimeInput ? exitTimeInput.value : "";
    if (entryTime && exitTime) {
      const [h, m] = calculateTimeDifference(entryTime, exitTime)
        .split(":")
        .map(Number);
      totalMinutes += h * 60 + m;
    }
  });

  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  const totalStr = `${hours.toString().padStart(2, "0")}:${minutes
    .toString()
    .padStart(2, "0")}`;

  const partialTotalElement = document.getElementById("partial-total");
  if (partialTotalElement) {
    partialTotalElement.textContent = totalMinutes > 0 ? totalStr : "--:--";
  }
}

function horasParaMinutos(horasStr) {
  if (!horasStr || !horasStr.includes(":")) return 0;
  const [h, m] = horasStr.split(":").map(Number);
  return h * 60 + (m || 0);
}

// Função para salvar registro na API
async function saveTimeEntry() {
  const formGrids = document.querySelectorAll(".form-grid");
  if (formGrids.length === 0) {
    alert("Nenhum registro para salvar.");
    return;
  }

  // Busca as horas diárias do usuário pela API
  let standardMinutes = horasParaMinutos("08:00"); // Padrão
  try {
    const response = await fetch(`${API_URL}/users/${usuario}`);
    if (response.ok) {
      const data = await response.json();
      standardMinutes = horasParaMinutos(data.horas);
    }
  } catch (e) {
    console.error("Erro ao buscar horas do usuário, usando padrão 8h.");
  }

  const registrosPorData = {};
  formGrids.forEach((row, idx) => {
    const date = row.querySelector(`.date-${idx}`)?.value;
    const entryTime = row.querySelector(`.entry-time-${idx}`)?.value;
    const exitTime = row.querySelector(`.exit-time-${idx}`)?.value;

    if (!date || !entryTime || !exitTime) return;

    if (!registrosPorData[date]) {
      registrosPorData[date] = [];
    }
    registrosPorData[date].push({ start: entryTime, end: exitTime });
  });

  if (Object.keys(registrosPorData).length === 0) {
    alert("Preencha ao menos uma linha completa para salvar.");
    return;
  }

  // Envia cada data como uma requisição separada
  for (const date in registrosPorData) {
    const periods = registrosPorData[date];
    let totalMinutes = 0;
    periods.forEach((p) => {
      const [h, m] = calculateTimeDifference(p.start, p.end).split(":").map(Number);
      totalMinutes += h * 60 + m;
    });

    const totalStr = `${Math.floor(totalMinutes / 60).toString().padStart(2, "0")}:${(totalMinutes % 60).toString().padStart(2, "0")}`;
    const diffMinutes = totalMinutes - standardMinutes;

    let credit = "00:00", debit = "00:00";
    if (diffMinutes > 0) {
      credit = `${Math.floor(diffMinutes / 60).toString().padStart(2, "0")}:${(diffMinutes % 60).toString().padStart(2, "0")}`;
    } else if (diffMinutes < 0) {
      debit = `${Math.floor(Math.abs(diffMinutes) / 60).toString().padStart(2, "0")}:${(Math.abs(diffMinutes) % 60).toString().padStart(2, "0")}`;
    }

    const payload = {
      user: usuario,
      date: date,
      periods: periods,
      total: totalStr,
      credit: credit,
      debit: debit,
    };

    try {
      const response = await fetch(`${API_URL}/records`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "Erro ao salvar registro");
      }
    } catch (error) {
      console.error("Erro:", error);
      alert(`Não foi possível salvar o registro para a data ${date}.`);
      return; // Interrompe se um salvar falhar
    }
  }

  // Limpa o formulário e atualiza a interface
  clearForm();
  await refreshData();
  alert("Registros salvos com sucesso!");
}

function clearForm() {
    const container = document.querySelector(".form-content");
    container.querySelectorAll(".form-grid:not(:first-child)").forEach((row) => row.remove());
    const firstRow = container.querySelector(".form-grid");
    if (firstRow) {
        firstRow.querySelector(".date-0").value = "";
        firstRow.querySelector(".entry-time-0").value = "";
        firstRow.querySelector(".exit-time-0").value = "";
    }
    updatePartialTotal();
}

// Função para renderizar registros na tabela
async function renderRecords() {
  const tbody = document.getElementById("records-tbody");
  tbody.innerHTML = "";
  const records = await fetchRecords();

  if (records.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #64748b;">Nenhum registro para o período.</td></tr>`;
    return;
  }

  const groupedByDate = records.reduce((acc, record) => {
    acc[record.date] = acc[record.date] || { periods: [], total: "00:00", credit: "00:00", debit: "00:00" };
    acc[record.date].periods.push(...record.periods);
    // Os totais já vêm do backend, então apenas os usamos.
    acc[record.date].total = record.total;
    acc[record.date].credit = record.credit;
    acc[record.date].debit = record.debit;
    return acc;
  }, {});

  Object.entries(groupedByDate).forEach(([date, data]) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="date-cell">${date}</td>
      <td>
        <div class="time-periods">
          ${data.periods.map((p) => `<span class="time-period">${p.start} - ${p.end}</span>`).join("")}
        </div>
      </td>
      <td class="center"><span class="badge total">${data.total}</span></td>
      <td class="center"><span class="badge credit">${data.credit}</span></td>
      <td class="center"><span class="badge debit">${data.debit}</span></td>
      <td class="center">
        <div class="actions">
          <button class="action-btn edit" onclick="editRecord('${date}')" title="Editar">✏️</button>
          <button class="action-btn delete" onclick="deleteRecord('${date}')" title="Remover">🗑️</button>
        </div>
      </td>
    `;
    tbody.appendChild(row);
  });
}

// Função para atualizar resumo
async function updateSummary() {
  const records = await fetchRecords();
  let totalMinutes = 0, creditMinutes = 0, debitMinutes = 0;

  records.forEach((r) => {
    totalMinutes += horasParaMinutos(r.total);
    creditMinutes += horasParaMinutos(r.credit);
    debitMinutes += horasParaMinutos(r.debit);
  });

  const formatTime = (min) => `${Math.floor(min / 60).toString().padStart(2, "0")}:${(min % 60).toString().padStart(2, "0")}`;

  document.getElementById("total-general").textContent = formatTime(totalMinutes);
  document.getElementById("total-credit").textContent = formatTime(creditMinutes);
  document.getElementById("total-debit").textContent = formatTime(debitMinutes);

  const saldoMinutes = creditMinutes - debitMinutes;
  const saldoText = `${saldoMinutes < 0 ? "-" : ""}${formatTime(Math.abs(saldoMinutes))}`;
  const saldoElement = document.getElementById("total-saldo");
  const saldoContainer = document.querySelector(".summary-stat.saldo");
  saldoElement.textContent = saldoText;

  saldoContainer.classList.remove("positivo", "negativo");
  if (saldoMinutes > 0) saldoContainer.classList.add("positivo");
  else if (saldoMinutes < 0) saldoContainer.classList.add("negativo");
}

// Função para editar registro
async function editRecord(date) {
    const records = await fetchRecords();
    const periodsToEdit = records.filter(r => r.date === date).flatMap(r => r.periods);

    if (periodsToEdit.length === 0) {
        alert("Nenhum período encontrado para editar.");
        return;
    }

    clearForm();
    const container = document.querySelector(".form-content");

    periodsToEdit.forEach((period, index) => {
        let currentRow;
        if (index === 0) {
            currentRow = container.querySelector(".form-grid");
        } else {
            addTimeEntry(false); // Adiciona nova linha sem validar a anterior
            currentRow = container.querySelector(`.form-grid-${index}`);
        }
        currentRow.querySelector(`.date-${index}`).value = date;
        currentRow.querySelector(`.entry-time-${index}`).value = period.start;
        currentRow.querySelector(`.exit-time-${index}`).value = period.end;
    });

    updatePartialTotal();
    window.scrollTo(0, 0);
}

// Função para deletar registro
async function deleteRecord(date) {
  if (confirm(`Tem certeza que deseja remover todos os registros do dia ${date}?`)) {
    try {
      const response = await fetch(`${API_URL}/records/${date}?user=${usuario}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "Erro ao deletar");
      }
      await refreshData();
    } catch (error) {
      console.error("Erro:", error);
      alert("Não foi possível remover o registro.");
    }
  }
}

// Função para adicionar período de tempo
function addTimeEntry(validate = true) {
  const container = document.querySelector(".form-content");
  const index = container.querySelectorAll(".form-grid").length;

  if (validate) {
      const lastRow = container.querySelector(`.form-grid-${index - 1}`);
      const date = lastRow.querySelector(`.date-${index - 1}`).value;
      const entryTime = lastRow.querySelector(`.entry-time-${index - 1}`).value;
      const exitTime = lastRow.querySelector(`.exit-time-${index - 1}`).value;
      if (!date || !entryTime || !exitTime) {
          alert("Preencha a linha anterior antes de adicionar uma nova.");
          return;
      }
  }
  
  const newRow = document.createElement("div");
  newRow.className = `form-grid form-grid-${index}`;
  const lastDate = container.querySelector(`.date-${index - 1}`)?.value || "";

  newRow.innerHTML = `
    <div class="form-group">
      <label for="date-${index}">Data</label>
      <input type="date" id="date-${index}" class="date date-${index}" value="${lastDate}"/>
    </div>
    <div class="form-group">
      <label for="entry-time-${index}">Entrada</label>
      <input type="time" id="entry-time-${index}" class="entry-time entry-time-${index}" />
    </div>
    <div class="form-group">
      <label for="exit-time-${index}">Saída</label>
      <input type="time" id="exit-time-${index}" class="exit-time exit-time-${index}" />
    </div>
    <div class="time-controls">
      <button class="control-btn add" onclick="addTimeEntry()" title="Adicionar">➕</button>
      <button class="control-btn delete" onclick="removeTimeEntry(event)" title="Remover">🗑️</button>
    </div>
  `;
  container.appendChild(newRow);
  newRow.querySelector(`.exit-time-${index}`).addEventListener("blur", updatePartialTotal);
}

// Função para remover período de tempo
function removeTimeEntry(event) {
  const row = event.target.closest(".form-grid");
  if (row && row.parentElement.children.length > 1 && row !== row.parentElement.firstElementChild) {
    row.remove();
    updatePartialTotal();
  }
}

async function refreshData() {
    await renderRecords();
    await updateSummary();
}

// Event Listeners
document.getElementById("month-filter").addEventListener("change", function () {
  currentFilterMonth = this.value;
  refreshData();
});

window.addEventListener("DOMContentLoaded", function () {
  const monthInput = document.getElementById("month-filter");
  if (monthInput) {
    const now = new Date();
    const month = (now.getMonth() + 1).toString().padStart(2, "0");
    const year = now.getFullYear();
    const formattedMonth = `${year}-${month}`;
    monthInput.value = formattedMonth;
    currentFilterMonth = formattedMonth;
  }
  refreshData();
  updatePartialTotal();
});

function horasParaMinutos(h) {
  if (!h || !h.includes(":")) return 0;
  const [a, b] = h.split(":").map(Number);
  return a * 60 + (b || 0);
}

function minutosParaHoras(m) {
  const s = m < 0 ? "-" : "";
  const v = Math.abs(m);
  return `${s}${String(Math.floor(v / 60)).padStart(2, "0")}:${String(v % 60).padStart(2, "0")}`;
}

function diasUteisNoMes(ano, mes) {
  let count = 0;
  const dias = new Date(ano, mes, 0).getDate();
  for (let d = 1; d <= dias; d++) {
    const dia = new Date(ano, mes - 1, d).getDay();
    if (dia !== 0 && dia !== 6) count++;
  }
  return count;
}

async function dashboardFetchRecords(user, month) {
  try {
    const r = await fetch(`${API_URL}/records/${encodeURIComponent(user)}?month=${encodeURIComponent(month)}`);
    if (!r.ok) return [];
    return await r.json();
  } catch {
    return [];
  }
}

async function fetchUserHours(user) {
  try {
    const r = await fetch(`${API_URL}/users/${encodeURIComponent(user)}`);
    if (!r.ok) return 480;
    const data = await r.json();
    return horasParaMinutos(data.horas);
  } catch {
    return 480;
  }
}

function getDaysWithRecords(records) {
  return new Set(records.map((r) => r.date));
}

function aggregateByDate(records) {
  return records.reduce((acc, r) => {
    if (!acc[r.date]) {
      acc[r.date] = { totalMin: 0, creditMin: 0, debitMin: 0 };
    }
    acc[r.date].totalMin += horasParaMinutos(r.total);
    acc[r.date].creditMin += horasParaMinutos(r.credit);
    acc[r.date].debitMin += horasParaMinutos(r.debit);
    return acc;
  }, {});
}

function renderDashboardCards(stats) {
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setVal("dash-days", stats.daysWorked);
  setVal("dash-days-sub", ` / ${stats.totalDays} dias \u00FAteis`);

  setVal("dash-avg", minutosParaHoras(Math.round(stats.avgDaily)));
  setVal("dash-avg-sub", `meta: ${minutosParaHoras(stats.goalMinutes)}/dia`);

  const proj = stats.avgDaily * stats.totalDays;
  setVal("dash-proj", minutosParaHoras(Math.round(proj)));
  const projDiff = proj - stats.goalMinutes * stats.totalDays;
  const projEl = document.getElementById("dash-proj-sub");
  if (projEl) {
    const cor = projDiff >= 0 ? "var(--success)" : "var(--danger)";
    projEl.innerHTML = `proje${"\u00E7"}ao final: <span style="color:${cor};font-weight:600">${projDiff >= 0 ? "+" : ""}${minutosParaHoras(Math.round(projDiff))}</span>`;
  }

  setVal("dash-saldo", minutosParaHoras(stats.balance));
  const saldoEl = document.getElementById("dash-saldo-sub");
  if (saldoEl) {
    saldoEl.textContent = stats.balance >= 0 ? "horas extras acumuladas" : "horas negativas acumuladas";
  }

  const card = document.getElementById("dash-saldo-card");
  if (card) {
    card.className = "dashboard-card";
    card.classList.add(stats.balance > 0 ? "success" : stats.balance < 0 ? "danger" : "warning");
  }
}

let barChart = null;
let donutChart = null;

function renderBarChart(dailyData) {
  const ctx = document.getElementById("chart-bar");
  if (!ctx || typeof Chart === "undefined") return;

  if (barChart) barChart.destroy();

  const labels = Object.keys(dailyData).sort();
  const values = labels.map((d) => dailyData[d].totalMin / 60);

  try {
    barChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels.map((d) => {
          const parts = d.split("-");
          return `${parseInt(parts[2])}/${parseInt(parts[1])}`;
        }),
        datasets: [{
          label: "Horas trabalhadas",
          data: values,
          backgroundColor: values.map((v) => {
            const avg = values.reduce((a, b) => a + b, 0) / values.length || 1;
            return v >= avg ? "rgba(79, 70, 229, 0.75)" : "rgba(251, 191, 36, 0.65)";
          }),
          borderColor: values.map((v) => {
            const avg = values.reduce((a, b) => a + b, 0) / values.length || 1;
            return v >= avg ? "#4f46e5" : "#f59e0b";
          }),
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.parsed.y.toFixed(2)}h`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { callback: (v) => `${v.toFixed(1)}h`, font: { size: 11 } },
            grid: { color: "rgba(0,0,0,0.04)" },
          },
          x: {
            ticks: { font: { size: 10 } },
            grid: { display: false },
          },
        },
      },
    });
  } catch (e) {
    console.error("Erro ao renderizar gr\u00E1fico de barras:", e);
  }
}

function renderDonutChart(records) {
  const ctx = document.getElementById("chart-donut");
  if (!ctx) return;

  if (donutChart) donutChart.destroy();

  let totalCredit = 0;
  let totalDebit = 0;
  records.forEach((r) => {
    totalCredit += horasParaMinutos(r.credit);
    totalDebit += horasParaMinutos(r.debit);
  });

  if (totalCredit === 0 && totalDebit === 0) totalCredit = 1;

  try {
    donutChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Cr\u00E9dito (extras)", "D\u00E9bito (negativas)"],
        datasets: [{
          data: [totalCredit, totalDebit],
          backgroundColor: ["rgba(16, 185, 129, 0.8)", "rgba(239, 68, 68, 0.8)"],
          borderColor: ["#10b981", "#ef4444"],
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { font: { size: 11 }, padding: 12, usePointStyle: true },
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                return `${ctx.label}: ${minutosParaHoras(ctx.parsed)} (${pct}%)`;
              },
            },
          },
        },
        cutout: "68%",
      },
    });
  } catch (e) {
    console.error("Erro ao renderizar gr\u00E1fico de rosca:", e);
  }
}

function getDashboardMonth() {
  const monthInput = document.getElementById("month-filter");
  if (monthInput && monthInput.value) return monthInput.value;
  if (window.currentFilterMonth) return window.currentFilterMonth;
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

async function refreshDashboard() {
  const usuario = sessionStorage.getItem("usuarioAtual");
  if (!usuario) return;

  const month = getDashboardMonth();
  const monthInput = document.getElementById("month-filter");
  if (monthInput && !monthInput.value) monthInput.value = month;
  if (!month || !month.includes("-")) return;

  const [year, mes] = month.split("-").map(Number);

  const [records, goalMinutes] = await Promise.all([
    dashboardFetchRecords(usuario, month),
    fetchUserHours(usuario),
  ]);

  const byDate = aggregateByDate(records);
  const daysWorked = getDaysWithRecords(records).size;
  const totalDays = diasUteisNoMes(year, mes);

  const totalMinutes = Object.values(byDate).reduce((s, d) => s + d.totalMin, 0);
  const totalCredit = Object.values(byDate).reduce((s, d) => s + d.creditMin, 0);
  const totalDebit = Object.values(byDate).reduce((s, d) => s + d.debitMin, 0);
  const avgDaily = daysWorked > 0 ? totalMinutes / daysWorked : 0;
  const balance = totalCredit - totalDebit;

  renderDashboardCards({ daysWorked, totalDays, avgDaily, goalMinutes, totalMinutes, balance });
  renderBarChart(byDate);
  renderDonutChart(records);
}

(function patchRefreshData() {
  const orig = window.refreshData;
  if (orig && !window._dashPatched) {
    window.refreshData = async function () {
      await orig();
      await refreshDashboard();
    };
    window._dashPatched = true;
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  const monthInput = document.getElementById("month-filter");
  if (monthInput) {
    monthInput.addEventListener("change", refreshDashboard);
  }
  setTimeout(refreshDashboard, 100);
});
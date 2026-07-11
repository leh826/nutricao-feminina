const CSV_PATH = "data/gold_recomendacoes.csv";

const phaseSelect = document.querySelector("#phaseSelect");
const selectedPhase = document.querySelector("#selectedPhase");
const selectedNutrient = document.querySelector("#selectedNutrient");
const phaseDescription = document.querySelector("#phaseDescription");
const topFood = document.querySelector("#topFood");
const cards = document.querySelector("#cards");
const bars = document.querySelector("#bars");
const tableBody = document.querySelector("#tableBody");

let records = [];

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines.shift().split(",");

  return lines.map((line) => {
    const values = line.split(",");
    return headers.reduce((row, header, index) => {
      row[header] = values[index];
      return row;
    }, {});
  });
}

function formatFood(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNutrient(value) {
  return String(value || "")
    .replace("_mg", "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatNumber(value) {
  return Number(value).toLocaleString("pt-BR", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  });
}

function renderPhase(phase) {
  const phaseRecords = records
    .filter((row) => row.fase_ciclo === phase)
    .sort((a, b) => Number(a.ranking) - Number(b.ranking));

  const first = phaseRecords[0];
  const maxValue = Math.max(...phaseRecords.map((row) => Number(row.valor_nutriente)));

  selectedPhase.textContent = first.fase_ciclo;
  selectedNutrient.textContent = formatNutrient(first.nutriente_prioritario);
  phaseDescription.textContent = first.descricao;
  topFood.textContent = formatFood(first.alimento);

  cards.innerHTML = phaseRecords
    .map(
      (row) => `
        <article class="recommendation-card">
          <div class="rank">${row.ranking}</div>
          <div class="food-name">${formatFood(row.alimento)}</div>
          <div class="nutrient">${row.nutriente_prioritario}: ${formatNumber(row.valor_nutriente)} mg</div>
          <p>${row.descricao}</p>
        </article>
      `
    )
    .join("");

  bars.innerHTML = phaseRecords
    .map((row) => {
      const width = maxValue === 0 ? 0 : (Number(row.valor_nutriente) / maxValue) * 100;
      return `
        <div class="bar-row">
          <strong>${formatFood(row.alimento)}</strong>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${width}%"></div>
          </div>
          <span class="bar-value">${formatNumber(row.valor_nutriente)} mg</span>
        </div>
      `;
    })
    .join("");

  tableBody.innerHTML = phaseRecords
    .map(
      (row) => `
        <tr>
          <td>${row.ranking}</td>
          <td>${formatFood(row.alimento)}</td>
          <td>${formatNutrient(row.nutriente_prioritario)}</td>
          <td>${formatNumber(row.valor_nutriente)}</td>
        </tr>
      `
    )
    .join("");
}

async function init() {
  const response = await fetch(CSV_PATH);

  if (!response.ok) {
    throw new Error("CSV nao encontrado.");
  }

  records = parseCsv(await response.text());

  const phases = [...new Set(records.map((row) => row.fase_ciclo))].sort();
  phaseSelect.innerHTML = phases
    .map((phase) => `<option value="${phase}">${phase}</option>`)
    .join("");

  phaseSelect.addEventListener("change", (event) => {
    renderPhase(event.target.value);
  });

  renderPhase(phases[0]);
}

init().catch((error) => {
  document.body.innerHTML = `<main class="page-shell"><section class="hero"><h1>Nutricao Feminina</h1><p class="hero-copy">${error.message}</p></section></main>`;
});

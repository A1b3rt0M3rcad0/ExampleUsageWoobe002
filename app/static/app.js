const api = async (path, options = {}) => {
  const response = await fetch(path, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || body.message || `HTTP ${response.status}`);
  return body;
};

const list = document.querySelector("#assessmentList");
const detail = document.querySelector("#detail");
const dialog = document.querySelector("#createDialog");

document.querySelector("#newAssessment").onclick = () => dialog.showModal();
document.querySelector("#closeDialog").onclick = () => dialog.close();

document.querySelector("#createForm").onsubmit = async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    vendor_name: form.get("vendor_name"),
    category: form.get("category"),
    criticality: form.get("criticality"),
    region: form.get("region"),
    data_handled: String(form.get("data_handled") || "").split(",").map(x => x.trim()).filter(Boolean),
    requirements: form.getAll("requirements"),
  };
  const created = await api("/api/assessments", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  dialog.close();
  event.currentTarget.reset();
  await load();
  await openAssessment(created.id);
};

async function load() {
  const data = await api("/api/assessments");
  const items = data.items;
  document.querySelector("#statTotal").textContent = items.length;
  document.querySelector("#statCompleted").textContent = items.filter(x => x.status === "COMPLETED").length;
  document.querySelector("#statReview").textContent = items.filter(x => ["DRAFT", "ANALYZING"].includes(x.status)).length;

  list.innerHTML = items.length ? items.map(item => `
    <div class="row">
      <button onclick="openAssessment('${item.id}')">
        <div class="vendor">${escapeHtml(item.vendor_name)}</div>
        <div class="meta">${escapeHtml(item.id)}</div>
      </button>
      <div>${escapeHtml(item.category)}</div>
      <div>${escapeHtml(item.criticality)}</div>
      <div><span class="badge ${item.status}">${escapeHtml(item.status)}</span></div>
    </div>
  `).join("") : `<div class="muted">No assessments yet.</div>`;
}

window.openAssessment = async (id) => {
  const item = await api(`/api/assessments/${id}`);
  const result = item.result || {};
  const domainScores = result.domain_scores || {};
  const findings = result.findings || [];

  detail.classList.remove("hidden");
  detail.innerHTML = `
    <div class="detail-head">
      <div>
        <p class="eyebrow">${escapeHtml(item.id)}</p>
        <h2>${escapeHtml(item.vendor_name)}</h2>
        <div class="meta">${escapeHtml(item.category)} · ${escapeHtml(item.region)} · ${escapeHtml(item.criticality)}</div>
      </div>
      <span class="badge ${item.status}">${escapeHtml(item.status)}</span>
    </div>

    <div class="upload">
      <input id="uploadFile" type="file" accept=".pdf,.txt,.md">
      <button class="primary" onclick="uploadDocument('${item.id}')">Upload evidence</button>
    </div>
    <div class="meta">${item.documents.length} document(s) stored by Atlas — not in Woobe Knowledge.</div>

    ${item.status === "COMPLETED" ? `
      <div style="margin-top:22px">
        <p class="eyebrow">Final risk</p>
        <div class="score">${escapeHtml(String(result.overall_risk_score ?? "—"))}<span class="muted"> / 100</span></div>
        <strong>${escapeHtml(result.recommendation || "")}</strong>
      </div>
      <div class="result-grid">
        ${Object.entries(domainScores).map(([key, value]) => `<div class="result-card"><span class="muted">${escapeHtml(key)}</span><div class="vendor">${escapeHtml(String(value))}/100</div></div>`).join("")}
      </div>
      <h2>Findings</h2>
      <div>${findings.map(finding => `
        <div class="finding">
          <span class="badge">${escapeHtml(finding.severity || "")}</span>
          <div class="vendor" style="margin-top:7px">${escapeHtml(finding.title || "")}</div>
          <div class="meta">${escapeHtml(finding.summary || "")}</div>
        </div>`).join("") || `<div class="muted">No findings.</div>`}
      </div>
    ` : `
      <div style="margin-top:20px">
        <button id="analyzeButton" class="primary" onclick="analyzeAssessment('${item.id}')">Run assessment with Woobe</button>
      </div>
    `}
  `;
};

window.uploadDocument = async (id) => {
  const input = document.querySelector("#uploadFile");
  if (!input.files?.[0]) return;
  const data = new FormData();
  data.append("file", input.files[0]);
  try {
    await api(`/api/assessments/${id}/documents`, {method: "POST", body: data});
    await openAssessment(id);
  } catch (error) {
    alert(error.message);
  }
};

window.analyzeAssessment = async (id) => {
  const button = document.querySelector("#analyzeButton");
  button.disabled = true;
  button.textContent = "Analyzing…";
  try {
    await api(`/api/assessments/${id}/analyze`, {
      method: "POST",
      headers: {"Idempotency-Key": `atlas:${id}:${crypto.randomUUID()}`},
    });
    await load();
    await openAssessment(id);
  } catch (error) {
    alert(error.message);
    await openAssessment(id);
  }
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

load().catch(error => {
  list.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
});

const API_BASE_URL = "http://127.0.0.1:8000";

const resultEl = document.getElementById("result");
const runButton = document.getElementById("run-analysis");

runButton.addEventListener("click", runPrediction);

async function runPrediction() {
    const payload = {
        sport: document.getElementById("sport").value,
        home_team: document.getElementById("home").value.trim(),
        away_team: document.getElementById("away").value.trim(),
        odds: Number(document.getElementById("odds").value)
    };

    resultEl.innerHTML = `<p class="muted">Running deterministic model...</p>`;
    runButton.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Prediction request failed.");
        }

        renderPrediction(data);
    } catch (error) {
        resultEl.innerHTML = `
            <h3 class="bad">Prediction unavailable</h3>
            <p>${escapeHtml(error.message)}</p>
            <p class="muted">Start the FastAPI backend at ${API_BASE_URL} and try again.</p>
        `;
    } finally {
        runButton.disabled = false;
    }
}

function renderPrediction(data) {
    const betClass = data.recommendation === "BET" ? "good" : "bad";
    const riskClass = data.risk === "LOW" ? "good" : data.risk === "MEDIUM" ? "warn" : "bad";
    const trace = data.trace || {};
    const agents = trace.agents || {};

    resultEl.innerHTML = `
        <div class="result-header">
            <div>
                <h3>${escapeHtml(data.match)}</h3>
                <p class="muted">${escapeHtml(trace.sport || "")} / decimal odds ${escapeHtml(String(trace.odds || ""))}</p>
            </div>
            <div class="recommendation ${betClass}">${escapeHtml(data.recommendation)}</div>
        </div>

        <div class="metrics">
            <div>
                <span>Home Win</span>
                <strong>${formatPercent(data.home_win_probability)}</strong>
            </div>
            <div>
                <span>Draw</span>
                <strong>${formatPercent(data.draw_probability)}</strong>
            </div>
            <div>
                <span>Away Win</span>
                <strong>${formatPercent(data.away_win_probability)}</strong>
            </div>
            <div>
                <span>Predicted Score</span>
                <strong>${escapeHtml(data.predicted_score)}</strong>
            </div>
            <div>
                <span>EV</span>
                <strong class="${data.ev > 0 ? "good" : "bad"}">${formatNumber(data.ev)}</strong>
            </div>
            <div>
                <span>Risk</span>
                <strong class="${riskClass}">${escapeHtml(data.risk)}</strong>
            </div>
            <div>
                <span>Confidence</span>
                <strong>${escapeHtml(data.confidence)}</strong>
            </div>
        </div>

        <h4>Agent Trace</h4>
        <div class="trace-grid">
            ${renderAgent("Data Analyst", agents.data_analyst)}
            ${renderAgent("Tactical Analyst", agents.tactical_analyst)}
            ${renderAgent("Statistical Model", agents.statistical_model)}
            ${renderAgent("Sentiment Analyst", agents.sentiment_analyst)}
            ${renderAgent("Risk Manager", agents.risk_manager)}
            ${renderAgent("Decision Engine", agents.decision_engine)}
        </div>
    `;
}

function renderAgent(name, details) {
    if (!details) {
        return "";
    }

    return `
        <article class="trace-item">
            <h5>${escapeHtml(name)}</h5>
            <pre>${escapeHtml(JSON.stringify(details, null, 2))}</pre>
        </article>
    `;
}

function formatPercent(value) {
    return `${(Number(value) * 100).toFixed(2)}%`;
}

function formatNumber(value) {
    return Number(value).toFixed(4);
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

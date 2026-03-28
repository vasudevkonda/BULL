# 📦 Bullwhip Effect Supply Chain Intelligence

An AI-powered supply chain analytics dashboard that simulates, diagnoses,
and prescribes solutions for the **bullwhip effect** — using **LangGraph**
for multi-agent orchestration, **Groq** for ultra-fast LLM inference, and
**Streamlit** for the interactive UI.

---

## Architecture

```
Streamlit UI
     │
     ▼
LangGraph StateGraph
  ├─ demand_analyzer  →  bullwhip ratios, tier orders, demand stats
  ├─ forecast_agent   →  Holt smoothing, optimal α, MAPE
  ├─ inventory_agent  →  safety stock, reorder points, stockout risk
  ├─ risk_agent       →  composite risk score 0-100, disruption alerts
  └─ llm_synthesis    →  Groq llama-3.3-70b narrative + recommendations
```

All agents share a single `SupplyChainState` TypedDict — each enriches it,
and the final LLM node synthesises everything into actionable insights.

---

## Quick start

### 1. Clone and install
```bash
git clone https://github.com/YOUR_USERNAME/bullwhip-ai.git
cd bullwhip-ai
pip install -r requirements.txt
```

### 2. Add your Groq API key
```bash
cp .env.example .env
# edit .env and add your GROQ_API_KEY
# get a free key at https://console.groq.com
```

### 3. Run locally
```bash
streamlit run app.py
```

---

## Deploy to Vercel

### Option A — Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

Then add your secret:
```bash
vercel env add GROQ_API_KEY production
```

### Option B — GitHub integration
1. Push to GitHub
2. Import project at vercel.com
3. Add `GROQ_API_KEY` in **Settings → Environment Variables**
4. Deploy

> **Note**: Vercel's Python runtime works well for Streamlit.
> For heavy production loads consider Railway or Fly.io instead.

---

## Features

| Feature | Detail |
|---|---|
| **5 demand scenarios** | Baseline, holiday surge, demand shock, growth, erratic |
| **Bullwhip simulation** | Order-up-to policy across 4 tiers |
| **LangGraph pipeline** | Parallel-ready multi-agent StateGraph |
| **Groq LLM** | llama-3.3-70b-versatile, ~500ms inference |
| **Safety stock** | z-score formula with service-level targets |
| **Risk scoring** | 4-driver composite 0–100 gauge |
| **Plotly charts** | Orders, ratios, inventory, risk donut |
| **Dark UI** | Streamlit custom theme |

---

## Configuration (sidebar)

- **Groq API key** — paste here or set in `.env`
- **Scenario** — pre-built demand patterns
- **Periods** — 12–48 months of simulation
- **Lead times** — 1–14 periods per tier
- **Order smoothing α** — Holt's method parameter per tier

---

## Agents

### `demand_analyzer`
Simulates orders tier-by-tier using exponential-smoothing order-up-to policy.
Computes `Var(orders) / Var(demand)` (the bullwhip ratio) for each tier.

### `forecast_agent`
Runs Holt's double exponential smoothing, grid-searches optimal α,
and reports MAPE per tier.

### `inventory_agent`
Calculates safety stock (`z × σ × √L`), reorder points, and per-tier
stockout risk (fraction of periods with inventory < demand).

### `risk_agent`
Aggregates signals into a 100-point composite score with four drivers
and generates human-readable disruption alerts.

### `llm_synthesis`
Sends a structured prompt to Groq's API and parses the response into
a narrative diagnosis plus prioritised recommendations.

---

## Project structure

```
bullwhip-ai/
├── app.py                 # Streamlit entry point
├── pipeline.py            # LangGraph graph builder
├── state.py               # SupplyChainState TypedDict
├── agents/
│   ├── demand_analyzer.py
│   ├── forecast_agent.py
│   ├── inventory_agent.py
│   ├── risk_agent.py
│   └── llm_synthesis.py
├── utils/
│   ├── scenarios.py       # Pre-built demand generators
│   └── charts.py          # Plotly chart helpers
├── .streamlit/
│   └── config.toml        # Dark theme config
├── requirements.txt
├── vercel.json
└── .env.example
```

---

## License
MIT

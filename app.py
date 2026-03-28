"""
Bullwhip Effect Supply Chain Intelligence
Streamlit dashboard powered by LangGraph + Groq LLM
"""

import streamlit as st
import sys
import os

# ── path setup so relative imports work on Vercel ──────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from pipeline import run_analysis
from utils.scenarios import SCENARIOS
from utils.charts import (
    orders_chart,
    bullwhip_ratio_chart,
    inventory_chart,
    risk_gauge,
)

# ── page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bullwhip Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #0f172a; }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stSlider label { color: #94a3b8 !important; font-size: 12px; }
  .metric-card {
    background: #1e293b;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    border-left: 3px solid #6366f1;
    margin-bottom: 0.5rem;
  }
  .metric-card .label { color: #94a3b8; font-size: 12px; margin-bottom: 4px; }
  .metric-card .value { color: #f1f5f9; font-size: 22px; font-weight: 600; }
  .alert-box {
    background: #1e293b;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 13px;
    color: #e2e8f0;
  }
  .insights-box {
    background: #1e293b;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
  }
  h1 { font-size: 1.6rem !important; }
  h2 { font-size: 1.15rem !important; color: #94a3b8 !important; font-weight: 400 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR — configuration
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📦 Bullwhip Intelligence")
    st.markdown("---")

    # Groq API key input
    groq_key = st.text_input(
        "Groq API key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        placeholder="gsk_...",
    )
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key

    st.markdown("---")
    st.markdown("**Demand scenario**")
    scenario_name = st.selectbox("Scenario", list(SCENARIOS.keys()))

    st.markdown("**Supply chain config**")
    n_periods = st.slider("Periods (months)", 12, 48, 24, step=6)

    st.markdown("*Lead times (periods)*")
    lt_retail = st.slider("Retailer", 1, 6, 1)
    lt_wholesale = st.slider("Wholesaler", 1, 8, 2)
    lt_dist = st.slider("Distributor", 1, 10, 3)
    lt_mfg = st.slider("Manufacturer", 2, 14, 5)

    st.markdown("*Order smoothing (α)*")
    alpha_retail = st.slider("Retailer α", 0.05, 0.95, 0.30, step=0.05)
    alpha_wholesale = st.slider("Wholesaler α", 0.05, 0.95, 0.25, step=0.05)
    alpha_dist = st.slider("Distributor α", 0.05, 0.95, 0.20, step=0.05)
    alpha_mfg = st.slider("Manufacturer α", 0.05, 0.95, 0.15, step=0.05)

    st.markdown("---")
    run_btn = st.button("▶  Run analysis", use_container_width=True, type="primary")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN — header
# ═══════════════════════════════════════════════════════════════════════════
st.title("📦 Bullwhip Effect Supply Chain Intelligence")
st.markdown("## Powered by LangGraph · Groq · llama-3.3-70b")

if not run_btn:
    st.info("Configure parameters in the sidebar and click **▶ Run analysis** to start.", icon="👈")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# RUN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════
tiers = ["retailer", "wholesaler", "distributor", "manufacturer"]
lead_times = {
    "retailer": lt_retail,
    "wholesaler": lt_wholesale,
    "distributor": lt_dist,
    "manufacturer": lt_mfg,
}
alphas = {
    "retailer": alpha_retail,
    "wholesaler": alpha_wholesale,
    "distributor": alpha_dist,
    "manufacturer": alpha_mfg,
}

chain_config = {
    "tiers": tiers,
    "lead_times": lead_times,
    "alphas": alphas,
    "safety_factors": {t: 1.5 for t in tiers},
}

consumer_demand = SCENARIOS[scenario_name](n=n_periods)

with st.spinner("Running LangGraph pipeline → Groq analysis..."):
    result = run_analysis(consumer_demand, chain_config, scenario_label=scenario_name)


# ═══════════════════════════════════════════════════════════════════════════
# TOP METRICS ROW
# ═══════════════════════════════════════════════════════════════════════════
ratios = result.get("bullwhip_ratios", {})
risk_score = result.get("risk_score", 0)
alerts = result.get("disruption_alerts", [])
stockout = result.get("stockout_risk", {})

max_ratio = max(ratios.values(), default=1.0)
avg_stockout = sum(stockout.values()) / len(stockout) if stockout else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Max bullwhip ratio</div>
        <div class="value">{max_ratio:.2f}x</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Risk score</div>
        <div class="value">{risk_score:.0f} / 100</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Avg stockout risk</div>
        <div class="value">{avg_stockout:.1f}%</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Active alerts</div>
        <div class="value">{len(alerts)}</div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# CHARTS — row 1
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
col_left, col_right = st.columns([3, 2])
with col_left:
    st.plotly_chart(
        orders_chart(consumer_demand, result.get("tier_orders", {})),
        use_container_width=True,
    )
with col_right:
    st.plotly_chart(
        bullwhip_ratio_chart(ratios),
        use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# CHARTS — row 2
# ═══════════════════════════════════════════════════════════════════════════
col_inv, col_risk = st.columns([3, 2])
with col_inv:
    st.plotly_chart(
        inventory_chart(
            result.get("inventory_levels", {}),
            result.get("reorder_points", {}),
        ),
        use_container_width=True,
    )
with col_risk:
    st.plotly_chart(
        risk_gauge(risk_score, result.get("risk_breakdown", {})),
        use_container_width=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# ALERTS + LLM INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
col_alerts, col_insights = st.columns([1, 2])

with col_alerts:
    st.markdown("### 🔔 Alerts")
    for alert in alerts:
        st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)

    st.markdown("### 📊 Forecast accuracy (MAPE)")
    for tier, mape in result.get("forecast_accuracy", {}).items():
        if tier != "consumer":
            bar_width = min(100, mape)
            color = "#ef4444" if mape > 30 else "#f59e0b" if mape > 15 else "#10b981"
            st.markdown(
                f"**{tier.capitalize()}**: {mape:.1f}%  "
                f"<span style='display:inline-block;width:{bar_width}px;height:8px;"
                f"background:{color};border-radius:4px;vertical-align:middle'></span>",
                unsafe_allow_html=True,
            )

with col_insights:
    st.markdown("### 🤖 Groq LLM analysis")
    insights = result.get("llm_insights", "No insights generated.")
    st.markdown(f'<div class="insights-box">{insights}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# DEBUG EXPANDER
# ═══════════════════════════════════════════════════════════════════════════
with st.expander("🔧 Pipeline debug log"):
    for msg in result.get("messages", []):
        st.text(msg)
    st.json({
        "safety_stock": result.get("safety_stock", {}),
        "reorder_points": result.get("reorder_points", {}),
        "recommended_smoothing": result.get("recommended_smoothing", {}),
        "policy_changes": result.get("policy_changes", {}),
    })

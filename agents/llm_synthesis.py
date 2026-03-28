"""
LLM Synthesis Node (Groq)
Calls llama-3.3-70b via Groq for ultra-fast narrative analysis and
actionable supply chain recommendations based on all agent outputs.
"""

import os
from groq import Groq
from state import SupplyChainState


def build_analysis_prompt(state: SupplyChainState) -> str:
    ratios = state.get("bullwhip_ratios", {})
    risk_score = state.get("risk_score", 0)
    risk_breakdown = state.get("risk_breakdown", {})
    stockout = state.get("stockout_risk", {})
    safety_stock = state.get("safety_stock", {})
    reorder_points = state.get("reorder_points", {})
    smoothing = state.get("recommended_smoothing", {})
    alerts = state.get("disruption_alerts", [])
    scenario = state.get("scenario_label", "baseline")
    demand_signal = state.get("demand_signal", {})

    ratio_lines = "\n".join(
        f"  - {tier}: {v:.2f}x amplification" for tier, v in ratios.items()
    )
    stockout_lines = "\n".join(
        f"  - {tier}: {v:.1f}% stockout risk" for tier, v in stockout.items()
    )
    alert_lines = "\n".join(f"  {a}" for a in alerts)

    return f"""You are a world-class supply chain analyst specialising in the bullwhip effect.

SCENARIO: {scenario}

DEMAND SIGNAL:
  - Mean: {demand_signal.get('mean', 'N/A')}, Std: {demand_signal.get('std', 'N/A')}
  - Coefficient of variation: {demand_signal.get('cv', 'N/A')}
  - Trend: {demand_signal.get('trend', 'N/A')} units/period

BULLWHIP RATIOS (Var(orders)/Var(demand)):
{ratio_lines}

STOCKOUT RISK:
{stockout_lines}

COMPOSITE RISK SCORE: {risk_score}/100
  - Amplification driver: {risk_breakdown.get('amplification', 0)}/40
  - Stockout driver: {risk_breakdown.get('stockout', 0)}/30
  - Demand volatility: {risk_breakdown.get('demand_volatility', 0)}/20
  - Lead-time driver: {risk_breakdown.get('lead_time', 0)}/10

CURRENT ALERTS:
{alert_lines}

RECOMMENDED SMOOTHING PARAMETERS:
{smoothing}

Please provide:
1. A concise narrative diagnosis (3-4 sentences) of the bullwhip dynamics observed.
2. The root causes in this specific scenario.
3. Five concrete, prioritised recommendations to reduce bullwhip amplification and stockout risk.
   Format each as: [TIER] Action — Expected impact.
4. Any lead-time or policy changes that would deliver the highest ROI.

Be specific, quantitative where possible, and actionable. Avoid generic supply chain platitudes."""


def llm_synthesis_node(state: SupplyChainState) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "llm_insights": "⚠️  GROQ_API_KEY not set. Add it to your .env file.",
            "recommendations": ["Set GROQ_API_KEY environment variable to enable LLM insights."],
            "policy_changes": {},
            "messages": ["[llm_synthesis] skipped — no API key"],
        }

    client = Groq(api_key=api_key)
    prompt = build_analysis_prompt(state)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        return {
            "llm_insights": f"LLM call failed: {e}",
            "recommendations": [],
            "policy_changes": {},
            "messages": [f"[llm_synthesis] error: {e}"],
        }

    # Parse numbered recommendations out of the response
    lines = raw.split("\n")
    recs = [l.strip() for l in lines if l.strip() and l.strip()[0].isdigit() and "." in l[:3]]

    return {
        "llm_insights": raw,
        "recommendations": recs if recs else [raw],
        "policy_changes": {
            t: {"alpha": v.get("alpha"), "safety_factor": 1.2}
            for t, v in state.get("recommended_smoothing", {}).items()
        },
        "messages": ["[llm_synthesis] Groq response received"],
    }

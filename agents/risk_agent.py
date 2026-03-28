"""
Risk Agent
Aggregates signals from all prior agents into a composite risk score (0–100)
and generates human-readable disruption alerts.
"""

import numpy as np
from state import SupplyChainState


ALERT_THRESHOLDS = {
    "bullwhip_ratio": 2.5,
    "stockout_risk": 20.0,   # percent
    "risk_score": 65.0,
    "cv": 0.35,              # coefficient of variation of demand
}


def score_bullwhip(ratios: dict[str, float]) -> float:
    """Map max bullwhip ratio to a 0-40 sub-score (dominant driver)."""
    max_ratio = max(ratios.values(), default=1.0)
    # ratio 1 = no amplification (0 pts), ratio 5+ = max 40 pts
    return round(min(40.0, (max_ratio - 1) / 4 * 40), 1)


def score_stockout(stockout: dict[str, float]) -> float:
    """Map average stockout risk to 0-30 sub-score."""
    avg = np.mean(list(stockout.values())) if stockout else 0
    return round(min(30.0, avg / 30 * 30), 1)


def score_demand_vol(cv: float) -> float:
    """Map demand CV to 0-20 sub-score."""
    return round(min(20.0, cv / 0.5 * 20), 1)


def score_lead_time(lead_times: dict[str, int]) -> float:
    """Map total supply chain lead time to 0-10 sub-score."""
    total_lt = sum(lead_times.values()) if lead_times else 4
    return round(min(10.0, total_lt / 12 * 10), 1)


def risk_agent_node(state: SupplyChainState) -> dict:
    ratios = state.get("bullwhip_ratios", {})
    stockout = state.get("stockout_risk", {})
    demand_signal = state.get("demand_signal", {})
    cfg = state.get("chain_config", {})
    lead_times = cfg.get("lead_times", {})

    cv = demand_signal.get("cv", 0.0)

    s_bw = score_bullwhip(ratios)
    s_so = score_stockout(stockout)
    s_dv = score_demand_vol(cv)
    s_lt = score_lead_time(lead_times)

    risk_score = round(s_bw + s_so + s_dv + s_lt, 1)

    risk_breakdown = {
        "amplification": s_bw,
        "stockout": s_so,
        "demand_volatility": s_dv,
        "lead_time": s_lt,
    }

    # generate alerts
    alerts: list[str] = []
    max_ratio_tier = max(ratios, key=ratios.get) if ratios else None
    if max_ratio_tier and ratios[max_ratio_tier] > ALERT_THRESHOLDS["bullwhip_ratio"]:
        alerts.append(
            f"⚠️  High bullwhip at {max_ratio_tier} (ratio {ratios[max_ratio_tier]:.2f}x) "
            f"— reduce order batch sizes and improve information sharing."
        )

    for tier, so in stockout.items():
        if so > ALERT_THRESHOLDS["stockout_risk"]:
            alerts.append(
                f"🔴  Stockout risk {so:.1f}% at {tier} — increase safety stock or lead-time buffer."
            )

    if cv > ALERT_THRESHOLDS["cv"]:
        alerts.append(
            f"📈  High demand volatility (CV={cv:.2f}) — consider collaborative forecasting (CPFR) with retailers."
        )

    if risk_score > ALERT_THRESHOLDS["risk_score"]:
        alerts.append(
            f"🚨  Overall supply chain risk score {risk_score}/100 — immediate review recommended."
        )

    if not alerts:
        alerts.append("✅  Supply chain operating within normal risk parameters.")

    return {
        "risk_score": risk_score,
        "risk_breakdown": risk_breakdown,
        "disruption_alerts": alerts,
        "messages": [f"[risk_agent] risk_score={risk_score}, alerts={len(alerts)}"],
    }

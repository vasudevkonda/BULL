"""
Shared state schema for the Bullwhip Effect LangGraph pipeline.
All agents read from and write to this TypedDict.
"""

from typing import TypedDict, Annotated, Sequence
import operator


class SupplyChainState(TypedDict):
    # ── inputs ──────────────────────────────────────────────
    consumer_demand: list[float]          # raw end-consumer demand series
    chain_config: dict                    # tier names, lead times, order policies
    scenario_label: str                   # e.g. "holiday surge", "baseline"

    # ── computed by demand_analyzer ─────────────────────────
    tier_orders: dict[str, list[float]]   # {retailer, wholesaler, distributor, manufacturer}
    bullwhip_ratios: dict[str, float]     # variance(orders) / variance(demand) per tier
    demand_signal: dict                   # moving avg, trend, seasonality

    # ── computed by forecast_agent ───────────────────────────
    smoothed_orders: dict[str, list[float]]
    forecast_accuracy: dict[str, float]
    recommended_smoothing: dict           # alpha, beta params per tier

    # ── computed by inventory_agent ──────────────────────────
    inventory_levels: dict[str, list[float]]
    safety_stock: dict[str, float]
    reorder_points: dict[str, float]
    stockout_risk: dict[str, float]

    # ── computed by risk_agent ────────────────────────────────
    risk_score: float                     # 0-100 composite risk
    risk_breakdown: dict                  # {demand_vol, lead_time, stockout, amplification}
    disruption_alerts: list[str]

    # ── LLM synthesis ─────────────────────────────────────────
    llm_insights: str                     # narrative analysis from Groq
    recommendations: list[str]            # prioritised action items
    policy_changes: dict                  # specific parameter changes suggested

    # ── pipeline control ──────────────────────────────────────
    messages: Annotated[Sequence[str], operator.add]   # debug log
    error: str | None

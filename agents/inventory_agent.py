"""
Inventory Agent
Computes safety stock, reorder points, and stockout risk for each tier
using demand signal statistics and lead-time uncertainty.
"""

import numpy as np
from state import SupplyChainState

Z_95 = 1.645   # service level 95%
Z_99 = 2.326   # service level 99%


def safety_stock(demand_std: float, lead_time: int, service_z: float = Z_95) -> float:
    """Classic formula: z * σ_d * √L"""
    return round(service_z * demand_std * np.sqrt(lead_time), 2)


def reorder_point(demand_mean: float, lead_time: int, ss: float) -> float:
    """ROP = μ_d * L + SS"""
    return round(demand_mean * lead_time + ss, 2)


def stockout_risk(inventory_series: list[float], demand_series: list[float]) -> float:
    """Fraction of periods where inventory < demand (proxy for fill-rate miss)."""
    inv = np.array(inventory_series)
    dem = np.array(demand_series[: len(inv)])
    risk = float(np.mean(inv < dem))
    return round(risk * 100, 1)  # percentage


def inventory_agent_node(state: SupplyChainState) -> dict:
    tier_orders = state["tier_orders"]
    demand = state["consumer_demand"]
    cfg = state["chain_config"]
    demand_signal = state["demand_signal"]

    tiers = list(tier_orders.keys())
    lead_times = cfg.get("lead_times", {t: i + 1 for i, t in enumerate(tiers)})

    d_mean = demand_signal["mean"]
    d_std = demand_signal["std"]

    inventory_levels: dict[str, list[float]] = {}
    safety_stocks: dict[str, float] = {}
    reorder_points: dict[str, float] = {}
    stockout_risks: dict[str, float] = {}

    for tier in tiers:
        orders = tier_orders[tier]
        lt = lead_times.get(tier, 2)
        order_arr = np.array(orders)
        tier_std = float(order_arr.std()) if order_arr.std() > 0 else d_std

        ss = safety_stock(tier_std, lt)
        rop = reorder_point(float(order_arr.mean()), lt, ss)
        safety_stocks[tier] = ss
        reorder_points[tier] = rop

        # simulate rolling inventory
        inv = ss
        inv_series = []
        for o in orders:
            inv = max(0.0, inv - o + rop / (lt + 1))
            inv_series.append(round(inv, 2))
        inventory_levels[tier] = inv_series
        stockout_risks[tier] = stockout_risk(inv_series, orders)

    return {
        "inventory_levels": inventory_levels,
        "safety_stock": safety_stocks,
        "reorder_points": reorder_points,
        "stockout_risk": stockout_risks,
        "messages": [f"[inventory_agent] reorder points: {reorder_points}"],
    }

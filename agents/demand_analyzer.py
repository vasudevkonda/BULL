"""
Demand Analyzer Agent
Simulates the beer-game model across supply chain tiers and computes
variance amplification (the bullwhip ratio) at each node.
"""

import numpy as np
from state import SupplyChainState


def simulate_orders(
    demand: list[float],
    lead_time: int,
    alpha: float = 0.3,
    safety_factor: float = 1.5,
) -> list[float]:
    """
    Simple order-up-to policy with exponential smoothing forecast.
    Captures the three classic bullwhip drivers:
      1. demand forecast updating
      2. order batching (implicit in discrete periods)
      3. safety-stock overreaction
    """
    orders = []
    forecast = demand[0]
    inventory = float(lead_time * demand[0])

    for t, d in enumerate(demand):
        # consume demand
        inventory = max(0.0, inventory - d)
        # update forecast
        forecast = alpha * d + (1 - alpha) * forecast
        # target inventory = forecast * (lead_time + 1) + safety buffer
        target = forecast * (lead_time + 1) * safety_factor
        order = max(0.0, target - inventory)
        orders.append(round(order, 2))
        # receive order placed `lead_time` periods ago
        if t >= lead_time:
            inventory += orders[t - lead_time]

    return orders


def bullwhip_ratio(orders: list[float], demand: list[float]) -> float:
    """Var(orders) / Var(demand) — values >1 indicate bullwhip amplification."""
    var_d = np.var(demand)
    var_o = np.var(orders)
    return round(float(var_o / var_d) if var_d > 0 else 1.0, 3)


def demand_analyzer_node(state: SupplyChainState) -> dict:
    demand = state["consumer_demand"]
    cfg = state["chain_config"]

    tiers = cfg.get("tiers", ["retailer", "wholesaler", "distributor", "manufacturer"])
    lead_times = cfg.get("lead_times", {t: i + 1 for i, t in enumerate(tiers)})
    alphas = cfg.get("alphas", {t: 0.3 for t in tiers})
    safety_factors = cfg.get("safety_factors", {t: 1.5 for t in tiers})

    tier_orders: dict[str, list[float]] = {}
    current_signal = demand

    for tier in tiers:
        orders = simulate_orders(
            current_signal,
            lead_time=lead_times.get(tier, 2),
            alpha=alphas.get(tier, 0.3),
            safety_factor=safety_factors.get(tier, 1.5),
        )
        tier_orders[tier] = orders
        current_signal = orders  # each tier responds to its downstream orders

    ratios = {
        tier: bullwhip_ratio(tier_orders[tier], demand) for tier in tiers
    }

    # simple demand signal decomposition
    arr = np.array(demand)
    window = min(4, len(arr))
    moving_avg = np.convolve(arr, np.ones(window) / window, mode="same").tolist()
    trend = float(np.polyfit(range(len(arr)), arr, 1)[0])
    demand_signal = {
        "moving_avg": [round(v, 2) for v in moving_avg],
        "trend": round(trend, 3),
        "mean": round(float(arr.mean()), 2),
        "std": round(float(arr.std()), 2),
        "cv": round(float(arr.std() / arr.mean()), 3) if arr.mean() > 0 else 0,
    }

    return {
        "tier_orders": tier_orders,
        "bullwhip_ratios": ratios,
        "demand_signal": demand_signal,
        "messages": [f"[demand_analyzer] ratios: {ratios}"],
    }

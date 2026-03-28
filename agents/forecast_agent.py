"""
Forecast Agent
Applies exponential smoothing (Holt's method) to dampen order variance
and suggests optimal alpha/beta per tier to reduce bullwhip amplification.
"""

import numpy as np
from state import SupplyChainState


def holt_smooth(series: list[float], alpha: float = 0.2, beta: float = 0.1) -> list[float]:
    """Holt's double exponential smoothing (level + trend)."""
    if len(series) < 2:
        return series
    level = series[0]
    trend = series[1] - series[0]
    smoothed = [level + trend]
    for val in series[1:]:
        prev_level = level
        level = alpha * val + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
        smoothed.append(round(level + trend, 2))
    return smoothed


def optimal_alpha(series: list[float], alpha_range=(0.05, 0.50, 0.05)) -> float:
    """Grid search for alpha minimising MAE on leave-one-out."""
    best_alpha, best_mae = 0.2, float("inf")
    for a in np.arange(*alpha_range):
        smoothed = holt_smooth(series, alpha=a)
        mae = float(np.mean(np.abs(np.array(series[1:]) - np.array(smoothed[:-1]))))
        if mae < best_mae:
            best_mae, best_alpha = mae, float(a)
    return round(best_alpha, 2)


def forecast_accuracy_mape(actual: list[float], forecast: list[float]) -> float:
    a, f = np.array(actual[1:]), np.array(forecast[:-1])
    with np.errstate(divide="ignore", invalid="ignore"):
        mape = float(np.mean(np.abs((a - f) / np.where(a != 0, a, 1e-9))) * 100)
    return round(mape, 2)


def forecast_agent_node(state: SupplyChainState) -> dict:
    tier_orders = state["tier_orders"]
    demand = state["consumer_demand"]

    smoothed_orders: dict[str, list[float]] = {}
    forecast_accuracy: dict[str, float] = {}
    recommended_smoothing: dict[str, dict] = {}

    for tier, orders in tier_orders.items():
        alpha = optimal_alpha(orders)
        smoothed = holt_smooth(orders, alpha=alpha)
        smoothed_orders[tier] = smoothed
        forecast_accuracy[tier] = forecast_accuracy_mape(orders, smoothed)
        recommended_smoothing[tier] = {"alpha": alpha, "beta": 0.1}

    # also smooth consumer demand for baseline comparison
    d_alpha = optimal_alpha(demand)
    smoothed_orders["consumer"] = holt_smooth(demand, alpha=d_alpha)
    forecast_accuracy["consumer"] = forecast_accuracy_mape(demand, smoothed_orders["consumer"])
    recommended_smoothing["consumer"] = {"alpha": d_alpha, "beta": 0.1}

    return {
        "smoothed_orders": smoothed_orders,
        "forecast_accuracy": forecast_accuracy,
        "recommended_smoothing": recommended_smoothing,
        "messages": [f"[forecast_agent] MAPE per tier: {forecast_accuracy}"],
    }

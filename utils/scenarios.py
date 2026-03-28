"""
Pre-built demand scenarios for demo and testing.
Each returns a list[float] of 24 periods (2 years monthly).
"""

import numpy as np


def baseline_demand(n: int = 24, mean: float = 100, noise: float = 10) -> list[float]:
    rng = np.random.default_rng(42)
    return [round(max(1.0, mean + rng.normal(0, noise)), 1) for _ in range(n)]


def holiday_surge(n: int = 24) -> list[float]:
    """Q4 spike pattern repeated twice."""
    rng = np.random.default_rng(7)
    seasonal = [1.0, 1.0, 1.1, 1.1, 1.05, 1.05, 0.95, 0.95, 1.0, 1.3, 1.5, 1.8] * (n // 12 + 1)
    base = 100.0
    return [round(max(1.0, base * seasonal[i] + rng.normal(0, 8)), 1) for i in range(n)]


def demand_shock(n: int = 24, shock_period: int = 10, shock_magnitude: float = 3.0) -> list[float]:
    """Sudden demand shock at period shock_period (e.g. pandemic buying)."""
    rng = np.random.default_rng(13)
    vals = [round(max(1.0, 100 + rng.normal(0, 8)), 1) for _ in range(n)]
    for i in range(shock_period, min(shock_period + 4, n)):
        vals[i] = round(vals[i] * shock_magnitude, 1)
    return vals


def gradual_growth(n: int = 24, growth_rate: float = 0.04) -> list[float]:
    """Steady market growth with low noise."""
    rng = np.random.default_rng(21)
    return [round(max(1.0, 80 * (1 + growth_rate) ** i + rng.normal(0, 5)), 1) for i in range(n)]


def erratic_demand(n: int = 24) -> list[float]:
    """High-variability intermittent demand."""
    rng = np.random.default_rng(99)
    return [round(max(0.0, rng.exponential(100)), 1) for _ in range(n)]


SCENARIOS = {
    "Baseline (steady)": baseline_demand,
    "Holiday surge": holiday_surge,
    "Demand shock": demand_shock,
    "Gradual growth": gradual_growth,
    "Erratic / intermittent": erratic_demand,
}

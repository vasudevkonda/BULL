"""
Plotly chart helpers for the Bullwhip Effect dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

TIER_COLORS = {
    "consumer": "#64748b",
    "retailer": "#6366f1",
    "wholesaler": "#f59e0b",
    "distributor": "#10b981",
    "manufacturer": "#ef4444",
}


def orders_chart(consumer_demand: list[float], tier_orders: dict[str, list[float]]) -> go.Figure:
    """Multi-line chart: consumer demand vs orders at each tier."""
    n = len(consumer_demand)
    periods = list(range(1, n + 1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=periods, y=consumer_demand, name="Consumer demand",
        line=dict(color=TIER_COLORS["consumer"], width=2, dash="dot"),
        mode="lines",
    ))
    for tier, orders in tier_orders.items():
        fig.add_trace(go.Scatter(
            x=periods, y=orders[:n], name=tier.capitalize(),
            line=dict(color=TIER_COLORS.get(tier, "#94a3b8"), width=2),
            mode="lines",
        ))

    fig.update_layout(
        title="Orders across supply chain tiers vs consumer demand",
        xaxis_title="Period",
        yaxis_title="Units",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    return fig


def bullwhip_ratio_chart(ratios: dict[str, float]) -> go.Figure:
    """Horizontal bar chart of bullwhip ratios with 1.0 reference line."""
    tiers = list(ratios.keys())
    values = list(ratios.values())
    colors = [
        "#ef4444" if v > 3 else "#f59e0b" if v > 1.5 else "#10b981"
        for v in values
    ]

    fig = go.Figure(go.Bar(
        x=values, y=[t.capitalize() for t in tiers],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.2f}x" for v in values],
        textposition="outside",
    ))
    fig.add_vline(x=1.0, line_dash="dash", line_color="rgba(128,128,128,0.6)",
                  annotation_text="No amplification", annotation_position="top")
    fig.update_layout(
        title="Bullwhip ratio by tier (Var orders / Var demand)",
        xaxis_title="Ratio",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        height=280,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    return fig


def inventory_chart(inventory_levels: dict[str, list[float]], reorder_points: dict[str, float]) -> go.Figure:
    """Inventory levels with reorder-point reference lines per tier."""
    n = max(len(v) for v in inventory_levels.values()) if inventory_levels else 1
    periods = list(range(1, n + 1))
    fig = go.Figure()

    for tier, inv in inventory_levels.items():
        color = TIER_COLORS.get(tier, "#94a3b8")
        fig.add_trace(go.Scatter(
            x=periods, y=inv[:n], name=f"{tier.capitalize()} inventory",
            line=dict(color=color, width=1.8),
        ))
        rop = reorder_points.get(tier)
        if rop is not None:
            fig.add_hline(y=rop, line_dash="dot", line_color=color,
                          annotation_text=f"ROP {tier}", annotation_font_size=10)

    fig.update_layout(
        title="Simulated inventory levels & reorder points",
        xaxis_title="Period", yaxis_title="Units",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10), height=320,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    return fig


def risk_gauge(risk_score: float, risk_breakdown: dict) -> go.Figure:
    """Gauge + breakdown donut side by side."""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "pie"}]],
        subplot_titles=["Overall risk score", "Risk drivers"],
    )

    color = "#ef4444" if risk_score > 65 else "#f59e0b" if risk_score > 35 else "#10b981"
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color=color),
            steps=[
                dict(range=[0, 35], color="#d1fae5"),
                dict(range=[35, 65], color="#fef3c7"),
                dict(range=[65, 100], color="#fee2e2"),
            ],
        ),
        domain=dict(column=0),
    ), row=1, col=1)

    labels = list(risk_breakdown.keys())
    values = list(risk_breakdown.values())
    fig.add_trace(go.Pie(
        labels=[l.replace("_", " ").capitalize() for l in labels],
        values=values,
        hole=0.45,
        marker=dict(colors=["#ef4444", "#f59e0b", "#6366f1", "#10b981"]),
        textinfo="label+percent",
        textfont_size=11,
    ), row=1, col=2)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=280,
        showlegend=False,
    )
    return fig

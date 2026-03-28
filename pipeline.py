"""
LangGraph pipeline for Bullwhip Effect Supply Chain Intelligence.
Wires the four specialist agents in sequence then calls the Groq LLM for synthesis.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from langgraph.graph import StateGraph, END
from state import SupplyChainState
from agents.demand_analyzer import demand_analyzer_node
from agents.forecast_agent import forecast_agent_node
from agents.inventory_agent import inventory_agent_node
from agents.risk_agent import risk_agent_node
from agents.llm_synthesis import llm_synthesis_node


def build_pipeline() -> StateGraph:
    graph = StateGraph(SupplyChainState)

    # register nodes
    graph.add_node("demand_analyzer", demand_analyzer_node)
    graph.add_node("forecast_agent", forecast_agent_node)
    graph.add_node("inventory_agent", inventory_agent_node)
    graph.add_node("risk_agent", risk_agent_node)
    graph.add_node("llm_synthesis", llm_synthesis_node)

    # sequential flow: each agent enriches the shared state
    graph.set_entry_point("demand_analyzer")
    graph.add_edge("demand_analyzer", "forecast_agent")
    graph.add_edge("forecast_agent", "inventory_agent")
    graph.add_edge("inventory_agent", "risk_agent")
    graph.add_edge("risk_agent", "llm_synthesis")
    graph.add_edge("llm_synthesis", END)

    return graph.compile()


# Convenience function used by the Streamlit app
def run_analysis(
    consumer_demand: list[float],
    chain_config: dict,
    scenario_label: str = "baseline",
) -> SupplyChainState:
    pipeline = build_pipeline()
    initial_state: SupplyChainState = {
        "consumer_demand": consumer_demand,
        "chain_config": chain_config,
        "scenario_label": scenario_label,
        # remaining keys are populated by agents
        "tier_orders": {},
        "bullwhip_ratios": {},
        "demand_signal": {},
        "smoothed_orders": {},
        "forecast_accuracy": {},
        "recommended_smoothing": {},
        "inventory_levels": {},
        "safety_stock": {},
        "reorder_points": {},
        "stockout_risk": {},
        "risk_score": 0.0,
        "risk_breakdown": {},
        "disruption_alerts": [],
        "llm_insights": "",
        "recommendations": [],
        "policy_changes": {},
        "messages": [],
        "error": None,
    }
    return pipeline.invoke(initial_state)

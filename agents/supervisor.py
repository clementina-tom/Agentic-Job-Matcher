"""LangGraph supervisor orchestrating the multi-agent workflow."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from agents import applier_agent, matcher_agent, refiner_agent, researcher_agent, tailor_agent
from core.state import AgentState


def _should_tailor(state: AgentState) -> str:
    high_fit = [job for job in state.shortlisted_jobs if float(job.get("fit_score", 0.0)) >= 0.68]
    return "tailor" if high_fit else "apply"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("research", researcher_agent.run)
    graph.add_node("match", matcher_agent.run)
    graph.add_node("tailor", tailor_agent.run)
    graph.add_node("apply", applier_agent.run)
    graph.add_node("refine", refiner_agent.run)

    graph.set_entry_point("research")
    graph.add_edge("research", "match")
    graph.add_conditional_edges("match", _should_tailor, {"tailor": "tailor", "apply": "apply"})
    graph.add_edge("tailor", "apply")
    graph.add_edge("apply", "refine")
    graph.add_edge("refine", END)

    return graph.compile()


def run_graph(initial_state: AgentState) -> AgentState:
    compiled = build_graph()
    return compiled.invoke(initial_state)

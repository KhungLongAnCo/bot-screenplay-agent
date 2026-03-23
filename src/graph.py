"""
Screenplay agent LangGraph pipeline.

IMPORTANT: agent5_generate_images is async. Always use graph.ainvoke() — never
graph.invoke() — or the async node will fail at runtime.
"""
from langgraph.graph import StateGraph, START, END

from src.state import GraphState
from src.agents.agent1_analyze import agent1_analyze
from src.agents.agent2_style import agent2_style
from src.agents.agent3_split_scenes import agent3_split_scenes
from src.agents.agent4_image_prompts import agent4_image_prompts
from src.agents.agent5_generate_images import agent5_generate_images


def route_after_agent4(state: GraphState) -> str:
    return "agent5_generate_images" if state["is_create_image"] else END


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("agent1_analyze", agent1_analyze)
    builder.add_node("agent2_style", agent2_style)
    builder.add_node("agent3_split_scenes", agent3_split_scenes)
    builder.add_node("agent4_image_prompts", agent4_image_prompts)
    builder.add_node("agent5_generate_images", agent5_generate_images)

    builder.add_edge(START, "agent1_analyze")
    builder.add_edge("agent1_analyze", "agent2_style")
    builder.add_edge("agent2_style", "agent3_split_scenes")
    builder.add_edge("agent3_split_scenes", "agent4_image_prompts")

    builder.add_conditional_edges(
        "agent4_image_prompts",
        route_after_agent4,
        {
            "agent5_generate_images": "agent5_generate_images",
            END: END,
        },
    )
    builder.add_edge("agent5_generate_images", END)

    return builder.compile()


graph = build_graph()

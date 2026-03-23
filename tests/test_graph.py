from src.graph import build_graph, route_after_agent4
from src.state import GraphState


def make_state(**kwargs) -> GraphState:
    base: GraphState = {
        "draft": "", "graphic_style": "", "is_create_image": False,
        "completed_script": "", "styled_script": "",
        "scenes": [], "scenes_with_prompts": [], "final_scenes": [],
    }
    base.update(kwargs)
    return base


def test_route_to_agent5_when_is_create_image_true():
    state = make_state(is_create_image=True)
    assert route_after_agent4(state) == "agent5_generate_images"


def test_route_to_end_when_is_create_image_false():
    from langgraph.graph import END
    state = make_state(is_create_image=False)
    assert route_after_agent4(state) == END


def test_graph_compiles():
    graph = build_graph()
    assert graph is not None


def test_graph_has_expected_nodes():
    graph = build_graph()
    node_names = set(graph.get_graph().nodes.keys())
    expected = {"agent1_analyze", "agent2_style", "agent3_split_scenes",
                "agent4_image_prompts", "agent5_generate_images"}
    assert expected.issubset(node_names)

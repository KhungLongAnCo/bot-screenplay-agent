import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.agent1_analyze import agent1_analyze
from src.state import GraphState, Scene


def make_state(**overrides) -> GraphState:
    base: GraphState = {
        "draft": "A young woman returns to her hometown after 10 years.",
        "graphic_style": "Cinematic Realism",
        "is_create_image": False,
        "completed_script": "",
        "styled_script": "",
        "scenes": [],
        "scenes_with_prompts": [],
        "final_scenes": [],
    }
    base.update(overrides)
    return base


def test_agent1_returns_completed_script():
    state = make_state()
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "Completed screenplay text here."

    with patch("src.agents.agent1_analyze.build_chain", return_value=mock_chain):
        result = agent1_analyze(state)

    assert "completed_script" in result
    assert result["completed_script"] == "Completed screenplay text here."
    mock_chain.invoke.assert_called_once_with({"draft": state["draft"]})


def test_agent2_returns_styled_script():
    from src.agents.agent2_style import agent2_style

    state = make_state(completed_script="Draft screenplay text.")
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "INT. CAFE - DAY\nFormatted text."

    with patch("src.agents.agent2_style.build_chain", return_value=mock_chain):
        result = agent2_style(state)

    assert result["styled_script"] == "INT. CAFE - DAY\nFormatted text."
    mock_chain.invoke.assert_called_once_with({"completed_script": state["completed_script"]})

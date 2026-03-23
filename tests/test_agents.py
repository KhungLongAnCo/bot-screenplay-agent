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


def test_agent3_returns_scene_list():
    from src.agents.agent3_split_scenes import agent3_split_scenes

    state = make_state(styled_script="INT. CAFE - DAY\nA woman enters.\nEXT. STREET - NIGHT\nShe walks away.")
    mock_scenes = [
        Scene(scene_number=1, title="Cafe Arrival", location="INT. CAFE - DAY", scene_script="A woman enters."),
        Scene(scene_number=2, title="Night Walk", location="EXT. STREET - NIGHT", scene_script="She walks away."),
    ]

    with patch("src.agents.agent3_split_scenes.build_structured_chain") as mock_build:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_scenes
        mock_build.return_value = mock_chain
        result = agent3_split_scenes(state)

    assert len(result["scenes"]) == 2
    assert result["scenes"][0].title == "Cafe Arrival"


def test_agent4_adds_image_prompt():
    from src.agents.agent4_image_prompts import agent4_image_prompts

    scenes = [
        Scene(scene_number=1, title="Opening", location="INT. CAFE - DAY", scene_script="She enters."),
    ]
    state = make_state(scenes=scenes, graphic_style="Cinematic Realism")

    with patch("src.agents.agent4_image_prompts.generate_image_prompt") as mock_gen:
        mock_gen.return_value = "cinematic realism, dramatic lighting, woman entering cafe"
        result = agent4_image_prompts(state)

    assert len(result["scenes_with_prompts"]) == 1
    assert result["scenes_with_prompts"][0].image_prompt == "cinematic realism, dramatic lighting, woman entering cafe"


def test_agent4_preserves_scene_data():
    from src.agents.agent4_image_prompts import agent4_image_prompts

    scenes = [
        Scene(scene_number=1, title="Opening", location="INT. CAFE - DAY", scene_script="She enters."),
    ]
    state = make_state(scenes=scenes, graphic_style="Anime / Ghibli")

    with patch("src.agents.agent4_image_prompts.generate_image_prompt", return_value="anime style"):
        result = agent4_image_prompts(state)

    s = result["scenes_with_prompts"][0]
    assert s.scene_number == 1
    assert s.scene_script == "She enters."

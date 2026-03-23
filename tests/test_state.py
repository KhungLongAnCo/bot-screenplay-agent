from src.state import Scene, GraphState
from typing import get_type_hints

def test_scene_defaults():
    scene = Scene(scene_number=1, title="Opening", location="INT. CAFE - DAY", scene_script="...")
    assert scene.image_prompt is None
    assert scene.image_url is None

def test_scene_full():
    scene = Scene(
        scene_number=2,
        title="Climax",
        location="EXT. ROOFTOP - NIGHT",
        scene_script="Hero stands at the edge.",
        image_prompt="cinematic realism, dramatic lighting",
        image_url="https://image.pollinations.ai/prompt/..."
    )
    assert scene.scene_number == 2
    assert scene.image_url is not None

def test_graph_state_keys():
    hints = get_type_hints(GraphState)
    required = {"draft", "graphic_style", "is_create_image", "completed_script",
                "styled_script", "scenes", "scenes_with_prompts", "final_scenes"}
    assert required.issubset(hints.keys())

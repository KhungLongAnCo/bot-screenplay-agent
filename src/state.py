from typing import TypedDict, List, Optional
from pydantic import BaseModel


class Scene(BaseModel):
    scene_number: int
    title: str
    location: str
    scene_script: str
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None


class GraphState(TypedDict):
    # User inputs
    draft: str
    graphic_style: str
    is_create_image: bool

    # Accumulated outputs
    completed_script: str       # Agent 1
    styled_script: str          # Agent 2
    scenes: List[Scene]         # Agent 3
    scenes_with_prompts: List[Scene]  # Agent 4
    final_scenes: List[Scene]   # Agent 5 or copy from Agent 4

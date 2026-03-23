from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

from src.state import GraphState, Scene
from src.prompts import AGENT4_SYSTEM_PROMPT, GRAPHIC_STYLES


def generate_image_prompt(scene: Scene, graphic_style: str, llm) -> str:
    style_value = GRAPHIC_STYLES.get(graphic_style, graphic_style)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT4_SYSTEM_PROMPT.format(graphic_style=style_value)),
        ("human", "Scene {number}: {title}\nLocation: {location}\n\n{script}"),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "number": scene.scene_number,
        "title": scene.title,
        "location": scene.location,
        "script": scene.scene_script,
    })


def agent4_image_prompts(state: GraphState) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=3000)
    scenes_with_prompts: List[Scene] = []
    for scene in state["scenes"]:
        prompt_text = generate_image_prompt(scene, state["graphic_style"], llm)
        scenes_with_prompts.append(scene.model_copy(update={"image_prompt": prompt_text}))
    return {"scenes_with_prompts": scenes_with_prompts}

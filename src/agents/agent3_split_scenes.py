from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from src.state import GraphState, Scene
from src.prompts import AGENT3_SYSTEM_PROMPT
from src.agents.config import get_llm


class SceneList(BaseModel):
    scenes: List[Scene]


def build_structured_chain():
    llm = get_llm(max_tokens=16000)
    structured_llm = llm.with_structured_output(SceneList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT3_SYSTEM_PROMPT),
        ("human", "{styled_script}"),
    ])
    return prompt | structured_llm


def agent3_split_scenes(state: GraphState) -> dict:
    chain = build_structured_chain()
    result: SceneList = chain.invoke({"styled_script": state["styled_script"]})
    return {"scenes": result.scenes}

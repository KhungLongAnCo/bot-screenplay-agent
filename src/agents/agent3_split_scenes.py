from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from src.state import GraphState, Scene
from src.prompts import AGENT3_SYSTEM_PROMPT


def build_structured_chain():
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=2500)
    structured_llm = llm.with_structured_output(List[Scene])
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT3_SYSTEM_PROMPT),
        ("human", "{styled_script}"),
    ])
    return prompt | structured_llm


def agent3_split_scenes(state: GraphState) -> dict:
    chain = build_structured_chain()
    scenes: List[Scene] = chain.invoke({"styled_script": state["styled_script"]})
    return {"scenes": scenes}

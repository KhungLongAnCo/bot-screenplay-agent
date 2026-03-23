from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.state import GraphState
from src.prompts import AGENT1_SYSTEM_PROMPT
from src.agents.config import get_llm


def build_chain():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT1_SYSTEM_PROMPT),
        ("human", "KỊCH BẢN DRAFT:\n{draft}"),
    ])
    return prompt | llm | StrOutputParser()


def agent1_analyze(state: GraphState) -> dict:
    chain = build_chain()
    result = chain.invoke({"draft": state["draft"]})
    return {"completed_script": result}

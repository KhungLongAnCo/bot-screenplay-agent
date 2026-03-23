from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.state import GraphState
from src.prompts import AGENT2_SYSTEM_PROMPT, REFERENCE_SCRIPT
from src.agents.config import get_llm


def build_chain():
    llm = get_llm(max_tokens=3000)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT2_SYSTEM_PROMPT.format(reference=REFERENCE_SCRIPT)),
        ("human", "{completed_script}"),
    ])
    return prompt | llm | StrOutputParser()


def agent2_style(state: GraphState) -> dict:
    chain = build_chain()
    result = chain.invoke({"completed_script": state["completed_script"]})
    return {"styled_script": result}

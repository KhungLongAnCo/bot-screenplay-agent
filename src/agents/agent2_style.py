from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

from src.state import GraphState
from src.prompts import AGENT2_SYSTEM_PROMPT, REFERENCE_SCRIPT


def build_chain():
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=3000)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT2_SYSTEM_PROMPT.format(reference=REFERENCE_SCRIPT)),
        ("human", "{completed_script}"),
    ])
    return prompt | llm | StrOutputParser()


def agent2_style(state: GraphState) -> dict:
    chain = build_chain()
    result = chain.invoke({"completed_script": state["completed_script"]})
    return {"styled_script": result}

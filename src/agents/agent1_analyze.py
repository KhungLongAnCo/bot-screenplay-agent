from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

from src.state import GraphState
from src.prompts import AGENT1_SYSTEM_PROMPT


def build_chain():
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", max_tokens=3000)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT1_SYSTEM_PROMPT),
        ("human", "KỊCH BẢN DRAFT:\n{draft}"),
    ])
    return prompt | llm | StrOutputParser()


def agent1_analyze(state: GraphState) -> dict:
    chain = build_chain()
    result = chain.invoke({"draft": state["draft"]})
    return {"completed_script": result}

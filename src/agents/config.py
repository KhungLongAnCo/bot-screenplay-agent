from langchain_openai import ChatOpenAI

MODEL_NAME = "gpt-4o-mini"


def get_llm(max_tokens: int = 3000) -> ChatOpenAI:
    return ChatOpenAI(model=MODEL_NAME, max_tokens=max_tokens)

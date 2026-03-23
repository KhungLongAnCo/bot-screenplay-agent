from langchain_openai import ChatOpenAI

MODEL_NAME = "gpt-5-nano"


def get_llm(max_tokens: int = 16000) -> ChatOpenAI:
    return ChatOpenAI(model=MODEL_NAME, max_tokens=max_tokens)

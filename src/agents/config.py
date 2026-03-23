from langchain_anthropic import ChatAnthropic

MODEL_NAME = "claude-sonnet-4-20250514"


def get_llm(max_tokens: int = 3000) -> ChatAnthropic:
    return ChatAnthropic(model=MODEL_NAME, max_tokens=max_tokens)

from langchain_ollama import ChatOllama

model = ChatOllama(
    model="qwen3:4b",
    temperature=0.0 # Strict aur factual answers ke liye
)
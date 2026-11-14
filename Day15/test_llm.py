from llm import call_llm

messages = [{
    "role":"user",
    "content":("Explain in one line"
    "What an AI_Agent is.")
}]

try:
    answer = call_llm(messages)
    print (answer)
except RuntimeError as e:
    print("Agent Connect to LLM Failed")
    print("Reason:",e)
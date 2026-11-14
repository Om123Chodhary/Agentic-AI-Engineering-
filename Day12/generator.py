from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODEL = "qwen3:1.7b"

def generate_answer(query,results):
    context = "\n\n".join(result["text"] for result in results)

    prompt = f"""Answer the user's question using only the provided context.
    Context:{context}

    Question:{query}

    Rules:
    1. Use Only The Provided Context.
    2.Do not invent information.
    3.If Answer no persent,say that information is not available
    4.Give a Clear and Concise answer"""

    response = client.chat.completions.create(
        model = MODEL,
        messages=[{
            "role":"user",
            "content":prompt
        }]
    )
    return (response.choices[0].message.content.strip())
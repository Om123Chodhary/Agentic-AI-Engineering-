from openai import OpenAI
from similarity import cosine_similarity

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
embedding1 = "pizza is delicious."
embedding2 = "python is in Data science and Machine learning."
embedding1 = client.embeddings.create(
    model="nomic-embed-text",
    input = embedding1
)
embedding1 = embedding1.data[0].embedding
embedding2 = client.embeddings.create(
    model="nomic-embed-text",
    input = embedding2
)
embedding2 = embedding2.data[0].embedding

print(cosine_similarity(embedding1,embedding2))


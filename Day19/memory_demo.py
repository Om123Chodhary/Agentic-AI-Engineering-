from model import model

response = model.invoke("my name is Omaram")

print("First Response")
print(response.content)

response = model.invoke("What is my name?")

print("Second Response")
print(response.content)
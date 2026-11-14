from model import model
from prompt import prompt

messages = prompt.invoke({
    "question":"What is an autonomous agent?"
})
response = model.invoke(messages)

print("Response:")
print(response.content)
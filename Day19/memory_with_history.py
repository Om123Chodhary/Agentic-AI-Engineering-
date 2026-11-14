from model import model

messages = [{
    "role":"user",
    "content":"My name is Omaram."

}]

first_response = model.invoke(messages)

print("First Response")
print(first_response.content)

messages.append({
     "role":"assistant",
    "content":first_response.content
    })
messages.append({
     "role":"user",
    "content":"what is my name?"
    })

second_response = model.invoke(messages)
print("Second Response")
print(second_response.content)

from model import model
from langchain.agents import create_agent
from tools import current_time, roll_dice, generate_password

# 1. Tools ki list banao
tools = [current_time, roll_dice, generate_password]

agent = create_agent(model = model,tools = tools)

result = agent.invoke({
    "messages":[{
        "role":"user",
        "content":"What is the current time?"
    }]
})
# 2. Model ko tools ke saath bind karo
# Yeh model ko bata raha hai: "Tumhare paas yeh capabilities hain"
model_with_tools = model.bind_tools(tools)

# 3. Model ko invoke karo
print("Asking model: 'What is the current time?'")
response = model_with_tools.invoke("What is the current time?")

# 4. Output dekho
print("\n--- RESPONSE OBJECT ---")
print(result["messages"][-1].content)
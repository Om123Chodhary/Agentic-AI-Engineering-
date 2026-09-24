from openai import OpenAI
from dotenv import load_dotenv
import os
from tools import(get_current_time,
                roll_dice,
                generate_password)

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)

messages = []

while True:

    user_input = input("\nYou : ")
    # Save the user's message
    messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )
    if "time" in user_input.lower():
        print(get_current_time())
        continue 
    if "password"in user_input.lower():
            print(generate_password())
            continue 
    if "dice" in user_input.lower():
            print(roll_dice())
            continue 
    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages= messages
    )
    ai_reply = response.choices[0].message.content

    print("\nAI :", ai_reply)

    #save ai reply
    messages.append( 
        {
        "role":"Assistant",
        "content":ai_reply
        }
    )
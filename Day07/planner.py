from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url = os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
def choose_tool(user_request):
    planner_prompt = f"""You are an AI planner.
    
    Available tools:
    
    1. get_current_time
        Use When the User asks for the current date or time.
        
    2. roll_dice
        Use When the User asks to roll a dice.
    3. generate_password
        use when user wamts a secure password.
        
    if no tool required, return:
    None
    Return ONLY the tool name
    
    User Request: {user_request}"""
    response = client.chat.completions.create(
        model = os.getenv("MODEL"),

        messages = [
            {
                "role":"system",
                "content":"You are an AI planner."
            },
            {
                "role":"User",
                "content":planner_prompt
            }

        ]

    )
    return response.choices[0].message.content.strip()
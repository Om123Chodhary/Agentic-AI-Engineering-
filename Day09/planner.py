from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()
# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

# Build Tool Descriptions
def build_tool_descriptions(tools):

    descriptions = ""
    for tool in tools:
        descriptions += f"""
        Tool:{tool.name}
        Description:{tool.description}
----------------------------
"""
    return descriptions

# Build Planner
def planner(state, tools):
    tool_descriptions = build_tool_descriptions(tools)
    prompt = f"""You are an AI Planner.
                Your Job is to decide ONLY the next action.
                User Request:
                {state["user_request"]}

                Available tools:
                {tools}

                Completed Actions:
                {state["actions"]}
                Previous_Observations:
                {state["observations"]}
                Rules:
                1. Choose only ONE next action.
                2. Never repeat an action that has already been completed.
                3. Use the observations to decide what is still required.
                4. If the user's request has been completely satisfied, return FINISH.
                5. Return ONLY the tool name or FINISH.
                6. Do not explain your answer.
                Next Action:"""
    response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI planner."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    
    return response.choices[0].message.content.strip()
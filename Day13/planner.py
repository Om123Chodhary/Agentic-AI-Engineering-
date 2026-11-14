import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration from the .env file
load_dotenv()

# Create a client that communicates with Ollama
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def build_tool_description(tools):
    #it receives the tools as input
    descriptions = ""

    for tool in tools:
        descriptions += f"""
    Tool: {tool.name}
    Description: {tool.description}

    input_schema = {tool.input_schema}


    --------------------------------
    """
    return descriptions

def planner(state, tools):

    tool_descriptions = (build_tool_description(tools))

    prompt = f"""
You are an AI Planner.
Your job is to decide ONLY the next action.

User Request: {state["user_request"]}

Actions already taken:
{state["actions"]}

Observations from those actions:
{state["observations"]}

Available Tools: {tool_descriptions}

Rules:
1. Choose only ONE next action.
2. NEVER repeat a tool that already appears in "Actions already taken" 
   UNLESS its observation shows an error.
3. Use the observations to decide what is still required.
4. If the user's request has been completely satisfied, return FINISH.
5. Return ONLY the tool name or FINISH.
6. Do not explain your answer.

Use exactly this format: {{
    "tool":"tool_name",
    "arguments":{{"arguments_name":"argument_value"}}
}}
For finish, return:
{{
    "tool":"FINISH",
    "arguments":{{}}
}}
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
    result  =   (response.choices[0].message.content.strip())
    return json.loads(result)
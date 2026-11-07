import asyncio 
from openai import OpenAI
from dotenv import load_dotenv
import os
from mcp_client import *
from planner import planner
from executor import execute_action
from loop import run_agent_loop

# Load configuration
load_dotenv()
# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def format_answer(state):
    prompt = f"""The User asked:
    {state["user_request"]}
    
    Actions performed :
    {state["observations"]}
    Answer the user naturally
    
    Do not mention internal planning
    Do not mention state
    Do not Mention tools"""
    response = client.chat.completions.create(
    
            model= os.getenv("MODEL"),
    
            messages=[
    
                {
                    "role": "user",
                    "content": prompt
                }
    
            ]
    
        )
    return response.choices[0].message.content.strip()

async def main():
    #step1: connect to the MCP Server
    client = await connect()
    # Step2: Discover All available tools
    tools = await discover_tools(
        client
    )
    print()
    print("Available Tools")
    print("===========================")

    for tool in tools:
        print(tool.name)

    user_request = input(
                "User : "
            )
    state = await run_agent_loop(
        user_request,
        planner,
        execute_action,
        format_answer, 
        tools,
        client
    )
    print()
    print("Final Answer:")
    print(state["final_answer"])

    await disconnect(client)

if __name__ == "__main__":
    asyncio.run(main())
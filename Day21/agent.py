from ollama import chat
from tools import (search_web, read_webpage,
 add_research_note, get_research_notes,
verify_finding , get_verified_research_notes)

MODEL = "qwen3:4b"

AVAILABLE_TOOLS = {
    "search_web": search_web,
    "read_webpage": read_webpage,
    "add_research_note": add_research_note,
    "get_research_notes": get_research_notes,
    "verify_finding": verify_finding,
    "get_verified_research_notes": get_verified_research_notes
}

TOOLS = [search_web, read_webpage, add_research_note, get_research_notes, verify_finding , get_verified_research_notes]


def generate_report(user_request: str, verified_notes: list) -> str:
    """ Generate a research report from verified research findings. """
    research_text = "\n\n".join([
        (f"Source:{note['source']}\n"
         f"Source:{note['finding']}\n"
         f"Source:{note['evidence']}\n"
         )
         for note in verified_notes
    ])

    response = chat(
        model = MODEL,
        messages = [{
            "role":"system",
            "content":(
                "You are a professional research report writer. "
                "Write a clear, structured report using ONLY the supplied verified research findings. "
                "Do not invent facts or sources. If the available research is insufficient for a section, say so."
            )
        },
        {
            "role": "user",
            "content": (
                f"Research Request:\n{user_request}\n\n"
                f"Verified Research Findings:\n{research_text}\n\n"
                "Create a report with the following sections:\n"
                "1. Executive Summary\n"
                "2. Introduction\n"
                "3. Key Findings\n"
                "4. Analysis\n"
                "5. Limitations\n"
                "6. Conclusion\n"
                "7. Sources\n"
            )
        }
    ],
    options={"temperature": 0.3}
    )
    return response.message.content

def create_research_plan(user_request):
    """
    Asks the LLM to create a structured research plan before executing tools.
    """
    print(f"\n[Planner] Creating research plan for: {user_request}")
    
    messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert research planning assistant. "
                    "Create a concise, ordered research plan for the user's request. "
                    "Return ONLY the numbered research steps (e.g., 1. ..., 2. ...). "
                    "Do not add any conversational filler or explanations."
                )
            },
        {
            "role": "user",
            "content": user_request
        }
    ]

    response = chat(
        model=MODEL,
        messages=messages
    )
    
    plan = response.message.content
    
    return plan

async def research_agent(user_request, max_steps=6):
    plan = create_research_plan(user_request)
    print("\n--- RESEARCH PLAN ---")
    print(plan)
    print("---------------------\n")
    search_done = False
    read_done = False
    
    messages = [{
        "role":"system",
        "content": (
    "You are a Research Agent. Investigate the user's request using the available tools.\n"
    f"Use this research plan as a guide:\n{plan}\n\n"
    "Rules:\n"
    "1. Search for relevant information using 'search_web'.\n"
    "2. Read useful sources using 'read_webpage'.\n"
    "3. Store important findings using 'add_research_note'.\n"
    "4. **CRITICAL:** For every important finding, you MUST use 'verify_finding' to check whether the evidence actually supports the finding.\n"
    "5. Do NOT invent sources.\n"
    "6. Before giving your final answer, use 'get_verified_research_notes' to ensure you only report verified facts."
)},
        {
            "role": "user",
            "content": f"Research Request:\n{user_request}\n\nResearch Plan:\n{plan}"
        }
    ]

    for step in range(max_steps):
        print(f"\n--- Agent Step {step + 1} / {max_steps} ---")
        
        response = chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            options={"temperature": 0.0} # Strict mode
        )
        
        messages.append(response.message)


        if not response.message.tool_calls:
            
           
            if search_done and not read_done:
                print("\n[ENFORCEMENT] You searched but didn't read any page. Forcing read_webpage...")
                messages.append({
                    "role": "system",
                    "content": "STOP. You have not read any webpage yet. You must use the 'read_webpage' tool on a URL from your search results before answering."
                })
                continue 
            
            else:
                print("\nNo tool call. Returning final answer.")
                return response.message.content


        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            
            arguments = tool_call.function.arguments
            
            print(f"\nCalling tool: {tool_name}")
            print(f"Arguments: {arguments}")
            
           
            if tool_name == "search_web":
                search_done = True
            elif tool_name == "read_webpage":
                read_done = True
            
            tool_function = AVAILABLE_TOOLS.get(tool_name)
            
            if tool_function is None:
                result = f"Unknown tool: {tool_name}"
            else:
                try:
                    result = await tool_function(**arguments)
                except Exception as e:
                    result = f"Error: {e}"
            
            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_name": tool_name
            })

    return "Agent reached max steps without finishing."

async def run_agent(request):
    answer = await research_agent(request, max_steps = 7)

    verified_notes = (get_verified_research_notes())

    print("\n Verified finding:",len(verified_notes))

    report = generate_report(
        user_request = request,
        verified_notes = verified_notes)

    print("="*20)
    print("\nFINAL ANSWER\n")
    print("="*20)
    print(report)
    return report
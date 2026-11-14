from langgraph.graph import (
    StateGraph,
    START,
    END
)
from langgraph.checkpoint.memory import (
    InMemorySaver
)
from langgraph.types import interrupt
from agent.executor import execute_action 
from agent.planner import planner
from agent.state import AgentState
from agent.runner import format_answer

def create_planner_node(tools):

    def planner_node(state: AgentState):

        action = planner(
            state,
            tools
        )

        print("\nPlanner Selected:")
        print(action)

        return {
            "actions": state["actions"],
            "observations": state["observations"],
            "current_step": state["current_step"],
            "finished": action == "FINISH",
            "action": action,
            "final_answer": state["final_answer"]
        }

    return planner_node

def route_after_planner(state: AgentState):
  
    if state["action"] == "FINISH":
        return "finish"
    return "needs_approval"

def approval_node(state:AgentState):
    decision = interrupt({
        "message":"Approve this tool call ? ",
        "action":state["action"]
    })
    return {"approval":decision}

def route_after_approval(state:AgentState):
    if state["approval"]=="yes":
        return "approved"
    return "rejected"

def create_tool_node(client):
    async def tool_node(state: AgentState):
        # 1. State se action uthao
        action = state["action"]
        print(f"\nExecuting Tool: {action}")
        # 2. MCP server par action execute karo
        observation = await execute_action(action, state, client)
        print(f"Observation: {observation}")
        
        
        return{ "observations":state["observations"] + [{
            "step": state["current_step"],
            "action": action,
            "observation": observation
        }],
        "actions":(state["actions"] + [action]),
        "current_step":(state["current_step"]+1)
        }
    return tool_node
def route_after_tool(state:AgentState):
    if state["current_step"] >= state["max_steps"]:
        return "stop"
    return "continue"
def create_format_answer(state:AgentState):
    answer = format_answer(state)
    print("\nFinal Answer:")
    print(answer)
    return {"final_answer":answer,
            "finished":True}

def build_graph(tools,client):
    builder = StateGraph(AgentState)
    planner_node = create_planner_node(tools)
    tool_node = create_tool_node(client)
    answer_node = create_format_answer
    
    builder.add_node("planner", planner_node)
    builder.add_node("tool_node", tool_node)
    builder.add_node("answer",answer_node)
    builder.add_node("approval", approval_node) 

    builder.add_edge(START, "planner")

    
    builder.add_conditional_edges(
        "planner",                 
        route_after_planner,        
        {
            "needs_approval": "approval",   
            "finish": "answer"    
        }
    )

    builder.add_conditional_edges("approval", route_after_approval,
                            {
                                "approved":"tool_node",
                                "rejected":"answer"

                            }
                        )
    builder.add_conditional_edges(
        "tool_node",                 
        route_after_tool,        
        {
            "continue": "planner",   
            "stop":"answer"   
        }
    )
    builder.add_edge("answer",END)

    checkpointer = InMemorySaver()

    return builder.compile(
        checkpointer=checkpointer
    )

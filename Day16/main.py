import asyncio

from langgraph.types import Command 
from agent.mcp_client import (
    connect,
    disconnect,
    discover_tools
)

from graph import build_graph


async def main():

    client = await connect()

    tools = await discover_tools(client)

    print("\nAvailable Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)

    graph = build_graph(tools, client)

    user_request = input("\nUser : ")

    config = {"configurable": {"thread_id": "user_1"}}

    initial_state = {
        "user_request": user_request,
        "current_step": 0,
        "max_steps": 5,
        "actions": [],
        "observations": [],
        "action": "",
        "approval": "",
        "finished": False,
        "final_answer": ""
    }

    print("\n--- Running Graph ---")
    result = await graph.ainvoke(initial_state, config=config)

    while True:
            interrupts = result.get(
            "__interrupt__"
            )

            if not interrupts:
                break

            if interrupts:

                interrupt_data = (
                interrupts[0].value
                )

                print(
                "\n=============================="
                )

                print(
                " HUMAN APPROVAL REQUIRED"
                )

                print(
                "=============================="
                )

                print(
                interrupt_data["message"]
                )

                print(
                "Tool:",
                interrupt_data["action"]
                )

                decision = input(
                "\nApprove? (yes/no): "
                ).strip().lower()

            result = await graph.ainvoke(
                Command(
                    resume=decision
                ),
                config
            )

    print("\n" + "="*20)
    print("FINAL RESPONSE")
    print("="*20)
    print(result.get("final_answer", "No answer generated."))

    await disconnect(client)


if __name__ == "__main__":
    asyncio.run(main())
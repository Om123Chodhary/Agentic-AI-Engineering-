from mcp_client import execute_tool
### The Agent Loop doesn't directly know how MCP works.
# it simply asks execute_action() to execute the selected actions. ###

async def execute_action(action,client):
    result = await execute_tool(client, action)
    if hasattr(result, "content"):
        ### This asks: Does The result object have a content attributr?###
        ### MCP tool results commonly contain their actual output inside content. ###

        if result.content:
                  ###This checks whether content actually contains
                  # siomething ###
                return result.content[0].text

        return str(result)
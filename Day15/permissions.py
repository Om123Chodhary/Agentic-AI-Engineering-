TOOL_PERMISSIONS = {
    "research":{
        "get_weather","read_file"
    },
    "coding": {
        "read_file"
    },
    "review":{"read_file"},
    "manager":{"get_weather","read_file"}
}

def demonstrate_permissions(agent_name, tool_name):
    allowed_tools = (TOOL_PERMISSIONS.get(agent_name,set()))
    return (tool_name in allowed_tools)
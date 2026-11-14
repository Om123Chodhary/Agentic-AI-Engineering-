from fastmcp import FastMCP
mcp = FastMCP("Weather Server")

@mcp.tool()
def get_weather(city:str):
    """Return Weather Information for a City."""
    weather_data={
        "Delhi":"Sunny, 32C ",
        "Paris":"Cloudy,9C",
        "Sydney":"Rainy,29C",
        "London":"Partly cloudy,15C"
        }
    return weather_data.get(city,"weather data not available.")
if __name__ =="__main__":
    print("Starting Weather MCP Server...")
    mcp.run()
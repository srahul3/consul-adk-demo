import httpx
from google.adk.tools import BaseTool, ToolContext
from typing_extensions import override, Any
import os
from typing import List


class WeatherTool(BaseTool):
    """A tool that provides weather information for multiple locations.

    Attributes:
        name: The name of the tool.
        description: A brief description of what the tool does.
    """
    name = "WeatherTool"
    description = "Gets the current weather information for one or more specified locations"

    async def get_weather(self, locations: List[str]) -> List[dict[str, Any]]:
        """Fetches weather information for one or more locations.

        Attributes:
            locations: A list of city names or locations to get weather for.
        Returns:
            A list of dictionaries containing weather data such as temperature, 
            condition, humidity, and wind for each location.
        """
        api_key = os.getenv("WEATHER_API_KEY", default="")
        url = f"https://api.weatherapi.com/v1/current.json"
        print(f"Processing {len(locations)} locations")

        results = []
        
        for location in locations:
            try:
                async with httpx.AsyncClient() as client:
                    # add query parameters to get call
                    params = {
                        "key": api_key,
                        "q": location
                    }
                    response = await client.get(url=url, params=params, timeout=10.0)

                    # If the response indicates a client error (like 404 for location not found)
                    if response.status_code >= 400 and response.status_code < 500:
                        # Return a default response for location not found
                        results.append({
                            "location": f"{location}",
                            "region": f"{location}",
                            "country": "Unknown",
                            "temperature": "20°C",
                            "condition": "Information not available",
                            "humidity": "30 %",
                            "wind": "2 mph"
                        })
                        continue

                    response.raise_for_status()
                    data = response.json()

                    weather_data = {
                        "location": data["location"]["name"],
                        "region": data["location"]["region"],
                        "country": data["location"]["country"],
                        "temperature": f"{data['current']['temp_c']}°C / {data['current']['temp_f']}°F",
                        "condition": data["current"]["condition"]["text"],
                        "humidity": f"{data['current']['humidity']}%",
                        "wind": f"{data['current']['wind_mph']} mph {data['current']['wind_dir']}"
                    }

                    results.append(weather_data)
            except Exception as e:
                # Add error response for this location
                results.append({
                    "location": location,
                    "region": "Unknown",
                    "country": "Unknown",
                    "temperature": "N/A",
                    "condition": "Information not available",
                    "humidity": "N/A",
                    "wind": "N/A",
                    "message": f"The location '{location}' could not be found or another error occurred: {str(e)}"
                })
        
        return results

    @override
    async def run_async(
            self, *, args: dict[str, Any], tool_context: ToolContext
    ) -> Any:
        """Runs the weather tool with the given arguments and context.

        Args:
            args: The LLM-filled arguments. The args should include a "locations" key
                 with either a string or a list of location strings.
            tool_context: The context of the tool.

        Returns:
            A list of dictionaries containing weather information or error messages.
        """
        print("Running WeatherTool with args:", args)

        # Handle both string and list inputs by normalizing to a list
        locations = args["locations"]
        if isinstance(locations, str):
            locations = [locations]
            print(f"Getting weather for location: {locations[0]}")
        else:
            print(f"Getting weather for {len(locations)} locations: {', '.join(locations)}")

        return await self.get_weather(locations=locations)

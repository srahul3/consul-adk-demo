# =============================================================================
# agents/weather_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines a WeatherAgent that provides real-time weather information
# for multiple locations worldwide.
# =============================================================================


# -----------------------------------------------------------------------------
# 📦 Built-in & External Library Imports
# -----------------------------------------------------------------------------

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

from agents.weather_agent.tools.weather_tool import WeatherTool
from utilities.consul_agent import ConsulEnabledAIAgent

# Load environment variables (like API keys) from a `.env` file
load_dotenv()


# -----------------------------------------------------------------------------
# 🌤️ WeatherAgent: AI agent that provides weather information for multiple locations
# -----------------------------------------------------------------------------

class WeatherAgent(ConsulEnabledAIAgent):
    """
    A specialized AI agent for providing real-time weather information.

    This agent helps users get weather data for:
    - Single or multiple locations
    - Current weather conditions
    - Location-based weather recommendations
    - Weather-based travel suggestions
    """

    def build_agent(self) -> LlmAgent:
        """
        Creates and configures a Gemini agent specialized in weather information.

        Returns:
            LlmAgent: A configured agent object from Google's ADK
        """
        # Configure the weather tool
        weather_tool = WeatherTool(
            name="WeatherTool",
            description="Gets the realtime weather for one or more locations"
        )

        self._append_user_defined_tool(FunctionTool(weather_tool.get_weather))
        self._set_orchestrator(False)

        return LlmAgent(
            model="gemini-1.5-flash-latest",
            name="weather_agent",
            description="Provides weather information for multiple locations",
            instruction=self._get_agent_instruction(),
            tools=self._get_llm_tools()
        )

    def _get_agent_instruction(self) -> str:
        """
        Returns the detailed instruction set for the weather agent.

        Returns:
            str: The instruction text for the agent
        """
        return """You are a helpful weather assistant specialized in providing accurate, real-time weather information worldwide.

🌍 CORE CAPABILITIES:
- Real-time weather data for any location globally
- Multi-location weather comparisons
- Weather-based location recommendations
- Current conditions and forecasts

📍 RESPONSE GUIDELINES:

LOCATION HANDLING:
- Always extract 'locations' parameter as a list (even for single locations)
- Use the WeatherTool for all weather queries
- Support city names, regions, and specific addresses

MULTI-LOCATION REQUESTS:
- Organize responses with clear headings for each location
- Present information in a structured, easy-to-read format
- Compare conditions when multiple locations are requested

RECOMMENDATION REQUESTS:
- When users ask for locations with specific weather conditions:
  1. First get weather for several cities in the requested region
  2. Analyze the data against user criteria
  3. Recommend locations that match the desired conditions
  4. Explain why each recommendation fits their needs

💡 RESPONSE STYLE:
- Be friendly, informative, and concise
- Use clear formatting with headings and bullet points
- Include relevant details like temperature, conditions, and any notable weather patterns
- Provide context when weather conditions are unusual or noteworthy

Your goal is to be the most reliable and user-friendly source for weather information and weather-based recommendations."""

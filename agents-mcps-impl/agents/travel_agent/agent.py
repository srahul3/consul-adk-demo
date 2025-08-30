# =============================================================================
# agents/travel_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# This file defines a TravelAgent that specializes in providing information about cities
# across countries, continents, and united regions.
# =============================================================================


# -----------------------------------------------------------------------------
# 📦 Built-in & External Library Imports
# -----------------------------------------------------------------------------

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

from agents.travel_agent.tools.destinations_tool import DestinationsTool
from utilities.consul_agent import ConsulEnabledAIAgent

# Load environment variables (like API keys) from a `.env` file
load_dotenv()


# -----------------------------------------------------------------------------
# 🧳 TravelAgent: AI agent that helps explore cities around the world
# -----------------------------------------------------------------------------

class TravelAgent(ConsulEnabledAIAgent):
    """
    A specialized AI agent for providing comprehensive travel and city information.

    This agent helps users explore cities worldwide by providing information about:
    - Cities in specific countries
    - Countries within continents or regions
    - United regions and their member countries
    - Currency exchange rates between regions
    """

    def build_agent(self) -> LlmAgent:
        """
        Creates and configures a Gemini agent specialized in travel and city information.

        Returns:
            LlmAgent: A configured agent object from Google's ADK
        """
        # Configure the destinations tool
        destinations_tool = DestinationsTool(
            name="DestinationsTool",
            description="Lists cities in countries, continents, or united regions with detailed information"
        )
        self._clear_user_defined_tool()
        self._append_user_defined_tool(FunctionTool(destinations_tool.list_cities_capped))
        self._set_orchestrator(False)

        return LlmAgent(
            model="gemini-2.5-flash-latest",  # Gemini model version
            name="travel_agent",  # Name of the agent
            description="Geographic expert that lists and provides information about cities worldwide",  # Description for metadata
            instruction="""You are a city information specialist focused on listing cities across different geographical regions.
            
            Your primary responsibility is to help users explore cities in:
            - Specific countries (e.g., "List cities in Japan")
            - Continents or major regions (e.g., "What are the countries in Europe?")
            - United regions (e.g., "Tell me about Scandinavian countries")
            
            When asked about a location, always use the DestinationsTool to retrieve accurate information. 
            Present the list of cities in a clear, organized manner:
            
            1. For continents/regions: List the countries they contain
            2. For countries: List major cities and destinations in a numbered or bulleted format
            3. For cities: Provide basic information about the city when available
            4. For the given two region, provide the currency exchange rate.
            
            If a user asks for recommendations about which cities to visit, you may provide a brief overview
            of the most notable cities in a region, but keep your focus on listing cities rather than detailed
            travel planning.
            
            Be precise, organized, and helpful - your primary goal is to provide comprehensive lists of cities
            when users ask about different regions of the world.
            """,
            tools=self._get_llm_tools(),
        )
# =============================================================================
# agents/cities_agent/__main__.py
# =============================================================================
# Purpose:
# This is the main script that starts the CitiesExplorer server, specializing in
# listing cities across different geographic regions.
# =============================================================================
from agents.travel_agent.agent import TravelAgent
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# Your custom A2A server class
from server.server import A2AServer

# Models for describing agent capabilities and metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# CLI and logging support
import click           # For creating a clean command-line interface
import logging         # For logging errors and info to the console
import os

from utilities.consul_discovery import ConsulDiscoveryClient

# -----------------------------------------------------------------------------
# Setup logging to print info to the console
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Main Entry Function – Configurable via CLI
# -----------------------------------------------------------------------------

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10005, help="Port number for the server")
def main(host, port):
    """
    This function sets up everything needed to start the CitiesExplorer server.
    You can run it via: `python -m agents.cities_agent --host 0.0.0.0 --port 12345`
    """
    agent_id = os.environ.get("SERVICE_NAME")  # Unique identifier for this agent
    # Define what this agent can do – in this case, it does NOT support streaming
    capabilities = AgentCapabilities(streaming=False)

    private_ip = os.environ.get("PRIVATE_IP", default=host)

    # Define the skills this agent offers (used in directories and UIs)
    skill_countries = AgentSkill(
        id="country_listing",
        name="Country Listing",
        description="Lists countries within continents or united regions",
        tags=["geography", "countries", "regions", "continents"],
        examples=["What countries are in Europe?", "List Scandinavian countries", "Tell me about the Balkans"]
    )

    skill_cities = AgentSkill(
        id="city_listing",
        name="City Listing",
        description="Lists cities within countries and provides basic information",
        tags=["geography", "cities", "urban centers", "destinations"],
        examples=["What cities are in Japan?", "List major cities in Italy", "Tell me about cities in Australia"]
    )

    skill_regions = AgentSkill(
        id="region_information",
        name="Region Information",
        description="Provides information about unified geographic regions",
        tags=["geography", "regions", "united regions", "territories"],
        examples=["What is the Benelux region?", "Tell me about Southeast Asia", "What countries are in the Caribbean?"]
    )

    skill_currency_exchange_rate = AgentSkill(
        id="currency_exchange",
        name="Currency Exchange",
        description="Provides real-time currency exchange rates and conversion between different currencies",
        tags=["currency", "exchange rate", "forex", "money", "conversion"],
        examples=["What's the exchange rate between USD and EUR?",
                 "Convert 100 USD to JPY",
                 "Show me the current exchange rate for British Pounds"]
    )

    # if env USE_DNS is set to True, use DNS-based service discovery
    if os.environ.get("USE_DNS") == "TRUE":
        # Use DNS-based service discovery
        url=f"http://{agent_id}.service.consul:{port}/" # Use consul service discovery
    else:
        url=f"http://{private_ip}:{port}/"  # The public URL where this agent lives

    # Create an agent card describing this agent's identity and metadata
    agent_card = AgentCard(
        id = agent_id,
        name="TravelAgent",
        description="This agent specializes in listing cities and providing information about geographic regions worldwide",
        url=url,
        version="1.0.0",
        defaultInputModes=TravelAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=TravelAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill_countries, skill_cities, skill_regions, skill_currency_exchange_rate]
    )

    # Start listening for tasks
    discovery_client = ConsulDiscoveryClient(id=agent_id, application_host=private_ip, application_port=port)
    agent = TravelAgent(discovery_client)

    # Start the A2A server with:
    # - the given host/port
    # - this agent's metadata
    # - a task manager that runs the cities agent
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=agent.getTaskManager()
    )



    # Start listening for tasks regardless of registration outcome
    server.start()


# -----------------------------------------------------------------------------
# This runs only when executing the script directly via `python -m`
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# =============================================================================
# agents/weather_agent/__main__.py
# =============================================================================
# Purpose:
# This is the main script that starts your WeatherAgent server.
# It:
# - Declares the agent's capabilities and skills
# - Sets up the A2A server with a task manager and agent
# - Starts listening on a specified host and port
#
# This script can be run directly from the command line:
#     python -m agents.weather_agent
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# Your custom A2A server class
from server.server import A2AServer

# Models for describing agent capabilities and metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Task manager and agent logic
from agents.weather_agent.agent import WeatherAgent

# CLI and logging support
import click           # For creating a clean command-line interface
import logging         # For logging errors and info to the console
import os

from utilities.consul_agent import ConsulTaskManager
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
@click.option("--port", default=10004, help="Port number for the server")
def main(host, port):
    """
    This function sets up everything needed to start the agent server.
    You can run it via: `python -m agents.weather_agent --host 0.0.0.0 --port 12345`
    """
    agent_id = os.environ.get("SERVICE_NAME")  # Unique identifier for this agent
    # Define what this agent can do – in this case, it does NOT support streaming
    capabilities = AgentCapabilities(streaming=False)

    private_ip = os.environ.get("PRIVATE_IP", default=host)

    # Define the skill this agent offers (used in directories and UIs)
    skill = AgentSkill(
        id="weather_tool",                                 # Unique skill ID
        name="Weather Tool",                          # Human-friendly name
        description="Provides realtime weather information for one or more locations",    # What the skill does
        tags=["weather", "location", "multi-location"],                                  # Optional tags for searching
        examples=["How is the weather in Bangalore and Tokyo?", "What's the current weather in Paris, London, and New York?"]  # Example queries
    )

    # if env USE_DNS is set to True, use DNS-based service discovery
    if os.environ.get("USE_DNS") == "TRUE":
        # Use DNS-based service discovery
        url=f"http://{agent_id}.service.consul:{port}/" # Use consul service discovery
    else:
        url=f"http://{private_ip}:{port}/"  # The public URL where this agent lives

    # Create an agent card describing this agent's identity and metadata
    agent_card = AgentCard(
        id = agent_id,                                    # Unique identifier for this agent
        name="WeatherAgent",                               # Name of the agent
        description="This agent provides current weather information for multiple locations",  # Description
        url=url,
        version="1.0.0",                                    # Version number
        defaultInputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES,  # Input types this agent supports
        defaultOutputModes=WeatherAgent.SUPPORTED_CONTENT_TYPES, # Output types it produces
        capabilities=capabilities,                          # Supported features (e.g., streaming)
        skills=[skill]                                      # List of skills it supports
    )

    discovery_client = ConsulDiscoveryClient(id=agent_id, application_host=private_ip,
                                      application_port=port)  # Uses default Consul discovery

    # 3) Instantiate the agent and its TaskManager
    agent = WeatherAgent(discovery=discovery_client)

    # Start the A2A server with:
    # - the given host/port
    # - this agent's metadata
    # - a task manager that runs the weather agent
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=agent.getTaskManager()
    )

    server.start()


# -----------------------------------------------------------------------------
# This runs only when executing the script directly via `python -m`
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

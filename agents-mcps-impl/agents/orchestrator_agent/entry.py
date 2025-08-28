# =============================================================================
# agents/host_agent/entry.py
# =============================================================================
# 🎯 Purpose:
# Boots up the OrchestratorAgent as an A2A server.
# Uses the shared registry file to discover all child agents,
# then delegates routing to the OrchestratorAgent via A2A JSON-RPC.

# run `SERVICE_NAME="host-ai" python -m agents.host_pipeline_agent.entry --host localhost --port 10010`
# =============================================================================

import logging                              # Standard Python logging module
import os
import click                                # Library for building CLI interfaces

from agents.orchestrator_agent.OrchestratorAgent import OrchestratorAgent
# Utility for discovering remote A2A agents from a local registry
# Shared A2A server implementation (Starlette + JSON-RPC)
from server.server import A2AServer
# Pydantic models for defining agent metadata (AgentCard, etc.)
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from utilities.consul_discovery import ConsulDiscoveryClient

# Configure root logger to show INFO-level messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host", default="localhost",
    help="Host to bind the OrchestratorAgent server to"
)
@click.option(
    "--port", default=10010,
    help="Port for the OrchestratorAgent server"
)
@click.option(
    "--registry",
    default=None,
    help=(
        "Path to JSON file listing child-agent URLs. "
        "Defaults to utilities/agent_registry.json"
    )
)
def main(host: str, port: int, registry: str):
    """
    Entry point to start the OrchestratorAgent A2A server.

    Steps performed:
    1. Load child-agent URLs from the registry JSON file.
    2. Fetch each agent's metadata via `/.well-known/agent.json`.
    3. Instantiate an OrchestratorAgent with discovered AgentCards.
    4. Wrap it in an OrchestratorTaskManager for JSON-RPC handling.
    5. Launch the A2AServer to listen for incoming tasks.
    """

    agent_id = os.environ.get("SERVICE_NAME")  # Unique identifier for this agent
    private_ip = os.environ.get("PRIVATE_IP", default=host)

    # 2) Define the OrchestratorAgent's own metadata for discovery
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="orchestrate",                          # Unique skill identifier
        name="Orchestrate Tasks",                  # Human-friendly name
        description=(
            "Create plan to orchestrate tasks across discovered child agents."
            "Delegates tasks to child agents based on their capabilities."
        ),
        # tags=["routing", "orchestration"],       # Keywords to aid discovery
        tags = ["orchestration"],
        examples=[]
    )
    orchestrator_card = AgentCard(
        id = agent_id,                     # Unique ID for this agent
        name="OrchestratorAgent",
        description="Delegates tasks to discovered child agents",
        url=f"http://{host}:{port}/",             # Public endpoint
        version="1.0.0",
        defaultInputModes=["text"],                # Supported input modes
        defaultOutputModes=["text"],               # Supported output modes
        capabilities=capabilities,
        skills=[skill]
    )

    discovery_client = ConsulDiscoveryClient(id=agent_id, application_host=private_ip,
                                      application_port=port)  # Uses default Consul discovery

    # 3) Instantiate the ConsulPipelineAgent (concrete implementation) instead of OrchestratorAgent
    orchestrator = OrchestratorAgent(discovery=discovery_client)

    # 4) Create and start the A2A server
    server = A2AServer(
        host=host,
        port=port,
        agent_card=orchestrator_card,
        task_manager=orchestrator.getTaskManager()
    )

    server.start()

if __name__ == "__main__":
    main()

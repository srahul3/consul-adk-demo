# File server.py
import logging

import httpx

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

import click                                # Library for building CLI interfaces

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Currency MCP Server 💵")

@mcp.tool()
def get_exchange_rate(
    currency_from: str = 'USD',
    currency_to: str = 'EUR',
    currency_date: str = 'latest',
):
    """Use this to get current exchange rate.

    Args:
        currency_from: The currency to convert from (e.g., "USD").
        currency_to: The currency to convert to (e.g., "EUR").
        currency_date: The date for the exchange rate or "latest". Defaults to "latest".

    Returns:
        A dictionary containing the exchange rate data, or an error message if the request fails.
    """
    logger.info(f"--- 🛠️ Tool: get_exchange_rate called for converting {currency_from} to {currency_to} ---")
    try:
        response = httpx.get(
            f'https://api.frankfurter.app/{currency_date}',
            params={'from': currency_from, 'to': currency_to},
        )
        response.raise_for_status()

        data = response.json()
        if 'rates' not in data:
            return {'error': 'Invalid API response format.'}
        logger.info(f'✅ API response: {data}')
        return data
    except httpx.HTTPError as e:
        return {'error': f'API request failed: {e}'}
    except ValueError:
        return {'error': 'Invalid JSON response from API.'}

# Set up the Server-Sent Events (SSE) transport for real-time communication
sse = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> None:
    _server = mcp._mcp_server
    async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
    ) as (reader, writer):
        await _server.run(reader, writer, _server.create_initialization_options())

async def health(request: Request):
    return JSONResponse({"status": "ok"}, status_code=200)

app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/health", endpoint=health),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

@click.command()
@click.option(
    "--host", default="0.0.0.0",
    help="Host to bind the MCP server to"
)
@click.option(
    "--port", default=5001,
    help="Port for the MCP server"
)
def main(host: str, port: int):
    """
    Entry point to start the Exchange rate MCP server.
    """
    uvicorn.run(app, host=host, port=port)
    # -----------------------------------------------------------------------------
    print("Calculator MCP server is running on http://{}:{}".format(host, port))

if __name__ == "__main__":
    main()
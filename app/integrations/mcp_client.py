"""
MCP Client for calling Model Context Protocol tools
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for calling MCP server tools"""

    def __init__(self):
        self.mcp_config_path = Path("c:/Users/Jochen/AppData/Roaming/Kilo-Code/MCP/proplanta-psm-scraper/package.json")

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call an MCP tool via stdio"""

        try:
            # Import the MCP server module
            import sys
            import subprocess
            from pathlib import Path

            # Path to the MCP server executable
            server_path = Path("c:/Users/Jochen/AppData/Roaming/Kilo-Code/MCP/proplanta-psm-scraper/build/index.js")

            if not server_path.exists():
                logger.error(f"MCP server executable not found: {server_path}")
                return None

            # Prepare the MCP call message
            call_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            # Start the MCP server process
            process = subprocess.Popen(
                ["node", str(server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )

            # Send the call message
            process.stdin.write(json.dumps(call_message) + "\n")
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    logger.info(f"MCP tool call successful: {tool_name}")
                    return response.get("result")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse MCP response: {e}")
                    return None

            # Check for errors
            error_output = process.stderr.read()
            if error_output:
                logger.error(f"MCP server error: {error_output}")

            process.terminate()
            return None

        except Exception as e:
            logger.error(f"Failed to call MCP tool {tool_name}: {e}")
            return None


# Global MCP client instance
mcp_client = MCPClient()


async def call_mcp_tool(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convenience function to call MCP tools"""
    return await mcp_client.call_tool(server_name, tool_name, arguments)
"""
MCP Client for calling Model Context Protocol tools
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Pfad zum MCP-Server-Executable wird ausschliesslich aus Env-Var gelesen.
# Kein Benutzerpfad im Code — SC-SECRETS-003.
_MCP_SERVER_PATH: Optional[Path] = (
    Path(os.environ["MCP_PROPLANTA_SERVER_PATH"])
    if "MCP_PROPLANTA_SERVER_PATH" in os.environ
    else None
)


class MCPClient:
    """Client for calling MCP server tools via stdio (JSON-RPC 2.0)."""

    def __init__(self, server_path: Optional[Path] = None) -> None:
        self._server_path = server_path or _MCP_SERVER_PATH

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Call an MCP tool via stdio."""
        if self._server_path is None:
            logger.warning("MCP_PROPLANTA_SERVER_PATH not set — MCP calls disabled")
            return None

        server_path = self._server_path.resolve()
        if not server_path.exists():
            logger.error("MCP server executable not found: %s", server_path)
            return None

        call_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            process = subprocess.Popen(  # noqa: S603 — args list, no shell expansion
                ["node", str(server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                shell=False,
            )

            process.stdin.write(json.dumps(call_message) + "\n")
            process.stdin.flush()

            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    logger.info("MCP tool call successful: %s", tool_name)
                    return response.get("result")
                except json.JSONDecodeError as exc:
                    logger.error("Failed to parse MCP response: %s", exc)
                    return None

            error_output = process.stderr.read()
            if error_output:
                logger.error("MCP server error: %s", error_output[:500])

            process.terminate()
            return None

        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to call MCP tool %s: %s", tool_name, exc)
            return None


mcp_client = MCPClient()


async def call_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Convenience function to call MCP tools."""
    return await mcp_client.call_tool(server_name, tool_name, arguments)

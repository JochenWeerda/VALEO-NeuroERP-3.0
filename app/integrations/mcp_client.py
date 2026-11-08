"""
MCP Client for calling Model Context Protocol tools
"""

import asyncio
import json
import logging
import math
import os
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

    def __init__(self, server_path: Optional[Path] = None, *, timeout: float = 30.0) -> None:
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("MCP timeout must be finite and positive")
        self._server_path = server_path or _MCP_SERVER_PATH
        self._timeout = timeout

    @staticmethod
    async def _discard_output(reader: asyncio.StreamReader) -> None:
        while await reader.read(65536):
            pass

    @classmethod
    async def _close_process(cls, process: asyncio.subprocess.Process) -> None:
        # Drain stdout during shutdown as a full pipe can otherwise block wait().
        drain = asyncio.create_task(cls._discard_output(process.stdout))
        process.stdin.close()
        try:
            if process.returncode is None:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass
            try:
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                await process.wait()
        finally:
            await drain

    async def _exchange(self, server_path: Path, call_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        process = await asyncio.create_subprocess_exec(
            "node", str(server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            # MCP stderr is optional diagnostics; ignore it rather than expose
            # credentials/applicant data or deadlock on an unread error pipe.
            stderr=asyncio.subprocess.DEVNULL,
            limit=1024 * 1024,
        )
        try:
            async with asyncio.timeout(self._timeout):
                process.stdin.write((json.dumps(call_message) + "\n").encode("utf-8"))
                await process.stdin.drain()
                while response_line := await process.stdout.readline():
                    response = json.loads(response_line.decode("utf-8"))
                    if not isinstance(response, dict) or response.get("jsonrpc") != "2.0":
                        raise ValueError("Invalid MCP response envelope")
                    if "id" not in response and isinstance(response.get("method"), str):
                        continue  # Notifications may precede the response.
                    if type(response.get("id")) is not int or response["id"] != call_message["id"]:
                        raise ValueError("Unexpected MCP response ID")
                    if "error" in response or not isinstance(response.get("result"), dict):
                        raise ValueError("MCP call did not return a result object")
                    return response["result"]
                return None
        finally:
            cleanup = asyncio.create_task(self._close_process(process))
            try:
                await asyncio.shield(cleanup)
            except asyncio.CancelledError:
                await cleanup
                raise

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
            return await self._exchange(server_path, call_message)
        except asyncio.TimeoutError:
            logger.error("MCP tool call timed out")
            return None
        except Exception:  # noqa: BLE001 — retain the existing optional-result boundary
            logger.error("MCP tool call failed")
            return None


mcp_client = MCPClient()


async def call_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Convenience function to call MCP tools."""
    return await mcp_client.call_tool(server_name, tool_name, arguments)

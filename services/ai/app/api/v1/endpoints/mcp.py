"""
MCP HTTP Endpoint
REST API für MCP-Funktionalität
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.mcp.server import mcp_server

router = APIRouter()


class ToolCallRequest(BaseModel):
    """Request to call an MCP tool"""
    tool_name: str
    parameters: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """Response from MCP tool call"""
    result: Dict[str, Any]
    status: str


@router.get("/tools")
async def list_tools():
    """Liste aller verfügbaren MCP Tools"""
    return {
        "tools": mcp_server.list_tools()
    }


@router.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """Ruft MCP Tool auf"""
    try:
        result = await mcp_server.call_tool(
            request.tool_name,
            **request.parameters
        )
        return ToolCallResponse(
            result=result,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def list_resources():
    """Liste aller verfügbaren MCP Resources"""
    return {
        "resources": mcp_server.list_resources()
    }


@router.get("/resources/{uri:path}")
async def get_resource(uri: str):
    """Holt Resource-Content"""
    try:
        content = await mcp_server.get_resource(f"resource://{uri}")
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/prompts")
async def list_prompts():
    """Liste aller verfügbaren MCP Prompts"""
    return {
        "prompts": mcp_server.list_prompts()
    }


@router.post("/prompts/render")
async def render_prompt(
    prompt_name: str,
    variables: Dict[str, str]
):
    """Rendert Prompt-Template mit Variablen"""
    try:
        rendered = mcp_server.render_prompt(prompt_name, **variables)
        return {"rendered": rendered}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


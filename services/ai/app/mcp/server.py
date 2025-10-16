"""
MCP (Model Context Protocol) Server
Provides tools, resources, and prompts for AI workflows
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable


@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str
    content_provider: callable


@dataclass
class MCPPrompt:
    """MCP Prompt template"""
    name: str
    description: str
    template: str
    variables: List[str]


class MCPServer:
    """
    MCP Server für AI-Workflows
    
    Stellt bereit:
    - Tools: Funktionen die der AI-Agent aufrufen kann
    - Resources: Daten/Dokumente für Kontext
    - Prompts: Vorkonfigurierte Templates
    """
    
    def __init__(self):
        self.tools: List[MCPTool] = []
        self.resources: List[MCPResource] = []
        self.prompts: List[MCPPrompt] = []
        self._register_built_in_tools()
        self._register_built_in_resources()
        self._register_built_in_prompts()
    
    def _register_built_in_tools(self):
        """Register built-in tools"""
        
        # Tool: Query Database
        self.tools.append(MCPTool(
            name="query_database",
            description="Query the ERP database for information",
            parameters={
                "query": {"type": "string", "description": "SQL query or natural language"},
                "domain": {"type": "string", "description": "Domain to query"}
            },
            handler=self._handle_database_query
        ))
        
        # Tool: Search Documents
        self.tools.append(MCPTool(
            name="search_documents",
            description="Search through indexed documents",
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "description": "Number of results"}
            },
            handler=self._handle_document_search
        ))
        
        # Tool: Create Order
        self.tools.append(MCPTool(
            name="create_procurement_order",
            description="Create a procurement order based on analysis",
            parameters={
                "article": {"type": "string"},
                "quantity": {"type": "number"},
                "supplier": {"type": "string"},
                "reason": {"type": "string"}
            },
            handler=self._handle_create_order
        ))
    
    def _register_built_in_resources(self):
        """Register built-in resources"""
        
        self.resources.append(MCPResource(
            uri="resource://policies/procurement",
            name="Procurement Policies",
            description="All procurement policies and rules",
            mime_type="application/json",
            content_provider=self._get_procurement_policies
        ))
        
        self.resources.append(MCPResource(
            uri="resource://templates/invoice",
            name="Invoice Templates",
            description="Standard invoice templates and examples",
            mime_type="text/plain",
            content_provider=self._get_invoice_templates
        ))
    
    def _register_built_in_prompts(self):
        """Register built-in prompts"""
        
        self.prompts.append(MCPPrompt(
            name="procurement_advisor",
            description="Analyzes inventory and suggests procurement",
            template="""Du bist ein Einkaufsberater für landwirtschaftliche Betriebe.

Analysiere folgende Daten:
- Lagerbestand: {inventory}
- Feldbuch-Planung: {field_plan}
- Aktuelle Saison: {season}

Erstelle konkrete Bestellvorschläge mit Begründung.""",
            variables=["inventory", "field_plan", "season"]
        ))
        
        self.prompts.append(MCPPrompt(
            name="compliance_assistant",
            description="Checks documents for compliance issues",
            template="""Du bist ein Compliance-Experte für EU-Agrar-Verordnungen.

Prüfe folgendes Dokument auf Compliance:
Dokumenttyp: {doc_type}
Inhalt: {content}

Achte besonders auf:
- EUDR (Entwaldung)
- Cross-Compliance
- Bio-Zertifizierung
- Pflanzenschutzmittel-Zulassungen

Gib konkrete Warnungen oder OK zurück.""",
            variables=["doc_type", "content"]
        ))
    
    # Tool Handlers
    async def _handle_database_query(self, **params) -> Dict[str, Any]:
        """Handle database query tool"""
        logger.info(f"Database query: {params}")
        # Mock - später echte DB-Abfrage
        return {"results": [], "count": 0}
    
    async def _handle_document_search(self, **params) -> Dict[str, Any]:
        """Handle document search tool"""
        logger.info(f"Document search: {params}")
        return {"documents": [], "count": 0}
    
    async def _handle_create_order(self, **params) -> Dict[str, Any]:
        """Handle create order tool"""
        logger.info(f"Create order: {params}")
        return {"order_id": "PO-2025-001", "status": "created"}
    
    # Resource Providers
    async def _get_procurement_policies(self) -> str:
        """Get procurement policies"""
        return '{"policies": []}'
    
    async def _get_invoice_templates(self) -> str:
        """Get invoice templates"""
        return "Invoice template..."
    
    # Public API
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools
        ]
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources"""
        return [
            {
                "uri": res.uri,
                "name": res.name,
                "description": res.description,
                "mime_type": res.mime_type
            }
            for res in self.resources
        ]
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts"""
        return [
            {
                "name": prompt.name,
                "description": prompt.description,
                "variables": prompt.variables
            }
            for prompt in self.prompts
        ]
    
    async def call_tool(self, tool_name: str, **params) -> Dict[str, Any]:
        """Call a tool by name"""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        return await tool.handler(**params)
    
    async def get_resource(self, uri: str) -> str:
        """Get resource content by URI"""
        resource = next((r for r in self.resources if r.uri == uri), None)
        if not resource:
            raise ValueError(f"Resource '{uri}' not found")
        return await resource.content_provider()
    
    def render_prompt(self, prompt_name: str, **variables) -> str:
        """Render prompt with variables"""
        prompt = next((p for p in self.prompts if p.name == prompt_name), None)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        return prompt.template.format(**variables)


# Global MCP server instance
mcp_server = MCPServer()


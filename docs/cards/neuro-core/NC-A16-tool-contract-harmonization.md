# NC-A16 - Tool Contract Harmonization

**Lane:** NC-A
**Prioritaet:** P2
**Status:** umgesetzt

## Umsetzung

- `request_payload_mode` als neues Contract-Feld in `MCPToolContract`
- Executor nutzt Contract-Metadaten fuer spezialisierte Body-Bildung
- Wave-31-Tool-Registry markiert die betroffenen Policy-, Approval- und DQ-Tools explizit
- gezielte MCP-/Broker-/Execution-Tests decken die Harmonisierung ab

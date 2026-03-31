# NC-A14 - Broker Tenant Overrides

**Lane:** NC-A
**Prioritaet:** P2
**Status:** umgesetzt

## Umsetzung

- Broker propagiert `tenant_policy_overrides` und `policy_context` jetzt in Verification und Tool-Execution
- Step-Level-Kontexte haben Vorrang vor allgemeinen Request-/Plan-Kontexten
- Tests decken Propagation bis an den Tool-Execution-Service ab

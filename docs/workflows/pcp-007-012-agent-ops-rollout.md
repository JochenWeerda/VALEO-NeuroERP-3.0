# PCP-007 bis PCP-012 Agent Ops Rollout

## Ziel

Die verbleibenden Paperclip-inspirierten Agent-Ops-Folgeslices auf der bestehenden NeuroASSIST-Runtime schliessen.

## Umgesetzter Scope

- Intervention Console fuer `pause`, `resume`, `escalate`, `override`, `close`
- zentrales Agent-Ops-Dashboard
- exportierbare Agent-Templates ohne Secrets
- Skill-Pack-Manifest pro Rolle/Capability
- Mobile-Ops-Read-Model fuer kompakte Freigabe- und Eskalationssicht
- Plugin-Boundary-Review als explizite Architekturgrenze

## Technischer Pfad

- Runtime: `app/agents/agent_ops.py`
- Service-Integration: `app/agents/neuroassist_service.py`
- API: `app/api/v1/endpoints/agents.py`
- Admin-UI: `packages/frontend-web/src/pages/admin/agenten-integration.tsx`

## Abnahme

- neue Ops-Endpunkte liefern Dashboard, Interventionen, Templates, Skill-Packs, Mobile-Overview und Boundary-Review
- Admin-Seite surfact alle neuen Bereiche
- Regressionen fuer Service, API und UI laufen gruen

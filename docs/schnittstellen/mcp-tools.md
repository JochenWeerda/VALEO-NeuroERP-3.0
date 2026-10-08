---
title: MCP-Tool-Referenz
type: reference
audience: [ki-agent, integrator, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# MCP-Tool-Referenz

> Automatisch generiert aus `config/mcp_erp_tools.yaml` via `python scripts/generate_mcp_tool_reference.py`. **Nicht manuell bearbeiten.**

Registry `MCP-ERP-TOOLS-001` (Schema 1.0) — 35 Tools in 14 Domaenen.

## Uebersicht

| Tool | Domaene | Scope | Idempotent | Risiko | Human-Approval |
|---|---|---|---|---|---|
| `agent.proposal.list` | agent | `agent:read` | ja | niedrig | nein |
| `agrar.contract.get` | agrar | `agrar:read` | ja | niedrig | nein |
| `agrar.feed_analysis.transition` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.feeding.actual_measure` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.feeding.configure_threshold` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.feeding.supply_handoff` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.ration.transition` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.weighing_ticket.list` | agrar | `agrar:read` | ja | niedrig | nein |
| `compliance.gate.status` | compliance | `compliance:read` | ja | niedrig | nein |
| `crm.activity.create` | crm | `crm:write` | ja | mittel | nein |
| `crm.contact.log` | crm | `crm:write` | ja | mittel | nein |
| `crm.customer.open` | crm | `crm:read` | ja | niedrig | nein |
| `crm.customer.search` | crm | `crm:read` | ja | niedrig | nein |
| `crm.customer.summary360` | crm | `crm:read` | ja | niedrig | nein |
| `crm.lead.qualify` | crm | `crm:write` | ja | mittel | nein |
| `dms.document.search` | nachweisraum | `nachweisraum:read` | ja | niedrig | nein |
| `dms.gobd.export_status` | nachweisraum | `nachweisraum:read` | ja | niedrig | nein |
| `einkauf.angebot.bestellen` | einkauf | `einkauf:write` | ja | mittel | nein |
| `einkauf.anlieferavis.wareneingang` | einkauf | `einkauf:write` | ja | mittel | nein |
| `einkauf.bestellung.list` | einkauf | `einkauf:read` | ja | niedrig | nein |
| `einkauf.bestellung.versenden` | einkauf | `einkauf:write` | ja | mittel | nein |
| `fibu.dunning.status` | finance | `finance:read` | ja | niedrig | nein |
| `fibu.open_items.list` | finance | `finance:read` | ja | niedrig | nein |
| `lager.bestand.get` | lager | `lager:read` | ja | niedrig | nein |
| `lager.inventur.status` | lager | `lager:read` | ja | niedrig | nein |
| `lager.stock_movement.stornieren` | lager | `lager:write` | ja | mittel | nein |
| `mobile.sync.process_pending` | mobile | `mobile:write` | ja | mittel | nein |
| `planung.calendar.reproject` | planung | `planung:write` | ja | mittel | nein |
| `produktion.control.sync` | produktion | `ops:write` | ja | mittel | nein |
| `qualitaet.reklamation.abschliessen` | qualitaet | `quality:write` | ja | mittel | nein |
| `sales.invoice.post` | sales | `sales:write` | ja | hoch | ja |
| `sales.invoice.propose` | sales | `sales:write` | nein | hoch | ja |
| `sales.order.status` | sales | `sales:read` | ja | niedrig | nein |
| `wms.cell.status` | inventory | `inventory:read` | ja | niedrig | nein |
| `wms.lot.trace` | inventory | `inventory:read` | ja | niedrig | nein |

## Domaene: agent

### `agent.proposal.list` — Agent-Proposals auflisten

Listet Agent-Proposals des Authentifizierungs-Mandanten (Supervisor-Scope agent:read). Nur Lesen; keine Approve/Reject-Aktion.

- **Scope:** `agent:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "nullable": true,
      "enum": [
        "pending",
        "approved",
        "rejected",
        "expired"
      ]
    },
    "limit": {
      "type": "integer",
      "default": 20
    }
  },
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array"
    },
    "count": {
      "type": "integer"
    }
  }
}
```

## Domaene: agrar

### `agrar.contract.get` — Agrar-Kontrakt abrufen

Gibt Agrar-Kontrakt (Menge, Preis, Status) im Authentifizierungs-Mandanten zurueck. parameters.kontrakt_id (UUID oder Vertragsnummer). Kein tenant_id-Parameter. Scope agrar:read; nur Lesen.

- **Scope:** `agrar:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kontrakt_id": {
      "type": "string",
      "description": "Kontrakt-UUID oder Vertragsnummer"
    }
  },
  "required": [
    "kontrakt_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kontrakt_id": {
      "type": "string"
    },
    "ware": {
      "type": "string",
      "nullable": true
    },
    "menge_t": {
      "type": "number"
    },
    "preis_eur": {
      "type": "number",
      "nullable": true
    },
    "status": {
      "type": "string"
    }
  }
}
```

### `agrar.feed_analysis.transition` — Futteranalyse freigeben oder zurueckweisen

Wechselt den Status einer Grundfutteranalyse (Maske futtermittel/analyse:release|reject). parameters.analysis_id, action_key (release|reject), reason. Default dryRun; execute erfordert idempotency_key. Scope agrar:write.

- **Scope:** `agrar:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "analysis_id": {
      "type": "string"
    },
    "action_key": {
      "type": "string",
      "enum": [
        "release",
        "reject"
      ]
    },
    "reason": {
      "type": "string"
    }
  },
  "required": [
    "analysis_id",
    "action_key",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "analysis_id": {
      "type": "string"
    },
    "from_status": {
      "type": "string"
    },
    "to_status": {
      "type": "string"
    },
    "revision": {
      "type": "integer"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `agrar.feeding.actual_measure` — Massnahme aus Futter-Abweichung

Legt eine Massnahme zu einem Abweichungsbefund an (Maske agrar/feeding-actuals:create_measure). parameters.actual_component_id, title, reason, due_date. Default dryRun; execute erfordert idempotency_key. Scope agrar:write.

- **Scope:** `agrar:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "actual_component_id": {
      "type": "string"
    },
    "title": {
      "type": "string"
    },
    "reason": {
      "type": "string"
    },
    "due_date": {
      "type": "string",
      "format": "date"
    },
    "owner_subject": {
      "type": "string",
      "nullable": true
    }
  },
  "required": [
    "actual_component_id",
    "title",
    "reason",
    "due_date"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "measure_id": {
      "type": "string"
    },
    "actual_component_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `agrar.feeding.configure_threshold` — Abweichungsschwellen konfigurieren

Legt eine neue Version der Abweichungsregeln an (Maske agrar/feeding-actuals:configure_threshold). parameters.feed_class, warning_pct, critical_pct, valid_from, reason. critical_pct > warning_pct. Default dryRun; execute erfordert idempotency_key. Scope agrar:write.

- **Scope:** `agrar:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "feed_class": {
      "type": "string",
      "enum": [
        "forage",
        "concentrate",
        "mineral",
        "additive",
        "byproduct",
        "liquid",
        "other"
      ]
    },
    "warning_pct": {
      "type": "number"
    },
    "critical_pct": {
      "type": "number"
    },
    "valid_from": {
      "type": "string",
      "format": "date"
    },
    "reason": {
      "type": "string"
    }
  },
  "required": [
    "feed_class",
    "warning_pct",
    "critical_pct",
    "valid_from",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "policy_id": {
      "type": "string"
    },
    "feed_class": {
      "type": "string"
    },
    "version": {
      "type": "integer"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `agrar.feeding.supply_handoff` — Futterbedarf an Einkauf uebergeben

Erzeugt eine Einkaufs-Uebergabe aus Planbedarf (Maske agrar/feed-readiness:create_handoff). parameters.plan_version_id, feed_id, reason (min. 10 Zeichen). Default dryRun; execute erfordert idempotency_key (wird an den Fachdienst weitergereicht). Scope agrar:write.

- **Scope:** `agrar:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "plan_version_id": {
      "type": "string"
    },
    "feed_id": {
      "type": "string"
    },
    "reason": {
      "type": "string"
    },
    "horizon_days": {
      "type": "integer",
      "default": 30
    },
    "safety_pct": {
      "type": "number",
      "default": 10
    }
  },
  "required": [
    "plan_version_id",
    "feed_id",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "handoff_id": {
      "type": "string"
    },
    "plan_version_id": {
      "type": "string"
    },
    "feed_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `agrar.ration.transition` — Rations-Lifecycle-Uebergang

Fuehrt einen Lifecycle-Schritt der aktuellen Rationsversion aus (submit_review/approve/schedule/activate/retire/archive; Maske agrar/ration:*). Gleicher Fachpfad wie RationLifecycleService.transition. schedule braucht feeding_start; retire/archive brauchen reason. Default dryRun; execute erfordert idempotency_key. Scope agrar:write. Kein FIBU/FIN-CLOSE.

- **Scope:** `agrar:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "ration_id": {
      "type": "string",
      "description": "Rations-UUID"
    },
    "action_key": {
      "type": "string",
      "enum": [
        "submit_review",
        "approve",
        "schedule",
        "activate",
        "retire",
        "archive"
      ],
      "description": "Masken-Aktionschluessel"
    },
    "reason": {
      "type": "string",
      "nullable": true,
      "description": "Begruendung; Pflicht fuer retire/archive; OVERRIDE: bei Readiness-Blockern"
    },
    "feeding_start": {
      "type": "string",
      "format": "date-time",
      "nullable": true,
      "description": "Pflicht fuer schedule"
    },
    "expected_status": {
      "type": "string",
      "nullable": true,
      "description": "Optionaler Optimistic-Lock-Status"
    }
  },
  "required": [
    "ration_id",
    "action_key"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "ration_id": {
      "type": "string"
    },
    "version_id": {
      "type": "string"
    },
    "from_status": {
      "type": "string"
    },
    "to_status": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `agrar.weighing_ticket.list` — Wiegescheine auflisten

Listet Wiegescheine des Authentifizierungs-Mandanten optional nach Kontrakt-/Partie-Referenz und Zeitraum. Scope agrar:read; nur Lesen.

- **Scope:** `agrar:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "partie_id": {
      "type": "string",
      "nullable": true,
      "description": "Filter auf contract_id oder reference_doc"
    },
    "von": {
      "type": "string",
      "format": "date",
      "nullable": true
    },
    "bis": {
      "type": "string",
      "format": "date",
      "nullable": true
    },
    "limit": {
      "type": "integer",
      "default": 50
    }
  },
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array"
    },
    "count": {
      "type": "integer"
    }
  }
}
```

## Domaene: compliance

### `compliance.gate.status` — Externe Gate-Status abfragen

Liest ehrliche Statussignale fuer ELSTER/DATEV/TSE/Auditor aus vorhandenen Domänentabellen des Authentifizierungs-Mandanten (keine Fake-Freigaben). Scope compliance:read; nur Lesen.

- **Scope:** `compliance:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "gate_typ": {
      "type": "string",
      "nullable": true,
      "enum": [
        "elster",
        "datev",
        "tse",
        "auditor",
        "all"
      ]
    }
  },
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array"
    },
    "count": {
      "type": "integer"
    }
  }
}
```

## Domaene: crm

### `crm.activity.create` — CRM-Aktivitaet anlegen

Legt eine CRM-Aktivitaet zum Kunden an (gleicher Fachpfad wie ActionRuntime create_activity). HTTP-Aufruf mit tool_name=crm.activity.create. Default dryRun; execute erfordert idempotency_key. OIDC-Token mit crm:write und tenant_id erforderlich.

- **Scope:** `crm:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string"
    },
    "betreff": {
      "type": "string"
    },
    "typ": {
      "type": "string",
      "enum": [
        "Anruf",
        "Besuch",
        "E-Mail",
        "Aufgabe",
        "Meeting",
        "Sonstiges"
      ]
    },
    "datum": {
      "type": "string",
      "format": "date",
      "nullable": true
    },
    "notiz": {
      "type": "string",
      "nullable": true
    },
    "verantwortlich": {
      "type": "string",
      "nullable": true
    }
  },
  "required": [
    "kunden_nr",
    "betreff",
    "typ"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "activity_id": {
      "type": "string"
    },
    "erfasst_am": {
      "type": "string"
    }
  }
}
```

### `crm.contact.log` — Kontaktprotokoll erfassen

Erfasst einen Kundenkontakt mit Ergebnis und Wiedervorlage. HTTP-Aufruf mit tool_name=crm.contact.log, parameters gemaess Eingabe-Schema, mode und idempotency_key. Default dryRun; execute erfordert einen stabilen Schluessel. OIDC-Token mit crm:write und tenant_id erforderlich.

- **Scope:** `crm:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string"
    },
    "kanal": {
      "type": "string",
      "enum": [
        "telefon",
        "email",
        "besuch",
        "post"
      ]
    },
    "ergebnis": {
      "type": "string"
    },
    "wiedervorlage_datum": {
      "type": "string",
      "format": "date",
      "nullable": true
    }
  },
  "required": [
    "kunden_nr",
    "kanal",
    "ergebnis"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kontakt_id": {
      "type": "string"
    },
    "erfasst_am": {
      "type": "string"
    }
  }
}
```

### `crm.customer.open` — Kunde oeffnen

Loest einen Kunden im Authentifizierungs-Mandanten auf und liefert die kanonische Masken-Route (/crm/customers/{id}) sowie Screen-ID crm/customer-360. Kein Schreiben. HTTP-Aufruf mit tool_name=crm.customer.open, parameters.kunden_nr (Kundennummer oder UUID). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit crm:read und tenant_id erforderlich.

- **Scope:** `crm:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string",
      "description": "Kundennummer oder CRM-Kunden-UUID"
    }
  },
  "required": [
    "kunden_nr"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "customer_id": {
      "type": "string"
    },
    "kunden_nr": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "route_path": {
      "type": "string"
    },
    "screen_id": {
      "type": "string"
    }
  }
}
```

### `crm.customer.search` — Kunden suchen

Sucht Kunden im Authentifizierungs-Mandanten nach Name, Kundennummer oder PLZ (domain_crm.customers, analog UI-Combobox). HTTP-Aufruf mit tool_name=crm.customer.search. Default dryRun; execute ist ebenfalls nur Lesen. Liefert items mit kunden_nr, name, ort, segment, customer_id und route_path. OIDC-Token mit crm:read und tenant_id erforderlich.

- **Scope:** `crm:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Suchbegriff (Name, Nr., PLZ)"
    },
    "limit": {
      "type": "integer",
      "default": 20,
      "minimum": 1,
      "maximum": 50
    }
  },
  "required": [
    "query"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "kunden_nr": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "ort": {
            "type": "string",
            "nullable": true
          },
          "segment": {
            "type": "string",
            "nullable": true
          },
          "customer_id": {
            "type": "string"
          },
          "route_path": {
            "type": "string"
          }
        }
      }
    },
    "count": {
      "type": "integer"
    }
  }
}
```

### `crm.customer.summary360` — Kunden-360-Zusammenfassung

Liefert 360-Grad-Zusammenfassung im Authentifizierungs-Mandanten: offene Auftraege, OP-Saldo, letzte Kontakte, Segment und route_path. HTTP-Aufruf mit tool_name=crm.customer.summary360, parameters.kunden_nr (Kundennummer oder UUID). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit crm:read und tenant_id erforderlich. Kein Cross-Tenant-Fallback.

- **Scope:** `crm:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string",
      "description": "Kundennummer oder CRM-Kunden-UUID"
    }
  },
  "required": [
    "kunden_nr"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "customer_id": {
      "type": "string"
    },
    "offene_auftraege": {
      "type": "integer"
    },
    "op_saldo_eur": {
      "type": "number"
    },
    "letzte_kontakte": {
      "type": "array"
    },
    "segment": {
      "type": "string",
      "nullable": true
    },
    "route_path": {
      "type": "string"
    },
    "screen_id": {
      "type": "string"
    }
  }
}
```

### `crm.lead.qualify` — Lead als Opportunity qualifizieren

Qualifiziert einen Lead des Authentifizierungs-Mandanten zu einer Opportunity (gleicher Fachpfad wie Maske crm/lead:qualifizieren). parameters.lead_id und customer_id oder kunden_nr. Default dryRun; execute erfordert idempotency_key. Scope crm:write. Kein tenant_id-Parameter.

- **Scope:** `crm:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "lead_id": {
      "type": "string",
      "description": "Lead-UUID"
    },
    "customer_id": {
      "type": "string",
      "description": "CRM-Kunden-UUID des Mandanten",
      "nullable": true
    },
    "kunden_nr": {
      "type": "string",
      "description": "Alternative Kundennummer statt customer_id",
      "nullable": true
    }
  },
  "required": [
    "lead_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "lead_id": {
      "type": "string"
    },
    "opportunity_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: einkauf

### `einkauf.angebot.bestellen` — Angebot in Bestellung ueberfuehren

Erzeugt eine Bestellung aus einem Einkaufsangebot des Authentifizierungs-Mandanten (Maske einkauf/angebot:bestellen). Kein Obligo/FIN-CLOSE. Default dryRun; execute erfordert idempotency_key. Scope einkauf:write.

- **Scope:** `einkauf:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "angebot_id": {
      "type": "string",
      "description": "Angebots-UUID oder Angebotsnummer"
    }
  },
  "required": [
    "angebot_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "angebot_id": {
      "type": "string"
    },
    "bestellung_id": {
      "type": "string"
    },
    "bestellnummer": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `einkauf.anlieferavis.wareneingang` — Wareneingang aus Anlieferavis buchen

Bucht Wareneingang aus Anlieferavis (Bestellpositionen + Lagerzugang; Maske einkauf/anlieferavis:wareneingang). Kein FIBU-Journal. Default dryRun; execute erfordert idempotency_key. Scope einkauf:write. parameters.avis_id, lager_id, lieferschein_nr.

- **Scope:** `einkauf:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "avis_id": {
      "type": "string",
      "description": "Anlieferavis-UUID"
    },
    "lager_id": {
      "type": "string",
      "description": "Lager-UUID des Mandanten"
    },
    "lieferschein_nr": {
      "type": "string",
      "description": "Lieferscheinnummer"
    }
  },
  "required": [
    "avis_id",
    "lager_id",
    "lieferschein_nr"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "avis_id": {
      "type": "string"
    },
    "bestellung_id": {
      "type": "string"
    },
    "bestellnummer": {
      "type": "string"
    },
    "positionen": {
      "type": "integer"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `einkauf.bestellung.list` — Offene Bestellungen auflisten

Listet Bestellungen des Authentifizierungs-Mandanten mit Status und Liefertermin. Scope einkauf:read; nur Lesen.

- **Scope:** `einkauf:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "nullable": true,
      "enum": [
        "offen",
        "teilgeliefert",
        "abgeschlossen"
      ]
    },
    "limit": {
      "type": "integer",
      "default": 50
    }
  },
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array"
    },
    "count": {
      "type": "integer"
    }
  }
}
```

### `einkauf.bestellung.versenden` — Bestellung versenden

Versendet eine Bestellung des Authentifizierungs-Mandanten (E-Mail/Fax/EDI/manuell; Maske einkauf/purchase-order:versenden). Kein Obligo-Journal (Freigabe bleibt eigener Pfad). Default dryRun; execute erfordert idempotency_key. Scope einkauf:write.

- **Scope:** `einkauf:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "bestellung_id": {
      "type": "string",
      "description": "Bestellungs-UUID oder Bestellnummer"
    },
    "versand_art": {
      "type": "string",
      "enum": [
        "email",
        "fax",
        "edi",
        "post",
        "manuell"
      ],
      "default": "email"
    },
    "empfaenger": {
      "type": "string",
      "nullable": true
    }
  },
  "required": [
    "bestellung_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "bestellung_id": {
      "type": "string"
    },
    "bestellnummer": {
      "type": "string"
    },
    "versand_status": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: finance

### `fibu.dunning.status` — Mahnstatus abfragen

Gibt Mahnstufe, letzte Mahnung und offenen Debitoren-Saldo fuer einen Kunden im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=fibu.dunning.status, parameters.kunden_nr (Kundennummer oder UUID). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit finance:read und tenant_id erforderlich. Kein Mahnlauf, kein FIN-CLOSE.

- **Scope:** `finance:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string",
      "description": "Kundennummer oder CRM-Kunden-UUID"
    }
  },
  "required": [
    "kunden_nr"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string"
    },
    "customer_id": {
      "type": "string"
    },
    "mahnstufe": {
      "type": "integer"
    },
    "letzte_mahnung": {
      "type": "string",
      "nullable": true
    },
    "gesamt_offen_eur": {
      "type": "number"
    }
  }
}
```

### `fibu.open_items.list` — Offene Posten auflisten

Listet offene Forderungen oder Verbindlichkeiten im Authentifizierungs-Mandanten nach Faelligkeit (domain_erp.offene_posten). HTTP-Aufruf mit tool_name=fibu.open_items.list. typ=forderung|verbindlichkeit. Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit finance:read und tenant_id erforderlich. Kein Kassenabschluss/Journal.

- **Scope:** `finance:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "typ": {
      "type": "string",
      "enum": [
        "forderung",
        "verbindlichkeit"
      ]
    },
    "faellig_bis": {
      "type": "string",
      "format": "date",
      "nullable": true
    },
    "limit": {
      "type": "integer",
      "default": 50,
      "minimum": 1,
      "maximum": 200
    }
  },
  "required": [
    "typ"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "beleg_nr": {
            "type": "string"
          },
          "kunden_nr": {
            "type": "string",
            "nullable": true
          },
          "betrag_eur": {
            "type": "number"
          },
          "faellig_am": {
            "type": "string",
            "nullable": true
          },
          "mahnstatus": {
            "type": "string"
          }
        }
      }
    },
    "count": {
      "type": "integer"
    },
    "typ": {
      "type": "string"
    }
  }
}
```

## Domaene: inventory

### `wms.cell.status` — Silozellen-Status

Gibt Fuellstand kg, aktuelles Material, QS-Status und Flush-/Reinigungsbedarf einer Silozelle im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=wms.cell.status, parameters.cell_code (Zellencode oder UUID). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit inventory:read und tenant_id erforderlich. Kein Transfer, keine QS-Aenderung.

- **Scope:** `inventory:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "cell_code": {
      "type": "string",
      "description": "Zellencode oder Silozellen-UUID"
    }
  },
  "required": [
    "cell_code"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "cell_code": {
      "type": "string"
    },
    "current_stock_kg": {
      "type": "number"
    },
    "qs_status": {
      "type": "string"
    },
    "current_material": {
      "type": "string",
      "nullable": true
    },
    "flush_required": {
      "type": "boolean"
    }
  }
}
```

### `wms.lot.trace` — Lot verfolgen

Gibt Artikel, Menge kg, Status, QS-Status, Silozelle und Bewegungshistorie eines Lots im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=wms.lot.trace, parameters.lot_id (Lot-UUID oder Virtual-/Lotnummer). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit inventory:read und tenant_id erforderlich. Keine Buchung, keine QS-Aenderung.

- **Scope:** `inventory:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "lot_id": {
      "type": "string",
      "description": "Lot-UUID oder Virtual-/Lotnummer"
    }
  },
  "required": [
    "lot_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "lot_id": {
      "type": "string"
    },
    "artikel_id": {
      "type": "string",
      "nullable": true
    },
    "menge_kg": {
      "type": "number"
    },
    "status": {
      "type": "string"
    },
    "qs_status": {
      "type": "string"
    },
    "silozelle": {
      "type": "string",
      "nullable": true
    },
    "bewegungen": {
      "type": "array"
    }
  }
}
```

## Domaene: lager

### `lager.bestand.get` — Lagerbestand abfragen

Gibt Artikelbestand (Menge/reserviert/verfuegbar) im Authentifizierungs-Mandanten zurueck. parameters.artikel_id; lager_id optional (Hinweis, Bestand ist artikelbezogen). Scope lager:read; nur Lesen.

- **Scope:** `lager:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "artikel_id": {
      "type": "string"
    },
    "lager_id": {
      "type": "string",
      "nullable": true
    }
  },
  "required": [
    "artikel_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "artikel_id": {
      "type": "string"
    },
    "menge": {
      "type": "number"
    },
    "einheit": {
      "type": "string"
    },
    "reserviert": {
      "type": "number"
    },
    "verfuegbar": {
      "type": "number"
    }
  }
}
```

### `lager.inventur.status` — Inventurstatus abfragen

Gibt offene Inventuren und Differenzwert-Schaetzung im Authentifizierungs-Mandanten zurueck. Scope lager:read; nur Lesen.

- **Scope:** `lager:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "lager_id": {
      "type": "string",
      "nullable": true
    }
  },
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "offene_inventuren": {
      "type": "integer"
    },
    "differenzen_eur": {
      "type": "number"
    },
    "letzter_abschluss": {
      "type": "string",
      "nullable": true
    }
  }
}
```

### `lager.stock_movement.stornieren` — Lagerbewegung stornieren

Storniert eine Lagerbewegung des Authentifizierungs-Mandanten per Gegenbuchung (Maske lager/stock-movement:stornieren). Kein FIBU. Default dryRun; execute erfordert idempotency_key. Scope lager:write.

- **Scope:** `lager:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "movement_id": {
      "type": "string",
      "description": "UUID der zu stornierenden Lagerbewegung"
    },
    "begruendung": {
      "type": "string",
      "nullable": true,
      "maxLength": 500
    }
  },
  "required": [
    "movement_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "movement_id": {
      "type": "string"
    },
    "storno_movement_id": {
      "type": "string"
    },
    "movement_type": {
      "type": "string"
    },
    "quantity": {
      "type": "number"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: mobile

### `mobile.sync.process_pending` — MDE-Queue verarbeiten

Verarbeitet pending Events der Mobile/MDE-Queue des Authentifizierungs-Mandanten (Maske schnittstelle/mde-inbox:process_pending). parameters.limit optional, reason. Default dryRun; execute erfordert idempotency_key. Scope mobile:write.

- **Scope:** `mobile:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "limit": {
      "type": "integer",
      "default": 50,
      "minimum": 1,
      "maximum": 500
    },
    "reason": {
      "type": "string",
      "default": "MCP MDE-Verarbeitung"
    }
  },
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "processed": {
      "type": "integer",
      "nullable": true
    },
    "failed": {
      "type": "integer",
      "nullable": true
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: nachweisraum

### `dms.document.search` — Dokument suchen

Sucht Nachweisraum-Dokumente im Authentifizierungs-Mandanten nach Typ, Zeitraum oder Beleg-Referenz. HTTP tool_name=dms.document.search. Default dryRun; execute nur Lesen. Scope nachweisraum:read.

- **Scope:** `nachweisraum:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "beleg_ref": {
      "type": "string",
      "nullable": true
    },
    "dokument_typ": {
      "type": "string",
      "nullable": true
    },
    "von": {
      "type": "string",
      "format": "date",
      "nullable": true
    },
    "bis": {
      "type": "string",
      "format": "date",
      "nullable": true
    },
    "limit": {
      "type": "integer",
      "default": 20
    }
  }
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array"
    },
    "count": {
      "type": "integer"
    }
  }
}
```

### `dms.gobd.export_status` — GoBD-Export-Status

Gibt Status und Pruefhinweis eines GoBD-Exports im Authentifizierungs-Mandanten zurueck. HTTP tool_name=dms.gobd.export_status, parameters.export_id. Scope nachweisraum:read; nur Lesen.

- **Scope:** `nachweisraum:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "export_id": {
      "type": "string"
    }
  },
  "required": [
    "export_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "export_id": {
      "type": "string"
    },
    "status": {
      "type": "string"
    },
    "dokument_anzahl": {
      "type": "integer"
    },
    "pruefprotokoll": {
      "type": "string",
      "nullable": true
    }
  }
}
```

## Domaene: planung

### `planung.calendar.reproject` — Planungskalender neu projizieren

Projiziert Kalender-Items des Authentifizierungs-Mandanten neu (Maske planung/kalender:reproject). parameters.horizon_days optional. Default dryRun; execute erfordert idempotency_key. Scope planung:write.

- **Scope:** `planung:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "horizon_days": {
      "type": "integer",
      "default": 120,
      "minimum": 1,
      "maximum": 366
    }
  },
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "projected": {
      "type": "integer",
      "nullable": true
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: produktion

### `produktion.control.sync` — Produktionsleitstand synchronisieren

Synchronisiert Mischfutter-Produktionsauftraege in den Leitstand (Maske produktion/produktionsleitstand:sync). parameters.reason. Default dryRun; execute erfordert idempotency_key. Scope ops:write. Kein FIBU/FIN-CLOSE.

- **Scope:** `ops:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "reason": {
      "type": "string",
      "description": "Audit-/Sync-Grund",
      "minLength": 3
    }
  },
  "required": [
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "synchronized": {
      "type": "integer"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: qualitaet

### `qualitaet.reklamation.abschliessen` — Reklamation abschliessen

Schliesst eine Reklamation des Authentifizierungs-Mandanten (Maske qualitaet/reklamation:abschliessen). parameters.reklamation_id, optional kommentar. Default dryRun; execute erfordert idempotency_key. Scope quality:write. Kein FIBU.

- **Scope:** `quality:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "reklamation_id": {
      "type": "string"
    },
    "kommentar": {
      "type": "string",
      "nullable": true
    }
  },
  "required": [
    "reklamation_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "reklamation_id": {
      "type": "string"
    },
    "status": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: sales

### `sales.invoice.post` — Rechnung aus freigegebenem Vorschlag anlegen

Legt eine Verkaufsrechnung (Status entwurf) aus einem freigegebenen agent_proposals-Datensatz (rechnung_vorschlag) an. Parameter nur proposal_id. Default dryRun. execute erfordert idempotency_key und approval_status=approved. Kein Freigabe-Boolean im Aufruf. FIBU-Journal/OP bleiben im UI-Pfad create-invoice. OIDC-Token mit sales:write und tenant_id erforderlich.

- **Scope:** `sales:write`
- **Idempotent:** ja
- **Risikoklasse:** hoch
- **Audit:** write
- **Human-Approval erforderlich:** ja
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "proposal_id": {
      "type": "string",
      "description": "entwurf_id aus sales.invoice.propose"
    }
  },
  "required": [
    "proposal_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "invoice_id": {
      "type": "string"
    },
    "invoice_number": {
      "type": "string"
    },
    "status": {
      "type": "string"
    },
    "posted": {
      "type": "boolean"
    }
  }
}
```

### `sales.invoice.propose` — Rechnungsvorschlag aus Lieferschein

Legt einen ausstehenden Rechnungsvorschlag zu einem gebuchten Lieferschein an. HTTP-Aufruf an POST /api/v1/mcp/tools/call mit tool_name=sales.invoice.propose. Default dryRun liest nur Summen. propose speichert agent_proposals mit approval_status pending und bucht keine Rechnung. execute ist nicht angebunden. Ein Freigabe-Boolean im Aufruf wird abgewiesen. OIDC-Token mit sales:write und tenant_id erforderlich.

- **Scope:** `sales:write`
- **Idempotent:** nein
- **Risikoklasse:** hoch
- **Audit:** write
- **Human-Approval erforderlich:** ja
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "lieferschein_nr": {
      "type": "string"
    },
    "rechnungsdatum": {
      "type": "string",
      "format": "date"
    }
  },
  "required": [
    "lieferschein_nr",
    "rechnungsdatum"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "entwurf_id": {
      "type": "string"
    },
    "betrag_netto": {
      "type": "number"
    },
    "mwst": {
      "type": "number"
    },
    "positionen": {
      "type": "integer"
    }
  }
}
```

### `sales.order.status` — Auftragsstatus pruefen

Gibt Lifecycle-Status, offene Positionen und naechsten Schritt eines Auftrags im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=sales.order.status, parameters.auftrag_nr (Auftragsnummer oder UUID). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit sales:read und tenant_id erforderlich.

- **Scope:** `sales:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "auftrag_nr": {
      "type": "string",
      "description": "Auftragsnummer oder Sales-Order-UUID"
    }
  },
  "required": [
    "auftrag_nr"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "auftrag_nr": {
      "type": "string"
    },
    "order_id": {
      "type": "string"
    },
    "status": {
      "type": "string"
    },
    "offene_positionen": {
      "type": "integer"
    },
    "naechster_schritt": {
      "type": "string"
    }
  }
}
```

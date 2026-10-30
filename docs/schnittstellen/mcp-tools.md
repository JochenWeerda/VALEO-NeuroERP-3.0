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

Registry `MCP-ERP-TOOLS-001` (Schema 1.0) — 69 Tools in 22 Domaenen.

## Uebersicht

| Tool | Domaene | Scope | Idempotent | Risiko | Human-Approval |
|---|---|---|---|---|---|
| `admin.postfach.speichern` | platform | `admin:write` | ja | hoch | nein |
| `agent.proposal.list` | agent | `agent:read` | ja | niedrig | nein |
| `agrar.contract.get` | agrar | `agrar:read` | ja | niedrig | nein |
| `agrar.feed_analysis.transition` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.feeding.actual_measure` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.feeding.configure_threshold` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.feeding.supply_handoff` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.ration.transition` | agrar | `agrar:write` | ja | mittel | nein |
| `agrar.weighing_ticket.list` | agrar | `agrar:read` | ja | niedrig | nein |
| `beleg.arten` | belege | `belege:read` | ja | niedrig | nein |
| `beleg.lesen` | belege | `belege:read` | ja | niedrig | nein |
| `beleg.suchen` | belege | `belege:read` | ja | niedrig | nein |
| `compliance.gate.status` | compliance | `compliance:read` | ja | niedrig | nein |
| `compliance.sanctions.check` | compliance | `compliance:write` | ja | mittel | nein |
| `crm.activity.create` | crm | `crm:write` | ja | niedrig | nein |
| `crm.activity.delete` | crm | `crm:write` | ja | mittel | nein |
| `crm.activity.update` | crm | `crm:write` | ja | mittel | nein |
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
| `einkauf.bestellung.speichern` | einkauf | `einkauf:write` | ja | mittel | nein |
| `einkauf.bestellung.status` | einkauf | `einkauf:read` | ja | niedrig | nein |
| `einkauf.bestellung.versenden` | einkauf | `einkauf:write` | ja | mittel | nein |
| `fibu.dunning.status` | finance | `finance:read` | ja | niedrig | nein |
| `fibu.open_items.list` | finance | `finance:read` | ja | niedrig | nein |
| `finance.ap_invoice.propose` | finance | `finance:write` | nein | hoch | ja |
| `hr.bewerbung.speichern` | hr | `hr:write` | ja | mittel | nein |
| `hr.einwilligung.anlegen` | hr | `hr:write` | ja | mittel | nein |
| `hr.onboarding.speichern` | hr | `hr:write` | ja | mittel | nein |
| `hr.qualifikation.speichern` | hr | `hr:write` | ja | mittel | nein |
| `hr.schulung.speichern` | hr | `hr:write` | ja | mittel | nein |
| `lager.bestand.get` | lager | `lager:read` | ja | niedrig | nein |
| `lager.inventur.propose_opening` | lager | `lager:write` | nein | hoch | ja |
| `lager.inventur.status` | lager | `lager:read` | ja | niedrig | nein |
| `lager.stock_movement.stornieren` | lager | `lager:write` | ja | mittel | nein |
| `logistik.ausgehendes_dokument.speichern` | logistics | `logistics:write` | ja | mittel | nein |
| `logistik.fahrzeug.loeschen` | logistics | `logistics:write` | ja | hoch | nein |
| `logistik.fahrzeug.speichern` | logistics | `logistics:write` | ja | mittel | nein |
| `logistik.frachttabelle.anlegen` | logistics | `logistics:write` | ja | mittel | nein |
| `logistik.rechnung.speichern` | logistics | `logistics:write` | ja | mittel | nein |
| `logistik.terminart.speichern` | logistics | `logistics:write` | ja | mittel | nein |
| `logistik.tour.anlegen` | logistics | `logistics:write` | ja | mittel | nein |
| `mask.action.execute` | masks | `masks:write` | ja | mittel | nein |
| `mask.actions.list` | masks | `masks:read` | ja | niedrig | nein |
| `mask.data.read` | masks | `masks:read` | ja | niedrig | nein |
| `mobile.sync.process_pending` | mobile | `mobile:write` | ja | mittel | nein |
| `planung.calendar.reproject` | planung | `planung:write` | ja | mittel | nein |
| `produktion.control.sync` | produktion | `ops:write` | ja | mittel | nein |
| `qualitaet.reklamation.abschliessen` | qualitaet | `quality:write` | ja | mittel | nein |
| `reporting.bonus.calculate` | reporting | `reporting:write` | ja | mittel | nein |
| `reporting.query.import_signed` | reporting | `reporting:write` | ja | mittel | nein |
| `sales.gutschrift.buchen` | sales | `sales:write` | ja | hoch | ja |
| `sales.gutschrift.propose` | sales | `sales:write` | nein | hoch | ja |
| `sales.gutschrift.speichern` | sales | `sales:write` | ja | mittel | nein |
| `sales.invoice.post` | sales | `sales:write` | ja | hoch | ja |
| `sales.invoice.propose` | sales | `sales:write` | nein | hoch | ja |
| `sales.order.status` | sales | `sales:read` | ja | niedrig | nein |
| `studio.migration.plan` | studio | `belege:write` | ja | niedrig | nein |
| `wms.cell.status` | inventory | `inventory:read` | ja | niedrig | nein |
| `wms.lot.trace` | inventory | `inventory:read` | ja | niedrig | nein |
| `workspace.fachaktion.katalog` | workspace | `agent:read` | ja | niedrig | nein |
| `workspace.fachaktion.resolve` | workspace | `agent:read` | ja | niedrig | nein |

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

Gibt Agrar-Kontrakt (Menge, Preis, Status) und kanonische Masken-Route (/agrar/kontrakt/{id}, Screen agrar/kontrakte) im Authentifizierungs-Mandanten zurueck. parameters.kontrakt_id (UUID oder Vertragsnummer). Kein tenant_id-Parameter. Scope agrar:read; nur Lesen.

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

Listet Wiegescheine des Authentifizierungs-Mandanten optional nach ticket_id, Kontrakt-/Partie-Referenz und Zeitraum. Items tragen kanonische Masken-Route (/waage/wiegeschein/{id}, Screen waage/wiegeschein). Scope agrar:read; nur Lesen.

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
    "ticket_id": {
      "type": "string",
      "nullable": true,
      "description": "Wiegeschein-UUID"
    },
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

## Domaene: belege

### `beleg.arten` — Belegarten und Belegkommandos beschreiben

Beschreibt die Belegarten des Belegvertrags (Bezeichnung, Partnerrolle, Steuerrichtung, mit oder ohne Preise, ob Finance bucht, Folgebelege) und das Verzeichnis der Belegkommandos (schreibend, Risiko, Freigabe, Idempotenz, Adresse). Keine Parameter. HTTP tool_name=beleg.arten. Scope belege:read; nur Lesen.

- **Scope:** `belege:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "vertragsversion": {
      "type": "string"
    },
    "status": {
      "type": "array"
    },
    "preisfelder": {
      "type": "array"
    },
    "belegarten": {
      "type": "array"
    },
    "kommandos": {
      "type": "array"
    }
  }
}
```

### `beleg.lesen` — Beleg lesen

Liefert einen Beleg des Authentifizierungs-Mandanten in der Form des Belegvertrags (docs/schnittstellen/contracts/belegvertrag.schema.json): Kopf, Partner, Positionen mit offener Menge, Summen je Steuerschluessel, Buchungsstand mit Grund, Belegkette, Statushistorie und die im Zustand moeglichen Aktionen mit Kommando und Sperrgrund. Dieselbe Antwort wie GET /api/v1/belege/{belegart}/{beleg_id}. HTTP tool_name=beleg.lesen. Scope belege:read; nur Lesen.

- **Scope:** `belege:read`
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
    "belegart": {
      "type": "string",
      "enum": [
        "sales_offer",
        "sales_order",
        "sales_delivery",
        "sales_invoice",
        "sales_credit_memo",
        "purchase_order",
        "goods_receipt",
        "purchase_invoice",
        "purchase_credit_memo"
      ]
    },
    "beleg_id": {
      "type": "string"
    }
  },
  "required": [
    "belegart",
    "beleg_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "beleg": {
      "type": "object"
    }
  }
}
```

### `beleg.suchen` — Belege suchen

Sucht Belege im Authentifizierungs-Mandanten nach Belegart, Status, Teil der Belegnummer oder Partnernummer; neueste zuerst, hoechstens 50. Belegarten ohne Preise (Lieferschein, Wareneingang) kommen ohne Betrag. HTTP tool_name=beleg.suchen. Scope belege:read; nur Lesen.

- **Scope:** `belege:read`
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
    "belegart": {
      "type": "string",
      "nullable": true,
      "enum": [
        "sales_offer",
        "sales_order",
        "sales_delivery",
        "sales_invoice",
        "sales_credit_memo",
        "purchase_order",
        "goods_receipt",
        "purchase_invoice",
        "purchase_credit_memo"
      ]
    },
    "status": {
      "type": "string",
      "nullable": true,
      "enum": [
        "draft",
        "open",
        "released",
        "posted",
        "reversed",
        "cancelled"
      ]
    },
    "beleg_nr": {
      "type": "string",
      "nullable": true,
      "description": "Teil der Belegnummer"
    },
    "partner_nr": {
      "type": "string",
      "nullable": true,
      "description": "Kunden- bzw. Lieferantennummer"
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

### `compliance.sanctions.check` — Sanktionsliste pruefen

Prueft einen Namen gegen die aktive Sanktionsliste und protokolliert bei execute mandantengebunden (Masken auswertungen/sanktionspruefung-kunden|personal:check; CE /api/v1/compliance/sanctions/actions/pruefen/{scope}). parameters.name, scope (customers|personal|manual), optional entity_ref. Default dryRun ohne Protokoll; execute erfordert idempotency_key. Scope compliance:write. Kein Auto-Freigeben von Treffern, kein FIBU/FIN-CLOSE.

- **Scope:** `compliance:write`
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
    "name": {
      "type": "string",
      "description": "Zu pruefender Name"
    },
    "scope": {
      "type": "string",
      "enum": [
        "customers",
        "personal",
        "manual"
      ],
      "description": "Pruefumfang der Maske"
    },
    "entity_ref": {
      "type": "string",
      "nullable": true,
      "description": "Personal-/Kunden-Nr."
    }
  },
  "required": [
    "name",
    "scope"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string"
    },
    "empfehlung": {
      "type": "string"
    },
    "treffer": {
      "type": "array"
    },
    "check_id": {
      "type": "string",
      "nullable": true
    },
    "auditEntryId": {
      "type": "string",
      "nullable": true
    }
  }
}
```

## Domaene: crm

### `crm.activity.create` — CRM-Aktivitaet anlegen

Kanonischer CRM-Aktivitaetencommand v1. Gleiche Fachregeln wie REST, Studio und CLI. Execute verlangt einen Idempotenzschluessel im MCP-Umschlag, Aendern und Loeschen die gelesene Version. Nur gepruefte menschliche Identitaet mit CRM-/SALES-Bearbeitungsrolle; Agenten nicht freigeschaltet.

- **Scope:** `crm:write`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "additionalProperties": false,
  "properties": {
    "type": {
      "enum": [
        "meeting",
        "call",
        "email",
        "note",
        "visit",
        "task"
      ],
      "title": "Type",
      "type": "string"
    },
    "title": {
      "maxLength": 200,
      "minLength": 1,
      "title": "Title",
      "type": "string"
    },
    "customer": {
      "default": "",
      "maxLength": 100,
      "title": "Customer",
      "type": "string"
    },
    "contact_person": {
      "default": "",
      "maxLength": 100,
      "title": "Contact Person",
      "type": "string"
    },
    "date": {
      "anyOf": [
        {
          "format": "date-time",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Date"
    },
    "status": {
      "default": "planned",
      "enum": [
        "planned",
        "completed",
        "cancelled"
      ],
      "title": "Status",
      "type": "string"
    },
    "assigned_to": {
      "default": "",
      "maxLength": 100,
      "title": "Assigned To",
      "type": "string"
    },
    "description": {
      "anyOf": [
        {
          "maxLength": 10000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Description"
    },
    "customer_id": {
      "anyOf": [
        {
          "maxLength": 64,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Customer Id"
    },
    "contact_id": {
      "anyOf": [
        {
          "maxLength": 64,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Contact Id"
    },
    "opportunity_id": {
      "anyOf": [
        {
          "maxLength": 36,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Opportunity Id"
    },
    "main_topics": {
      "items": {
        "maxLength": 200,
        "type": "string"
      },
      "maxItems": 100,
      "title": "Main Topics",
      "type": "array"
    },
    "orders_placed": {
      "items": {
        "maxLength": 200,
        "type": "string"
      },
      "maxItems": 100,
      "title": "Orders Placed",
      "type": "array"
    },
    "follow_up_actions": {
      "items": {
        "maxLength": 200,
        "type": "string"
      },
      "maxItems": 100,
      "title": "Follow Up Actions",
      "type": "array"
    },
    "audit_reason": {
      "anyOf": [
        {
          "maxLength": 2000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Audit Reason"
    },
    "correlation_id": {
      "anyOf": [
        {
          "maxLength": 200,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Correlation Id"
    }
  },
  "required": [
    "type",
    "title"
  ],
  "type": "object"
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "activity_id": {
      "type": "string"
    },
    "version": {
      "type": "integer"
    },
    "activity": {
      "properties": {
        "type": {
          "enum": [
            "meeting",
            "call",
            "email",
            "note",
            "visit",
            "task"
          ],
          "title": "Type",
          "type": "string"
        },
        "title": {
          "maxLength": 200,
          "minLength": 1,
          "title": "Title",
          "type": "string"
        },
        "customer": {
          "default": "",
          "maxLength": 100,
          "title": "Customer",
          "type": "string"
        },
        "contact_person": {
          "default": "",
          "maxLength": 100,
          "title": "Contact Person",
          "type": "string"
        },
        "date": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Date"
        },
        "status": {
          "default": "planned",
          "enum": [
            "planned",
            "completed",
            "cancelled"
          ],
          "title": "Status",
          "type": "string"
        },
        "assigned_to": {
          "default": "",
          "maxLength": 100,
          "title": "Assigned To",
          "type": "string"
        },
        "description": {
          "anyOf": [
            {
              "maxLength": 10000,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "customer_id": {
          "anyOf": [
            {
              "maxLength": 64,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Customer Id"
        },
        "contact_id": {
          "anyOf": [
            {
              "maxLength": 64,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Contact Id"
        },
        "opportunity_id": {
          "anyOf": [
            {
              "maxLength": 36,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Opportunity Id"
        },
        "main_topics": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Main Topics",
          "type": "array"
        },
        "orders_placed": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Orders Placed",
          "type": "array"
        },
        "follow_up_actions": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Follow Up Actions",
          "type": "array"
        },
        "id": {
          "title": "Id",
          "type": "string"
        },
        "version": {
          "minimum": 1,
          "title": "Version",
          "type": "integer"
        },
        "created_at": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Created At"
        },
        "updated_at": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Updated At"
        },
        "created_by": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Created By"
        },
        "updated_by": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Updated By"
        },
        "overdue": {
          "readOnly": true,
          "title": "Overdue",
          "type": "boolean"
        }
      },
      "required": [
        "type",
        "title",
        "id",
        "version",
        "overdue"
      ],
      "title": "ActivityRead",
      "type": "object"
    }
  }
}
```

### `crm.activity.delete` — CRM-Aktivitaet loeschen

Kanonischer CRM-Aktivitaetencommand v1. Gleiche Fachregeln wie REST, Studio und CLI. Execute verlangt einen Idempotenzschluessel im MCP-Umschlag, Aendern und Loeschen die gelesene Version. Nur gepruefte menschliche Identitaet mit CRM-/SALES-Bearbeitungsrolle; Agenten nicht freigeschaltet.

- **Scope:** `crm:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "additionalProperties": false,
  "properties": {
    "expected_version": {
      "minimum": 1,
      "title": "Expected Version",
      "type": "integer"
    },
    "audit_reason": {
      "anyOf": [
        {
          "maxLength": 2000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Audit Reason"
    },
    "correlation_id": {
      "anyOf": [
        {
          "maxLength": 200,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Correlation Id"
    },
    "activity_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64
    }
  },
  "required": [
    "expected_version",
    "activity_id"
  ],
  "type": "object"
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "activity_id": {
      "type": "string"
    },
    "version": {
      "type": "integer"
    },
    "activity": {
      "properties": {
        "type": {
          "enum": [
            "meeting",
            "call",
            "email",
            "note",
            "visit",
            "task"
          ],
          "title": "Type",
          "type": "string"
        },
        "title": {
          "maxLength": 200,
          "minLength": 1,
          "title": "Title",
          "type": "string"
        },
        "customer": {
          "default": "",
          "maxLength": 100,
          "title": "Customer",
          "type": "string"
        },
        "contact_person": {
          "default": "",
          "maxLength": 100,
          "title": "Contact Person",
          "type": "string"
        },
        "date": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Date"
        },
        "status": {
          "default": "planned",
          "enum": [
            "planned",
            "completed",
            "cancelled"
          ],
          "title": "Status",
          "type": "string"
        },
        "assigned_to": {
          "default": "",
          "maxLength": 100,
          "title": "Assigned To",
          "type": "string"
        },
        "description": {
          "anyOf": [
            {
              "maxLength": 10000,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "customer_id": {
          "anyOf": [
            {
              "maxLength": 64,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Customer Id"
        },
        "contact_id": {
          "anyOf": [
            {
              "maxLength": 64,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Contact Id"
        },
        "opportunity_id": {
          "anyOf": [
            {
              "maxLength": 36,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Opportunity Id"
        },
        "main_topics": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Main Topics",
          "type": "array"
        },
        "orders_placed": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Orders Placed",
          "type": "array"
        },
        "follow_up_actions": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Follow Up Actions",
          "type": "array"
        },
        "id": {
          "title": "Id",
          "type": "string"
        },
        "version": {
          "minimum": 1,
          "title": "Version",
          "type": "integer"
        },
        "created_at": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Created At"
        },
        "updated_at": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Updated At"
        },
        "created_by": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Created By"
        },
        "updated_by": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Updated By"
        },
        "overdue": {
          "readOnly": true,
          "title": "Overdue",
          "type": "boolean"
        }
      },
      "required": [
        "type",
        "title",
        "id",
        "version",
        "overdue"
      ],
      "title": "ActivityRead",
      "type": "object"
    }
  }
}
```

### `crm.activity.update` — CRM-Aktivitaet bearbeiten

Kanonischer CRM-Aktivitaetencommand v1. Gleiche Fachregeln wie REST, Studio und CLI. Execute verlangt einen Idempotenzschluessel im MCP-Umschlag, Aendern und Loeschen die gelesene Version. Nur gepruefte menschliche Identitaet mit CRM-/SALES-Bearbeitungsrolle; Agenten nicht freigeschaltet.

- **Scope:** `crm:write`
- **Idempotent:** ja
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "additionalProperties": false,
  "properties": {
    "type": {
      "anyOf": [
        {
          "enum": [
            "meeting",
            "call",
            "email",
            "note",
            "visit",
            "task"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Type"
    },
    "title": {
      "anyOf": [
        {
          "maxLength": 200,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Title"
    },
    "customer": {
      "anyOf": [
        {
          "maxLength": 100,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Customer"
    },
    "contact_person": {
      "anyOf": [
        {
          "maxLength": 100,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Contact Person"
    },
    "date": {
      "anyOf": [
        {
          "format": "date-time",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Date"
    },
    "status": {
      "anyOf": [
        {
          "enum": [
            "planned",
            "completed",
            "cancelled"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Status"
    },
    "assigned_to": {
      "anyOf": [
        {
          "maxLength": 100,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Assigned To"
    },
    "description": {
      "anyOf": [
        {
          "maxLength": 10000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Description"
    },
    "customer_id": {
      "anyOf": [
        {
          "maxLength": 64,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Customer Id"
    },
    "contact_id": {
      "anyOf": [
        {
          "maxLength": 64,
          "minLength": 1,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Contact Id"
    },
    "opportunity_id": {
      "anyOf": [
        {
          "maxLength": 36,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Opportunity Id"
    },
    "main_topics": {
      "anyOf": [
        {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Main Topics"
    },
    "orders_placed": {
      "anyOf": [
        {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Orders Placed"
    },
    "follow_up_actions": {
      "anyOf": [
        {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Follow Up Actions"
    },
    "expected_version": {
      "minimum": 1,
      "title": "Expected Version",
      "type": "integer"
    },
    "audit_reason": {
      "anyOf": [
        {
          "maxLength": 2000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Audit Reason"
    },
    "correlation_id": {
      "anyOf": [
        {
          "maxLength": 200,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Correlation Id"
    },
    "activity_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64
    }
  },
  "required": [
    "expected_version",
    "activity_id"
  ],
  "type": "object"
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "activity_id": {
      "type": "string"
    },
    "version": {
      "type": "integer"
    },
    "activity": {
      "properties": {
        "type": {
          "enum": [
            "meeting",
            "call",
            "email",
            "note",
            "visit",
            "task"
          ],
          "title": "Type",
          "type": "string"
        },
        "title": {
          "maxLength": 200,
          "minLength": 1,
          "title": "Title",
          "type": "string"
        },
        "customer": {
          "default": "",
          "maxLength": 100,
          "title": "Customer",
          "type": "string"
        },
        "contact_person": {
          "default": "",
          "maxLength": 100,
          "title": "Contact Person",
          "type": "string"
        },
        "date": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Date"
        },
        "status": {
          "default": "planned",
          "enum": [
            "planned",
            "completed",
            "cancelled"
          ],
          "title": "Status",
          "type": "string"
        },
        "assigned_to": {
          "default": "",
          "maxLength": 100,
          "title": "Assigned To",
          "type": "string"
        },
        "description": {
          "anyOf": [
            {
              "maxLength": 10000,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Description"
        },
        "customer_id": {
          "anyOf": [
            {
              "maxLength": 64,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Customer Id"
        },
        "contact_id": {
          "anyOf": [
            {
              "maxLength": 64,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Contact Id"
        },
        "opportunity_id": {
          "anyOf": [
            {
              "maxLength": 36,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Opportunity Id"
        },
        "main_topics": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Main Topics",
          "type": "array"
        },
        "orders_placed": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Orders Placed",
          "type": "array"
        },
        "follow_up_actions": {
          "items": {
            "maxLength": 200,
            "type": "string"
          },
          "maxItems": 100,
          "title": "Follow Up Actions",
          "type": "array"
        },
        "id": {
          "title": "Id",
          "type": "string"
        },
        "version": {
          "minimum": 1,
          "title": "Version",
          "type": "integer"
        },
        "created_at": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Created At"
        },
        "updated_at": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Updated At"
        },
        "created_by": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Created By"
        },
        "updated_by": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Updated By"
        },
        "overdue": {
          "readOnly": true,
          "title": "Overdue",
          "type": "boolean"
        }
      },
      "required": [
        "type",
        "title",
        "id",
        "version",
        "overdue"
      ],
      "title": "ActivityRead",
      "type": "object"
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

Listet Bestellungen des Authentifizierungs-Mandanten mit Status, Liefertermin und kanonischer Masken-Route (/einkauf/bestellung/{id}, Screen einkauf/purchase-order). Scope einkauf:read; nur Lesen.

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

### `einkauf.bestellung.speichern` — Bestellung speichern

Aktualisiert erlaubte Bestell-Kopffelder im Authentifizierungs-Mandanten (Maske einkauf/purchase-order:speichern; CE /api/v1/einkauf/bestellungen/{id}/actions/speichern). parameters.bestellung_id plus optionale Felder (Liefer-/Ladetermine, Referenzen, Notiz, versand_art), reason. Status/Summen nicht aenderbar. Default dryRun; execute erfordert idempotency_key. Scope einkauf:write. Kein tenant_id-Parameter.

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
      "type": "string"
    },
    "lieferdatum_wunsch": {
      "type": "string"
    },
    "lieferdatum_zugesagt": {
      "type": "string"
    },
    "ladetermin": {
      "type": "string"
    },
    "ladetermin_ab": {
      "type": "string"
    },
    "versand_art": {
      "type": "string",
      "enum": [
        "email",
        "fax",
        "edi",
        "post",
        "telefon",
        "manuell"
      ]
    },
    "unsere_referenz": {
      "type": "string"
    },
    "ihre_referenz": {
      "type": "string"
    },
    "notiz": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "bestellung_id",
    "reason"
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
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `einkauf.bestellung.status` — Bestellungs-Status

Gibt Status, Lieferant und kanonische Masken-Route (/einkauf/bestellung/{id}, Screen einkauf/purchase-order) einer Bestellung im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=einkauf.bestellung.status, parameters.bestellung_id (UUID oder Bestellnummer). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit einkauf:read und tenant_id erforderlich. Kein Versand, kein Obligo.

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
    "bestellung_id": {
      "type": "string",
      "description": "Bestellungs-UUID oder Bestellnummer"
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
    "status": {
      "type": "string"
    },
    "lieferant": {
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

### `finance.ap_invoice.propose` — AP-Freigabe vorschlagen

Legt einen ausstehenden Freigabe-Vorschlag fuer eine Eingangsrechnung im Authentifizierungs-Mandanten an. HTTP-Aufruf mit tool_name=finance.ap_invoice.propose, parameters.invoice_id. Default dryRun liest nur Status/Brutto/route_path. propose speichert agent_proposals (ap_invoice_freigabe) mit approval_status pending und ruft den Freigabe-Endpoint nicht auf. execute ist deaktiviert; die verbindliche Entscheidung trifft eine berechtigte unabhaengige Person in der AP-Maske. Ein freigegebener Vorschlag ist keine Belegfreigabe. Ein Freigabe-Boolean im Aufruf wird abgewiesen. OIDC-Token mit finance:write und tenant_id erforderlich. Kein Journal/FIN-CLOSE.

- **Scope:** `finance:write`
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
    "invoice_id": {
      "type": "string",
      "description": "AP-Rechnungs-ID bzw. Belegnummer"
    }
  },
  "required": [
    "invoice_id"
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
    "invoice_id": {
      "type": "string"
    },
    "invoice_number": {
      "type": "string"
    },
    "status": {
      "type": "string"
    },
    "brutto_eur": {
      "type": "number",
      "nullable": true
    },
    "route_path": {
      "type": "string"
    },
    "screen_id": {
      "type": "string"
    },
    "approval_status": {
      "type": "string"
    }
  }
}
```

## Domaene: hr

### `hr.bewerbung.speichern` — Bewerbung speichern

Erfasst eine Bewerbung im Authentifizierungs-Mandanten (Maske personal/bewerbungen:speichern; CE /api/v1/personal/applications/actions/speichern). parameters.applicant_name, applicant_email, optional position_title/source, reason. Default dryRun; execute erfordert idempotency_key. Scope hr:write. Kein tenant_id-Parameter.

- **Scope:** `hr:write`
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
    "applicant_name": {
      "type": "string"
    },
    "applicant_email": {
      "type": "string"
    },
    "position_title": {
      "type": "string"
    },
    "source": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "applicant_name",
    "applicant_email",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "application_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `hr.einwilligung.anlegen` — Einwilligungserklaerung anlegen

Legt eine unveraenderliche Fassung der Einwilligungserklaerung im Authentifizierungs-Mandanten an (Maske personal/einwilligungserklaerungen:anlegen; CE /api/v1/personal/applications/einwilligungserklaerungen/actions/anlegen). parameters.wortlaut, optional erstellt_durch, reason. Default dryRun; execute erfordert idempotency_key. Scope hr:write.

- **Scope:** `hr:write`
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
    "wortlaut": {
      "type": "string"
    },
    "erstellt_durch": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "wortlaut",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "erklaerung_id": {
      "type": "string"
    },
    "fassung": {
      "type": "integer"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `hr.onboarding.speichern` — Onboarding-Lauf speichern

Legt einen Einarbeitungslauf im Authentifizierungs-Mandanten an (Maske personal/onboarding:speichern; CE /api/v1/training/onboarding/runs/actions/speichern). parameters.employee_ref, checklist_id, optional assigned_by/due_date, reason. Checkliste muss Mandant gehoeren (sonst 404). Default dryRun; execute erfordert idempotency_key. Scope hr:write.

- **Scope:** `hr:write`
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
    "employee_ref": {
      "type": "string"
    },
    "checklist_id": {
      "type": "string"
    },
    "assigned_by": {
      "type": "string"
    },
    "due_date": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "employee_ref",
    "checklist_id",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "run_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `hr.qualifikation.speichern` — Qualifikation speichern

Legt ein Qualifikationsprofil im Authentifizierungs-Mandanten an (Maske personal/qualifikationen:speichern; CE /api/v1/training/qualifications/actions/speichern). parameters.employee_ref, role_code, optional qualification_level/skills/valid_until, reason. Default dryRun; execute erfordert idempotency_key. Scope hr:write.

- **Scope:** `hr:write`
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
    "employee_ref": {
      "type": "string"
    },
    "role_code": {
      "type": "string"
    },
    "qualification_level": {
      "type": "string"
    },
    "skills": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "valid_until": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "employee_ref",
    "role_code",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "qualification_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `hr.schulung.speichern` — Schulungszuweisung speichern

Legt eine Schulungszuweisung im Authentifizierungs-Mandanten an (Maske personal/schulungen:speichern; CE /api/v1/training/assignments/actions/speichern). parameters.employee_ref, course_id, optional assigned_by/due_date, reason. Kurs muss Mandant gehoeren (sonst 404). Default dryRun; execute erfordert idempotency_key. Scope hr:write.

- **Scope:** `hr:write`
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
    "employee_ref": {
      "type": "string"
    },
    "course_id": {
      "type": "string"
    },
    "assigned_by": {
      "type": "string"
    },
    "due_date": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "employee_ref",
    "course_id",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "assignment_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: inventory

### `wms.cell.status` — Silozellen-Status

Gibt Fuellstand kg, aktuelles Material, QS-Status, Flush-/Reinigungsbedarf und kanonische Masken-Route (/lager/silo-zellen/{id}, Screen lager/silo-cell) einer Silozelle im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=wms.cell.status, parameters.cell_code (Zellencode oder UUID). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit inventory:read und tenant_id erforderlich. Kein Transfer, keine QS-Aenderung.

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
    "cell_id": {
      "type": "string"
    },
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

### `wms.lot.trace` — Lot verfolgen

Gibt Artikel, Menge kg, Status, QS-Status, Silozelle, Bewegungshistorie und kanonische Masken-Route (/charge/stamm/{id}, Screen charge/stamm) eines Lots im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=wms.lot.trace, parameters.lot_id (Lot-UUID oder Virtual-/Lotnummer). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit inventory:read und tenant_id erforderlich. Keine Buchung, keine QS-Aenderung.

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

## Domaene: lager

### `lager.bestand.get` — Lagerbestand abfragen

Gibt Artikelbestand (Menge/reserviert/verfuegbar) und kanonische Masken-Route (/lager/artikel/{id}, Screen lager/article-stock) im Authentifizierungs-Mandanten zurueck. parameters.artikel_id (UUID oder Artikelnummer); lager_id optional (Hinweis, Bestand ist artikelbezogen). Scope lager:read; nur Lesen.

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

### `lager.inventur.propose_opening` — Bestandsvortrag vorschlagen

Legt einen ausstehenden Bestandsvortrag-Vorschlag zu einer Inventur (inventory_counts) im Authentifizierungs-Mandanten an. HTTP-Aufruf mit tool_name=lager.inventur.propose_opening, parameters.count_id. Default dryRun liest Zeilen/Differenzen/vorlaeufigen Wert aus Inventurzeilen (gleiche Quelle wie InventoryAuxiliaryService). propose speichert agent_proposals (inventur_opening) mit approval_status pending und erzeugt keinen opening_balance-Batch. execute ist nicht angebunden (501) — kein CommandEndpoint, kein Booking/Journal. Freigabe-Boolean im Aufruf wird abgewiesen. OIDC-Token mit lager:write und tenant_id erforderlich.

- **Scope:** `lager:write`
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
    "count_id": {
      "type": "string",
      "description": "Inventur-UUID (inventory_counts.id)"
    },
    "reason": {
      "type": "string",
      "nullable": true,
      "description": "Optionale Begruendung fuer den Vorschlag"
    }
  },
  "required": [
    "count_id"
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
    "count_id": {
      "type": "string"
    },
    "line_count": {
      "type": "integer"
    },
    "difference_count": {
      "type": "integer"
    },
    "preliminary_value": {
      "type": "number"
    },
    "approval_status": {
      "type": "string"
    },
    "booked": {
      "type": "boolean"
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

## Domaene: logistics

### `logistik.ausgehendes_dokument.speichern` — Ausgehendes Dokument speichern

Legt einen ausgehenden Belegtyp im Authentifizierungs-Mandanten an oder aktualisiert ihn (Maske fuhrpark/ausgehende-dokumente:speichern; CE /api/v1/fuhrpark/ausgehende-dokumente/actions/speichern). parameters.beleg_typ, optional id/formular, reason. Default dryRun; execute erfordert idempotency_key. Scope logistics:write.

- **Scope:** `logistics:write`
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
    "beleg_typ": {
      "type": "string"
    },
    "id": {
      "type": "string"
    },
    "formular": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "beleg_typ",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "dokument_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `logistik.fahrzeug.loeschen` — Fahrzeug loeschen

Loescht ein Fahrzeug im Authentifizierungs-Mandanten (Maske fuhrpark/fahrzeug-stamm:loeschen; CE /api/v1/fuhrpark/fahrzeuge/{entity_id}/actions/loeschen). parameters.fahrzeug_id, reason. Cross-Tenant → 404. Default dryRun; execute erfordert idempotency_key. Scope logistics:write.

- **Scope:** `logistics:write`
- **Idempotent:** ja
- **Risikoklasse:** hoch
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "fahrzeug_id": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "fahrzeug_id",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "fahrzeug_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `logistik.fahrzeug.speichern` — Fahrzeug speichern

Legt ein Fahrzeug im Authentifizierungs-Mandanten an oder aktualisiert es (Maske fuhrpark/fahrzeug-stamm:speichern; CE /api/v1/fuhrpark/fahrzeuge/actions/speichern). parameters.kennzeichen, typ, optional id, reason. Token-Mandant; Cross-Tenant-ID → 404. Default dryRun; execute erfordert idempotency_key. Scope logistics:write.

- **Scope:** `logistics:write`
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
    "kennzeichen": {
      "type": "string"
    },
    "typ": {
      "type": "string"
    },
    "id": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "kennzeichen",
    "typ",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "fahrzeug_id": {
      "type": "string"
    },
    "kennzeichen": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `logistik.frachttabelle.anlegen` — Frachttabelle anlegen

Legt eine mandantengebundene Frachttabelle an (Maske logistik/frachttabellen:anlegen; CE /api/v1/logistik/frachttabellen/actions/anlegen). parameters.tabelle_nr, bezeichnung, optional einheit/waehrung. Default dryRun; execute erfordert idempotency_key. Scope logistics:write. Kein FIBU.

- **Scope:** `logistics:write`
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
    "tabelle_nr": {
      "type": "string"
    },
    "bezeichnung": {
      "type": "string"
    },
    "einheit": {
      "type": "string",
      "nullable": true
    },
    "waehrung": {
      "type": "string",
      "nullable": true,
      "default": "EUR"
    }
  },
  "required": [
    "tabelle_nr",
    "bezeichnung"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "tabelle_nr": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `logistik.rechnung.speichern` — Fuhrpark-Rechnung speichern

Legt eine Fuhrpark-Rechnung im Authentifizierungs-Mandanten an oder aktualisiert sie (Maske fuhrpark/rechnungen:speichern; CE /api/v1/fuhrpark/rechnungen/actions/speichern). parameters.rechnungs_nr, datum, betrag_eur, optional id, reason. Default dryRun; execute erfordert idempotency_key. Scope logistics:write.

- **Scope:** `logistics:write`
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
    "rechnungs_nr": {
      "type": "string"
    },
    "datum": {
      "type": "string"
    },
    "betrag_eur": {
      "type": "number"
    },
    "id": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "rechnungs_nr",
    "datum",
    "betrag_eur",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "rechnung_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `logistik.terminart.speichern` — Terminart speichern

Legt eine Fuhrpark-Terminart im Authentifizierungs-Mandanten an oder aktualisiert sie (Maske fuhrpark/terminarten:speichern; CE /api/v1/fuhrpark/terminarten/actions/speichern). parameters.terminart, optional id/intervall_*, reason. Default dryRun; execute erfordert idempotency_key. Scope logistics:write.

- **Scope:** `logistics:write`
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
    "terminart": {
      "type": "string"
    },
    "id": {
      "type": "string"
    },
    "intervall_monate": {
      "type": "integer"
    },
    "intervall_km": {
      "type": "integer"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "terminart",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "terminart_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `logistik.tour.anlegen` — Tour anlegen

Legt eine Tour im Authentifizierungs-Mandanten an (Maske logistik/tourenplanung:anlegen; CE /api/v1/logistik/tours/actions/anlegen). parameters.date, vehicle_id, driver_id, notes, optional delivery_note_ref (tenant-scoped Lookup), reason. Default dryRun; execute erfordert idempotency_key. Scope logistics:write. Kein tenant_id-Parameter.

- **Scope:** `logistics:write`
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
    "date": {
      "type": "string",
      "description": "ISO-Datum/Zeit"
    },
    "vehicle_id": {
      "type": "string"
    },
    "driver_id": {
      "type": "string"
    },
    "notes": {
      "type": "string"
    },
    "delivery_note_ref": {
      "type": "string"
    },
    "reason": {
      "type": "string",
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
    "tour_id": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: masks

### `mask.action.execute` — Maskenaktion ausfuehren

Fuehrt eine Maskenaktion ueber ihren deklarierten Kommando-Endpunkt aus (gleicher Umschlag wie die Maske). Gesperrt sind forbiddenForAgents, humanApprovalRequired, Command-Adapter und Eingabefluesse. Default dryRun; execute erfordert idempotency_key.

- **Scope:** `masks:write`
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
    "screen_id": {
      "type": "string"
    },
    "action": {
      "type": "string"
    },
    "entity_id": {
      "type": "string",
      "nullable": true
    },
    "input": {
      "type": "object",
      "nullable": true
    },
    "audit_reason": {
      "type": "string",
      "nullable": true
    }
  },
  "required": [
    "screen_id",
    "action"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "screen_id": {
      "type": "string"
    },
    "action": {
      "type": "string"
    },
    "mode": {
      "type": "string"
    },
    "result": {
      "type": "object"
    }
  }
}
```

### `mask.actions.list` — Maskenaktionen auflisten

Liest die Aktionen einer Maske aus der mandantengenauen ScreenDefinition, mit Eingabefeldern und Befund, ob ein Agent sie ausfuehren darf. Nur Lesen.

- **Scope:** `masks:read`
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
    "screen_id": {
      "type": "string"
    }
  },
  "required": [
    "screen_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "screen_id": {
      "type": "string"
    },
    "title": {
      "type": "string",
      "nullable": true
    },
    "actions": {
      "type": "array"
    }
  }
}
```

### `mask.data.read` — Maskendaten lesen

Liest eine deklarierte GET-Datenquelle derselben mandantengenauen Maske wie Human-UI und CLI. Fachrollen und Objektzugriff prueft der Ziel-Endpunkt erneut mit dem Token des Aufrufers; keine freie URL oder Mandantenangabe.

- **Scope:** `masks:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "screen_id": {
      "type": "string"
    },
    "source_key": {
      "type": "string"
    },
    "entity_id": {
      "type": "string",
      "nullable": true
    },
    "page": {
      "type": "integer",
      "minimum": 1,
      "maximum": 1000000
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    },
    "q": {
      "type": "string",
      "nullable": true,
      "maxLength": 200
    },
    "table_key": {
      "type": "string"
    },
    "sort": {
      "type": "string"
    },
    "sort_dir": {
      "type": "string",
      "enum": [
        "asc",
        "desc"
      ]
    },
    "complete": {
      "type": "boolean",
      "default": false
    },
    "preset_filters": {
      "type": "object",
      "maxProperties": 8,
      "propertyNames": {
        "minLength": 1,
        "maxLength": 200
      },
      "additionalProperties": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200
      }
    },
    "filter_plan": {
      "type": "object",
      "maxProperties": 20,
      "additionalProperties": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "op",
          "value"
        ],
        "properties": {
          "op": {
            "type": "string",
            "enum": [
              "eq",
              "neq",
              "contains",
              "lt",
              "lte",
              "gt",
              "gte",
              "in",
              "between"
            ]
          },
          "value": {},
          "label": {
            "type": "string",
            "nullable": true,
            "maxLength": 200
          }
        }
      }
    }
  },
  "required": [
    "screen_id",
    "source_key"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "screen_id": {
      "type": "string"
    },
    "source_key": {
      "type": "string"
    },
    "page": {
      "type": "integer"
    },
    "limit": {
      "type": "integer"
    },
    "data": {
      "oneOf": [
        {
          "type": "object"
        },
        {
          "type": "array"
        }
      ]
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

Sucht Nachweisraum-Dokumente im Authentifizierungs-Mandanten nach Typ, Zeitraum, Beleg-Referenz oder dokument_id (UUID/Bezeichnung/Referenz). Items tragen kanonische Masken-Route (/docflow/nachweisraum/{id}, Screen docflow/nachweisraum). HTTP tool_name=dms.document.search. Default dryRun; execute nur Lesen. Scope nachweisraum:read.

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
    "dokument_id": {
      "type": "string",
      "nullable": true,
      "description": "Dokument-UUID, Bezeichnung oder referenz_id"
    },
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

Gibt Status, Pruefhinweis und kanonische Masken-Route (/docflow/gobd-export/{id}, Screen docflow/gobd-export) eines GoBD-Exports im Authentifizierungs-Mandanten zurueck. HTTP tool_name=dms.gobd.export_status, parameters.export_id. Scope nachweisraum:read; nur Lesen.

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

## Domaene: platform

### `admin.postfach.speichern` — Postfach speichern

Legt ein Mandanten-Postfach an oder aendert es (Maske admin/postfaecher:speichern; CE /api/v1/admin/postfaecher/actions/speichern). parameters.kennung, absender_email, anbieter, optional postfach_id/passwort/smtp_*, reason. Passwort nie im Audit. Default dryRun; execute erfordert idempotency_key. Scope admin:write. Cross-Tenant-ID → 404.

- **Scope:** `admin:write`
- **Idempotent:** ja
- **Risikoklasse:** hoch
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kennung": {
      "type": "string"
    },
    "absender_email": {
      "type": "string"
    },
    "anbieter": {
      "type": "string",
      "enum": [
        "ionos",
        "google",
        "microsoft",
        "smtp",
        "alias"
      ]
    },
    "anmeldung": {
      "type": "string",
      "enum": [
        "passwort",
        "oauth2"
      ]
    },
    "postfach_id": {
      "type": "string"
    },
    "passwort": {
      "type": "string"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "kennung",
    "absender_email",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "postfach_id": {
      "type": "string"
    },
    "kennung": {
      "type": "string"
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

## Domaene: reporting

### `reporting.bonus.calculate` — Bonuslauf berechnen

Berechnet einen immutable Bonuslauf im Authentifizierungs-Mandanten (Maske auswertungen/bonus-berechnung:calculate; CE /api/v1/l3-report-catalog/bonus-runs/actions/calculate). parameters.report_id (bonus-by-customer|bonus-by-article-group), from_date, to_date, rate_pct, reason. Default dryRun ohne INSERT; execute erfordert idempotency_key. Scope reporting:write. Kein FIBU/FIN-CLOSE.

- **Scope:** `reporting:write`
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
    "report_id": {
      "type": "string",
      "enum": [
        "bonus-by-customer",
        "bonus-by-article-group"
      ]
    },
    "from_date": {
      "type": "string",
      "description": "ISO-Datum"
    },
    "to_date": {
      "type": "string",
      "description": "ISO-Datum"
    },
    "rate_pct": {
      "type": "number"
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "report_id",
    "from_date",
    "to_date",
    "rate_pct",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "run_id": {
      "type": "string"
    },
    "total_bonus": {
      "type": "number"
    },
    "lines": {
      "type": "integer"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `reporting.query.import_signed` — Signierte Abfrage importieren

Importiert eine HMAC-signierte Abfragedefinition (Maske auswertungen/abfrage-center:import; CE /api/v1/query-center/actions/import). parameters.bundle (schema_version/definition/signature), reason. Default dryRun nur Signaturpruefung; execute erfordert idempotency_key. Scope reporting:write. Kein beliebiges SQL.

- **Scope:** `reporting:write`
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
    "bundle": {
      "type": "object",
      "description": "Signiertes Export-Bundle"
    },
    "reason": {
      "type": "string",
      "minLength": 5
    }
  },
  "required": [
    "bundle",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "definition_id": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

## Domaene: sales

### `sales.gutschrift.buchen` — Gutschrift aus freigegebenem Vorschlag buchen

Bucht eine Gutschrift (Erloes netto, Umsatzsteuer getrennt, Forderung brutto, OP-Minderung der bezogenen Rechnung) nur aus einem agent_proposals-Datensatz (sales_credit_note_buchung), den ein Mensch freigegeben hat. Parameter nur proposal_id. Default dryRun. execute erfordert idempotency_key und approval_status=approved; hat sich die Gutschrift seit der Freigabe geaendert, HTTP 409 und neuer Vorschlag noetig. Kein Freigabe-Boolean im Aufruf. Scope sales:write. Kein tenant_id-Parameter.

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
      "description": "entwurf_id aus sales.gutschrift.propose"
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
    "credit_note_id": {
      "type": "string"
    },
    "credit_note_number": {
      "type": "string"
    },
    "netto": {
      "type": "number"
    },
    "steuer": {
      "type": "number"
    },
    "brutto": {
      "type": "number"
    },
    "posted": {
      "type": "boolean"
    },
    "approved_by": {
      "type": "string"
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

### `sales.gutschrift.propose` — Buchung einer Gutschrift vorschlagen

Legt einen ausstehenden Buchungsvorschlag fuer eine Gutschrift (Entwurf) im Authentifizierungs-Mandanten an. parameters.credit_note_id. Default dryRun liest, was gebucht wuerde (Erloes netto, Umsatzsteuer, Forderung brutto, Buchungszeilen) oder den Pruefgrund (HTTP 409), wenn sich die Gutschrift nicht buchen laesst. propose (mit idempotency_key) speichert agent_proposals (sales_credit_note_buchung) mit approval_status pending und bucht nicht. execute ist nicht angebunden. Ein Mensch prueft und gibt in der Maske sales/gutschrift frei; danach sales.gutschrift.buchen. Ein Freigabe-Boolean im Aufruf wird abgewiesen. Scope sales:write. Kein tenant_id-Parameter.

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
    "credit_note_id": {
      "type": "string",
      "description": "ID der Gutschrift (Entwurf)"
    }
  },
  "required": [
    "credit_note_id"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "entwurf_id": {
      "type": "string",
      "description": "proposal_id fuer sales.gutschrift.buchen"
    },
    "credit_note_id": {
      "type": "string"
    },
    "credit_note_number": {
      "type": "string"
    },
    "netto": {
      "type": "number"
    },
    "steuer": {
      "type": "number"
    },
    "brutto": {
      "type": "number"
    },
    "buchungszeilen": {
      "type": "array"
    },
    "route_path": {
      "type": "string"
    },
    "screen_id": {
      "type": "string"
    },
    "approval_status": {
      "type": "string"
    }
  }
}
```

### `sales.gutschrift.speichern` — Gutschrift als Entwurf speichern

Legt eine Gutschrift (kaufmaennische Rechnungskorrektur) als Entwurf im Authentifizierungs-Mandanten an (Maske sales/gutschrift:speichern; CE /api/v1/sales/credit-notes/actions/speichern). parameters.credit_note_number, customer_id, grund, lines[] mit description, quantity, unit_price und tax_code (Steuerschluessel des Mandanten aus finance/tax-keys; kein Prozentsatz, kein Vorgabewert), optional invoice_reference, reason. Default dryRun liefert Netto/Umsatzsteuer/Brutto oder den Pruefgrund. execute erfordert idempotency_key. Gebucht wird NICHT: Buchen geht nur ueber sales.gutschrift.propose, menschliche Freigabe und sales.gutschrift.buchen. Scope sales:write. Kein tenant_id-Parameter.

- **Scope:** `sales:write`
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
    "credit_note_number": {
      "type": "string"
    },
    "customer_id": {
      "type": "string"
    },
    "customer_name": {
      "type": "string"
    },
    "invoice_reference": {
      "type": "string",
      "description": "Rechnungsnummer, deren offener Posten beim Buchen gemindert wird"
    },
    "grund": {
      "type": "string",
      "description": "Grund der Gutschrift, z. B. Retoure"
    },
    "lines": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "properties": {
          "description": {
            "type": "string"
          },
          "quantity": {
            "type": "number"
          },
          "unit_price": {
            "type": "number",
            "description": "Einzelpreis netto"
          },
          "tax_code": {
            "type": "string",
            "description": "Steuerschluessel des Mandanten"
          }
        },
        "required": [
          "description",
          "quantity",
          "unit_price"
        ]
      }
    },
    "reason": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": [
    "credit_note_number",
    "customer_id",
    "grund",
    "lines",
    "reason"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "credit_note_id": {
      "type": "string"
    },
    "credit_note_number": {
      "type": "string"
    },
    "netto": {
      "type": "number"
    },
    "steuer": {
      "type": "number",
      "nullable": true
    },
    "brutto": {
      "type": "number",
      "nullable": true
    },
    "pruefgrund": {
      "type": "string",
      "nullable": true
    },
    "auditEntryId": {
      "type": "string"
    }
  }
}
```

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

Gibt Lifecycle-Status, offene Positionen, naechsten Schritt und kanonische Masken-Route (/sales/order-editor/{id}, Screen sales/sales-order) eines Auftrags im Authentifizierungs-Mandanten zurueck. HTTP-Aufruf mit tool_name=sales.order.status, parameters.auftrag_nr (Auftragsnummer oder UUID). Default dryRun; execute ist ebenfalls nur Lesen. OIDC-Token mit sales:read und tenant_id erforderlich.

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

## Domaene: studio

### `studio.migration.plan` — Studio-Aenderungsplan festhalten

Versionierter Authoring-Command: erzeugt nur einen revisionsgebundenen Plan in der vorhandenen Historie; keine Freigabe, Schemaausfuehrung oder Geschaeftsbuchung. Fachrollen prueft derselbe HTTP-Endpunkt wie Human-UI/CLI.

- **Scope:** `belege:write`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/mcp/tools/call`

**Eingabe-Schema:**

```json
{
  "$defs": {
    "StudioColumnIn": {
      "additionalProperties": false,
      "properties": {
        "name": {
          "pattern": "^[a-z][a-z0-9_]{0,47}$",
          "title": "Name",
          "type": "string"
        },
        "type": {
          "enum": [
            "text",
            "integer",
            "boolean",
            "date",
            "datetime",
            "decimal",
            "uuid"
          ],
          "title": "Type",
          "type": "string"
        },
        "nullable": {
          "default": true,
          "title": "Nullable",
          "type": "boolean"
        }
      },
      "required": [
        "name",
        "type"
      ],
      "title": "StudioColumnIn",
      "type": "object"
    },
    "StudioSchemaChangeIn": {
      "additionalProperties": false,
      "properties": {
        "operation": {
          "enum": [
            "create_table",
            "add_columns"
          ],
          "title": "Operation",
          "type": "string"
        },
        "schema_name": {
          "pattern": "^domain_[a-z][a-z0-9_]{0,35}$",
          "title": "Schema Name",
          "type": "string"
        },
        "table": {
          "pattern": "^[a-z][a-z0-9_]{0,47}$",
          "title": "Table",
          "type": "string"
        },
        "columns": {
          "items": {
            "$ref": "#/$defs/StudioColumnIn"
          },
          "maxItems": 50,
          "minItems": 1,
          "title": "Columns",
          "type": "array"
        }
      },
      "required": [
        "operation",
        "schema_name",
        "table",
        "columns"
      ],
      "title": "StudioSchemaChangeIn",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "draft_id": {
      "format": "uuid",
      "title": "Draft Id",
      "type": "string"
    },
    "expected_revision": {
      "pattern": "^[0-9a-f]{64}$",
      "title": "Expected Revision",
      "type": "string"
    },
    "schema_changes": {
      "items": {
        "$ref": "#/$defs/StudioSchemaChangeIn"
      },
      "maxItems": 20,
      "title": "Schema Changes",
      "type": "array"
    }
  },
  "required": [
    "draft_id",
    "expected_revision"
  ],
  "title": "StudioPlanParameters",
  "type": "object"
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object"
}
```

## Domaene: workspace

### `workspace.fachaktion.katalog` — Fachaktionskatalog Adaptive Workspace

Liefert den typisierten Fachaktionskatalog (permission, idempotency, audit, event-out, Aliase) aus config/adaptive_workspace_fachaktionen.yaml. Nur Lesen. parameters.access optional read|write. Scope agent:read. Kein tenant_id-Parameter.

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
    "access": {
      "type": "string",
      "enum": [
        "read",
        "write"
      ],
      "description": "Optionaler Filter"
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
    "registry_id": {
      "type": "string"
    },
    "count": {
      "type": "integer"
    },
    "actions": {
      "type": "array"
    },
    "lead_contract": {
      "type": "object"
    },
    "event_gaps": {
      "type": "array"
    }
  }
}
```

### `workspace.fachaktion.resolve` — Kurzkommando auf Fachaktion aufloesen

Mappt ein natuerliches Kurzkommando deterministisch (Alias/Action-ID, kein LLM) auf eine typisierte Fachaktion und prueft Scope sowie Agenten-/Vier-Augen-Grenze. Nur Lesen, keine Ausfuehrung. parameters.command. Scope agent:read; die Zielaktion hat zusaetzlich ihre Fach-Scope. Writes werden nicht ausgeloest.

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
    "command": {
      "type": "string",
      "description": "Kurzkommando oder Action-ID"
    }
  },
  "required": [
    "command"
  ]
}
```

**Ausgabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "action_id": {
      "type": "string",
      "nullable": true
    },
    "authorized": {
      "type": "boolean"
    },
    "reason": {
      "type": "string"
    },
    "mcp_tool_id": {
      "type": "string",
      "nullable": true
    },
    "four_eyes": {
      "type": "boolean"
    },
    "command_endpoint": {
      "type": "string",
      "nullable": true
    }
  }
}
```

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

Registry `MCP-ERP-TOOLS-001` (Schema 1.0) — 12 Tools in 6 Domaenen.

## Uebersicht

| Tool | Domaene | Scope | Idempotent | Risiko | Human-Approval |
|---|---|---|---|---|---|
| `compliance.gate.status` | compliance | `compliance:read` | ja | niedrig | nein |
| `crm.contact.log` | crm | `crm:write` | nein | mittel | nein |
| `crm.customer.search` | crm | `crm:read` | ja | niedrig | nein |
| `crm.customer.summary360` | crm | `crm:read` | ja | niedrig | nein |
| `dms.document.search` | nachweisraum | `nachweisraum:read` | ja | niedrig | nein |
| `dms.gobd.export_status` | nachweisraum | `nachweisraum:read` | ja | niedrig | nein |
| `fibu.dunning.status` | finance | `finance:read` | ja | niedrig | nein |
| `fibu.open_items.list` | finance | `finance:read` | ja | niedrig | nein |
| `sales.invoice.propose` | sales | `sales:write` | nein | hoch | ja |
| `sales.order.status` | sales | `sales:read` | ja | niedrig | nein |
| `wms.cell.status` | inventory | `inventory:read` | ja | niedrig | nein |
| `wms.lot.trace` | inventory | `inventory:read` | ja | niedrig | nein |

## Domaene: compliance

### `compliance.gate.status` — Externe Gate-Status abfragen

Gibt Status ausstehender externer Abnahmen (ELSTER, DATEV, TSE, Auditor) zurueck.

- **Scope:** `compliance:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/compliance/external-gates`

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
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "gate_id": {
        "type": "string"
      },
      "gate_typ": {
        "type": "string"
      },
      "status": {
        "type": "string"
      },
      "faellig_am": {
        "type": "string",
        "nullable": true
      }
    }
  }
}
```

## Domaene: crm

### `crm.contact.log` — Kontaktprotokoll erfassen

Erfasst einen Kundenkontakt (Anruf, E-Mail, Besuch) mit Ergebnis und Wiedervorlage.

- **Scope:** `crm:write`
- **Idempotent:** nein
- **Risikoklasse:** mittel
- **Audit:** write
- **Human-Approval erforderlich:** nein
- **Endpoint:** `POST /api/v1/crm/kontakte`

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

### `crm.customer.search` — Kunden suchen

Sucht Kunden anhand von Name, Kundennummer oder PLZ. Gibt eine Liste von Kunden zurueck.

- **Scope:** `crm:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/kunden?search={query}&limit={limit}`

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
      "default": 20
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
        "type": "string"
      },
      "segment": {
        "type": "string"
      }
    }
  }
}
```

### `crm.customer.summary360` — Kunden-360-Zusammenfassung

Liefert 360-Grad-Zusammenfassung: offene Auftraege, letzte Kontakte, OP-Saldo, Segmentierung.

- **Scope:** `crm:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/crm/kunden/{kunden_nr}/360`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string"
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
      "type": "string"
    }
  }
}
```

## Domaene: finance

### `fibu.dunning.status` — Mahnstatus abfragen

Gibt Mahnstatus und letzte Mahnaktionen fuer einen Kunden zurueck.

- **Scope:** `finance:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/dunning/status/{kunden_nr}`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "kunden_nr": {
      "type": "string"
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

Listet offene Forderungen oder Verbindlichkeiten nach Faelligkeit.

- **Scope:** `finance:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/open-items?typ={typ}&faellig_bis={faellig_bis}&limit={limit}`

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
      "default": 50
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
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "beleg_nr": {
        "type": "string"
      },
      "kunden_nr": {
        "type": "string"
      },
      "betrag_eur": {
        "type": "number"
      },
      "faellig_am": {
        "type": "string"
      },
      "mahnstatus": {
        "type": "string"
      }
    }
  }
}
```

## Domaene: inventory

### `wms.cell.status` — Silozellen-Status

Gibt Fuellstand, Artikel, QS-Status und Sperren einer Silozelle zurueck.

- **Scope:** `inventory:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/silo/cells/{cell_code}/status`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "cell_code": {
      "type": "string"
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

Gibt Herkunft, Silozelle, QS-Status und Bewegungshistorie eines Lots zurueck.

- **Scope:** `inventory:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/inventory/lots/{lot_id}/trace`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "lot_id": {
      "type": "string"
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
      "type": "string"
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

## Domaene: nachweisraum

### `dms.document.search` — Dokument suchen

Sucht Dokumente im Nachweisraum nach Typ, Zeitraum oder Beleg-Referenz.

- **Scope:** `nachweisraum:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/nachweisraum/dokumente`

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
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "dokument_id": {
        "type": "string"
      },
      "titel": {
        "type": "string"
      },
      "status": {
        "type": "string"
      },
      "erstellt_am": {
        "type": "string"
      }
    }
  }
}
```

### `dms.gobd.export_status` — GoBD-Export-Status

Gibt Status und Pruefprotokoll eines GoBD-Exports zurueck.

- **Scope:** `nachweisraum:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/nachweisraum/gobd-exporte/{export_id}`

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

## Domaene: sales

### `sales.invoice.propose` — Rechnungsvorschlag aus Lieferschein

Erzeugt einen Rechnungs-Entwurf aus einem abgeschlossenen Lieferschein. Erfordert Human Approval.

- **Scope:** `sales:write`
- **Idempotent:** nein
- **Risikoklasse:** hoch
- **Audit:** write
- **Human-Approval erforderlich:** ja
- **Endpoint:** `POST /api/v1/sales-invoices/propose`

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

Gibt Lifecycle-Status, offene Positionen und naechsten Schritt eines Auftrags zurueck.

- **Scope:** `sales:read`
- **Idempotent:** ja
- **Risikoklasse:** niedrig
- **Audit:** read
- **Human-Approval erforderlich:** nein
- **Endpoint:** `GET /api/v1/sales-orders/{auftrag_nr}/status`

**Eingabe-Schema:**

```json
{
  "type": "object",
  "properties": {
    "auftrag_nr": {
      "type": "string"
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

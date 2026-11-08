"""DATEV export preserves the existing guarded read API and its server-created file."""


def build_datev_export() -> dict:
    return {
        "schemaVersion": 1, "id": "finance/datev-export", "domain": "finance",
        "mode": "list", "title": "DATEV-Export",
        "subtitle": "Vereinfachter Buchungsstapel offener Posten. Kein zertifizierter EXTF; finale DATEV-/Steuerberaterabnahme erforderlich.",
        "adapter": {"type": "native", "sourceId": "finance/datev-export", "temporary": False},
        "dataSources": [{"key": "export-" + typ, "endpoint": "/api/v1/finance/datev-export?typ=" + typ}
                        for typ in ("alle", "debitor", "kreditor")], "tables": [],
        "actions": [{
            "key": "export_erstellen", "label": "Export erstellen", "kind": "primary",
            "dangerLevel": "safe", "permission": "finance.datev.export", "localEffect": "download",
            "download": {"endpoint": "/api/v1/finance/datev-export", "contentField": "csv",
                         "filenameField": "filename", "mediaType": "text/csv;charset=utf-8"},
            "inputFields": [{"key": "typ", "label": "Buchungsstapel-Typ", "type": "select", "required": True,
                             "options": [{"value": "alle", "label": "Alle"},
                                         {"value": "debitor", "label": "Debitoren"},
                                         {"value": "kreditor", "label": "Kreditoren"}]}],
        }],
        "noWorkflowReason": "Der bestehende GET-Export liest offene Posten ohne Buchungswirkung; Auswahl, Vorschau und Dateidownload gehoeren zusammen.",
        "agentContract": {"businessPurpose": "Offene Posten als vereinfachte DATEV-CSV ausgeben.",
                          "examplePrompts": ["Exportiere die offenen Debitorenposten fuer DATEV."],
                          "sensitiveFields": ["csv"],
                          "testSelectors": {"screenRoot": "[data-testid='screen-finance/datev-export']"}},
        "layout": {"floorplan": "worklist", "density": "compact", "contextRail": "none", "tableProfile": "financial"},
    }

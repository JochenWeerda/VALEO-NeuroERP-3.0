"""Meridian controls for explicit harvest rules and financial evidence."""
BASE = "/api/v1/agrar/harvest-acceptance"
CONTROL = BASE + "/settlement-controls"
COMMAND_PATHS = {
    "create_rule": CONTROL + "/rules", "approve_rule": CONTROL + "/rules/{version_id}/approve",
    "revoke_rule": CONTROL + "/rules/{version_id}/revoke",
    "bind_rule": CONTROL + "/acceptances/{acceptance_id}/bind-rule",
    "attest": CONTROL + "/acceptances/{acceptance_id}/attest-measurement",
    "calculate": BASE + "/{acceptance_id}/calculate",
    "approve_calculation": CONTROL + "/acceptances/{acceptance_id}/approve-calculation",
    "release": BASE + "/{acceptance_id}/release?release_status=final&create_stock_movement=true&create_credit_note=true",
}


def build_harvest_controls():
    def field(key, label, kind="text", **extra):
        return {"key": key, "label": label, "type": kind, **extra}
    def lookup(key, label, source):
        return field(key, label, "lookup", dataSourceKey=source, minSearchChars=2)
    actions = []
    labels = {"create_rule": "Regelversion erstellen", "approve_rule": "Regel genehmigen",
              "revoke_rule": "Regelgenehmigung widerrufen", "bind_rule": "Regel an Annahme binden",
              "attest": "Messnachweis bestätigen", "calculate": "Verbindlich berechnen",
              "approve_calculation": "Berechnungsfassung genehmigen", "release": "Gutschrift und Wareneingang erzeugen"}
    for key, path in COMMAND_PATHS.items():
        critical = key in {"approve_rule", "revoke_rule", "approve_calculation", "release"}
        inputs = []
        if critical:
            inputs.append(field("confirm_execution", "Genau diese geprüfte Fassung ausführen", "select", required=True,
                                options=[{"value": "confirm", "label": "Ja, genau diesen Vorgang ausführen"}]))
        if key in {"approve_rule", "revoke_rule", "approve_calculation"}:
            inputs.append(field("reason", "Prüfvermerk / Begründung", "textarea", required=True))
        if key in {"approve_rule", "approve_calculation"}:
            inputs.append(field("expires_at", "Genehmigung gültig bis (Ortszeit)", "datetime", required=True))
        actions.append({"key": key, "label": labels[key], "command": "harvest.control." + key,
            "commandEndpoint": path, "method": "POST", "permission": key,
            "commandBinding": {"adapter": "harvest.control.v1", "command": key, "preview": False},
            "kind": "primary" if key == "calculate" else "secondary", "zone": "header",
            "dangerLevel": "high" if critical else "moderate", "requiresConfirmation": critical,
            "auditReasonRequired": key in {"approve_rule", "revoke_rule", "approve_calculation"},
            "forbiddenForAgents": True, "humanApprovalRequired": critical, "inputFields": inputs})
    actions.insert(0, {"key": "refresh", "label": "Annahme und Nachweise laden", "kind": "secondary", "zone": "header",
                       "dangerLevel": "safe", "permission": "refresh", "localEffect": "navigation", "command": "harvest.control.refresh"})
    return {"schemaVersion": 1, "id": "agrar/harvest-controls", "domain": "agrar", "mode": "workflow",
        "title": "Ernte-Abrechnung: Vertragsregeln und Freigaben",
        "subtitle": "Regelversion wählen, Messnachweis bestätigen, berechnen und durch eine zweite Person genehmigen lassen.",
        "adapter": {"type": "native", "sourceId": "agrar/harvest-controls", "temporary": False},
        "fields": [lookup("acceptance_id", "Annahme suchen", "acceptances"),
                   field("control_status", "Aktueller Nachweisstand", readOnly=True),
                   field("calculation_hash", "Geprüfte Berechnungsfassung", readOnly=True),
                   *[field(key, label, "currency", readOnly=True) for key, label in [
                       ("net_amount", "Geprüftes Netto"), ("vat_amount", "Geprüfte Steuer"), ("gross_amount", "Geprüftes Brutto")]]],
        "dataSources": [{"key": "rules", "endpoint": CONTROL + "/rules", "pageSize": 25, "staleTimeMs": 0},
            *[{"key": key, "endpoint": CONTROL + "/choices/" + kind, "minSearchChars": 2, "pageSize": 25}
              for key, kind in [("acceptances", "acceptance"), ("customers", "customer"), ("articles", "article"), ("contracts", "contract")]]],
        "tabs": [{"key": "rules", "label": "Vertragsfassungen", "fields": [
            field("rule_id", "Regelbezeichnung"), lookup("customer_id", "Kunde / Lieferant", "customers"),
            lookup("article_id", "Artikel", "articles"), lookup("contract_id", "Kontrakt (optional)", "contracts"),
            field("valid_from", "Vertraglich gültig ab", "date"), field("valid_until", "Vertraglich gültig bis", "date"),
            field("source_reference", "Vertragsgrundlage / Fundstelle"),
            field("measurement_method", "Untersuchungsmethode"), field("measurement_method_version", "Methodenfassung"),
            field("impurities_free_pct", "Vereinbarter abzugsfreier Besatz (%)", "percentage"),
            field("quality_limit_pct", "Qualitätsgrenze Besatz (%) – keine Freigrenze", "percentage"),
        ], "tables": [{"key": "rules", "label": "Unveränderliche Regelversionen – Zeile zum Prüfen auswählen",
            "dataSourceKey": "rules", "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 44,
            "rowActions": [{"key": "inspect_rule", "label": "Regelversion prüfen", "command": "harvest.control.inspect_rule"}],
            "columns": [{"key": key, "label": label, "width": width} for key, label, width in [
                ("rule_id", "Regel", 170), ("rule_version", "Fassung", 80),
                ("status", "Genehmigung", 110), ("impurities_free_pct", "Abzugsfrei (%)", 110),
                ("quality_limit_pct", "Qualitätsgrenze (%)", 120),
                ("measurement_method", "Methode", 160), ("measurement_method_version", "Methodenfassung", 110),
                ("valid_from", "Gültig ab", 110), ("valid_until", "Gültig bis", 110),
                ("source_reference", "Grundlage", 200), ("created_by", "Urheber", 170)]]}]},
            {"key": "calculation", "label": "Berechnungspositionen", "tables": [{"key": "positions",
                "label": "Konkrete Berechnungsfassung – bei veraltetem Nachweis nicht freigabefähig", "pageSize": 25,
                "virtualized": True, "rowHeight": 44, "columns": [{"key": key, "label": label, "width": width}
                    for key, label, width in [("position_number", "Position", 80), ("description", "Berechnung", 220),
                        ("quantity_kg", "Menge (kg)", 120), ("quantity_pct", "Anteil (%)", 100),
                        ("amount_eur", "Betrag (EUR)", 120), ("calculation_formula", "Grundlage / Regelversion", 320)]]}]},
            {"key": "measurement", "label": "Messung und Freigabe", "fields": [
                field("measurement_source", "Messbericht / Nachweisquelle"),
                field("acknowledge_quality_exception", "Qualitätsabweichung für genau diese Berechnung geprüft", "boolean"),
                field("quality_note", "Qualitätsbewertung", readOnly=True),
            ]}],
        "actions": actions,
        "layout": {"floorplan": "cockpit", "density": "expertDense", "contextRail": "audit", "tableProfile": "audit"},
        "performance": {"initialPayloadBudgetKb": 64, "requiresLazyTabs": True, "requiresVirtualTables": True,
                        "lookupMinChars": 2, "bundleGroup": "agrar"},
        "noWorkflowReason": "Verbindliche Zustands- und Vier-Augen-Prüfung erfolgt in den versionierten Domain-Commands.",
        "agentContract": {"businessPurpose": "Vertragsregeln und konkrete Ernte-Abrechnungsfassungen nachvollziehbar prüfen.",
            "sensitiveFields": ["customer_id", "source_reference"], "editableFields": [],
            "forbiddenAgentTasks": ["Genehmigungen selbst erteilen", "Mess- oder Berechnungsnachweise überschreiben"]}}


HARVEST_CONTROL_BUILDERS = {"agrar/harvest-controls": build_harvest_controls}

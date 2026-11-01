"""Native finance workbenches: declared fields and guarded human actions."""
from typing import Any


def _field(key: str, label: str, kind: str = "text", *, read_only: bool = True) -> dict[str, Any]:
    return {"key": key, "label": label, "type": kind, "readOnly": read_only}


def _action(key: str, label: str, endpoint: str | None = None, method: str = "POST", *, primary: bool = False, surface_only: bool = False) -> dict[str, Any]:
    action: dict[str, Any] = {"key": key, "label": label, "kind": "primary" if primary else "secondary", "dangerLevel": "safe", "forbiddenForAgents": True}
    if endpoint:
        action.update(permission=f"studio.finance-workbench.{key}", inputFlow={"kind": "humanForm", "submitEndpoint": endpoint, "method": method})
    else:
        action["localEffect"] = "download" if key == "export" else "view"
    if surface_only:
        action["surfaceOnly"] = True
    return action


def _screen(screen_id: str, title: str, fields: list[dict[str, Any]], actions: list[dict[str, Any]], sources: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "schemaVersion": 1, "id": screen_id, "domain": "finance", "mode": "cockpit",
        "title": title, "subtitle": "Finanzbuchhaltung",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {"floorplan": "cockpit", "density": "expertDense", "contextRail": "combined", "tableProfile": "financial"},
        "fields": fields, "actions": actions,
        "dataSources": [{"key": key, "endpoint": endpoint, "staleTimeMs": 15000} for key, endpoint in sources],
        "specialized": {"type": "finance_workbench", "id": screen_id},
        "workflow": {"processKey": "finance-to-close", "status": "operator-workspace", "auditRequired": True},
        "performance": {"initialPayloadBudgetKb": 100, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
        "agentContract": {"businessPurpose": title, "examplePrompts": ["Welche Eingaben und Aktionen sind verfügbar?"], "sensitiveFields": [field["key"] for field in fields], "forbiddenAgentTasks": ["Fachaktionen ausführen"], "testSelectors": {"screenRoot": f"[data-testid='native-cockpit-{screen_id.replace('/', '-')}']"}},
    }


def build_bank_workbench() -> dict[str, Any]:
    fields = [_field("kontoId", "Bankkonto", read_only=False), _field("camtFile", "Kontoauszug", "file", read_only=False)]
    fields += [_field(key, label) for key, label in [("statementId", "Statement"), ("startSaldo", "Startsaldo"), ("endSaldo", "Endsaldo"), ("gebuchteUmsaetze", "Umsätze"), ("zugeordnet", "Zugeordnet"), ("nichtZugeordnet", "Nicht zugeordnet"), ("abgleichsDifferenz", "Differenz"), ("accountingBalance", "Hauptbuchsaldo"), ("zuordnungData", "Umsatzzeilen"), ("importErrors", "Importprotokoll"), ("differences", "Differenzen"), ("comparisonState", "Nachweisstatus")]]
    return _screen("finance/bank-abgleich", "Bankabgleich", fields, [
        _action("import", "Kontoauszug importieren", "/api/v1/finance/bank-statements/import"),
        _action("validate", "Salden vergleichen", "/api/v1/finance/bank-reconciliation/{statement_id}/reconcile", primary=True),
        _action("export", "Umsatzzeilen exportieren"),
    ], [])


def build_dunning_workbench() -> dict[str, Any]:
    fields = [_field(key, label) for key, label in [("op_id", "Posten"), ("rechnungsnr", "Rechnung"), ("partner", "Partner"), ("tage_ueberfaellig", "Überfällig"), ("offen", "Offen"), ("aktuelle_stufe", "Aktuelle Stufe"), ("naechste_stufe", "Nächste Stufe"), ("dunning_fee", "Gebühr"), ("interest", "Zinsen"), ("total_amount", "Gesamt"), ("id", "Mahnung"), ("stufe", "Stufe"), ("gesamt", "Gesamtbetrag"), ("frist", "Frist"), ("datum", "Datum"), ("status", "Status"), ("versand_art", "Versandart"), ("empfaenger", "Empfänger")]]
    fields.append(_field("auswahl", "Auswahl", "boolean", read_only=False))
    return _screen("mahnwesen/mahnlauf", "Mahnlauf", fields, [
        _action("refresh", "Aktualisieren"),
        _action("run", "Mahnlauf ausführen", "/api/v1/finance/mahnlauf/run", primary=True),
        _action("sendEmail", "Per E-Mail senden", "/api/v1/finance/dunning/{id}/send", "PUT", surface_only=True),
        _action("sendPost", "Postversand festhalten", "/api/v1/finance/dunning/{id}/send", "PUT", surface_only=True),
    ], [("candidates", "/api/v1/finance/mahnlauf/candidates"), ("notices", "/api/v1/finance/mahnlauf/notices")])

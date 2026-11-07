# MCP-Zeilencommands: unabhaengige Freigabepruefung

Der laufende Arbeitsstand ist noch nicht abgenommen. Zwei konkrete Sicherheitsbefunde muessen vor Freigabe geschlossen werden:

1. Der generische Maskenadapter muss unbekannte Schreibendpunkte standardmaessig ablehnen. Das globale masks:write und Rollen am Ziel ersetzen keine ausdrueckliche Capability-Freigabe. Registrierung, Endpunkt, Domain-Command und Version muessen eindeutig sein; unvollstaendige, doppelte oder deaktivierte Eintraege duerfen nicht freigeben.
2. Die Capability-Rollenpruefung muss am authentifizierten MCP-Dispatch vor jeder Weiterleitung greifen, auch wenn das weitergereichte Token eine menschliche Identitaet besitzt. Ein frei gesetzter Kanalheader ist kein vertrauenswuerdiger Nachweis. Direkte menschliche REST-Bedienung behaelt ihre bestehende Fachrollenpruefung; deklarierte Agenten werden zusaetzlich im Domain-Command kontrolliert.

Erforderliche Negativnachweise: unbekanntes Ziel, doppelte Registrierung, falsche Version, deaktivierte Freigabe, fehlende spezifische Rolle trotz globalem Scope und menschlichem Token. Jeder dieser Faelle muss vor HTTP-Weiterleitung abgewiesen werden. Lesende readView-Aktionen bleiben getrennt; widerspruechliche Schreib-/Lesedeklarationen sind bereits bei Definition/Validierung abzuweisen.

Dieser Bericht dokumentiert Reviewanforderungen und ist kein bestandener Ausfuehrungsnachweis. Der verantwortliche Slice ist MCP-ROW-COMMANDS-20261107; Implementierung und Tests laufen dort weiter.

## Zweites lesendes Review: Personal-Versionierung

Die drei Personal-Tabellen verwenden TIMESTAMPTZ. Die API-Serialisierung erhaelt Mikrosekunden; die Masken geben updated_at als Originalstring weiter und wandeln ihn nicht durch JavaScript Date in Millisekunden um. Der Command normalisiert die Zeitzone und vergleicht unter Zeilensperre. Der Replayvertrag bindet Mandant, Aktion, Schluessel, Akteur und normalisierten Payload. Im gelesenen Zwischenstand wurde hierbei kein konkreter Fehler gefunden. Dies ersetzt weder PostgreSQL- noch HTTP-/Oberflaechentests. Die vorhandenen PostgreSQL-Fixtures ohne ausdrueckliche Anwendungsrolle belegen SQL-Mandantenpraedikate, keine RLS-Wirkung.

## Alias- und Versionskorrektur

Lead hat den weiterhin vorhandenen globalen Eindeutigkeitszwang fuer Endpunkt/Command entfernt: explizite Screen-Aliase duerfen dieselbe Fachaktion teilen. Die Bindung je Screen und Aktion muss weiterhin eindeutig sein; widerspruechliche Eintraege sperren. Der Commandname muss zur freigegebenen Version v1 passen. Die bestehende Negativsuite samt neuem Alias-/Versionstest besteht mit 19 Tests. Dieser Nachweis ist keine pauschale Freigabe der noch deaktivierten Fachaktionen.

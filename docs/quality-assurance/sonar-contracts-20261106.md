---
title: Gezielte Sonar-Vertragskorrekturen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: in Arbeit
last_reviewed: 2026-11-06
---

# Befund und Korrektur

Der Lauf 42179275386 scheiterte nach erfolgreichem Analyseupload am Sonar-Quality-Gate. Das Joblog belegt keinen Speicherabbruch. Gemeldet wurden Reliability D, Security B und 67,5 Prozent New-Code-Coverage bei geforderten 80 Prozent. Bezugszeitraum ist previous_version seit April 2026.

Zwei synthetische URL-Parserbasen verwenden jetzt HTTPS. Die Navigation liefert weiterhin lokale Pfad-/Query-/Fragmentbestandteile. Im Workspace-Parser ist eine identische Bedingungsverzweigung entfernt; die nachfolgende Vertragsvalidierung bleibt massgeblich.

Gesondert offen: weitere Sonar-Befunde, Coverage-Luecken, risikobasierte CI-Auswahl sowie authentifizierte Studio-Browser-/Kontrastabnahme. SSE-Herkunftsvertrag und Zeilenaktionskatalog sind im Nachlauf korrigiert. Keine pauschale Wiederholung bereits erfolgreicher Gesamtsuiten zur Abnahme dieser drei lokalen Aenderungen.

Abnahme: Drei bestehende Testsuiten, 16 Tests bestanden. git diff --check gruen. Sonar-Neubewertung dieser Korrekturen steht aus.

## SSE-Zielvertrag

appendSseAuthToken und SSEClient verwenden dieselbe Herkunftspruefung. Tokenziele sind auf die aktuelle Origin und die explizit beim Build konfigurierte VITE_MCP_EVENTS_URL-Origin begrenzt. Fremde, fehlerhafte und URL-Credentials enthaltende Ziele werden abgewiesen. HTTPS-Seiten duerfen keinen HTTP-Downgrade ausloesen. Explizite lokale HTTP-Entwicklung bleibt geprueft moeglich. Ohne den angeforderten Token oeffnet SSEClient keine Verbindung.

Fuenfzehn gezielte Regressionen bestanden, einschliesslich Encoding, fremder Origin, fehlendem Token, HTTPS-Downgrade und konfigurierter lokaler API. Vollstaendige Typpruefung gruen. Absolute Konfigurationen brauchen kuenftig die explizite Build-Origin; dynamische Drittziele erhalten kein Token.

Unabhaengiges Review: fehlender Token wird mit begrenztem Backoff erneut geprueft, stop entfernt den Timer; keine parallelen Retry-Timer. Same-Origin bleibt bei fehlerhafter Fremdzielkonfiguration nutzbar, relative Pfade beziehen sich auf location.href.

Browser: aktuellen Vite-Stand auf 3001 gestartet, Anmeldung sichtbar und SSO ueber localhost erfolgreich bis zum Keycloak-Anmeldeformular verfolgt. 127.0.0.1 ist kein freigegebener Callback-Host und wurde durch den konfigurierten localhost ersetzt; keine Authentifizierung aufgeweicht. Keine authentifizierte Webhook-/Kontrastabnahme behauptet.

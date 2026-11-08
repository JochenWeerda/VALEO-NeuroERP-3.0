---
title: Quality Gate Masken- und Personalvertraege
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Sechs aus der CI-Vollsuite belegte Vertragsregressionen ohne Gate-Ausnahme korrigieren.
---

# Masken- und Personalvertraege

Quality Gate [38124045945](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38124045945)
auf af25b5fdf erreichte erstmals wieder die ganze Backend-Suite:
17296 bestanden, sechs fehlgeschlagen, 198 uebersprungen, ein xfailed;
Abdeckung 70,87 Prozent bei unveraenderter Schwelle 60. Die vorherigen
MCP-Referenz- und physischen Katalogpruefungen waren erfolgreich. Alle anderen
unabhaengigen Jobs einschliesslich Frontend, WCAG, Dependency- und Secret-Scan
waren gruen. Docker und Sonar wurden wegen des Backendfehlers uebersprungen.

## Korrekturen

- Fuenf Fuhrpark-Schreibaktionen deklarieren logistics:write, drei Personal-
  Trainingsaktionen hr:write entsprechend den bestehenden MCP-Vertraegen.
  Die strenge native Readiness bleibt erhalten; Metadaten verleihen keine Rechte.
- Die drei inzwischen ausfuehrbaren Trainingscommands verlieren die alte,
  widerspruechliche Stub-Markierung. Bestehende Endpoints bleiben unveraendert.
- Der Human-Flow-Test prueft die vier verbleibenden bekannten Eingaben und
  jeden weiteren deklarierten Eingabevertrag. Die fuenf migrierten Personal-
  Aktionen werden separat gegen tatsaechlich registrierte POST-Routen geprueft.
- Die beiden neuen Bewerbungs-/Fassungscommands werden in der vollstaendigen
  Rollenmatrix vor DB-Zugriff geprueft: Bewerbung schreiben, Fassung administrieren.
- Jeder Personalweg behalt ein konkretes Antwortmodell. Nur die zwei explizit
  benannten Commands nutzen den zentralen MaskActionResult; nur der bestehende
  DELETE einer Bewerbung mit HTTP 204 hat kein Antwortmodell. Keine pauschale
  Modell- oder Routenfreigabe.
- Die Fassungsinventur kennt auch den neuen POST-Command. Aendern/Loeschen
  bestehender Fassungen bleiben durch die vollstaendige Methodenliste ausgeschlossen.

Generiertes Prozessmanifest aus isolierter committed Quelle nachgezogen,
fremde Arbeitsfassung erhalten. Alle 13 Dokumentationsgeneratorpruefungen
und die Godfile-Ratsche bestanden ohne neue Ausnahme oder Baseline-Anhebung.
Die fokussierten Vertragspruefungen brauchen keine echte Datenbank und keinen
Container; HTTP-Grenzen verwenden das vorhandene TestClient-Fixture.
Fokussierte Nachabnahme: 226 Tests bestanden in 43,65 Sekunden (2026-10-11).

## Fachlicher Handshake

Die von Claude benannten echten Personalbefunde sind gesondert offen:
Urheber der Einwilligungsfassung aus geprueftem Token an beiden Wegen;
Idempotenz bei Wiederholung tatsaechlich durchsetzen;
keine Bewerber-Eingabewerte in Validierungsfehlern und ein gepruefter
Audit-Urheber bei Bewerbungen. Dieser Slice besitzt nicht personal_bewerbungen.py
oder dessen Fachservice. Claude kann diese Dateien als eigenen Fachslice claimen;
die vier hier bearbeiteten Vertragsdateien sind mit diesem Ergebniscommit
freigegeben. Claudes Claim BEWERBUNG-COMMAND-URHEBER-20261011 ist im Workboard
bereits dokumentiert; die Urhebererwartung muss die gepruefte Tokenkennung pruefen.
Diese Befunde werden weder durch gruenes CI noch durch neue Testerwartungen
als fachlich geschlossen ausgegeben.

Vollstaendige GitHub-Nachabnahme und Sonar-Folgepruefung nach Push bleiben offen.

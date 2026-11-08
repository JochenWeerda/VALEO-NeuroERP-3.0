---
title: Codex Integration der Claude-RLS-Kette bis PR73
type: handshake
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-10-27
---

# Codex an Claude: RLS-Kette bis PR73

Alle zehn neuen Handshakes gelesen. Integrationsreihenfolge nach PR63:
PR64, PR65, PR66, PR67, PR68, PR69, PR70, PR71, PR72, PR73.
Jede Stufe hat einen eigenen geordneten Mergecommit; PR73 ist mit
`b802b79ac858373ff758ab81f264c3c7dec5dd90` integriert.

Die Uebernahme von 943ba2bb0 als 42dd12f5d wurde erkannt. Die Korrektur wurde
nicht erneut implementiert. Fuer P3/P5 gelten nun Claudes neuere Tests und die
gemeinsame Policy-Formpruefung: system-Lesen ausschliesslich begruendet. Die
zusaetzlichen eigenen Schreibgrenzentests bleiben erhalten.

## Erhalt eigener Arbeit

Intrastat wurde inhaltlich zusammengefuehrt: eigener mandantengebundener
Detailabruf plus Claudes PUT-404-Korrektur. Uncommittete OpenAPI- und
Inventararbeitsstaende wurden gesichert und erhalten; sie werden nach dem
Quellabgleich vollstaendig neu erzeugt, nicht blind uebernommen.
Vier mitgelieferte generierte `.husky/_`-Git-LFS-Hooks sind nicht in den
Integrationstree aufgenommen. Sie gehoeren nicht zum RLS-Fachstand.

Die 17 Detailmaskenbindungen und 16 begrenzten Legacy-Neuerfassungsfixes sind
als `fb4d0c1dc` committet. 65 kombinierte Frontendfaelle und die vollstaendige
Frontend-Typpruefung bestanden. Keine Gesamt-CI-Freigabe daraus ableiten.

## Noch im Lead-Slice

- `rls_verified_agrar_20261027`: eigener noch uncommitteter Entwurf fuer
  Biostimulanzien und Kontraktallokationen, jetzt hinter
  `rls_docflow_child_keys_20261027`; kein system-Lesen. Diese beiden Tabellen
  bitte nicht parallel bearbeiten.
- Allokationsservice prueft optionalen Wiegeschein vor jeder
  Restmengenmutation mandantengebunden; fehlend/fremd einheitlich abgelehnt.
- Buchungsvorlagenmaske: Kennzeichnung Gemeinsam und Loeschaktion nur bei
  shared=false im kanonischen Builder, Artefaktabgleich folgt.
- Vollstaendige RLS-/Docflow-Abnahme und generierte Schnittstellenartefakte.

## Datenbank und Betrieb

Eigenes vorheriges Fenster beendet: alle Migrationen bis zum damaligen
Agrarentwurf zurueckgerollt, keine Revision auf dem gemeinsamen Pruefstand
fortgeschrieben. Die 503 Tabellen und 30/70 Tests aus diesem Checkpoint sind
kein Nachweis fuer PR73.

Vor dem neuen Fenster wurde `agent:claude-rls-domains` aktiv auf valeo_probe
gefunden. Codex hat deshalb keine weitere Migrations-/Gesamtabnahme gestartet.
Ein neues Fenster erst nach freiem Pruefstand koordinieren; keine fremde
Sitzung beenden und keinen Reset ausfuehren.

Lokale Systemrollen-Konfiguration vervollstaendigt und Anmeldung geprueft.
Kennwort und Container-URL ausschliesslich in ignorierter Root-.env, keine
Werte in Repository/Protokoll. Live weiterhin null RLS-Tabellen, kein
Backend-Rollout, kein P4-Cleanup.

## GitHub-Nachweise

PR70 bis PR72: Docs Build, Docs Governance und Rollenvertraege erfolgreich;
CodeRabbit uebersprungen. PR73: Docs Build und Docs Governance erfolgreich,
CodeRabbit uebersprungen. Kein vollstaendiges Quality Gate in diesen
PR-Checklisten vorhanden. RLS-Gesamtsuite und Docflow-Bestand bleiben offen,
bis sie auf dem tatsaechlichen Integrationsstand bestanden haben.


## Nachtrag: Pruefstand wieder frei

Claudes Nachweis183b2bc9e uebernommen. Eigene integrierte Abnahme269Tests
gruen, anschliessend77API-Vertraegegruen, keineSkips. Pruefstanddanach
loading_stop_fk_20261023, keineSitzung, keineeigeneRegressionstabelle.
Codex-Fenster beendet; Claude kann die sieben Verhaltenstests mit gesetzter
TEST_DATABASE_URL am bestehenden valeo_probe ausfuehren. Keine neue
Datenbank/Container, kein Reset; eigene Transaktionen zurueckrollen.
Eigene Agrar-Folgemigration hinterPR73:522RLSTabellen,193Ausnahmen,ready0.
LivePoliciesweiterhinnichtaktiviert. QA rls-integrated-acceptance-20261027.md.

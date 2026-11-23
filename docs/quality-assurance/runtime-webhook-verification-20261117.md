---
title: WhatsApp-Webhook-Verifikation und Runtime-Sweep
owner: Codex
type: reference
status: in Arbeit
last_reviewed: 2026-11-17
---

# WhatsApp-Webhook-Verifikation

Der Runtime-Sweep 43748929572 meldete fuer den parameterlosen GET
`/api/v1/channels/whatsapp/webhook` einen 503. Der Verifikationsweg prueft nun
zuerst, ob Modus `subscribe`, Token und Challenge vorhanden sind. Unvollstaendige
oder ungueltige Anfragen erhalten 400. Eine vollstaendige Anfrage ohne
konfiguriertes Verifikationstoken bleibt mit 503 gesperrt; ein falsches Token
ergibt 403, ein richtiges liefert die Challenge als Klartext. Dies aktiviert
keine Meta-Anbindung und aendert keine WhatsApp-Web-Funktion.

Der enge datenbankfreie Vertragstest liegt in
`tests/test_channel_webhook_verification_contract.py`. Der isolierte pytest-Lauf
mit deaktivierten Plugins und `--noconftest` bestand im gemeinsamen Nachlauf.
Der erste lokale Lauf hing an der eingeschraenkten Windows-Ereignisschleife;
ausserhalb dieser Beschraenkung bestanden 13 Webhook-/Runtime-Tests in 2,27 Sekunden.

Der Runtime-Sweep erzeugt den echten Doku-Drift-Bericht aus dem vollstaendigen
Checkout vor dem Backendstart. Der Workflow-Nachlauf steht aus. Ein Bericht im
Backend-Image bleibt offen: der Buildkontext schliesst die erforderliche Doku aus.
Ein erneuter Runtime-Sweep und eine reale Meta-Verifikation sind nicht belegt.

## Uebrige vier Sweep-Befunde

- Proplanta list/stats: API und Integrationshelfer verwenden jetzt dieselbe
  Clientinstanz (Transport und Cache). Zwei neue Vertrage bestaetigen die
  Verdrahtung und die Sperre ohne echten Transport. Ein realer Proplanta-Zugang
  samt angebundenem MCP-ToolCaller fehlt weiterhin; URL/Servername allein sind
  kein Betriebsnachweis. Kein Mock-Erfolg, keine Freischaltung behauptet.
- Doku-Drift: echter Bericht wird im Sweep vor Backendstart erzeugt. Der neue
  GitHub-Sweep und die separate Bereitstellung im Backendimage sind noch offen.
- FAOSTAT: beide oeffentlich gelesenen alten Fenix-Pfade (bisheriger Default und
  data/RFN) antworteten am 17.11.2026 mit 403. Die offizielle aktuelle Dokumentation
  nennt https://faostatservices.fao.org/api/v1/{lang}/data/{domain_code} mit
  bearerAuth: https://www.fao.org/faostat/en/docs/redoc-static.html . Dies belegt
  einen erforderlichen Transport-/Zugangsnachlauf, keinen lokalen Erfolg. Keine
  Zugangsdaten erfinden oder eine blockierte Quelle durch Leerwerte ersetzen.

## Separater main-Sonar-Nachlauf

Quality Gate 44021259183 auf main f9630be04: Backend, Frontend, Docker,
Sicherheit und uebrige Jobs gruen; Sonar rot ausschliesslich wegen New Coverage
71,2 % bei geforderten 80 %. Fehler-/Security-/Wartbarkeitsbewertungen A,
Duplikate 0,9 %, Hotspot-Review 100 %. Der main-Neucodezeitraum beginnt am
04.04.2026 (previous_version), also deutlich breiter als die gruene PR-Abnahme.
Die oeffentliche Messung zeigt 140377 ausfuehrbare Zeilen mit 38078 ungedeckten
sowie 20188 Bedingungen mit 8183 ungedeckten. Bei konstantem Nenner fehlen etwa
14148 weitere abgedeckte Zeilen/Bedingungen. Dies ist eine breite echte
Testluecke; keine Schwellen-, Baseline- oder Ausschlussaenderung vorgenommen.

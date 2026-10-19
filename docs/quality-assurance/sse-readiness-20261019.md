# SSE-Bereitschaft ohne Mandantendaten

## Befund und Korrektur

Runtime-Sweep 39107421367 auf 423a94935 meldete einen unerwarteten 503 auf /readyz. check_sse_hub rief get_connection_count ohne den inzwischen obligatorischen tenant_id auf. Der gesunde Hub wurde dadurch als gestoert gemeldet.

SSEHub.ping prueft nun seine vorhandene asyncio-Sperre, ohne Teilnehmer, Kanaele oder Mandantenzaehler zu lesen. Der Healthcheck begrenzt diese echte Funktionsprobe auf eine Sekunde. Blockierung oder Ausnahme bleiben nicht bereit; Abbruch wird weitergereicht. Die unveraenderte PostgreSQL-Pruefung kann die gesamte Bereitschaft weiterhin sperren. Fehlermeldungen enthalten keine internen Probe-Details. Es wurde keine pauschale Bereitschaft und kein globaler Mandanten-Zaehlzugriff eingefuehrt.

## Nachweis

Neue Gesund-Regressionspruefung vor der Korrektur rot. Abschliessend zehn Async-/Hubvertraege erfolgreich: kein Zaehlerzugriff, echte Zwei-Mandanten-Zustellung bleibt isoliert, blockierte Sperre mit Timeout und anschliessender Erholung, Ausnahme, Abbruch ohne liegengebliebene Sperre, Datenbankfehler bleibt rot sowie bestehende Stream-Abbruchvertraege. Die echte ungemockte Readiness-Funktion wurde zusaetzlich lesend gegen den vorhandenen valeo_probe ausgefuehrt: ready, postgresql und sse_hub jeweils true. Kein Reset, keine Migration, kein neuer Container und keine neue Datenbank.

## Verbleibender Runtime-Nachlauf

Der alte Sweep ist damit nicht insgesamt abgenommen. Er verwendete einen alten Dev-Token und klassifizierte 1026 von 1033 Routen als erwartete 4xx; das beweist keine authentifizierte Fachroutenabdeckung. Dazu kamen 19 bereits am 30.09.2026 abgelaufene Allowlist-Eintraege. Diese wurden weder geloescht noch pauschal verlaengert. Authentifizierter Aufbau, aktuelle Modulentscheidung und voller Sweep bleiben erforderlich. Ein gruener lokaler Hub-Test ersetzt diesen Nachlauf nicht.

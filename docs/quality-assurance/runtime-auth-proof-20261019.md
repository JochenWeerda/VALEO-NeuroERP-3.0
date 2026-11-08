# Runtime-Sweep mit nachgewiesener Anmeldung

Stand19.10.2026, RUNTIME-AUTH-PROOF-20261019.

Der bisherige Sweep sendete dev-token und akzeptierte401 als erwartete Fachantwort. Ein Lauf mit1026 solchen Antworten bewies deshalb keine ausgefuehrten Fachwege. Die Schema-Nulltest-Sperre allein reichte nicht.

Vor dem Schema-/Fachlauf verlangt das Werkzeug jetzt ein echtes Zugriffstoken und eine erfolgreiche Antwort des produktiven Sitzungspfads /api/v1/identity/session mit Subject und exakt angefordertem Mandanten. Keine ungepruefte JWT-Auswertung.401 waehrend des Laufs erhaelt eine eigene Fehlerklasse und sperrt das Gesamtergebnis. Die erfolgreiche Sitzungspruefung wird im Bericht ausgewiesen; Token und Kennwort werden nicht aufgenommen. Fehlgeschlagene Vorpruefung scheitert sofort.

Der GitHub-Job verwendet denselben vorhandenen CI-Keycloak-Bootstrap wie kritische E2E-Tests und einen Redis-Jobservice. Die neue Anmeldung ist ausserhalb CI gesperrt; sie nutzt ausschliesslich den lokalen Wegwerf-Provider und die je Job generierten synthetischen Zugangsdaten. Das Zugriffstoken bleibt in der Prozessumgebung und wird nach dem Aufruf entfernt. Keine lokale Identitaet oder Rechte erweitert, kein lokaler Container oder neue Datenbank erzeugt. CI verwendet die bereits bereitgestellte Jobdatenbank.

20 lokale Werkzeugvertraege bestehen: unbrauchbares Schema, leere Routenauswahl, fehlende/fremde/defekte Sitzung, Erfolg,401/500 im Fachlauf, fehlendes/Dev-Token, CI-Sperre, fehlende Konfiguration, Providerfehler, leeres Token, Erfolg und fehlgeschlagener Sweep mit anschliessender Tokenbereinigung. Diese Tests kontrollieren HTTP-Antworten und ersetzen nicht die echte Providerabnahme im GitHub-Nachlauf.

Alle19 abgelaufenen Ausnahmen bleiben unveraendert sperrend. Die reparierte Anmeldung kann weitere bisher verdeckte Fachfehler zeigen; diese sind einzeln zu beheben.403 bleibt eine ausgewiesene erwartete Verweigerung und beweist keine erfolgreiche Fachausfuehrung. Kein gruener Gesamt-Runtime-Nachweis behauptet.

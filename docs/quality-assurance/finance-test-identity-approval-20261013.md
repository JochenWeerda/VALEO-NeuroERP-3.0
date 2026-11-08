---
title: Finanztest-Anmeldegrenze und Zahlungsfreigabe
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Finanztest-Anmeldegrenze und Zahlungsfreigabe

Die gemeldeten vier Finanztestdateien ersetzten Nutzerrollen, aber isolierte FastAPI-Router hatten keinen verifizierten Mandantenkontext. Sie verwenden jetzt die vorhandene explizite Testgrenze aus testgrenze.py. Die Ersetzung gilt ausschliesslich in Tests; Produktionsanmeldung, Rollen und Mandantenbindung bleiben unveraendert. Die beiden Mandantensuiten verweigern Schreibproben auf einer Entwicklungsdatenbank und enthalten keinen fest eingebauten Datenbankzugang mehr.

Zahlungs-Atomizitaetsproben fragen die zentrale ZahlungslaufFreigabe an und entscheiden als zweite Person. Erfolgreiche Ausfuehrung verbraucht die Freigabe; echte PostgreSQL-Fehler erhalten sie beim Rollback. Wiederholung und parallele Ausfuehrung zahlen nur einmal. Abgelaufene oder ungueltige Freigaben verhindern den Abschluss. Die SQL-Attrappe der API-Unitprobe liefert einen inhaltsgebundenen Freigabedatensatz, ohne die Engine zu ersetzen.

Abnahme auf dem vorhandenen valeo_probe, Revision approval_log_20261013: 238 Faelle bestanden in den vier gemeldeten Dateien sowie test_mandant_token_bindung.py und test_mcp_oidc_verification.py. Die Identitaetsnachbarn pruefen echte RSA/JWKS-Verifikation ohne Auth-Override. Eine Starlette/httpx-Abkuendigungswarnung bleibt. Kein Reset, keine neue Datenbank oder Dockerinstanz. Eigene Zahlungsdaten werden aufgeraeumt; unveraenderliche Freigabeprotokolle bleiben als Testnachweis erhalten.

DocFlow-Command- und Freigabeanbindung im Frontend bleibt der naechste eigene Slice. Dieser Nachweis ist kein gruener Gesamt-CI-Nachweis.

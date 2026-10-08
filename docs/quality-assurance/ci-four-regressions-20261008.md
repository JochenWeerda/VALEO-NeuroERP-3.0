---
title: Vier Backend-CI-Regressionen nachziehen
type: qa
audience: [entwickler, qa, agent]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# Vier Backend-CI-Regressionen nachziehen

## Ausgangsbefund

GitHub CI/CD Pipeline Run 37736512236 auf 9176e248a: **16499 bestanden,
vier fehlgeschlagen**, Coverage 70,47 Prozent bei unveraenderter Schwelle 60.
Zwei eBilanz-Tests erwarteten noch 6.7; der amtlich abgeleitete Katalog und
der kanonische Export liefern bereits 6.9. Zwei Kommissionier-Tests hatten
keinen Lagerplatz im Mock, obwohl die vorhandene Buchung ihn tenantgebunden
prueft. Keine dieser vier Meldungen wird durch einen Skip unterdrueckt.

## Aenderung und Abnahme

Die zwei Taxonomieassertions und der alte Testname beziehen sich jetzt auf 6.9.
Die bestehenden NOT_READY_EXTERNAL_GATE-, False-Readiness- und
ERiC-Abhaengigkeitsassertions bleiben erhalten. Kein behaupteter Steuererfolg.

Das WMS-Mock beantwortet die vorhandenen Lagerplatz- und Artikelabfragen und
liefert einen identifizierbaren Bestandsdatensatz. Die Fachimplementierung
bleibt unveraendert. Die bestehenden Tests pruefen weiterhin Versand erst bei
abgeschlossener DELIVERY_NOTE-Kommissionierung und keinen Lieferscheinupdate
bei einer manuellen Kommissionierliste.

Auf isoliertem Lieferstand bestehen die kompletten zwei betroffenen Module
sowie `test_security_warehouse_transfers.py` und
`test_inventory_stock_movements_canonical.py`: **30 bestanden in 50,54 s**.
Pruefung ohne Coverage-Auswertung der kleinen Auswahl; die globale CI-Schwelle
bleibt bestehen. Alle geprueften Datenbankinteraktionen sind Mocks; kein
Datenbank-, Container-, Reset- oder Migrationsvorgang. Die lokale Statusabfrage
meldete keine konfigurierte TEST_DATABASE_URL; es wurde keine eingerichtet.

## Handshake und verbleibende Abnahme

Dateibesitz ausschliesslich zwei Testdateien und diese QA-/Workboard-Dokumentation.
Fremde Mailkonto-, Frontend- und Inventaraenderungen bleiben erhalten.
GitHub-Folgeabnahme des grossen Backend-Testlaufs ist nach Push erforderlich.
Der separate Node-Sicherheitsmeilenstein hat 45 bestandene Vertraege; seine
Review endet ausschliesslich 15.10.2026. ELSTER-Zugang und SDK bleiben externe
Abhaengigkeiten, bis der Benutzer die Zugangsdaten nachreicht.

---
title: Self-Billing – kanonische Kontierung und Transaktionsgrenze
status: in arbeit
type: reference
owner: Codex
last_reviewed: 2026-10-14
---

# Self-Billing-Korrektur

Das Ernteannahme-Journal verwendet den zentralen Eingangssteuervertrag app.finance.steuerschluessel.vorsteuergruppen. Aufwand und Vorsteuer stehen im Soll, die Lieferverbindlichkeit brutto im Haben. Keine festen Ersatzkonten, keine Ableitung des Steuerschlüssels nur aus einem Prozentsatz, kein Verschlucken von Buchungsfehlern. Belegnetto, Steuer und Brutto müssen exakt mit der kanonischen Berechnung übereinstimmen.

## Erforderliche Konfiguration

Der Mandant benötigt eine ausdrücklich gepflegte system_properties-Einstellung agrar.self_billing.tax_code mit dem gültigen Eingangssteuerschlüssel. Der Schlüssel enthält Aufwands- und Vorsteuerkonto; der Kontenrahmen liefert das Kreditorensammelkonto. Ohne eindeutige Konfiguration wird keine Freigabe durchgeführt. Unterschiedliche Steuerfälle sind mit der passenden ausdrücklichen Zuordnung zu prüfen; es gibt keine automatische Vermutung.

## Transaktion

Der SelfBillingRepositoryImpl unterstützt commit_on_success=False. Der Ernteannahmeweg verwendet dies für die Gutschrift und FinanceTransactionService ebenso für den Journalentwurf. Beide schreiben nur add/flush; erst die Annahme schreibt die gemeinsame Transaktion fest. Die eigentliche Journalbuchung bleibt ein gesonderter Finanzschritt. Der Aufrufer muss Fehler zurückrollen; die bestehende Datenbankabhängigkeit schließt die Session entsprechend.

## Abnahme

Drei neue Vertragsfälle prüfen fehlende Konfiguration, korrekte Soll/Haben-Zuordnung und die fehlende Zwischenfestschreibung. Zusammen mit acht neuen zentralen Studio-Freigabefällen elf grün. 31 vorherige gezielte Backendfälle und neun aktualisierte Studio-Oberflächenfälle bestanden.

Das echte grain.v1-Profil auf valeo_probe besteht alle zwölf Invarianten: Annahme, Qualität, Gutschrift, Steuer, Journal, Bestand, fremder Mandant, Rollenentscheidung, Gegenbuchung, Korrekturverweigerung, Wiederholungsverweigerung und Rollback. Eigene Fixdaten, keine neue Datenbank/Container und keine externen Aufrufe. Dieser Lauf allein ist keine vollständige Abnahme der Studio-Veröffentlichung: SQL-Nachweispersistenz, alte Veröffentlichungstests, Artefaktsynchronisierung und Browserabnahme sind im STUDIO-CLOSURE-Claim weiter offen.

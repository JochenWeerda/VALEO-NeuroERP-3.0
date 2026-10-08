# Offene Punkte geschlossen (Slice OFFENES-SCHLIESSEN-20261008)

Stand: 2026-10-08 · Folgeslice zu [Folgefunde](folgefunde-restbefunde-20261008.md)

## Auftrag

„Weiter und Offenes schließen“: Ausgangspunkt waren die drei offenen Punkte der Vorslices. Beim Abarbeiten kamen gleichartige Scheinerfolge zutage; sie sind hier mit behoben.

## Befunde und Behebung

| # | Befund | Behebung |
|---|---|---|
| 1 | Eine doppelte Gelangensbestätigung (gleicher Lieferschein) antwortete mit **503** „Dienst nicht verfügbar“, samt rohem SQL-Text. Der UAT-Vertrag nutzte eine feste Lieferschein-Nr. und war nach dem ersten Lauf dauerhaft rot. | Dublette → 409, sonstige Datenregel → 422. Der UAT-Vertrag erzeugt je Lauf eine eigene Nr. und prüft 409. Der Steuernachweis-Vertrag, der die 503 festschrieb, ist angepasst. |
| 2 | **Im ganzen System wurde nie eine E-Mail versendet.** `ProductionEmailService.send_email` protokollierte nur und meldete `True`. Der Newsletter (Kunden- und Lieferantenliste) meldete `in_queue` ohne Warteschlange und schickte nur einen Betreff. | Neu: `app/services/mail_versand.py`, echter SMTP-Versand über `EMAIL_SMTP_*` und `EMAIL_FROM` (neu). Fehlt die Einrichtung oder lehnt der Server ab, wird ein Fehler geworfen statt Erfolg gemeldet. Der Newsletter versendet je Empfänger, zählt die Annahmen und antwortet ohne Einrichtung mit 503, ohne Text mit 422. Die Listen fragen Betreff und Text über `ActionInputDialog` ab (Mask Builder) und melden die tatsächliche Zahl. |
| 3 | **Bestellkommunikation:** Die Wege an `/purchase-orders/{id}/communications` schrieben in den Dokumentspeicher und fanden nur Altbelege (kanonische Bestellungen: 404). „E-Mail senden“ und „Im Portal veröffentlichen“ setzten `sent`/`published`, ohne zu versenden oder zu veröffentlichen. | Neuer `bestell_kommunikation_service`. Die Einträge landen in `domain_einkauf.bestellung_kommunikation`; dort liest der Reiter „Kommunikation“ der Bestellmaske. Die E-Mail geht per SMTP an die angegebene oder die beim Lieferanten hinterlegte Adresse und wird erst nach Annahme als `versendet` eingetragen. Ohne Einrichtung kommt 503, bei Ablehnung 502, und nichts wird eingetragen. Das Portal trägt `veroeffentlicht` ein, und **das Lieferantenportal zeigt es** (`GET /supplier-portal/lieferanten/{id}/bestellungen`). Entwürfe und stornierte Bestellungen werden nicht veröffentlicht. Altbelege sind nur lesbar. |
| 4 | **Bankkonten:** `domain_ops.ops_bankkonten` hatte **keine `tenant_id`**, `/banken/konten` zeigte, änderte und summierte die Konten aller Mandanten. Die IBAN war systemweit eindeutig. Geprüft wurde die Rohform der IBAN, gespeichert die normalisierte. `/konten/iban-validate` stand hinter `/konten/{id}`, war damit nie erreichbar und prüfte nur die Länge (BIC `"UNKNOWN"`). | Migration `offenes_schliessen_20261008`: `tenant_id NOT NULL` mit Fremdschlüssel, IBAN je Mandant eindeutig. Gibt es Altzeilen ohne Mandant, bricht sie ab; der Mandant wird nicht erraten. Repository und Wege arbeiten im Mandanten. Die IBAN wird nach ISO 13616 geprüft (`validation_contracts.validate_iban`), die Prüfung ist erreichbar, BIC und Bank bleiben leer statt erfunden. |
| 5 | `domain_erp.bank_accounts.account_number` war systemweit eindeutig. | Eindeutig je Mandant (dieselbe Migration). |
| 6 | **Lieferantenportal:** Lieferungen, Kontrakte, Preisauskunft und Silobestand fragten Spalten ab, die es nicht gibt (`acceptance_date`, `article_name`, `net_weight_kg`, `quantity_contracted`, `capacity_kg`, `current_quantity_kg` …). Der Fehler wurde still zu „leer“ bzw. „0 t“ bzw. „kein Preis“. **Das Portal zeigte nie etwas.** | Die Abfragen nutzen jetzt die echten Spalten: Wiegeschein-Nettogewicht, Artikelname über den Artikel, Kontraktmengen `total`/`remaining_quantity_kg`, Silo `capacity_tons`/`quantity_tons`. Ein Datenbankfehler führt zu Rollback und 503. |

## Nachweis

- `tests/test_offenes_schliessen.py`, 22 Tests gegen `valeo_probe`. Der SMTP-Ersatzserver sitzt an der `smtplib`-Grenze; der Versanddienst läuft echt. Abgedeckt sind:
  - Versand bzw. Ablehnung ohne Einrichtung
  - Newsletter: Zählung, Text-Pflicht, 503
  - Bestellkommunikation: erfassen, Mail an den Lieferanten, keine Eintragung ohne Einrichtung oder bei Ablehnung, Portal samt Portal-Lesepfad, Entwurf, fremder Mandant
  - Bankkonten im Mandanten, IBAN-Dublette in beiden Schreibweisen, ungültige IBAN, erreichbare Prüfung
  - Bankkontonummer je Mandant
  - Portal mit echten Daten: Lieferung 25 t Braugerste, Kontrakt 100/25/75 t, Preis 215 €/t, Silo 25/500 t
- Vitest `newsletter-versand.test.tsx` (3 Tests): Betreff und Text werden abgefragt, die Rückmeldung zeigt die echte Zahl, ohne Text wird nichts gesendet, Fehler werden angezeigt.
- Regression über 22 Testdateien zu Banken, Newsletter, Bestellungen, Portal, Mail und Gelangensbestätigung: 598 grün.
- Gates im HEAD-Worktree: Response-Modelle (Schwelle 0) und OpenAPI-Doku grün, Tabellenkatalog grün, Single Head, Improvement-Pipelines grün.
- Live auf dem gewachsenen Bestand antworten alle vier Portalwege mit 200.

## Weitere Befunde (benannt, nicht Teil)

- Auf HEAD ist die ADR-Navigation (`mkdocs.yml`) seit `d81a86b38` veraltet. Das ist Codex' Claim EBILANZ-CI-DOCFIX.
- Auf der Dev-DB ist kein SMTP eingerichtet: Newsletter und Bestellmail antworten dort ehrlich mit 503, bis `EMAIL_SMTP_SERVER`, `EMAIL_FROM` usw. gesetzt sind.
- Der Vitest `LaunchpadBoard` („44 Pixel“) ist im geteilten Baum rot. Das liegt an fremder WIP in `components/navigation`, nicht an diesem Slice.

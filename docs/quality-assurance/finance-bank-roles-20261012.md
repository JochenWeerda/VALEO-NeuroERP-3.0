---
title: Rollen fuer Bankdaten und Finanzaktionen
type: reference
audience: [entwickler, qa, agent, buchhaltung]
owner: Codex
status: aktiv
last_reviewed: 2026-10-12
description: Bestehende Finanzrollen schuetzen 31 Bank- und Finanzaktionswege vor Datenzugriff; breite benoetigte Leserechte bleiben bestehen.
---

# Bank- und Finanzaktionsrollen

## Befund und Abgrenzung

Die drei eigenen Dateien bank_accounts.py, bank_reconciliation.py und
finance_actions.py prueften an keiner ihrer 31 Routen eine Fachrolle.
Der erste Abgleich hatte 32 angenommen; der vollstaendige Route-Vertrag
belegt sieben Bankstamm-, vier Vergleichs- und zwanzig Finanzaktionswege.
Dieser Slice ergaenzt nur bestehende Rollen-Dependencies und aendert keine
Vergleichs-, Buchungs-, Zahlungs- oder Abschlusslogik. Zentraler Rollenvertrag
in app/auth/finance_roles.py unveraendert, keine parallele Authentifizierung.

## Rollenvertrag

| Vorgang | Bestehendes Profil |
| --- | --- |
| Bankstamm lesen/Vorlage, Bankvergleich einschliesslich lesender POST-/run-Wege | finance_read |
| Bank-Buchungskonto-Optionen | kontenplan_read: Finanzrollen und Einkauf |
| Bankstamm anlegen/aendern | finance_write |
| Bankstamm loeschen | finance_admin |
| Journalbuchung freigeben/posten | finance_write, wie am kanonischen Journalweg |
| Kassenabschluss (weiterhin gesperrt), Lastschrift ausfuehren, Abschluss sperren/ausfuehren/genehmigen, SEPA-Batch erstellen | finance_admin |
| Abschluss nur berechnen, Sicherheiten/Zahlungsvorschlaege/Readiness/Mahnstufentrail lesen, Buchungsuebergabe exportieren | finance_read |
| Kreditlimits lesen | open_items_read: Finanz-, Verkaufs-, CRM- und Einkaufsrollen |
| SEPA-Mandat anlegen/widerrufen, Ratenplan/Rate erfassen, Mahnstufe eskalieren | finance_write |

Lesen wird nicht pauschal auf Administratoren reduziert. Das breite
Kreditlimit-Profil dient den Bereichen, die Auftraege oder Bestellungen
pruefen. Ein Einkaufs-Leserecht auf Buchungskonto-Optionen gewaehrt weder
Bankstammpflege noch Salden-/Buchungszugriff. Steuerschluessel,
Zahlungsbedingungen, Debitoren und Kreditoren ausserhalb dieser Dateien wurden
nicht eingeschraenkt. Deren eigene bereichsuebergreifende Lesevertraege sind
bei spaeteren Slices zu erhalten.

## Abnahme

Final 668 Tests bestanden: 593 neue Rollen-/Route-/Anmeldevertraege und
75 bestehende Bank-, Vergleichs-, Finanzaktions-, SEPA-/Raten-/Mahnservice-
und Kassenabschlussvertraege. Die initiale Rollen-Gegenprobe am alten Code
hatte 452 Fehler bei 593 Faellen; abschliessend wurde die rein lesende
Abschlussberechnung ebenfalls finance_read zugeordnet.

Die Rollenmatrix nutzt echte FastAPI-Dependencies mit 18 Rollenprofilen und
einer absichtlich verweigerten Datenbankgrenze. Falsche Rolle oder fehlende
Anmeldung darf die Grenze nicht erreichen. Berechtigte Requests erreichen
418 an dieser Grenze oder 200 bei der datenbankfreien Bankvorlage; ein 404
oder beliebiger Fehlerstatus gilt nicht als bestandene Positivprobe. Eine
Vollstaendigkeitsratsche erfasst alle tatsaechlichen Methoden/Routen.
Die Identitaetsgrenze ist im Rollentest ersetzt; keine echte Token-/Provider-
oder Mandantenabnahme dadurch belegt.

Bestehende Fachtest-Router erhalten eine explizit berechtigte FINANCE_ADMIN-
Testidentitaet; die Rollen-Dependencies selbst werden nicht uebersprungen.
Bank-Proof, pensionierte Direktbuchung und Kassenabschluss wurden auch gegen
den vorhandenen gemeinsamen valeo_probe geprueft (vorher --status, Revision
audit_urheber_20261011). Vorhandene eigene Fixtures und deren gezielte
Bereinigung wiederverwendet, keine neue Datenbank, kein Docker, kein Reset.
Die bestehende Bankfixture verwendet ein kurzlebiges eigenes Schema innerhalb
desselben Pruefstands, das sie nach Abschluss entfernt.

Alle 31 lokalen OpenAPI-Operationen wurden gegen veroeffentlichten Quellstand
verglichen: Pfade, Payloads, Antworten und Modelle unveraendert; Bearer-
Anmeldung nun lokal deklariert. Der eng begrenzte Kassenabschluss-Snapshot
enthaelt diese Anmeldung ebenfalls; die Sperre 409 bleibt bestehen.
Die vorhandene Starlette/httpx-Warnung wurde nicht durch diesen Slice behoben.

## Praxis und parallele Arbeit

Der User hat Claude Token-Mandantenbindung und Kontenplanmaskenpflege
zugewiesen. Keine konkurrierende Umsetzung an chart_of_accounts.py oder
der Pflegemaske. Kontenpflege ist eine delegierbare Fachaufgabe; Anzeige
und Pflege sind getrennt. Eine Bestaetigungsfrage ergaenzt ein Recht, ersetzt
es aber nicht. SAP beschreibt breite Anzeige bei begrenzter Anlage-/
Aenderungsberechtigung: [Sachkontenberechtigungen](https://help.sap.com/docs/SAP_ERP/17ec785ed2294431b933daf9a926af80/f091d7531a4d414de10000000a174cb4.html).
Dynamics prueft Referenzen vor Loeschung und nennt Sperren fuer nicht
loeschbare Konten: [Main-account deletion](https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/delete-main-account).
Diese Quellen stuetzen die Gestaltung; sie behaupten keine fertige Umsetzung
in VALEO und keine pauschale gesetzliche Vorgabe.

## Offene Sicherheitsarbeit

Rollen sind keine Mandantenbindung. Diese Bank-/Finanzaktionswege verwenden
weiterhin den bisherigen Header-/Default-Kontext; die sieben SEPA-/Raten-/
Mahnwege besitzen zudem ihren eigenen default-Fallback. Mahnstufenoperator
kommt noch aus dem Rumpf. Verifizierte Tokenbindung, Tokenurheber und
mandantengepruefte Folgeobjekte sind separat zu schliessen und mit zwei echten
Kontexten zu pruefen. Breite Leserechte erlauben keinen Fremdmandantenzugriff.
Die 229 zuvor gemeldeten restlichen Finanzwege sind kein durch diesen Slice
abgeschlossener Gesamtbestand; neue Claims/weitere Schreiber erneut vermessen.

---
title: Studio-API-Vertraege und Mandantengrenzen 2026-10-25
type: verification
owner: Codex API slice
status: teilweise abgeschlossen
last_reviewed: 2026-10-26
---

# Studio-API-Vertraege: Uebergabe

## API-Integrationsabnahme 2026-10-26

Der API-Slice wurde in der privaten Integrationsansicht erneut geprueft; dieser
Nachweis ersetzt keine aktuelle Gesamtauswertung der vom Lead betreuten
ScreenDefinitions und generierten Artefakte. Die folgenden Gate-Zahlen sind der
historische Zwischenstand vom 25.10.

Die 135 datenbezogenen Routen der 14 vorhandenen WIP-Router verwenden den zentralen `get_tenant_id` aus dem
verifizierten Identitaetskontext statt eines frei waehlbaren Tenant-Headers.
Die einzige weitere Route ist die reine Skontoberechnung ohne Datenzugriff;
sie besitzt den bestehenden `finance_write`-Guard.
Kontrakt-Unterobjekte binden Updates, Loeschungen und Folgeabfragen an den
Pfadkontrakt; Zuschlagspositionen pruefen die mandanteneigene Elterngruppe.
Die zentrale Entity-Projektion gibt ausschliesslich deklarierte skalare Felder
kanonisch registrierter Masken aus, prueft die Entity-ID und uebernimmt keine
Projektionsanweisung aus einem veroeffentlichten Tenant-Draft.

Aktueller Testlauf: `python artifacts/run-migration-repair.py -m pytest -o addopts= tests/test_studio_contract_http_boundaries.py tests/test_studio_intrastat_detail_binding.py tests/test_studio_api_detail_bindings.py tests/test_studio_remaining_detail_contracts.py tests/test_studio_stamm_detail_reads.py tests/test_mask_entity_projection.py tests/test_studio_canonical_stamm_bindings.py -q`
ergab **55 bestanden, keine Skips, Exit 0, 119.08 s**. Vier Faelle verwenden
PostgreSQL mit eigenen eindeutigen Zeilen und explizitem Rollback. Der Status
des vorhandenen `valeo_probe` wurde vorher ausschliesslich lesend geprueft:
Revision `loading_stop_fk_20261023`. Kein Reset, keine Migration oder neue
Ressource. Die signierten Stamm-HTTP-Tests verwenden echtes RSA/JWKS und
SQLite; die Sessionvalidierung ist dort eine ausdrueckliche Attrappe.
Die UI-/CLI-/MCP-Projektionsparitaet verwendet einen isolierten Fachtransport
und beweist die gemeinsame Feldselektion, keinen externen Produktivbetrieb.

Ergaenzende Regression: `python artifacts/run-migration-repair.py -m pytest -o addopts= tests/test_weighing_ticket_validation.py tests/test_weighing_ticket_contract_allocation.py tests/test_studio_openapi_read_bindings.py -q`
ergab **22 bestanden, keine Skips, Exit 0, 120.67 s**. Sie prueft die vorhandenen
Gewichts-/Allokationsregeln sowie konkrete GET-/POST-/Enum-Vertraege des
Studio-Gates anhand isolierter OpenAPI-Eingaben. Beide Laeufe enthalten nur
die vorhandene Starlette-TestClient-Abkuendigungswarnung. Zusammen **77/77**;
kein Quellfix oder abgeschwaechter Test war erforderlich.

Lieferbare Quellen dieses API-Slices: `app/api/v1/endpoints/{artikel_mengeneinheiten,fibu_geschaeftsjahre,fibu_stammdaten,fibu_zahlungsmeldungen,individualpreise,individuelle_artikelnummern,intrastat,kontrakt_mengenzeitraum,op_skonto_auszifferung,preis_rabattgruppen,produktion_rezepturgruppen,training,warengruppen,weighing_tickets}.py`
und `app/services/mask_data_read.py`. Die sieben oben aufgefuehrten Testdateien
sind der zugehoerige Abnahmenachweis. `closing_checklists.py` wurde in diesem
Nachlauf nicht veraendert; dessen bereits integrierte Sicherheit bleibt separat
unter `closing-validation-security-20261025.md` dokumentiert.

Restgrenzen: kein neuer Browser-/Gesamt-CI-Nachweis durch diesen API-Slice,
keine pauschale Write-Paritaetsabnahme. Die kundenbezogene Zuordnung fuer
`portal/zertifikat` ist weiterhin fachlich durch den Lead zu bewerten; ein
interner Zertifikatsbestand darf nicht allein per Tenantfilter freigegeben werden.

## Historischer Gesamtstand 2026-10-25

Der aktuelle Registrierungs- und Gate-C-Lauf bewertet **alle 857** ScreenDefinitions, darunter die zuvor gemeldeten 22 fehlenden API-Bindungen. Ergebnis im Reparaturstand: **855/857 Gate C gruen**. Die zwei verbliebenen Screen-IDs sind:

| Screen-ID | Zustand | Naechster Nachweis |
|---|---|---|
| `artikel/zoll-intrastat` | Die Maske liest nun eine echte, mandantengefilterte Intrastat-Meldung per `GET /api/v1/intrastat/meldungen/{meldung_id}` mit fachlichen Feldern. Gate C sieht den neuen GET noch nicht, da sein statisches OpenAPI-Artefakt erst nach Integration vom Lead neu erzeugt wird. | OpenAPI/Agentenhandbuch erzeugen und Gate C erneut ausfuehren. |
| `portal/zertifikat` | Detail-GET bleibt offen. Interne Ops-Zertifikate haben keine belegte Kundenkonto-Zuordnung; ein blosser Tenantfilter waere Datenfreigabe an alle Kunden des Mandanten. | Kundenbezogene Dokument-/Zertifikatszuordnung samt Portalrecht fachlich implementieren, erst danach Detail-GET und Maske binden. |

Die separate Liste `portal/zertifikate` nutzt jetzt den kanonischen `GET /api/v1/portal/zertifikate` mit `portal_recht(AUSWERTUNGEN)`, echten Feldern (`art`, `nummer`, `gueltigBis`, `status`) und ohne Detail-Zeilenlink. Fuer nicht zugeordnete interne Zertifikate liefert der bisherige Portalservice absichtlich keine Daten. Die Liste ist daher sicher gebunden, aber fachlich erst nach einer Kunden-Dokumentzuordnung mit Inhalt versorgt. Sie wird nicht als Ersatz fuer `portal/zertifikat` gezaehlt.

Der bestehende Abschlusschecklisten-Detail-GET liest den Mandanten aus dem geprueften Tokenkontext und gibt fremde IDs als 404 zurueck. Der PostgreSQL-JSONB-Wert `items` wird als Liste verarbeitet; zuvor verursachte `json.loads` darauf einen 500er. Die Qualitaets-Worklist verwendet die echten API-Felder `protocol_number`, `is_final` und `moisture_pct`.

## Tests und Grenze

`python artifacts/run-migration-repair.py -m pytest -o addopts= tests/test_studio_contract_http_boundaries.py tests/test_studio_intrastat_detail_binding.py tests/test_studio_api_detail_bindings.py -q`: **15 bestanden, Exit 0**. Drei Persistenz-/HTTP-Faelle nutzen ausschliesslich den bestehenden PostgreSQL-Pruefstand `valeo_probe`, eigene eindeutige Zeilen und einen Rueckroll-Block. HTTP prueft fehlende Authentifizierung, fehlendes Finanz-/Portalrecht, eigenen und fremden Mandanten sowie 404 fuer nicht vorhandene IDs. Acht weitere Detailvertraege sind gezielte Unit-Checks ihrer Tenant-Parameter und Routenschemas; sie ersetzen keinen End-to-End-Beleg. Keine neue Datenbank, Migration oder Reset.

Das statische OpenAPI-/Gate-Artefakt ist noch nicht generiert. Gate A/B/E, Browserbedienung, Write-Paritaet und CLI/MCP-Aktionen sind mit diesen API-Tests nicht vollstaendig abgenommen. Die 22 API-Bindungen sind daher nicht als gesamtes Produktversprechen geschlossen; `portal/zertifikat` ist ein echtes Fachmodell-Gap.

## Quelldateien fuer die Integration

API-Router: `app/api/v1/endpoints/closing_checklists.py`, `fibu_geschaeftsjahre.py`, `fibu_stammdaten.py`, `fibu_zahlungsmeldungen.py`, `individualpreise.py`, `intrastat.py`, `op_skonto_auszifferung.py`, `preis_rabattgruppen.py`, `produktion_rezepturgruppen.py`, `warengruppen.py`.

ScreenDefinitions: `app/core/screen_definitions_domain_batch15.py`, `screen_definitions_kontrolle.py`, `screen_definitions_stamm.py`, `screen_definitions_stamm_batch13.py`.

Tests: `tests/test_studio_api_detail_bindings.py`, `tests/test_studio_intrastat_detail_binding.py`, `tests/test_studio_contract_http_boundaries.py`.

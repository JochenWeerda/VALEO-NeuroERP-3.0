---
title: Studio Debitoren OP – Integrationsnachweis
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Kanonische OP-Quelle, Geldkennzahlen, Detailbindung und naechste echte Runtimefamilien.
---

# Integrationsnachweis

Die Debitoren-OP-Liste nutzt die echte NativeListPage und den kanonischen
konto_typ/only_open-Vertrag. OP-IDs oeffnen den offenen Posten statt einer
unzugehoerigen Verkaufsrechnung. Die OP-Verwaltung und Detailzusammenfassung
verwenden dieselbe Tabellenquelle; Ausgleiche werden ueber die konkrete
Auditverknuepfung zugeordnet und mit der gespeicherten Waehrung angezeigt.

81 gezielte Tests bestehen: 30 Backend, fuenf CRM-Proxy, 45 Frontend/Compiler,
ein signiertes SQL-Szenario fuer REST/MCP/CLI samt zwei Zahlungshistorien.
Typpruefung und Produktionsbuild gruen. Eigene SQL-Daten zurueckgerollt,
Pruefstand rls_domain_shared_20261027, keine andere Sitzung. Keine neue DB,
kein Container, kein Reset, keine Migration. Zwoelf aktuelle synthetische NativeListPage-Ansichten Hell/Dunkel, drei
Breiten und EUR/Mixed ohne axe/Overflow/JS-Befund; siehe QA.

Gate A/B/C851, E804/851:47 bleiben offen. Eine Maske
funktional migriert, eine obsolete zweite Identitaet entfernt; keine doppelte
Funktionslieferung behaupten. Originalinventar bleibt nachvollziehbar.

Naechster Kandidat CRM-Aktivitaeten: aktueller Builder hat falsche Feldnamen
und Detailroute, fehlende Datum-/Verantwortlichenfilter sowie 500-vs-200-
Paginierung. Nicht durch einen Wrapper ersetzen. Backendproxy nun tenantbound
und fail-closed, das ist noch keine UI-Migration. Portalzertifikat-Detail war
ein verwaister Builder ohne kundenautorisierte Datenquelle und ist bereinigt;
keinen unsicheren Detailendpunkt erfinden. Bestehende sichere Liste erhalten.

Lieferquelle ausschliesslich artifacts/migration-repair-source, exaktes Manifest
und privater Index; Push ausschliesslich codex/migration-parity-repair-20261022.
Root und fremde Aenderungen unveraendert lassen. Keine lokalen Identitaeten,
E-Mails, Tokens oder .env-Dateien liefern. Bei Python-Dateibearbeitung immer
encoding="utf-8" explizit setzen; Windows-Standard CP1252 hat einen Textfehler
verursacht und wurde vor Abnahme korrigiert. HTTP-Tests brauchen lokalen
Socketzugriff; isolierte Windows-Python-3.11.0-Instrumentierung kann abstuerzen.
Die freigegebenen HTTP-Tests liefen mit WindowsSelectorPolicy ohne Plugin-
Autoload, unveraenderten Fachvertraegen und echten signierten HTTP-Aufrufen.

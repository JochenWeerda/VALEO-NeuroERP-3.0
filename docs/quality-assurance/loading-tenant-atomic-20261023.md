---
title: Mandantengebundene atomare Verladung 2026-10-23
type: reference
owner: Codex
status: umgesetzt
last_reviewed: 2026-10-23
---

# Verladung: Mandant, Urheber und atomarer Abschluss

Nutzerauftrag: die fehlende Mandantenspalte schliessen. Betroffen ist das alte Verladungsmodell domain_log.log_touren, nicht der parallele Logistik-Tourenplaner. Cursors Workspace/UI/Signalmapping bleibt in dessen Dateibesitz.

## Vertrag

- Tour.tenant_id ist VARCHAR(120), verpflichtend, ohne Serverdefault und nichtleer. Tournummern sind pro Mandant eindeutig; Datum und Status besitzen tenantfuehrende Indizes.
- Alle vier Verladungsrepositories verlangen expliziten Kontext. Jeder API-Aufrufer liefert ihn aus get_tenant_id, das einen serverseitig verifizierten Kontext verlangt. Keine Ableitung aus Body, Query oder Standardmandant.
- Touren, Stopps, Lieferscheine und Tourprotokoll sind beim Lesen/Aendern/Loeschen auf den Tour-Parent beschraenkt. Fehlender, leerer und legacy-unassigned Kontext wird abgelehnt. Altzeilen werden ausschliesslich als legacy-unassigned zurueckgehalten, niemals einem echten Mandanten zugeschlagen.
- Batchzuordnung prueft alle Quellnoten und den Zielstopp vor dem ersten Write. Lieferschein und Stopp muessen dieselbe Tour haben: zusammengesetzter Fremdschluessel plus NULL-Check sichern dies auch in SQL. Fremde oder widerspruechliche Altdaten fuehren zum Migrationsabbruch; keine stillen Verschiebungen/Loeschungen.
- Objektidentitaet und Tenant sind nicht per PATCH veraenderbar. Beziehungen sowie Audit-/Systemfelder werden abgelehnt. Oeffentliches Tour-PATCH erlaubt nur bestehende Eingabefelder und Tournummer, keine direkte Status-/Summenmutation. GET baut DTOs und veraendert keine ORM-Collections.
- Start/Ende der Verladung und Dispatch verwenden die gepruefte Providerkennung und deren Anzeigenamen statt vom Aufrufer gesetzter Auditkennung. Die beiden Loading-Wege bestaetigen Status, Tourprotokoll und Outbox gemeinsam; bei Fehler folgt Rollback. Der optionale Outbox-Parameter mirror_on_store=False verhindert dort vorzeitige SSE; der bestehende Versandpfad bleibt fuehrend.
- Fahrzeugzuordnung verlangt einen eigenen Fahrzeugdatensatz. Das Fahreraltmodell besitzt noch keine Mandantenspalte: nichtleere neue Fahrerzuweisungen werden deshalb sicher abgelehnt, statt aus einer Fahrzeugverknuepfung Eigentum zu erfinden. Dessen vollstaendige Migration ist ein weiterer Slice.

## Migration und Ressourcen

Zwei regulare Revisionen: loading_tenant_20261023 folgt dms_inbox_tenant_20261022; loading_stop_fk_20261023 folgt loading_tenant_20261023. Die bereits angewandte erste Revision wurde nicht mit neuen Constraint-Operationen wiederholt. Eine solche Wiederholung wurde vom automatischen Approval-Review abgelehnt; die sichere Alternative ist die separate Folgerevision.

Beide Revisionen auf dem gemeinsamen valeo_probe angewandt: vorher jeweils keine fremden aktiven Transaktionen, strikte Vorgaengerpruefung, kurzer Locktimeout und atomarer Revisionsfortschritt. Vorher/Nachher jeweils null bestehende Tourzeilen; keine Zeilen geloescht. Damit ist noch kein Backfill an vorhandenen realen Tourdaten behauptet. Kein Reset, keine neue PostgreSQL-Datenbank/Container/Volume. SQL-Fachtests nutzen eigene Zeilen innerhalb einer aeusseren Rollbacktransaktion und Savepoints; fremde Outboxzeilen bleiben unberuehrt.

Die Probeabnahme und die Laufzeitaktualisierung sind getrennte Schritte: Anschliessend wurde auch valeo_neuro_erp nach lokaler Sicherung und bestandenem Importtest regulaer ueber die neun ausstehenden Revisionen auf loading_stop_fk_20261023 gehoben. Keine Fachtests auf der Entwicklungsdatenbank. Der anschliessende gezielte Backend-Neustart/Sichtnachweis wird in local-frontend-refresh-20261023.md dokumentiert.

## Nachweise

- 48 kombinierte Faelle bestanden, darunter 30 gezielte Verladungsfaelle: je SQLite im Speicher und echtes PostgreSQL. Erfolge, Outboxfehler-Rollback, verifizierter statt gefaelschter HTTP-Urheber, zwei Mandanten, nicht zugeordnete Altzeilen, fremde Reads/Writes/Deletes, vollstaendige Bulk-Vorpruefung, unveraenderte Auditfelder/Collections, DTO-Read ohne Dirty-State, echte FK-Abweisung und Bindung aller Deliver-Pfad-IDs.
- SQLite meldet die erwartete FK-Abweisung als OperationalError, PostgreSQL als IntegrityError. Der Test verlangt in beiden Faellen ausdruecklich die jeweilige Fremdschluesselverletzung; keine pauschale Fehlerakzeptanz.
- API-Artefakt aus kanonischer Entwicklungs-Konfiguration: 3246 Pfade erhalten. Tabellenkatalog: 681 Tabellen und unabhängiger --check gruen. Fuenf Agent-Handbuchartefakte neu erzeugt.
- Katalog-Nebenbefund behoben: Lazy-Registry-Vervollstaendigung waehrend Iteration verursachte dictionary changed size during iteration. Gleiche zentrale Vervollstaendigung wie beim Agent-Handbuch vor stabilem sortiertem Snapshot; eigener Importreihenfolge-Vertrag.
- Unabhaengiger lesender Agent-Review fand und bestaetigte die Korrekturen an Collection-Cascades, Patch-Audit und Deliver-Pfadbindung. Kein Browser-/Vollmigrationsnachweis durch diese Backendtests.

## Offene Grenzen

Allgemeine Command-Idempotenz/Versionspruefung und strikte Loading-Zustandsuebergaenge bleiben gesondert; dieser Slice behauptet sie nicht. Ebenso bleiben vorbestehende allgemeine Outbox-Retry-/Parallelworkerfragen getrennt. Fremde aktive Workspace-Dateien und deren Release werden hier nicht als abgeschlossen markiert.

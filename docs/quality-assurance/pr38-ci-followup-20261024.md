---
title: PR38 CI-Nachlauf und Integrationsstand
type: reference
owner: Codex
status: in-arbeit
last_reviewed: 2026-10-24
---

# Gepruefter Stand

Die neun Workspace-Reviewbefunde sind geschlossen. Der anschliessende Gesamt-CI-Lauf bleibt eine getrennte Abnahme.

- `78aaecf5f`: fehlende Migration dms_inbox_tenant_20261022 wiederhergestellt. Alle437 Migrationsdateien stimmen nach LF-Normalisierung mit dem separat geprueften PR39 ueberein. Die nachfolgenden CI-Migrationen laufen durch; keine lokale DB wurde dafuer zurueckgesetzt.
- `ae330988a`: CRM-Test prueft beide Definitionswege unabhaengig von der ternary-Schreibweise; drei echte Renderfaelle sichern Lead/Kunde/Default und Kontextweitergabe.49 Python- und8 Frontendfaelle bestanden.
- `83bbfa774`: Fastify5.12.7, Storybook8.6.19 und abgegrenzte AI-Sicherheitskorrekturen integriert. Ungenutzter AI-Vectorstore entfernt; simulierte RAG-Ergebnisse durch ehrliches503 ersetzt. Historische Nachweise bleiben gekennzeichnet erhalten. Lokale Einzelpruefungen gruen; kein Docker-Rollout behauptet.
- `9af9d7b2e`: Tabellenkatalog aus nachgewiesen gleichem Frischschema:31Schemas,688Tabellen,9096Spalten. Consumer-Bezuege aus sauberem HEAD statt pending WIP;14 statische Tests bestanden. Direkter PR38-Frischkatalogvergleich steht aus.
- `7b5de73b8`: Bestellrouten, fehlender SSE-Helperexport, unechte Legacy-Artikel und Banktest-Mock korrigiert.33 Frontendtests gemeinsam bestanden.
- `8b81d3408`: PSM-Liste an registrierte BVL-Definition gebunden und Erreichbarkeitsscanner gegen falsche Importtexte gehaertet.14 Tests erneut bestanden.272 Erreichbarkeitsbefunde bleiben sichtbar.

# Aktueller Nachlauf

Der GitHub-Lauf40115727623 auf8b81 erreicht nach erfolgreichem Migrationsgraph weiterhin den Doc-Drift-Fehler. Der strenge Datenbanklauf40115727664 ist gruen. Agrar-/Finanz-Smokes und weitere Frontendabnahmen sind nicht insgesamt gruen. Der Sicherheitslauf40115727683 scheitert beim Abgleich der Audit-Schweregradzahlen; die Ursache wird geprueft, keine Ausnahme oder Gateabsenkung ist genehmigt.

Die neue Nutzerfreigabe erlaubt die Integration bisher fremder Arbeit. Drei klar abgegrenzte Owners pruefen die noch nicht integrierten Studio-API-, Antwortprojektions- und Runtimeaenderungen. Aeltere gemeinsame Arbeitskopien duerfen keine bereits veroeffentlichten Sicherheits-/Fachkorrekturen zuruecknehmen. Fehlende Dateien der partiellen Commit-Ansicht sind keine beabsichtigten Loeschungen.

# Offene Grenzen

Keine Gesamtfreigabe fuer Studio, Browser oder vollstaendige Maskenmigration. Portal-Zertifikatsdetails besitzen bislang keine nachgewiesene autorisierte Kundenquelle. Interne Ops-Zertifikate werden nicht als Ersatz exponiert. Weitere Fachluecken und Erreichbarkeitsbefunde werden einzeln geprueft.

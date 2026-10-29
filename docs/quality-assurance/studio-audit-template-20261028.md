---
title: Studio Audit- und Vorlagenmigration
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Funktionale Audit- und Vorlagenmigration mit echten SQL- und Runtime-Nachweisen.
---

# Audit und Kampagnenvorlage: funktionale Studio-Migration

Zwei weitere urspruengliche Runtime-Punkte sind migriert:

- `kontrakte/FrmKontraktProtokoll`: echte vertragsgebundene Auditquelle, sechs
  Spalten mit vollstaendig lesbarer Datumsspalte und Nullwertdarstellung, zwei
  kombinierte Filter, eingebetteter und eigenstaendiger Kontext. Der zentrale
  NativeAuditListPage nutzt Definition, Compiler, Runtime und Renderer. Ohne
  Vertragskennung wird nichts abgerufen. Alle Seiten des begrenzten Projektors
  werden vor der lokalen Filterung gesammelt; unvollstaendige Quellen scheitern.
- `crm/campaign-template`: echte Detail-ID statt unveraenderlicher /new-Liste,
  deklarierte Neuanlage, Bearbeiten, Duplizieren, Abbrechen und Ruecknavigation.
  Sechs backendkonforme Felder; Systemmetadaten bleiben erhalten. Leere optionale
  Texte sind loeschbar, Pflichtwerte und unzulaessige Typen werden vor SQL abgewiesen.

## Gemeinsame Korrekturen

Deklarierte Editfelder werden auf Wunsch aus dem Datensatz vorbefuellt und nur
freigegebene Eingaben an den bestehenden REST-Endpunkt uebergeben. Ein expliziter
`resource.v1`-Antwortadapter bestaetigt die Ressourcenkennung: Update muss dieselbe,
Duplizieren eine neue Kennung melden. Fehlende oder ungueltige Bestaetigung bleibt
Fehler. Der Adapter ist auf die geprueften Vorlagenwege begrenzt; Agenten und
Vorschauaufrufe werden ohne HTTP-Schreibwirkung abgewiesen. Studio-Entwuerfe duerfen
diese native Bruecke nicht selbst freischalten. Es ist kein neuer Domain-Command
und keine Freigabe schreibender MCP-Capabilities.

Vorlagen serialisieren JSON korrekt und lesen Antworten mandantengefiltert zurueck.
Der gemeinsame Maskendatenauftrag akzeptiert nun die bereits registrierten
ASCII-Grossbuchstaben in nativen Kennungen. Registry, Datenquellen-Whitelist,
Syntaxgrenzen und Mandantenbindung bleiben bestehen; Traversal und fremde
Ressourcen werden weiterhin abgewiesen. Keine Readiness-Grenze wurde gelockert.

## Nachweise

36 Frontendfaelle in sechs Dateien bestehen, einschliesslich echter Runtime und
Renderer, Routen-/Create-/Edit-/Duplicate-/Fehler-/Deny-Verhalten sowie Regression
von Reklamationen und Prozesskatalog. 20 zusaetzliche Unit-/Negativ-/Strukturfaelle
bestehen (darunter Dateigroessen-Ratsche und verbotene Studio-Metadaten).
Zwei signierte HTTP/SQL-Faelle bestehen auf `valeo_probe`: Audit via REST/MCP/CLI
mit identischem Inhalt, fremder Kontrakt/fehlende Rolle abgewiesen; Vorlagen
anlegen/aendern/duplizieren mit echtem JSON und Mandantentrennung. Das ergibt58
unterschiedliche gezielte Faelle. Keine neue Datenbank oder Container; die eigene
Datengrenze wurde zurueckgerollt. Der Pruefstand ist nachkontrolliert frei(0Sitzungen).
Seine Revision bleibt `rls_domain_shared_20261027`. Kein Live-RLS-Rollout.

Vollstaendige Typpruefung und Produktionsbuild bestanden. OpenAPI, Rechteprojektion,
Studioversionen, Agentenhandbuch und Inventare sind neu erzeugt. Die beiden Aktionen
sind vollstaendig klassifiziert; A/B853, C852 (bestehende Portalzertifikatfrage),
E804/853.49 Runtime-Punkte und fuenf strukturell bereite Draft-Projektionen bleiben.

Zwoelf reale Browseransichten mit synthetischem Transport und synthetischer Identitaet,
1366/1440/1920 jeweils Hell/Dunkel je Familie: kein horizontaler Ueberlauf und kein
axe-WCAG2A/AA-Befund. Datum/Nullwerte und hell/dunkel wurden gesichtet.
[Ergebnisse](screenshots/studio-audit-template-20261028/results.json).
Dies ist eine Komponentenabnahme, keine persoenliche Anmeldung oder Gesamt-E2E-Freigabe.
Die eigene Vorschau auf3011 wurde beendet und beide Einstiegdateien entfernt.

## Verbleibend

Der Gesamtauftrag ist nicht abgeschlossen.49 Runtime-Punkte bleiben im
[Arbeitsinventar](studio-runtime52-inventory-20261028.md). Andere CRM-Detailrouten,
Prozessraeume, Waage/Annahme und weitere komplexe Masken brauchen weiterhin ihre
eigenen vollstaendigen Funktionsvertraege. Gleiche Routen oder eine Katalogkennung
ersetzen diese Abnahme nicht. Der versehentliche Root-Edit des Vorlagenagenten ist
separat dokumentiert; geliefert wird ausschliesslich der akzeptierte Quellbaum.

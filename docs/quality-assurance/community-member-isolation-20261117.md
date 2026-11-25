---
title: Mandantenbindung der Gemeinschaftsmitglieder
owner: Codex
type: reference
status: in Arbeit
last_reviewed: 2026-11-17
---

# Gemeinschaftsmitglieder: Mandant und URL-Elternobjekt

## Bestaetigter Befund

Die vier Mitgliedschaftswege im Partnerstamm nutzten bisher einen leeren
Mandantenkontext. Die Existenzpruefung des Partners war global; Listen zeigten
alle Mitglieder einer Gemeinschaft, Aendern/Loeschen ignorierten community_id
aus der URL. Die Tabelle besitzt keine eigene tenant_id. Direkte vorhandene
Verbraucher wurden in app/modules/packages/services gesucht; die aktiven
Zugriffe liegen im Partner-Endpunkt und BusinessPartnerService.

## Korrektur

- Mitgliedschaftswege verwenden get_tenant_id und denselben Service mit
  vertrauenswuerdigem aktiven Mandanten.
- Jeder Mitglieder-Leser/-Schreiber bindet den Datensatz ueber den zugehoerigen
  BusinessPartner an dessen tenant_id; Mutationen binden zusaetzlich die
  Mitglieds-ID und die Gemeinschaft aus der URL.
- Erstellen und Neuzuordnung verlangen einen eigenen Partner. Ein fehlender
  Partner/Elternsatz oder eine fremde Zuordnung wird vor Mutation abgewiesen;
  explizites partner_id=NULL liefert einen Validierungsfehler.
- Lesen verwendet die vorhandene bereichsuebergreifende open_items_read-Policy
  (CRM, Sales, Finance, Einkauf, admin). Schreiben behaelt die vorhandene
  CRM-Policy. Eine Portalrolle allein berechtigt zu keinem Mitgliedschaftsweg.
- Der bestehende globale Gemeinschaftskatalog bleibt gemeinsam lesbar.
  Seine globale Pflege verlangt jetzt die bestehende PLATTFORM/admin-Policy;
  ein CRM_ADMIN eines Bereichs darf ihn nicht global veraendern.
- Der alte ungebundene Partnerpruefer und ein unbenutzter Commit-Helfer entfallen.
  Der Endpunkt schrumpft von2716 auf2704 Zeilen; die Godfile-Ratsche wird gesenkt.

Keine neue Tabelle, kein DDL, kein neues Rollenmodell, kein weiterer Container
oder Pruefstand. Interne globale Katalogmetadaten bleiben ein bestehender
Shared-Data-Vertrag; dessen fachliche Modellierung wird hier nicht ersetzt.
Unabgenommene schreibende MCP-Freischaltungen dieser Unterbereiche erfolgen nicht.

## Nachweise

Neun isolierte Vertraege bestanden: echter kompilierter Partner-Join mit Tenant-
und Community-Parametern, fehlender Mandant, falsche Eltern-ID, fremde/NULL-
Neuzuordnung, erlaubte Mutationen, Rollenmatrix und Tenant-Abhaengigkeit.

Ein echter PostgreSQL-Vertrag mit zwei synthetischen Mandanten, drei Partnern
und zwei gemeinsamen Gemeinschaften bestand als valeo_agent (NOSUPERUSER,
NOBYPASSRLS): jede Seite sieht ihre eigenen Mitglieder; fremdes Anlegen,
Umhaengen, Aendern/Loeschen und falsche URL-Elternobjekte bleiben gesperrt;
erlaubtes Umhaengen/Loeschen wirkt und laesst den fremden Datensatz unveraendert.
Alle Fachzeilen wurden in der gemeinsamen aeusseren Transaktion zurueckgerollt.
Vorher: keine fremde Probe-Sitzung, Revision psm_register_entfernt_20261104.
Keine Migration oder zusaetzliche Rechtevergabe in diesem Slice.

49 angrenzende Partner-/Kundenprofil-/HTTP-Vertraege bestanden. Zusaetzlich
bestehen die drei Profilmetadaten-Vertraege: Bank-, Steuer-, Kontakt- und
Datenschutzfelder bleiben auch im expliziten AgentMaskContract als sensibel
gekennzeichnet. Der Zugriffsschutz erfolgt durch die vorhandenen Rollen und
Mandantenpruefungen; diese Metadatenkennzeichnung ist keine neue Berechtigung.

## Integration

Separater Branch codex/community-membership-isolation-20261117 auf dem
konfliktbereinigten PR153-Head cd2644b92. PR153 laeuft weiter ohne Abbruch oder
Neustart seiner erfolgreichen Tests. Gemeinsame CI fuer diesen Sicherheitsslice
und eine Browserabnahme stehen noch aus.

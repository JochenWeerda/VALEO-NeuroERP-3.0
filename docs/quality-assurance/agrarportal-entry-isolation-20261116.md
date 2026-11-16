---
title: Agrarportal-Einstieg, Kundenpruefung und Kontextbindung
type: reference
audience: [agent, entwickler, qa, architect]
owner: Codex
status: aktiv
last_reviewed: 2026-11-16
version: 1.0.0
description: Nachgewiesene Frontend-Grenzen und ausdruecklich offene Identity-/Fachkettenvertraege.
---

# Nachgewiesener Slice

Der bestehende Launcher enthaelt eine Agrarportal-Gruppe mit den vorhandenen
Portalrouten. Interne Belegleser sehen Kundenansicht pruefen; die Auswahl
verwendet den bestehenden CustomerPortalLayout/PortalKontoGate und den
serverseitig geprueften Kundenkontext, keine neue Kundenanmeldung.
Eine Anmeldung mit vom Server bestaetigten Kundenkonten gelangt nach dem
Callback direkt ins Portal des bereits gebundenen Mandanten. Interne Rollen
bleiben im Launcher. Fehler/Malformed bei der Kontenabfrage werden nicht als
erfolgreicher interner Einstieg behandelt.

Die interne Pruefansicht ist sichtbar markiert und bleibt beim Portal-
Unterseitenwechsel erhalten. Die Sitzungsbindung umfasst sub, Mandant,
normalisierte Rollen/Scopes und, sofern vorhanden, Issuer und Provider-Sitzung.
Auswahl und Pruefmodus verfallen bei anderem Kontext, auch vor dem naechsten
UI-Ereignis. Kein fremder alter X-Kundenkonto nach Kontextwechsel. Ein normaler
Tokenrefresh derselben Sitzung behaelt den Kontext. Ein Kundenkontowechsel
bricht alte Anfragen ab, bevor er neue Auswahl freigibt; geaenderte Rechte bei
gleicher Kunden-ID werden neu uebernommen. QueryClient war bereits ueber
DataBootstrap partitioniert; dieser Slice ergaenzt den globalen Kontostore und
den Kontenlistenschluessel, statt eine generell fehlende Cachetrennung zu behaupten.

Der Portal-Abmeldeknopf nutzt jetzt den kanonischen Logout statt nur eine
Navigation. Harte Beispiel-Benachrichtigungszahl entfernt. Portalrahmen und
Kopfzeile verwenden Theme-Tokens und passen in die drei Desktopgroessen.
Pruefansicht erteilt keine Rechte und ist keine vollstaendige Simulation der
Portalrolle: der Akteur bleibt ein interner Bearbeiter.

## Wichtige Abgrenzungen

- Der aktive Mandant bleibt ausschliesslich an die gepruefte Identitaet gebunden.
  Ein echter autorisierter Wechsel zu einem anderen Handelspartner fehlt noch.
  Kein freier Header- oder Dropdown-Bypass wurde eingefuehrt.
- Interne Futterberatung liest teilweise tenantweite Rezeptur-/Betriebsdaten.
  Diese wird im kundengekennzeichneten Pruefmodus nicht als Kundenansicht geladen;
  ein deutlich benannter interner Einstieg bleibt verfuegbar. Kundenbezogene
  Futterberatung benoetigt noch einen durchgaengigen Portal-Kundenvertrag.
- Portal-Shop schreibt bisher ein separates CustomerOrder-Modell. Die vom
  Nutzer gewuenschte gemeinsame Angebots-/Auftragsvariante samt Adressen,
  Historienvorschlaegen, Kundensilos und Fotoanfrage ist noch umzusetzen.
- Keine Analyse-, Marketing- oder Trainingsfreigabe aus kostenloser Nutzung
  abgeleitet, keine neue Datensammlung oder Kundenrollen vergeben.

Entscheidungsvertraege: [Handelspartnerauswahl](../architecture/agrarportal-tenant-selection-20261116.md)
und [Kunden-Belegvariante](../workflows/portal-customer-document-variant-20261116.md).

## Belege

33 gezielte Frontend-Verhaltenstests in sieben Dateien bestanden: Portallanding,
Pruefmodus ohne Identitaetstausch, Abmeldung, Kontext-/Rechte-/Provider-Sitzungswechsel,
Abbruchreihenfolge, Metadatenwiderruf und Navigation. Vollstaendige Typpruefung
bestanden. Tests verwenden synthetische Identitaeten und HTTP-Adapter, sie
belegen keine neue PostgreSQL-/OIDC-Mehrmandantenabnahme.

Sechs synthetische Portalrahmenansichten und sechs Launcheransichten bestanden
bei 1366x768, 1440x900, 1920x1080 jeweils hell/dunkel: keine Kontrastverletzungen
oder offenen Axe-Hinweise, keine horizontalen Ueberlaeufe, keine Laufzeitfehler
oder externen Anfragen. Portalrahmen verwendet echte Layout-/Kontokomponenten
mit synthetischem Testbetrieb, sein Inhaltsbereich ist ausdruecklich eine
Testflaeche und keine abgenommene native Fachmaske. Ergebnisse/Screenshots unter
artifacts/portal-preview-visual-20261116 sowie artifacts/app-launcher-visual-20261116.

Bestehende serverseitige PortalKunde-/Tenantguards wurden lesend geprueft;
keine Backendautorisierung veraendert und keine neue DB-Verhaltenssuite
behauptet. Keine lokalen Fachtest-Schreibdaten, Migrationen, Datenbank- oder
Containerneuanlage. Lokaler Einzel-Frontendbuild folgt im Betriebsnachlauf.

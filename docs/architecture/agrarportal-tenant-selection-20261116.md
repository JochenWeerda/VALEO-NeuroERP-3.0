---
title: Agrarportal mit mehreren Handelspartnern und interner Kundenansicht
type: explanation
audience: [agent, architect, entwickler, qa]
owner: Codex
status: geplant
last_reviewed: 2026-11-16
version: 1.0.0
description: Verbindliches Ziel fuer Kundenzugang, Handelsmandantenauswahl und getrennte Datenzwecke.
---

# Kundenzugang und Handelspartnerauswahl

Ein Login kann mehreren Kundenbetrieben bei mehreren Handelsmandanten
zugeordnet sein. Auswahlkette: gepruefte Person -> autorisierter
Handelspartner/Mandant -> dort berechtigtes Kundenkonto/Betrieb ->
rollen- und objektgebundene Fachaktion. Kundennummern und Rollen duerfen
sich zwischen Handelspartnern unterscheiden. Dieselbe Person oder derselbe
Betrieb eroeffnet keinem Haendler Zugriff auf die Daten eines anderen.

## Gepruefter Ist-Stand

portal_kunde.py prueft aktuellen signierten Mandanten, sub, gueltige und nicht
widerrufene Kundenzuordnung, kundenbezogene Rechte und gegebenenfalls Schlaege.
Die vorhandene Kontowahl arbeitet nur innerhalb dieses Mandanten.
Die zentrale tenant_binding-/OIDC-/RLS-Kette verweigert abweichende Header.
Ein autorisierter Mehrmandantenwechsel existiert darin noch nicht. Die
Tenant-Registry fuer Worker ist KEIN Mitgliedschaftsverzeichnis fuer Kunden.

## Erforderlicher Identitaetsvertrag (noch umzusetzen)

1. Die Identitaetsschicht liefert ausschliesslich aktive, nicht widerrufene
   Zuordnungen der geprueften Person zu Handelspartnern, ohne fremde Geschaeftsdaten.
2. Bei mehreren Zuordnungen explizite Auswahl; bei genau einer kann sie
   vorbelegt werden. Bei keiner kein Standard-/Demo-Mandant als Ersatz.
3. Der Server prueft jede Auswahl und erzeugt ueber den vertrauenswuerdigen
   Identitaetsweg einen auf genau den aktiven Mandanten gebundenen Kontext.
   Rollen/Scopes gelten pro Zuordnung, niemals als Vereinigung aller Haendler.
   Token-Issuer, Audience, Sitzung, Ablauf und Widerruf bleiben verpflichtend.
4. Kein globales Umschreiben des tenant_id-Benutzerattributs fuer einen Wechsel:
   parallele Sitzungen/Tabs duerfen sich nicht gegenseitig umhaengen.
5. Kein frei gesetzter X-Tenant-ID und keine Browserliste als Autorisierung.
   Bestehende ERP-/MCP-/CLI-/Export-/Download-/Event-Pruefungen bleiben erhalten.
6. Erst danach Datenbanktransaktion/RLS und Kundenkonto im neuen Kontext.
   Laufende alte Anfragen abbrechen, alte Anzeigen entkoppeln, Caches, Entwuerfe,
   Downloads und Live-Abonnements nach Kontext neu initialisieren.
7. Echte Negativnachweise: fremder Mandant, fremder Kunde im gleichen Mandanten,
   gleiche Kunden-ID in zwei Mandanten, abgelaufene/widerrufene Beziehung,
   Rollenwechsel, verspaetete Antworten und Rueckwechsel.

Die Einfuehrung dieses Vertrags erfordert einen eigenen Identity-/Provider-
Slice samt Migrations- und Authentifizierungsabnahme. Ein UI-Selektor wird
vorher nicht als funktionsfaehiger Mandantenwechsel ausgeliefert.

## Landings und interne Pruefansicht

Eine Anmeldung mit serverseitig bestaetigter Kundenkonto-Zuordnung gelangt
direkt ins Agrarportal des bereits geprueften Mandanten. Interne Belegleser
bleiben im ERP-Launcher. Dort ist Kundenansicht pruefen erreichbar: vorhandene
interne Kundenauswahl innerhalb des aktiven Mandanten, sichtbarer Pruefmodus,
Actor bleibt der interne Bearbeiter. Kein Kundenkennwort, kein Identitaetstausch,
keine Rechteerweiterung. Diese Ansicht belegt UI-Fortschritt, nicht die
vollstaendige Gleichheit zu den Rechten einer echten Kundenanmeldung.

## Dienste, Daten und Bedarfsermittlung

Bestellungen, eigene Dokumente, Schlagkartei und Futterberatung sind getrennte
Kundendienste. Portal-URLs allein belegen keine Kundenisolation: insbesondere
interne Futterrezepturen sind bisher nur mandantenbezogen und duerfen nicht
unverprueft als kundenweite Quelle freigeschaltet werden.

Kostenlose Bereitstellung erteilt keine pauschale Freigabe zur Vermarktung.
Notwendige Servicedaten, optionale Bedarfsempfehlungen, Werbung und etwaiges
Modelltraining haben getrennte Zwecke, Empfaenger und Rechtsgrundlagen.
Keine automatische Weitergabe von Betriebsdaten an andere Handelsmandanten.
Einwilligung, soweit verwendet, muss freiwillig, informiert, zweckspezifisch
und widerrufbar sein; eine unnoetige Verarbeitung als Zugangsvoraussetzung
kann diese Freiwilligkeit ausschliessen.
[EDPB](https://www.edpb.europa.eu/sme/be-compliant/process-personal-data-lawfully_en),
[DSGVO Art. 6/7](https://eur-lex.europa.eu/legal-content/DE/ALL/?uri=celex%3A32016R0679).
Es wurde in diesem Slice weder Profiling noch Marketingtracking eingeschaltet.

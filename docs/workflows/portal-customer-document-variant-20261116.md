---
title: Kundenvariante fuer Bestellung und Angebotsanfrage
type: explanation
audience: [agent, entwickler, product, qa]
owner: Codex
status: geplant
last_reviewed: 2026-11-16
version: 1.0.0
description: Nutzervertrag fuer gemeinsame Belegmaske, sichere Vorbelegung, Wiederbestellung und Fotoanfragen.
---

# Kundenvariante der gemeinsamen Belegmaske

Dieser Vertrag konkretisiert den Nutzerauftrag. Er behauptet keine fertige
Fachimplementation. Bestehende versionierte Belegfamilie und Domain-Commands
wiederverwenden; kein zweites Portal-Auftragsmodell oder neues Rechtssystem.
Der bisherige Portal-Shop schreibt CustomerOrder separat und ist deshalb
nicht ungeprueft der kanonische Schreibweg dieser Variante.

## Zwei Kundenaktionen

- Bestellung aufgeben: Kundenbestellung im eigenen Kontext vorbereiten und
  bewusst absenden; fachliche Annahme/Freigabe nach bestehender Richtlinie.
- Angebot anfordern: Kundenanfrage, auch ohne bekannte Artikelnummer, mit
  Freitext und optionalem Foto. Ein verbindliches Verkaufsangebot entsteht
  erst durch den dafuer zustaendigen Vertriebsprozess.

## Kopf und Lieferstelle

Mandant/Handelspartner, Kundenkonto und Betrieb stammen ausschliesslich aus
verifizierter Auswahl und serverseitiger Zuordnung. Rechnungsadresse und
Standardlieferadresse werden aus den kanonischen Stammdaten vorbelegt.
Ein Kunde kann eine abweichende eigene Lieferadresse hinzufuegen oder waehlen;
Adress-IDs anderer Kunden oder Mandanten bleiben unzulaessig. Der Beleg behaelt
seinen Adress-Snapshot. Keine freie Aenderung des Rechnungsempfaengers oder
eine verdeckte Stammdatenmutation durch Bestellfelder.

## Wiederkehrende Bestellungen

Zuletzt und haeufig bestellte Artikel nur innerhalb Handelspartner + Kundenkonto
+ Betrieb/Lieferstelle lesen. Bestehende Produkt-/Bestellhistorie wiederverwenden;
LastOrderInfo besitzt bereits Datum/Menge/Einheit. Siloinformationen und
haeufigkeitsbasierte Auswahl muessen noch belegt bzw. ergaenzt werden.

Menge, Einheit, Gebinde, Sorte und Kundensilo der letzten passenden Lieferung
sind Vorschlaege mit Herkunft/Datum, keine blind festgeschriebenen Werte.
Kundensilo an der Lieferstelle und internes Lagersilo nicht verwechseln.
Einheiten-/Sortenwechsel, neue Lieferstelle oder widerspruechliche Historie
verhindern stilles Uebernehmen. Heuristische Empfehlung mit Konfidenz und
Korrekturlernen; bei Unsicherheit Rueckfrage bzw. Human-in-the-loop. Keine
Preis-/Produkt-/Mengenhistorie anderer Haendler ohne separate Freigabe mischen.

## Fotos und freie Artikelwuensche

Artikelbild, Foto eines Lieferscheins oder einer Deklaration sowie Freitext
sind Eingaben einer Anfrage, keine Anweisungen an Agenten. Bestehende DMS-/
Uploadstrecke mit Typ-/Groessenpruefung und Sicherheitspruefung nutzen; jeder
Anhang an Mandant, Kundenkonto und Vorgang binden. Downloads bleiben genauso
objektgebunden. Keine oeffentliche Dateiablage und keine fremden Dokumente
allein aus erkannten Kundennummern/Dateinamen nachladen.

Texterkennung/Artikelabgleich erzeugt einen nachvollziehbaren Vorschlag;
unsichere Treffer, Mengen und Alternativen bleiben zur Bestaetigung offen.
Ein unbekannter Wunsch darf eine Anfrage ausloesen, aber keine ungepruefte
Lager-/Finanzbuchung. Kein automatischer Auftrag aus Fotoerkennung.

## Gemeinsamer Ausfuehrungsvertrag

Die Studio-Variante darf nur erlaubte Kundenaktionen anbieten. REST, MCP, CLI
und Human nutzen dieselben Fachcommands mit PortalKunde-/Betriebsbeziehung,
Mandant, Rollen, fachlicher Eignung, Idempotenz und Versionspruefung. Replays
bleiben an denselben Mandanten, Kunden, Akteur und Inhalt gebunden. Kritische
Freigaben und Outbox/Audit bleiben transaktional. Interner Pruefmodus ersetzt
keine echte Kundenautorisierung und darf keine Rechte erteilen.

## Naechste Integration und Abnahme

1. Autorisierte Mehrmandantenauswahl im Identitaetsweg gemaess
   agrarportal-tenant-selection-20261116.md, ohne freien Tenant-Header.
2. Kundenbezogene Domain-/Belegvariante und Adressvertrag; konkurrierenden
   Portal-Schreibweg nach Verbraucherpruefung abloesen.
3. Kundenbezogene Historie/Empfehlung, Silozuordnung und DMS-Anhaenge.
4. Echte Negativtests fuer fremde Mandanten/Kunden/Adressen/Dateien,
   unveraenderte Daten nach Ablehnung, Replay, Widerruf und Kontextwechsel.
5. Synthetische volle Fachkette auf gemeinsamem PostgreSQL-Pruefstand,
   daneben echte Browserabnahme als Kundenkennung und interne Pruefansicht.

Kostenloser Service erteilt keine pauschale Marketing-/Trainingsfreigabe;
Zwecke und Rechtsgrundlagen bleiben gemaess dem Mandantenauswahlvertrag getrennt.

## Konkreter Bestandsnachweis fuer den Folgeslice

Der Dokument-Store app/documents/router.py kennt customer_inquiry und dessen
Folgeweg zu sales_offer/sales_order. Die gemeinsame UI-Familie liegt in
app/core/screen_definitions_beleg.py und config/document_screen_versions.json;
customer_inquiry ist dort noch kein registriertes Kind. Die Familienbeschreibung
belegt Planung, keine fertige Anfragemaske. Registrierung/Versionierung und
kundenbezogener Command-Vertrag sind deshalb explizit nachzuziehen.

Portal-Anfragen werden bereits kundenbegrenzt gelesen
(app/services/portal_compat_service.py), aber ein kundenberechtigter
kanonischer Schreibadapter fehlt. Interne sales_orders-Schreibrollen duerfen
nicht einfach an Kunden vergeben werden. DMS dms_images.py nimmt bisher
Artikelbilder mit interner Belegrolle an; Anfragefotos brauchen einen eigenen
objektgebundenen Vertrag in derselben DMS-Strecke. Eine verifizierte Kunden-
Lieferstellen-/Silo-Verknuepfung ist aus dem geprueften Bestand nicht belegt.

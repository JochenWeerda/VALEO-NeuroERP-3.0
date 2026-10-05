---
title: Launchpad Spaces und Pages
type: reference
audience: [design, entwickler, agent]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-17
version: 1.5.0
description: Startseite als belegzentriertes Launchpad. Fiori-Struktur (Spaces/Pages) als Informationsarchitektur, nicht als visuelle Kopie. Hierarchie Sprint 1+2 in launchpad-informationshierarchie.md.
---

# Launchpad Spaces und Pages

Produktive Launchpads von Agrarhandelshäusern (AGRAVIS, BayWa) sind nicht
öffentlich. VALEO übernimmt das **Strukturmuster**, nicht Look-and-Feel,
Kachelfarben oder Transaktionscodes.

## Abbildung

| Fiori | VALEO |
|---|---|
| Catalog / Target Mapping | Navigationskatalog und Masken-Registry |
| Space | Arbeitswelt, nicht Modul |
| Page | Aufgabe in der Arbeitswelt |
| App-Kachel | Beleg oder Arbeitsliste, dieselbe Entität darf mehrfach vorkommen |
| Enterprise Search | Startsuche plus Ctrl+K |
| Personalisierung | Startseite anpassen: Overlay über Spaces/Pages, App-Katalog, letzter Space |
| Notifications | bestehende Notification-Center in der TopBar |
| Control Tower / Prozesse | Leitstand, nicht die Startseite |

Kette: **Space → Arbeitswelt → Page → Aufgabe → Business Object.**
Nicht: Modul → Untermodul → Maske → Maske.

Die Startseite darf diese Kette nicht **gleichzeitig** als volle linke Navigation,
Bereichsreiter, Unterreiter, Kacheln, Schnellaktionen und KPIs zeigen.
Sprint 1+2: [`launchpad-informationshierarchie.md`](launchpad-informationshierarchie.md)
— Sidebar auf Start eingeklappt, 6–10 Kacheln je Seite, drei Kunden-Einstiege,
Finder mit Kategorie und Beschreibung. Sprint 3 (KIM Object Page) bleibt
Claude-Claim. Personalisierung bleibt.

## Agrarhandel

1. **Handel & CRM** — Meine Kunden, CRM/Außendienst, Angebote & Aufträge, Verkauf, Einkauf, Kontrakte, Preise, Kasse
2. **Ernte & Warenannahme** — Annahme & Waage, Erntekampagne, Qualität & Labor, Proben, Abrechnungsvorbereitung
3. **Lager & Logistik** — Lager & Silo, Bestände, Tagesdisposition, Touren/Fuhrpark, Versand, Umlagerungen, Inventur
4. **Betriebsmittel & Produktion** — Dünger, Pflanzenschutz, Saatgut, Futtermittel, Mischungen, Chargen
5. **Finanzen & Controlling** — Debitoren, Kreditoren, Zahlungen, Belegkontrolle, Kostenrechnung, Controlling, Abschluss
6. **Steuerung & Compliance** — Leitstand, Freigaben, Dokumente, QS, GMP+, PSM/Zulassungen, Nachhaltigkeit, Audit

Ein Kontrakt liegt in Handel **und** in der Ernte-Abrechnung. Ein Kunde liegt in CRM, bei Debitoren und in der Disposition. Der Vorgangsstand bleibt am Beleg (`ProcessBand`).

## Technik

Die Startseite zeigt oben die Arbeitswelt (Katalog und Anpassen in derselben
Zeile). Der Prozessraum ist eine Auswahl, keine zweite Reiterleiste; bei nur
einem Raum eine Überschrift. Darunter liegen die Kacheln (App- und
Task-Kacheln, max. 10). Die linke Navigation ist auf `/` ausgeblendet, bis sie
über die Top-Leiste geöffnet wird. Schnellaktionen sind vier primäre plus
Mehr. KPI-Karten führen zur Auswertung; Zeitraum/Trend/Abweichung stehen
einmal darunter, ohne erfundene Werte. App-Finder hat Kategorie (= Arbeitswelt)
und sucht in Name, Beschreibung und Pfad, auch ohne Anpassen-Modus.

Kachelfarben kommen aus den Chart-Slots
(Fläche plus linker Akzent), nicht aus einer SAP-Palette und nicht aus
Status-Grün/Rot.

**Anpassen** ist ein Modus, kein SAP-Lookalike: Klick auf eine Kachel öffnet
sonst die App; im Anpassen-Modus erscheinen Entfernen, Kachel anpassen,
Verschieben und Ziehen. Gruppen entsprechen Seiten. Katalogseiten lassen sich
zurücksetzen und ausblenden, die erste Seite einer Arbeitswelt bleibt
gesperrt. Selbst angelegte Gruppen können gelöscht werden. Der Overlay liegt
lokal in `localStorage` (`valeo.launchpad.overlay`), nicht in der
ScreenDefinition. Katalog:
`packages/frontend-web/src/app/navigation/launchpad-spaces.ts`.
Flow-Spine-Routen sind ausgeschlossen. Alte Space-IDs werden umgebogen.

Die früheren Katalog-Lücken (Kategorie, Finder ohne Anpassen, Beschreibung)
sind in `HOME-IA-HIERARCHIE` Sprint 2 geschlossen. Aktionen an der Kachel
statt SAP-Aktionsblatt bleiben Absicht. Details:
[`claude-cursor-launchpad-katalog-2026-09-17.md`](../agent-ops/handshakes/claude-cursor-launchpad-katalog-2026-09-17.md).

---
title: Genossenschaft und Mitglieder
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.2.0
---

# Genossenschaft und Mitglieder

Genossenschaftliche Landhandelsbetriebe verwalten Mitglieder, Geschäftsanteile
und Mitgliederbezüge getrennt vom allgemeinen CRM-Kundenstamm.

## Voraussetzungen

- Bereich **Genossenschaft** ist freigeschaltet.
- Mitgliederstammdaten und Geschäftsanteilsregeln sind definiert.
- Verknüpfung zu CRM/Kundenstamm ist bei Bedarf eingerichtet.

## Mitglied anlegen oder pflegen

1. Öffnen Sie *Genossenschaft* → *Mitglieder*.
2. Legen Sie ein neues Mitglied an oder öffnen Sie einen bestehenden Datensatz.
3. Erfassen Sie Name, Anschrift, Mitgliedsnummer und Status (aktiv/ausgetreten).
4. Pflegen Sie Geschäftsanteile, Eintrittsdatum und ggf. Vertretungsberechtigte.
5. Speichern Sie und prüfen Sie Dubletten im CRM-Kontaktstamm.

## Geschäftsanteile und Auswertungen

1. Öffnen Sie das Mitglied → Register *Geschäftsanteile*.
2. Prüfen Sie Anzahl, Nennwert und Buchungsstand.
3. Nutzen Sie Listen-/Exportfunktionen für Mitgliederversammlung oder Jahresabschluss.
4. Gleichen Sie Mitgliederumsätze mit Kontrakt- und Annahmedaten ab, wenn erforderlich.

## Ergebnis

- Mitgliederstamm ist getrennt vom Vertriebs-CRM nachvollziehbar gepflegt.
- Geschäftsanteile und Mitgliedsstatus sind für Abrechnung und Reporting verfügbar.

## Häufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Dublette im CRM | Mitglied parallel als Kunde angelegt | Zuordnung/Dublettenprüfung nutzen |
| Anteile stimmen nicht | Manuelle Korrektur ohne Buchung | Geschäftsanteilsbuchung nachziehen |
| Mitglied nicht auffindbar | Filter Status/Austritt | Listenfilter zurücksetzen |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/commercial.tsx`: Genossenschaft/Mitglieder.
- `docs/benutzerhandbuch/crm.md`: Abgrenzung CRM-Kontakt vs. Genossenschaftsmitglied.

Reverse-Pflege: Bei neuen Mitgliedsfeldern, Anteilsarten oder Exporten diese Seite
und die Genossenschaftsmaske gemeinsam aktualisieren.

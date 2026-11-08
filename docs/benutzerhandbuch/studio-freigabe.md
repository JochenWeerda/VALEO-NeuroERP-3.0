---
title: Studio-Definition mit Vier-Augen-Pruefung freigeben
type: how-to
audience: [anwender, administrator, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# Studio-Definition freigeben

Die Abnahme verwendet ausschliesslich synthetische Kennungen und einen Testmandanten. Eine Freigabe aktiviert die exakt gepruefte Maskenfassung. Sie erzeugt keine Rechnung, Buchung oder Bestandsbewegung.

## Entwurf und Pruefung

Der Bearbeiter speichert den Entwurf und gibt ihn mit **Pruefung** zur Kontrolle. Die Historie zeigt Zeitpunkt, Urheber, Aktion und Revision. **Aenderungen ansehen** vergleicht unveraenderliche Fassungen. Nach einer lokalen Aenderung muss der Bearbeiter zuerst erneut speichern und pruefen.

Eine andere angemeldete menschliche Administration oeffnet den gespeicherten Entwurf. **Prozess simulieren** prueft die aktuelle Revision. Nur ein vollstaendiger erfolgreicher Nachweis laesst **Freigeben** zu. Derzeit ist das feste lesende Agrar-Profil grain.v1 abgenommen; nicht nachgewiesene Fachaktionen und Regelvarianten bleiben gesperrt.

## Freigabe durch die zweite Person

Nach bestandener Simulation waehlt die zweite Person **Freigeben**. Der Status wechselt zu **published_temp**. In der Historie bleiben Bearbeiter und Freigeber getrennt erkennbar. Aenderungen oder veraltete Nachweise erfordern eine neue Pruefung.

![Erfolgreiche Veroeffentlichung des Testentwurfs](img/studio-freigabe-20261015/01-vier-augen-veroeffentlicht.jpg)

Mit **Freigegebene Maske oeffnen** wird die aktive Fassung in der normalen Masken-Runtime geladen. Die Abnahme bestaetigt diesen Aufruf mit der urspruenglichen Bearbeiterrolle; der Testmandant hat hier keine Artikelzeilen.

![Freigegebene lesende Maske mit unveraenderter Bearbeiterrolle](img/studio-freigabe-20261015/03-freigegebene-lesemaske.jpg)

## Temporaere Testrechte zuruecknehmen

Die zusaetzliche Prueferkennung dient ausschliesslich dieser Abnahme. Anschliessend wurden ihre admin-Rolle entfernt, ihre Sitzungen beendet und die Kennung gesperrt. Der Browser wurde regulaer abgemeldet. Die erneute Anmeldung muss scheitern.

![Keycloak weist die Anmeldung der gesperrten Prueferkennung ab](img/studio-freigabe-20261015/02-prueferkennung-gesperrt.jpg)

Die urspruengliche Bearbeiterkennung behaelt ihre vorhandene Bereichsrolle. Diese temporaere Testvergabe ist kein Verfahren zur dauerhaften Vergabe von Administrationsrechten an Fachanwender.

Technische Nachweise und Grenzen stehen in der [Abnahmedokumentation](../quality-assurance/studio-closure-20261015.md).

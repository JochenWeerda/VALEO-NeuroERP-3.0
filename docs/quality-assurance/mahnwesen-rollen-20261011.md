# Mahnwesen: Rollen vor der Datenbank

Stand: 2026-10-11 · Slice `MAHNWESEN-ROLLEN-20261011` · offener Punkt aus [Ein Mahnlauf](ein-mahnlauf-20261011.md)

## Befund

Die elf Mahnwege verlangten eine Anmeldung, aber keine Rolle. Wer angemeldet war – Lager, Personal,
Verkauf –, konnte einen Mahnlauf auslösen, Mahnstufen-Regeln anlegen und Mahnungen an Kunden versenden.

## Abhilfe

Das Muster der Zahlungsläufe und Eingangsrechnungen (`app/auth/finance_roles.py`, seit 07.10.2026):

| Zugang | Rollen | Wege |
|---|---|---|
| Lesen (`finance_read`) | `FINANCE_LESEN`, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`, `admin`, `manager` | Kandidaten, erzeugte Mahnungen, Mahnungsliste, Regeln lesen |
| Bearbeiten (`finance_write`) | `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`, `admin`, `manager` | Mahnlauf, Mahnung anlegen, Regel anlegen, verarbeiten, versenden, Bezahlt-Vermerk |

Die Rolle wird **vor** dem ersten Datenbankzugriff geprüft (Abhängigkeit am Dekorator).

**Warum Bearbeiten und nicht Admin:** Mahnen ist Tagesgeschäft der Debitorenbuchhaltung. Ein Mahnlauf
bewegt kein Geld und bucht nicht ins Hauptbuch; die strengere Klasse bleibt Freigabe und Ausführung
von Zahlungen vorbehalten.

**In der Maske:** Ein abgelehnter Abruf sah aus wie „Keine überfälligen Debitoren-OP". Die Seite sagt
jetzt „Für das Mahnwesen fehlt die Finanzrolle" und hält den Knopf gesperrt.

## Wirkung im Betrieb

Wer bisher ohne Finanzrolle gemahnt hat, bekommt 403. Vor einer Inbetriebnahme prüfen, dass die
Debitorenbuchhaltung im Anmeldedienst `FINANCE_BEARBEITEN` (oder `FINANCE_ADMIN`) trägt.

## Nachweis

`tests/test_mahnwesen_rollen_vertrag.py`, ohne Datenbank:

- zehn Rollen (darunter keine, `user`, `LAGER_ADMIN`, `PERSONAL_ADMIN`, `SALES_BEARBEITEN`) an elf Wegen:
  erlaubt erreicht die Datenbankgrenze, sonst 403 **ohne** Datenbankzugriff;
- ohne Anmeldung kein Weg;
- jeder Mahnweg hat eine Zugangsklasse – ein neuer Weg ohne Eintrag macht den Vertrag rot.

Dazu ein Vitest für die Meldung in der Maske. Nachbarschaft (25 Dateien rund um Mahnwesen und offene
Posten) grün gegen `valeo_probe`.

## Offen

1. **Mahnen aus den Offenen Posten** (`open_items.py`, Masken-Command `mahnen`) und der Agentenweg
   sind hier nicht geprüft.
2. **Nicht aus diesem Slice:** `docs/schnittstellen/openapi.json` driftet auf `main` um eine
   Beschreibung aus dem WhatsApp-Slice (`fix(whatsapp)`, 6a4199ddf); die Prüfung
   `generate_openapi.py --check` ist daran rot.

# Offene Posten: Rollen vor der Datenbank

Stand: 2026-10-11 · Slice `OFFENE-POSTEN-ROLLEN-20261011` · Befund aus
[Mahnwesen: Rollen](mahnwesen-rollen-20261011.md)

## Befund

Keiner der elf Wege unter `/finance/open-items` prüfte eine Rolle. Wer angemeldet war, konnte offene
Posten anlegen, ändern, ausgleichen, einen Ausgleich zurücknehmen, löschen und mahnen.

## Entscheidung

Vorgabe des Auftraggebers: „Was nicht einfach läuft, läuft einfach nicht."

| Zugang | Rollen | Wege |
|---|---|---|
| Lesen (`open_items_read`) | Finanzrollen, dazu `SALES_*`, `CRM_*`, `EINKAUF_*`, `admin`, `manager` | Liste, einzelner Posten, Ausgleiche eines Postens |
| Bearbeiten (`finance_write`) | `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`, `admin`, `manager` | anlegen, ändern, ausgleichen (einzeln und im Stapel), Ausgleich zurücknehmen, mahnen |
| Leitung (`finance_admin`) | `FINANCE_ADMIN`, `admin` | löschen |

**Warum Verkauf, Vertrieb und Einkauf lesen dürfen:** Wer einen Auftrag annimmt, muss sehen, was der
Kunde schuldet; wer bestellt, was dem Lieferanten zusteht. Das Einkaufs-Dashboard liest die offenen
Posten bereits. Eine reine Finanz-Leserolle hätte diese Wege im Alltag still geleert. Lager, Personal,
Qualität und Ernteannahme lesen nicht.

**Warum Ausgleichen bei der Bearbeiterrolle liegt:** Zahlungseingänge zuordnen ist die tägliche Arbeit
der Buchhaltung. Die Leitungsrolle bleibt dem Löschen vorbehalten – ein offener Posten verschwindet
sonst durch Ausgleich oder Storno, nicht durch Löschen.

Die Rolle wird **vor** dem ersten Datenbankzugriff geprüft (Abhängigkeit am Dekorator). Aufrufe aus
dem eigenen Code (der Mahn-Command liest den Posten über die Funktion, nicht über HTTP) sind davon
nicht berührt.

## Wirkung im Betrieb

Vor einer Inbetriebnahme prüfen, dass die Buchhaltung im Anmeldedienst `FINANCE_BEARBEITEN` trägt
und die Finanzleitung `FINANCE_ADMIN`. Verkauf, Vertrieb und Einkauf lesen mit ihren eigenen Rollen.

## Nachweis

`tests/test_offene_posten_rollen_vertrag.py`, ohne Datenbank: fünfzehn Rollen an elf Wegen – erlaubt
erreicht die Datenbankgrenze, sonst 403 **ohne** Datenbankzugriff; ohne Anmeldung kein Weg; die
Leserollen des Verkaufs ändern nichts; jeder Weg hat eine Zugangsklasse.

## Offen

1. **Übrige Finanzwege:** `finance_roles` nutzen jetzt Zahlungsläufe, Eingangsrechnungen, E-Bilanz,
   Mahnwesen und offene Posten. Die anderen Finanz-Endpunkte (Buchungen, Konten, Zahlungseingang,
   Bankabgleich …) sind nicht geprüft.
2. **Einkaufs-Dashboard:** Scheitert der Abruf der offenen Posten, zeigt es still „0" statt eines
   Hinweises.

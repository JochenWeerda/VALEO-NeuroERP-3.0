# Kein „gebucht" ohne Buchung: Gutschrift, Inventur, Bestandskorrektur

Stand: 2026-10-12 · Slice `BUCHUNG-STILL-20261012` · offene Punkte aus
[Kontosperre: Meldung](konto-sperre-meldung-20261012.md)

## Befunde

**Gutschrift buchen** (`POST /sales/credit-notes/{id}/post`) hatte vier Fehler hintereinander:

1. Der Buchungskopf wurde festgeschrieben, bevor die Zeilen geschrieben waren.
2. Die Zeilen trugen die Kontonummern `1400` und `8400` im Feld für die Konto-ID. Das scheiterte am
   Fremdschlüssel; der Fehler wurde protokolliert und verschluckt. Ergebnis: Gutschrift „gebucht",
   Buchungskopf ohne Zeilen.
3. Wären die Zeilen durchgegangen, hätte die OP-Minderung **jeden** offenen Posten des Kunden
   getroffen (`rechnungsnr = … OR kunde_id = …`), jeweils um den vollen Betrag.
4. Die Antwort passte nicht zum Antwortmodell: Der Weg endete nach dem Festschreiben immer mit 500.

In beiden Datenbanken gibt es keine Gutschrift; Altdaten sind nicht zu bereinigen.

**Inventur verbuchen** und **Bestandskorrektur** protokollierten einen Fehler der
Hauptbuchbuchung und meldeten Erfolg. Bestand und Buchung teilen eine Transaktion; nach einem
Datenbankfehler war auch die Bestandsänderung verworfen.

**Inventur, Mandant:** Alle Wege nahmen den Mandanten aus `?tenant_id=`. Eine einzelne Inventur
lesen, ihre Positionen lesen, sie löschen und verbuchen sowie eine einzelne Position ändern und
löschen filterten gar nicht nach Mandant.

## Lieferung

- **Gutschrift:** Kopf, zwei Zeilen, Status und OP-Minderung in einer Transaktion; scheitert etwas,
  bleibt nichts stehen. Die Konten werden über den Kontenplan aufgelöst (eigenes Konto des
  Mandanten, sonst gemeinsamer Rahmen); fehlt eines, 409 mit Satz. Gemindert wird nur der offene
  Posten der Rechnung aus `invoice_reference`. Antwort passt zum Modell.
- **Inventur, Bestandskorrektur:** Ein Buchungsfehler ist ein Fehler (500 mit Satz, nichts
  gespeichert). Die Kontosperre bleibt 409.
- **Inventur:** Mandant aus der Anmeldung (`get_tenant_id`); eine fremde Inventur ist 404. Der
  Query-Parameter `tenant_id` entfällt (OpenAPI nachgezogen).

Auslegungen (einfachste tragfähige):

- Eine Gutschrift **ohne** Rechnungsbezug mindert keinen offenen Posten. Welcher Posten gemeint
  wäre, lässt sich ohne Bezug nicht sagen.
- Die frühere Absicht „Buchung nicht blockierend, Bestand bleibt" war mit einer gemeinsamen
  Transaktion nie erreichbar. Statt sie nachzubauen, gilt: ohne Buchung keine Bestandsänderung.

## Nachweis

Gegen `valeo_probe`:

- `tests/test_buchung_nicht_still.py` – 8 bestanden: Gutschrift bucht zwei Zeilen auf echte Konten;
  mindert nur den Posten ihrer Rechnung (250 → 150, der zweite Posten des Kunden bleibt 400);
  gesperrtes Konto: 409, kein Kopf, Gutschrift bleibt Entwurf, Posten unberührt; Bestandskorrektur
  und Inventur melden Buchungsfehler als Fehler und speichern nichts; Inventur wird mit Buchung
  verbucht; fremde Inventur gibt es nicht (lesen, Positionen, verbuchen, löschen, Position ändern
  und löschen: 404).
- `tests/test_kontosperre_meldung.py` – 8 bestanden; die Ausnahme der Ratsche für die Gutschrift ist
  entfernt.
- Nachbarn (`test_security_sales_credit_notes`, `test_inventory_counts`,
  `test_inventory_operations`, `test_process_kernel_wave73_…`): zusammen 95 bestanden.
- `generate_openapi.py --check` nach Neuerzeugung sauber; `check_dead_transactions.py` ohne neue
  Fundstelle; Ruff ohne neue Meldung.

## Nicht geprüft

- Die Masken (Gutschrift buchen, Inventur) im Browser.
- Gutschrift mit fehlendem Konto: Der gemeinsame Rahmen enthält 1400 und 8400 immer; der Fall ist
  nur im Code abgesichert, nicht im Test.

## Offen

- **Umsatzsteuer:** Die Gutschrift bucht den Gesamtbetrag gegen 8400. Eine Korrektur der
  Umsatzsteuer (1776) fehlt. Das ist eine fachliche Frage (brutto/netto, Steuersatz je Position)
  und nicht Teil dieses Slices.
- **Inventur anlegen** setzt `counted_by` nicht, das Feld ist Pflicht: `POST /inventory/counts`
  scheitert in einer frischen Datenbank. Wer gezählt hat, müsste aus der Anmeldung kommen.
- **Inventur-Wege ohne Rolle:** Jeder Angemeldete des Mandanten kann Inventuren verbuchen und
  löschen. Die Lagerrollen (`LAGER_*`) sind an diesen Wegen nicht gesetzt.
- Das Frontend (`inventory-count-service.ts`) ruft `PUT /inventory/counts/{id}`; den Weg gibt es
  nicht.

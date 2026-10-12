# Kontenplan: Mandant aus dem Kontext

Stand: 2026-10-12 · Slice `KONTENPLAN-MANDANT-20261012` · Befund aus
[Hauptbuch: Rollen](hauptbuch-rollen-20261011.md)

## Befund

`app/api/v1/endpoints/chart_of_accounts.py` nahm den Mandanten aus der Anfrage statt aus dem
Mandantenkontext:

| Weg | bisher |
|---|---|
| Liste, Prüfung, DATEV-Ausgabe | Query-Parameter `tenant_id`, sonst der Vorgabemandant – der Kopf `X-Tenant-ID` zählte nicht |
| einzelnes Konto lesen, ändern, löschen | Suche nur nach der Kennung, kein Mandantenfilter |
| anlegen | Mandant aus dem Feld `tenant_id` im Rumpf |

Wer lesen durfte, bekam mit `?tenant_id=` den Kontenplan und über die DATEV-Ausgabe die gebuchten
Buchungen eines anderen Mandanten; wer schreiben durfte, änderte und deaktivierte fremde Konten.

Zwei weitere Fehler traten beim Prüfen gegen die echte Datenbank zutage:

- **Anlegen scheiterte immer mit 500.** Das Schema trägt `currency` und `allow_manual_entries`, die
  Tabelle nicht. Der vorhandene Test brach bei jedem Status ungleich 200 stillschweigend ab.
- **Ändern wirkte nur, wenn der Name im Rumpf stand** – sonst meldete der Weg Erfolg ohne Wirkung.

## Entscheidung

- Der Mandant kommt an allen sieben Wegen aus dem Mandantenkontext (`get_tenant_id`). Ein
  Query-Parameter `tenant_id` wird nicht mehr gelesen, das Feld im Rumpf entscheidet nichts.
- Ein fremdes Konto gibt es nicht: lesen, ändern und löschen antworten 404.
- Der gemeinsame Kontenrahmen (`system`) bleibt für jeden Mandanten sichtbar **und pflegbar** – so
  ist es dokumentiert gewollt, und in der Entwicklungsdatenbank liegen 28 von 29 Konten dort. Ein
  Kontenplan, den niemand ändern kann, wird nicht benutzt.
- Anlegen und Ändern übergeben nur, was die Tabelle speichert.

## Geänderte Dateien

- `app/api/v1/endpoints/chart_of_accounts.py`
- `tests/test_kontenplan_mandant_vertrag.py` (neu)
- `docs/schnittstellen/openapi.json` – nur die vier Pfade des Kontenplans

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_kontenplan_mandant_vertrag.py` gegen den Prüfstand `valeo_probe` | 10 bestanden |
| derselbe Vertrag gegen den Stand davor (nur das Anlegen lauffähig gemacht) | 9 von 10 rot |
| 19 Testdateien, die den Kontenplan berühren | 1141 bestanden, 2 übersprungen |
| Ruff auf der Endpunktdatei | keine neue Meldung |

Der Vertrag prüft gegen die echte Datenbank mit zwei eigenen Mandanten und räumt seine Konten wieder
ab. Eine Ratsche verbietet jedem Weg des Kontenplans einen Query-Parameter `tenant_id`.

Keine Sichtprüfung: Im Entwicklungsbetrieb sendet die Oberfläche den Vorgabemandanten im Kopf; Liste
und Kontierung im Rechnungseingang lesen dieselben Konten wie zuvor.

## Offen

- **Gemeinsamer Kontenrahmen bei mehreren Mandanten:** Ändert oder deaktiviert ein Mandant ein Konto
  unter `system`, gilt das für alle. Solange je Installation ein Haus arbeitet, ist das richtig; mit
  mehreren Mandanten braucht es eine Kopie je Mandant oder eine Sperre.
- **Maske „Kontenplan" (`pages/finance/kontenplan.tsx`):** Die Felder heißen dort `kontonummer`,
  `bezeichnung`, `kontenart`; der Weg erwartet `account_number`, `account_name`, `account_type` und
  ein Pflichtfeld `tenant_id`. Ob beim Speichern übersetzt wird, ist nicht geprüft – Verdacht, dass
  Speichern aus der Maske nie ankam.
- **`openapi.json`:** Drei fremde Pfade weichen weiterhin vom Code ab (WhatsApp-Slices, Codex).
- **Übrige Finanzwege:** dieselbe Prüfung (Mandant aus Query oder Rumpf) steht für die anderen
  Finanzdateien aus.

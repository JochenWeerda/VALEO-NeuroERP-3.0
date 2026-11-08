# BELEG-012: Rechte an Belegen

Stand: 2026-10-13 · Slice `BELEG-012` · aus dem
[Masterplan Belegmaske mit Varianten](../design/belegmaske-varianten-masterplan.md) ·
Folge aus [Lesender Belegweg](belege-lesen-20261013.md) und
[Lesende MCP-Werkzeuge](belege-mcp-lesen-20261013.md)

## Vorher

Jeder angemeldete Benutzer eines Mandanten konnte jeden DocFlow-Beleg mit Preisen lesen, anlegen,
ändern, freigeben, buchen und stornieren. Eine Rolle prüfte kein DocFlow-Weg.

## Jetzt

Die Rolle der Anmeldung entscheidet, je Recht und Belegart (`app/auth/beleg_roles.py`). Es sind die
vorhandenen Rollen der Bereiche; ein zweites Rechtesystem gibt es nicht.

| Recht | Verkaufsbelege | Einkaufsbelege |
|---|---|---|
| lesen (Mengen, Stand, Kette) | Verkauf, Vertrieb, Buchhaltung, Lager | Einkauf, Buchhaltung, Lager |
| Preise sehen | Verkauf, Vertrieb, Buchhaltung | Einkauf, Buchhaltung |
| bearbeiten, ausstellen | `SALES_BEARBEITEN`, `SALES_ADMIN`; Lieferschein auch Lager | `EINKAUF_BEARBEITEN`, `EINKAUF_ADMIN`; Wareneingang auch Lager |
| buchen | Sachbearbeitung Verkauf, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN` | Sachbearbeitung Einkauf, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN` |
| Gebuchtes stornieren | `SALES_ADMIN`, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN` | `EINKAUF_ADMIN`, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN` |

`admin` hat jedes Recht; `manager` jedes außer dem Stornieren gebuchter Belege. Was Finance nicht bucht
(Angebot, Auftrag, Lieferschein, Bestellung, Wareneingang), nimmt zurück, wer es bearbeiten darf.

### Wo es gilt

- **Belegweg** `GET /belege/…`: ohne Leserecht 403 — vor dem ersten Datenbankzugriff, auch für einen
  Beleg, den es nicht gibt. Ohne Preisrecht liefert der Server weder Preisfelder noch Summen. Eine
  Aktion ohne Recht ist gesperrt („Keine Berechtigung."); ein sachlicher Sperrgrund bleibt stehen.
- **DocFlow-Kommandos:** anlegen, ändern, Entwurf löschen, freigeben, Druck und Export vermerken,
  umwandeln, buchen, stornieren prüfen ihr Recht vor dem ersten Schreibzugriff. Ein Folgebeleg
  braucht das Recht an der Belegart, die entsteht. Das Recht je Kommando steht im Verzeichnis
  (`app/core/belegkommandos.py`).
- **DocFlow lesend:** `GET /docflow/{id}` und die Liste liefern Preise und verlangen deshalb das
  Preisrecht; die Liste zeigt nur Belegarten, deren Preise der Leser sehen darf. Die Statushistorie
  verlangt das Leserecht.
- **MCP-Werkzeuge:** Der Scope `belege:read` öffnet das Werkzeug; welche Belegarten es zeigt und ob mit
  Preisen, entscheidet die Rolle des Tokens. Ein Agent mit Scope, aber ohne Rolle, sieht keinen Beleg.

## Nachweis

- `tests/test_beleg_rechte.py`: 14 bestanden gegen `valeo_probe`, an den 17 Referenzbelegen —
  Rollen je Recht; ohne Rolle und mit der Rolle des anderen Bereichs 403; Lager bekommt die Rechnung
  ohne jeden Betrag; Lesen ohne Aktion; Sachbearbeitung bucht, storniert aber nichts Gebuchtes;
  DocFlow liefert Preise nur mit Preisrecht; dreizehn Schreibversuche ohne Recht ändern weder Status noch
  Buchungen; Agent sieht, was seine Rolle sieht; Buchhaltung bucht und storniert, der Akteur steht in
  der Historie.
- Nachbarn (übrige DocFlow-Tests, MCP-Ausführung und Mandantentrennung, Belegvertrag, Belegweg,
  MCP-Belegwerkzeuge, Referenzbelege): 358 bestanden, 28 übersprungen.

## Auslegungen (meine, nicht entschieden)

- **Buchen darf auch die Sachbearbeitung des Bereichs**, nicht nur die Buchhaltung: Die Rechnung zu
  buchen ist heute der Abschluss des Fakturierens im Verkauf. Gebucht wird in jedem Fall von Finance.
- **Gebuchtes stornieren ohne `manager`** und ohne Sachbearbeitung (Risikoklasse R4).
- **Das Lager liest alle Belege ohne Preise.**
- **Vertrieb (`CRM_*`) liest Verkaufsbelege mit Preisen**, wie er schon offene Posten liest.
- **Freigabe:** Seit APPROVAL-001 entscheidet die Freigabematrix, ob ein Vorgang zusätzlich eine zweite
  Person braucht — siehe [Risikobasierte Freigabe](approval-001-freigabe-20261013.md).

## Folgen für den Betrieb

- **Wer DocFlow heute ohne eine dieser Rollen benutzt, bekommt ab jetzt 403** — auch in der
  Rechnungsmaske des Verkaufs (`sales/invoice-editor`). Die Rollen müssen in der Anmeldung vergeben
  sein; die Testkennung für die Sichtprüfung braucht sie ebenfalls.

## Grenzen

- **Kassenbelege** (`pos_receipt`, `pos_storno`, `pos_retoure`) prüft diese Stelle nicht; sie laufen
  über DocFlow wie bisher.
- **Kein Recht am einzelnen Beleg** (eigene Kunden, eigene Niederlassung) — nur je Belegart.
- Die Wege daneben (`/sales/…`, `/einkauf/…`, `/finance/…`) haben ihre eigenen Prüfungen und sind
  nicht angefasst.
- Nicht im Browser geprüft.

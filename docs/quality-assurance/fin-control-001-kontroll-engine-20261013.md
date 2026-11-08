# FIN-CONTROL-001: Kontroll-Engine und Prüfkorb des Controllers

Stand: 2026-10-13 · Slice `FIN-CONTROL-001` · Entscheidung des Auftraggebers vom 13.10.2026 (abends) ·
**ersetzt die Freigabematrix aus** [APPROVAL-001](approval-001-freigabe-20261013.md); Engine, gemeinsamer
Freigabeweg und Protokoll von dort bleiben

## Entscheidung

„Der Finanzbuchhalter hat den Hut auf. Der Controller überwacht die Ausnahmen – nicht jede einzelne
Routinebuchung." Nicht der Betrag allein entscheidet, sondern das Risiko, die Abweichung vom
Standardprozess und die finanzielle Auswirkung. Eine moderne Finanzbuchhaltung weist auf
Unregelmäßigkeiten hin und nimmt dem Controlling einen Hauptteil der Arbeit ab.

- **Warnung:** Der Vorgang bleibt zulässig und wird ausgeführt; der Befund geht in den Prüfkorb.
- **Kritischer Befund:** Der Vorgang ist gesperrt, bis der Controller oder eine andere unabhängige
  berechtigte Person freigibt.

## Was jetzt gilt

| Vorgang | Regel |
|---|---|
| Rechnung, Gutschrift mit Bezugsrechnung, manuelle Hauptbuchbuchung, wiederkehrende Finanzrechnung, Abrechnungskorrektur der Ernte | Rollenrecht, ohne zweite Person |
| Regelkonformer Storno (Beleg, Hauptbuchbuchung, alter Rechnungsweg) | Buchhaltung bzw. Leitung des Bereichs, mit Begründung, ohne zweite Person |
| Zahlungslauf ausführen | weiter nur mit unabhängiger Freigabe (bestehendes Vier-Augen-Verfahren, an Empfänger, IBAN und Beträge gebunden) |

### Warnungen (Prüfkorb)

| Befund | Auslöser (Startwert) |
|---|---|
| `betrag` | Ausgangsrechnung über 10.000 €, Eingangsrechnung über 5.000 €, Gutschrift über 1.000 €, manuelle Hauptbuchbuchung ab 10.000 € |
| `stueckelung` | mehrere Belege desselben Vorgangs überschreiten zusammen die Schwelle |
| `abweichung_ueblich` | Finanzrechnung weicht um mehr als 10 % vom üblichen Betrag des Lieferanten ab |
| `agrar_korrektur` | Abrechnungskorrektur ab 250 € |
| `storno_haeufung` | dritter Storno desselben Partners in 90 Tagen |
| `massenimport` | jeder Massenimport von Buchungen |

### Kritische Befunde (Sperre bis zur unabhängigen Freigabe, unabhängig vom Betrag)

| Befund | Auslöser |
|---|---|
| `dublette` | andere aktive Eingangsrechnung desselben Lieferanten mit derselben Fremdnummer oder demselben Betrag am selben Tag; dieselbe Importdatei für dieselbe Periode |
| `abweichung_vorgaenger` | Eingangsrechnung aus Bestellung oder Wareneingang mit anderem Preis, höherer Menge oder zusätzlicher Position |
| `geschuetztes_konto` | manuelle Buchung auf Forderungen, Verbindlichkeiten oder ein Steuerkonto (Liste je Mandant einstellbar: `kontrolle.geschuetzte_konten`) |
| `gutschrift_ohne_bezug` | Gutschrift über der Schwelle ohne Bezugsrechnung |

Unverändert gesperrt (ohne Freigabemöglichkeit): Die Buchung eines DocFlow-Belegs wird nicht über das
Hauptbuch oder den alten Rechnungsweg storniert — eine festgeschriebene Buchung wird nur über ihren
Beleg berichtigt.

### Prüfkorb

- **Speicher:** `domain_docflow.control_findings` (Migration `control_findings_20261013`, ein Head); ein
  Befund je Vorgang, Aktion und Art; nicht löschbar.
- **Wege:** `GET /api/v1/kontrolle/befunde?status=offen|geprueft`,
  `POST /api/v1/kontrolle/befunde/{id}/pruefung` mit Bewertung.
- **Wer prüft:** `controller`, `CONTROLLING`, `FINANCE_ADMIN`, `admin` — nie, wer gebucht hat, und kein
  Dienstkonto. Die Buchhaltung sieht den Korb.
- **Wer kritische Befunde freigibt:** dieselben Rollen wie bisher, dazu der Controller.
- Auch ein freigegebener kritischer Befund steht im Korb, mit seiner Freigabe.

### Schwellen

Je Mandant einstellbar (`freigabe.grenze.ausgangsrechnung`, `.eingangsrechnung`, `.gutschrift`,
`.hauptbuch`); der Mandant kann sie jetzt auch höher setzen. Die Werte sind Startwerte für Tests,
**keine gesetzlichen Schwellen und keine endgültige Risikopolitik**.

## Nachweis

- `tests/test_freigabe.py` (29): Regel an den Schwellen; Routine ohne zweite Person; über der Schwelle
  gebucht und im Prüfkorb, Prüfung nur durch eine andere Person mit Kontrollrolle und mit Bewertung;
  Mandantenschwelle; Gutschrift mit und ohne Bezug; gehäufte Stornos; Dublette mit Fremdnummer und mit
  gleicher Summe am selben Tag (Ausgangsrechnungen gleicher Summe sind keine); Abweichung von der
  Bestellung; Freigabe verliert nach Änderung, Ablauf und Ablehnung ihre Wirkung; Sperre gilt auch im
  Dienst selbst; fremder Mandant.
- `tests/test_freigabe_zweitwege.py` (9), `tests/test_freigabe_hauptbuch_zahlung.py` (10),
  `tests/test_freigabe_import_einkaufsmemo.py` (11): dieselbe Regel an Finanzrechnung, Prozesskern,
  Verkaufsgutschrift, altem Rechnungsweg, Hauptbuch, Zahlungslauf, Massenimport, Lieferantengutschrift.
- Belegweg, Rechte, Maskenaktionen, Definition, MCP-Werkzeuge an die Regel angepasst.

## Auslegungen (meine, nicht entschieden)

- **Ausgangsrechnung, Eingangsrechnung und Gutschrift über der Schwelle sind Warnungen, keine
  Sperren.** Ihre Entscheidung nennt sie nicht einzeln; sie folgt aus „nicht der Betrag allein".
- **Gutschrift ohne Bezugsrechnung über der Schwelle sperrt** — als Forderungsverzicht ohne Beleg.
- **Dublette nur bei Eingangsrechnungen und Importen.** Zwei Ausgangsrechnungen gleicher Summe an
  denselben Kunden am selben Tag sind im Landhandel Alltag.
- **Geschützte Konten** sind ohne Einstellung des Mandanten: 1400, das Kreditorenkonto des
  Kontenrahmens und die Steuerkonten der Steuerschlüssel. „Ungewöhnliche Kontenkombination" ist damit
  nur in diesem Sinn umgesetzt.
- **Der Zahlungslauf behält seine Freigabe**, weil die Entscheidung Zahlungen nicht zur Routine zählt.
- **Die Agrar-Korrektur** warnt ab 250 €; die Schwelle „2 %" ist nicht umgesetzt, weil dem Beleg der
  Abrechnungsbetrag fehlt, auf den sich das Prozent bezöge.

## Nicht umgesetzt

- **Kasse und Rücklastschriften** (laut Entscheidung zuerst Untersuchung durch Codex).
- **Bankverbindungsänderung mit anschließender Zahlung, Wertberichtigungen, Forderungsverzicht** als
  eigene Vorgänge.
- **Der alte Rechnungsweg** (`/finance/invoices`) schreibt keine Befunde in den Prüfkorb; er hat keinen
  gespeicherten Vorgang.
- **Die Belegmaske zeigt Warnungen nicht vorab.** Der Belegvertrag nennt nur gesperrte Aktionen mit
  Grund; ein Hinweis „geht in den Prüfkorb" fehlt (die Vertragsdatei ist bei Codex in Arbeit).
- **Keine Maske für den Prüfkorb**, keine Benachrichtigung des Controllers.
- Nicht im Browser geprüft.

**Produktivfreigabe:** unverändert gesperrt, bis die fachliche Abnahme der Schwellen und die
Integrationstests über alle Zugänge vorliegen.

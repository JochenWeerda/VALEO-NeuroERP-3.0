# APPROVAL-001: Risikobasierte Freigabe für Buchen und Stornieren

Stand: 2026-10-13 · Slice `APPROVAL-001-DOCFLOW` · Entscheidung des Auftraggebers vom 13.10.2026 ·
Folge aus [Rechte an Belegen](beleg-rechte-20261013.md) · gebunden an
[MCP-WRITE](../architecture/mcp-write-standard.md) (Regel 008)

## Entscheidung

Buchen und Stornieren unterliegen einer risikobasierten Freigabe — kein generelles Vier-Augen-Prinzip,
sondern Betragsgrenzen, Risikoklassen und Funktionstrennung. Jeder Zugang geht durch dieselbe Stelle.
Die Beträge sind Startwerte der ERP-Governance, **keine gesetzlichen Schwellen**, und vor produktiver
Anwendung fachlich abzunehmen.

## Umgesetzt (DocFlow-Belege)

| Vorgang | Freigabe |
|---|---|
| Ausgangsrechnung buchen bis 10.000 € brutto | Rollenrecht |
| Ausgangsrechnung buchen darüber | zweite Person (R3) |
| Eingangsrechnung buchen bis 5.000 € brutto, Rechnungsabgleich in Ordnung | Rollenrecht |
| Eingangsrechnung darüber, mit Preis-/Mengenabweichung oder ohne Bestellung/Wareneingang | zweite Person (R3) |
| Gutschrift buchen bis 1.000 € brutto | zweite Person (R3) |
| Gutschrift darüber | zweite Person mit erhöhter Berechtigung (R4) |
| Gebuchten Beleg stornieren | zweite Person mit erhöhter Berechtigung (R4), gleich welcher Betrag |
| Entwurf, Lieferschein, Folgebeleg, Freigeben (Belegnummer) | Rollenrecht |

- **Regel:** `app/core/freigabe.py`. **Engine:** `app/services/docflow_freigabe.py`. **Speicher:**
  `domain_docflow.approvals` (Migration `approval_engine_20261013`, ein Head).
- **In jedem Zugang:** Die Prüfung sitzt im Kommando (`DocflowService.post_document`,
  `reverse_document`), nicht im Endpunkt. Ein Skript oder ein künftiges MCP-Werkzeug, das den Dienst
  direkt ruft, kommt nicht daran vorbei.
- **Bindung:** Eine Freigabe gilt für Mandant, Beleg, Belegversion, Aktion und Betrag und läuft nach
  24 Stunden ab. Ihr Abdruck umfasst Belegart, Partner, Summen und jede Position; ändert sich davon
  etwas, ist sie ungültig. Sie wird beim Ausführen verbraucht — in derselben Transaktion wie die Buchung.
- **Funktionstrennung:** Wer den Beleg angelegt oder die Freigabe angefragt hat, entscheidet nicht — auch
  nicht als Administrator. Ein Dienstkonto entscheidet nie. Zusätzlich verbietet eine Bedingung der
  Tabelle, dass Antragsteller und Entscheider dieselbe Kennung sind.
- **Wer freigibt:** R3 — Leitung des Bereichs, Buchhaltung, `manager`, `admin`; R4 — Leitung des
  Bereichs, `FINANCE_ADMIN`, `admin` (`app/auth/beleg_roles.py`, Rechte `freigeben`,
  `freigeben_erhoeht`).
- **Stückelung:** Mehrere Belege derselben Art aus demselben Vorgänger zählen zusammen; ohne Vorgänger
  die desselben Partners am selben Tag.
- **Grenzen je Mandant:** `domain_shared.system_properties`, Schlüssel `freigabe.grenze.ausgangsrechnung`,
  `.eingangsrechnung`, `.gutschrift`. Ein Mandant setzt die Grenze nur enger; ein unlesbarer Wert lockert
  nichts.
- **Protokoll:** Jede Anfrage, Entscheidung, Ablehnung und jeder Verbrauch steht mit Kennung im
  unveränderlichen Kommandoprotokoll des Belegs. Freigaben werden nicht gelöscht.
- **Wege:** `GET/POST /api/v1/docflow/{id}/approvals`, `POST …/approvals/{freigabe}/decision`.
- **Belegvertrag:** `freigaben[]` am Beleg; `buchen`/`stornieren` sind gesperrt mit Grund, solange die
  zweite Person fehlt, dazu die Aktionen „Freigabe anfragen" bzw. „Freigabe erteilen" (letztere gesperrt
  für Antragsteller und Ersteller).
- **Verzeichnis der Belegkommandos:** Die Klasse dort ist die höchste, die ein Kommando erreichen kann;
  Freigeben (Belegnummer vergeben) ist jetzt R2.

## Nachweis

- `tests/test_freigabe.py`: 27 bestanden gegen `valeo_probe` — Matrix an den Grenzen (10.000,00 /
  10.000,01 usw.); Buchen über der Grenze scheitert ohne Freigabe und ändert nichts; Antragstellerin,
  dieselbe Person als Administratorin, Dienstkonto und Rolle ohne Recht werden abgewiesen; Ersteller gibt
  nicht frei; nach Änderung des Belegs, nach Ablauf und nach Ablehnung gilt die Freigabe nicht;
  Gutschrift klein R3, groß R4 nur mit erhöhter Berechtigung; Stückelung zweier Gutschriften; Storno
  R4; Eingangsrechnung frei erfasst und mit Preisabweichung; Mandantengrenze nur enger; **der Dienst
  selbst verweigert ohne Freigabe**; fremder Mandant.
- Nachbarn (DocFlow, Belegweg, Rechte, MCP, Referenzbelege, Tabellenkatalog): 380 und 37 bestanden.
- Die Referenzbelege entstehen weiter über DocFlow und gehen dabei durch die Engine.

## Auslegungen (meine, nicht entschieden)

- **Der Kontrollpunkt ist das Buchen.** „Ausgangsrechnung über 10.000 €: zweite Person" ist an der
  Buchung umgesetzt, nicht am Freigeben (Vergabe der Belegnummer).
- **Rechnungsabgleich** der Eingangsrechnung: Jede Position stammt aus einer Position von Bestellung
  oder Wareneingang, mit deren Preis (ohne Toleranz) und höchstens deren Menge. Eine frei erfasste
  Eingangsrechnung hat keinen Abgleich und braucht deshalb die zweite Person.
- **Stückelung** wie oben; eine Frist über mehrere Tage gibt es nicht.
- **Der Mandant setzt Grenzen nur enger**, bis die Werte fachlich abgenommen sind.
- **Dienstkonto** erkennt die Engine am Anmeldenamen `service-account-…` bzw. an einem Token mit
  `client_id` ohne Benutzernamen. Die Abgrenzung von Agentenidentitäten gehört in die Identität.
- **Ausführen darf auch die Person, die freigegeben hat** — beteiligt sind dann trotzdem zwei.

## Nicht umgesetzt

- **Manuelle Hauptbuchbuchung (R3) und Zahlungsfreigabe (R4):** Die Engine ist allgemein gehalten
  (`subject_type`), aber nur DocFlow ruft sie. Journal und Zahlungslauf sind nicht angeschlossen.
- **Die Wege neben DocFlow** (`/sales/…`, `/finance/ap/…`, `/sales/credit-notes`) buchen weiter ohne
  diese Freigabe.
- **Kassenbelege** sind ausgenommen wie bei den Rechten; vor einer Freischaltung schreibender
  MCP-Aktionen zu schließen (Entscheidung vom 13.10.2026).
- **Storno einer gebuchten Gutschrift** gibt es weiterhin nicht (Gegenbuchung fehlt).
- **Storno einer nicht gebuchten Rechnung** lässt DocFlow nicht zu; der Entwurf wird gelöscht.
- Keine Benachrichtigung der zweiten Person, keine Arbeitsliste offener Freigaben.
- Nicht im Browser geprüft; die Belegmaske zeigt die Freigabe noch nicht.

**Produktivfreigabe:** Buchen, Stornieren und schreibende MCP-Aktionen bleiben gesperrt, bis die
Integrationstests über alle Zugänge und die fachliche Abnahme der Schwellen vorliegen.

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

## Nachtrag: Die Buchungswege neben DocFlow (APPROVAL-001-ZWEITWEGE)

Drei Wege buchten, ohne dass der Beleg in DocFlow steht — und damit an der Freigabe vorbei. Jetzt gehen
sie durch dieselbe Engine.

- **Die Engine ist allgemein** (`app/services/freigabe_engine.py`): Ein Bereich schließt sich an, indem
  er liefert, was sein Vorgang ist (Belegart, Betrag, Stand, Ersteller, freigaberelevanter Inhalt).
  Regel, Funktionstrennung, Bindung an den Inhalt, Ablauf und Verbrauch sind für alle gleich.
  DocFlow ist einer dieser Bereiche (`docflow_freigabe.py`).
- **Ein gemeinsamer Freigabeweg:** `GET/POST /api/v1/approvals/{bereich}/{id}` und
  `POST …/{freigabe}/decision` für `docflow_document`, `finance_ap_invoice`, `sales_credit_note`,
  `finance_sales_invoice`.
- **Ein gemeinsames Protokoll:** `domain_docflow.approval_log` (Migration `approval_log_20261013`, ein
  Head), unveränderlich. DocFlow-Belege tragen den Eintrag zusätzlich in ihrem Kommandoprotokoll.

| Weg | Jetzt |
|---|---|
| Eingangsrechnung der Finanzbuchhaltung, `POST /finance/ap/invoices/{id}/post` | Bucht erst mit zentraler Freigabe. Eine Finanzrechnung hat weder Bestellung noch Wareneingang, also keinen Rechnungsabgleich — sie braucht immer die zweite Person. Wer angelegt hat, steht jetzt am Beleg (`createdBy`) und gibt nicht frei. |
| Derselbe Beleg über den Prozesskern (`PostAPInvoice`) | Bucht ohne gültige Freigabe nicht. |
| Verkaufsgutschrift, `POST /sales/credit-notes/{id}/post` und `…/actions/buchen` | Jede Gutschrift braucht die zweite Person, über 1.000 € die erhöhte Berechtigung; Gutschriften zur selben Rechnung zählen zusammen. Die Prüfung sitzt in der Buchung selbst und gilt damit auch für den Weg über den Buchungsvorschlag eines Agenten. |
| Alter Rechnungsweg, `POST/PUT /finance/invoices` | Legt an und bucht in einem Schritt und kann keine Freigabe einholen: Er bucht nur bis 10.000 €; darüber 409 mit Verweis auf den Belegweg, und es entsteht kein Beleg. |
| Storno über den alten Rechnungsweg, `POST /finance/invoices/{nr}/storno` | Braucht die Freigabe einer zweiten Person mit erhöhter Berechtigung. **Eine DocFlow-Rechnung storniert er nicht mehr.** |

### Befunde dabei

- **Umgehungsweg geschlossen:** Der Storno des alten Rechnungswegs fand die Buchung über die
  Rechnungsnummer — auch die einer DocFlow-Rechnung — und nahm sie ohne Beleg, Statushistorie und
  Freigabe zurück. Der DocFlow-Beleg wäre „gebucht" geblieben.
- **Behoben:** Derselbe Storno antwortete immer 500, obwohl er storniert hatte (dem Antwortmodell fehlte
  ein Pflichtfeld).
- **Behoben:** Der alte Rechnungsweg legt für sein Archivstück einen DocFlow-Kopf an
  (`source_system = gobd_artifact`). Belegweg und `beleg.suchen` hielten ihn für einen Beleg; jetzt nicht
  mehr.
- **Nicht behoben:** Der Dokumentspeicher des alten Rechnungswegs kennt keinen Mandanten —
  `GET /finance/invoices/{nr}` liefert die Rechnung jedes Mandanten. Der Storno-Vorgang der Engine
  stützt sich deshalb auf die Buchung, nicht auf diesen Speicher.
- **Nicht behoben:** Der Buchende der Eingangsrechnung (`posted_by`) kommt weiter aus der Anfrage, nicht
  aus der Anmeldung; im Freigabeprotokoll steht die Anmeldung.

### Nachweis

- `tests/test_freigabe_zweitwege.py`: 10 bestanden gegen `valeo_probe` — Finanzrechnung nur mit zweiter
  Person, Antragstellerin und Erstellerin geben nicht frei, Prozesskern bucht nicht ohne Freigabe;
  Gutschrift auf beiden Buchungswegen, R4 über 1.000 € und bei Stückelung; alter Rechnungsweg nur bis
  zur Grenze, darüber entsteht nichts; Storno mit erhöhter Freigabe; **der alte Weg storniert keine
  DocFlow-Rechnung**; gemeinsamer Weg je Bereich, Lesen ist nicht Buchen, fremder Mandant.
- Vorhandene Tests der drei Wege holen die Freigabe über die Engine (`tests/freigabehilfe.py`). Ein
  Test änderte das Aufwandskonto nach der Freigabe und scheiterte daran zu Recht.
- Gesamtlauf über 37 Testdateien (Finanzwege, DocFlow, Belegweg, Rechte, MCP): 2.104 bestanden, 31
  fehlgeschlagen. Dieselben drei Testdateien schlagen ohne meine Änderung fehl (33 im Vergleichslauf
  auf `main`: `test_eingangsrechnung_mandant`, `test_gap_fixes_batch3`, `test_sales_cn_inv_001`).

### Auslegungen (meine, nicht entschieden)

- **Jede Finanzrechnung braucht die zweite Person**, auch unter 5.000 €: Die Matrix verlangt für das
  Rollenrecht einen erfolgreichen Rechnungsabgleich, den es ohne Bestellung nicht gibt. Der
  Freigabeablauf des AP-Moduls (`ap_approval_workflow`) bleibt daneben bestehen — das sind vorerst
  zwei Schritte. Für wiederkehrende Finanzrechnungen (Miete, Versicherung) wäre eine vorab genehmigte
  Richtlinie der passende Weg; die gibt es noch nicht.
- **Der alte Rechnungsweg bekommt keinen Freigabeablauf**, weil er ohnehin abgelöst wird.

### Weiter offen

- Manuelle Hauptbuchbuchung (R3) und Zahlungsfreigabe (R4) rufen die Engine nicht auf.
- Der zweite Freigabeablauf der Eingangsrechnung (`ap_approval_workflow`) ist nicht in die Engine
  überführt.
- Die Einkaufsgutschriften und Belastungen unter `/einkauf/credit-memos`, `/einkauf/debit-memos` und
  die Kasse habe ich nicht untersucht.

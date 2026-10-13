# APPROVAL-001: Risikobasierte Freigabe für Buchen und Stornieren

Stand: 2026-10-13 · Slice `APPROVAL-001-DOCFLOW` · Entscheidung des Auftraggebers vom 13.10.2026 ·
Folge aus [Rechte an Belegen](beleg-rechte-20261013.md) · gebunden an
[MCP-WRITE](../architecture/mcp-write-standard.md) (Regel 008)

> **Überholt in der Regel, gültig in der Technik.** Die Freigabematrix dieses Dokuments ist seit dem Abend
> des 13.10.2026 durch [FIN-CONTROL-001](fin-control-001-kontroll-engine-20261013.md) ersetzt: Routine
> bucht die Buchhaltung selbst, nur kritische Befunde sperren. Engine, gemeinsamer Freigabeweg, Protokoll,
> Funktionstrennung und die geschlossenen Umgehungswege gelten weiter.

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

## Nachtrag: Manuelle Hauptbuchbuchung und Zahlungslauf (APPROVAL-001-HAUPTBUCH-ZAHLUNG)

| Vorgang | Jetzt |
|---|---|
| Manuelle Hauptbuchbuchung buchen, `POST /journal-entries/{id}/post` | braucht die Freigabe einer zweiten Person (R3) |
| Gebuchte Hauptbuchbuchung stornieren, `POST …/{id}/reverse` | braucht die Freigabe einer zweiten Person mit erhöhter Berechtigung (R4) |
| Buchung eines DocFlow-Belegs über das Hauptbuch stornieren | geht nicht mehr: 409, storniert wird über den Beleg |
| Zahlungslauf freigeben, `POST /finance/payment-runs/{id}/approve` | die Freigabe ist jetzt eine Freigabe der zentralen Engine (R4) |
| Zahlungslauf ausführen, `POST /finance/payment-runs/{id}/execute` | nur mit gültiger Engine-Freigabe für genau diesen Inhalt |

- **Wer entscheidet:** Hauptbuch R3 — Buchhaltung und Finanzleitung (`FINANCE_BEARBEITEN`, `FINANCE_ADMIN`,
  `manager`, `admin`); R4 und Zahlung — nur Finanzleitung (`FINANCE_ADMIN`, `admin`). Lesen und anfragen
  nur Finanzrollen. Jeder Bereich der Engine bestimmt seine Rollen selbst (`leserollen`,
  `anfragerollen`, `freigaberollen`); Belege benutzen weiter `app/auth/beleg_roles.py`.
- **Zahlungslauf:** Das bisherige Vier-Augen-Verfahren (`pruefe_freigabe`) bleibt und läuft jetzt in die
  Engine: Angefragt hat, wer den Lauf angelegt hat; der Aufruf von `/approve` entscheidet. Die Freigabe
  ist an Empfänger, IBAN und Beträge gebunden — ändert sich nach der Freigabe eine Zahlung, wird nicht
  ausgeführt. Ein Lauf, der nur den Status „freigegeben" trägt, wird nicht ausgeführt.
- **Hauptbuch:** Der Abdruck umfasst Nummer, Bezug, Daten und jede Zeile (Konto, Soll, Haben).

### Befund dabei

- **Umgehungsweg geschlossen:** `POST /journal-entries/{id}/reverse` stornierte jede Buchung
  des Mandanten, auch die einer DocFlow-Rechnung — der Beleg blieb „gebucht". Jetzt 409 mit Verweis auf
  den Belegweg.
- **Vorbestehend rot, nicht von mir:** Die Tests der Zahlungsläufe schlagen auf `main` fehl
  (`test_finance_payment_runs_api`, `test_payment_execution_atomicity`, `test_zahlungslauf_mandant`:
  zusammen 53, Ursache `401 Missing bearer token` — die Tests kennen die Anmeldegrenze noch nicht).
  Die Ausführung eines Zahlungslaufs mit SEPA und Ausgleich ist deshalb **nicht** durch einen
  bestehenden Test abgedeckt; meine Tests prüfen die Freigabe davor.

### Nachweis

`tests/test_freigabe_hauptbuch_zahlung.py`, 8 bestanden gegen `valeo_probe`: Matrix; manuelle Buchung
nur mit zweiter Person (Verkauf darf weder anfragen noch entscheiden, Antragstellerin nicht
entscheiden); Storno nur mit Finanzleitung; geänderte Buchung verliert ihre Freigabe; Buchung eines
DocFlow-Belegs nicht über das Hauptbuch stornierbar; Zahlungsfreigabe als Engine-Freigabe mit
Antragsteller und Entscheider, ungültig nach geänderter IBAN; Lauf mit bloßem Status wird nicht
ausgeführt; Rollen je Bereich. Gesamtlauf über 17 Testdateien: 950 bestanden.

### Auslegungen (meine, nicht entschieden)

- **Jede manuelle Hauptbuchbuchung braucht die zweite Person** — die Ausnahme der Matrix („sofern keine
  genehmigte automatisierte Buchungsregel greift") gibt es nicht, weil es keine solchen Regeln gibt.
  Das ändert die Entscheidung vom 11.10.2026, nach der die Buchhaltung ihre Buchungen allein bucht und
  storniert.
- **Zahlungsberechtigung = Finanzleitung.** Eine eigene, delegierbare Zahlungsrolle gibt es nicht.

### Weiter offen

- **Wer eine Hauptbuchbuchung angelegt hat**, steht nur im FiBu-Audit; fehlt der Eintrag, greift die
  Funktionstrennung nur gegenüber dem Antragsteller.
- **Massenimport** (`POST /finance/bulk-journal-import/csv`) bucht ohne die Engine.
- **Zahlungsläufe, die vor dieser Änderung freigegeben wurden**, tragen keine Engine-Freigabe und
  werden nicht ausgeführt; sie müssen neu angelegt werden.
- Rücklastschrift (`return-payment`) und SEPA-Datei habe ich nicht angefasst.

## Nachtrag: Massenimport und Lieferantengutschriften/-belastungen (APPROVAL-001-IMPORT-EINKAUFSMEMO)

| Vorgang | Jetzt |
|---|---|
| Massenimport von Buchungen, `POST /finance/bulk-journal-import/csv` | bucht nur mit Freigabe einer zweiten Person aus der Finanzleitung für **genau diese Datei** |
| Lieferantengutschrift und -belastung buchen, `POST /einkauf/credit-memos/{id}/buchung`, `…/debit-memos/…` | braucht die zweite Person, über 1.000 € die erhöhte Berechtigung |
| Dieselben verrechnen, `…/settle` | braucht dieselbe Freigabe; sie gilt für den Geschäftsvorfall (einmal erteilt, deckt sie Buchen und Verrechnen bei unverändertem Inhalt) |

- **Massenimport:** Der Vorgang ist der Abdruck von Mandant, Periode und Datei. Der Probelauf
  (`dry_run=true`) nennt ihn als `approval_subject`; angefragt und entschieden wird über
  `/api/v1/approvals/journal_import/{abdruck}`. Eine andere Datei ist ein anderer Vorgang; dieselbe
  Datei ein zweites Mal braucht eine neue Freigabe.
- **Gutschrift/Belastung:** Mandant und Ersteller kommen jetzt aus der Anmeldung und stehen am Beleg.
  Anlegen verlangt das Recht des Einkaufs, Buchen und Verrechnen das Buchungsrecht.

### Befunde dabei

- **Behoben — fremder Mandant beim Massenimport:** Der Mandant kam aus der Anfrage (Vorgabe „system").
  Wer importieren durfte, konnte in jeden Mandanten buchen. Jetzt gilt der Mandant der Anmeldung; die
  Angabe darf ihn nur bestätigen (sonst 403).
- **Behoben für die Schreibwege — kein Mandant, kein Recht:** Die Gutschriften und Belastungen des
  Einkaufs hatten weder Mandant noch Rollenprüfung; der Ersteller kam aus dem Kopf `X-User-ID`, den
  jeder setzen kann. Anlegen, Buchen und Verrechnen sind jetzt an Mandant, Recht und Freigabe gebunden.
- **Nicht behoben — Lesen und die modul-eigene Freigabe:** `GET /einkauf/credit-memos`, `…/{id}` und
  die Wege `…/freigabe` sind weiter ohne Mandant und ohne Recht.
- **Nicht behoben — „gebucht" ohne Buchung:** `…/buchung` schreibt einen Buchungsvermerk in den
  Dokumentspeicher mit einer ausgedachten Journalnummer; im Hauptbuch entsteht nichts. Die Verrechnung
  mindert dagegen wirklich offene Posten. Führend für Einkaufsgutschriften ist DocFlow
  (`purchase_credit_memo`), das über Finance bucht.
- **Folge:** Belege dieses Weges, die vor dem 13.10.2026 angelegt wurden, tragen keinen Mandanten und
  werden nicht mehr gebucht oder verrechnet.

### Nachweis

`tests/test_freigabe_import_einkaufsmemo.py`, 9 bestanden gegen `valeo_probe`: Import nur mit Freigabe
für genau diese Datei (andere Datei abgewiesen, zweiter Lauf braucht neue Freigabe, nur die
Finanzleitung fragt an und entscheidet); **Import nur in den Mandanten der Anmeldung**; Gutschrift und
Belastung nur mit zweiter Person, Mandant und Ersteller aus der Anmeldung; Verrechnen nur mit Recht
und Freigabe; über 1.000 € erhöhte Berechtigung; Beleg eines anderen Mandanten 404; ohne Recht kein
Anlegen. Angepasst: `test_process_kernel_wave100_settlement_completion` (nachgestellte Datenbank,
Freigabe dort ausgeblendet), `test_process_kernel_wave31_dq_finance_import_paths`.

### Weiter offen

- Die Abrechnungskorrektur des Agrarbereichs erzeugt Gutschriften und Belastungen über diesen Weg
  (`settlementId`); sie braucht jetzt je Beleg die zweite Person. Ob das im Ernteablauf trägt, ist
  fachlich zu prüfen.
- Kasse und Rücklastschrift habe ich nicht untersucht.

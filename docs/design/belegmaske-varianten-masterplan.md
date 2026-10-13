# Eine Belegmaske, viele Varianten — Bestand und Masterplan (BELEG)

Stand: 2026-10-13 · Auslöser: Vorgaben des Auftraggebers vom 13.10.2026 (eine Masken-Engine, mehrere
Belegdefinitionen, getrennte fachliche Prozesse; fünf Regeln zur belegführenden Domäne) ·
Verwandt: `flow-spine-entlastung-masterplan.md` (belegzentrierter Alltag, Positionsbezug bei
Split/Merge), `flow-spine-ebene1-kriterienkatalog.md` (wann eine Belegmaske alltagstauglich ist),
`docs/MASKEN.md` (Gewohnheitsprinzip der Belegkette).

Dieser Plan ist ein Vorschlag zur Entscheidung. Umgesetzt ist davon nichts außer den unter
„Schon vorhanden" genannten Bausteinen.

## A. Die Vorgaben, gegen die geplant wird

1. **Eine Masken-Engine, mehrere Belegdefinitionen.** Für die Schritte einer Belegfolge gibt es keine
   eigene Maske je Schritt, sondern eine Variante der Belegmaske. Die Variante steuert Beschriftung,
   Feldsichtbarkeit, Pflichtfelder, Berechnungen, Aktionen, Berechtigungen, Statusübergänge und
   fachliche Wirkung.
2. **Gemeinsame Maske heißt nicht gemeinsamer Belegdatensatz.** Auftrag, Lieferschein und Rechnung
   sind eigenständige Belege. Der Folgebeleg wird aus dem Vorgänger erzeugt und dauerhaft referenziert
   (ein Auftrag → drei Teillieferscheine → zwei Rechnungen). Ein Variantenwechsel überschreibt nichts.
3. **Berechtigung wirkt an der API.** Ein Lieferschein blendet Preise nicht nur aus; wer keine
   Preisberechtigung hat, bekommt sie nicht geliefert.
4. **Belegführende Domäne.** Jeder Beleg hat genau einen fachlichen Besitzer (Einkauf, Verkauf,
   Lager/Logistik). Keine zweite Rechnungsverwaltung in der Finanzbuchhaltung; Ausnahme: reine
   Finanzrechnungen ohne Waren- oder Leistungsbezug.
5. **Finance ist Buchungsautorität.** Kontenzuordnung, Umsatzsteuer, Nebenbücher und Hauptbuch werden
   zentral erzeugt. Ein freigegebener Beleg wird über ein idempotentes Ereignis gebucht; Fehler führen
   zu einem prüfbaren Buchungsstatus.
6. **GoBD.** Festgeschriebene Belege und Buchungen werden nicht überschrieben oder gelöscht, sondern
   korrigiert, storniert oder neu gebucht.
7. **Fachliche Services und Belegidentitäten bleiben getrennt**; gemeinsam sind Belegnummern,
   Versionen, Anhänge, Freigaben und Audit-Trail als Standard.

## B. Bestand — am Code und an beiden Datenbanken geprüft

### B1. Ein Speicher je Belegschritt, kein gemeinsamer Vertrag

| Beleg | Lebende Maske (Navigation) | Speicher | Zeilen |
|---|---|---|---:|
| Verkaufsangebot | `sales/angebot-erstellen` | `/sales/offers` | 1.284 |
| Verkaufsauftrag neu | `sales/order-editor` → `OrderEditorLegacyPage` | `/sales/orders` (`domain_crm.sales_orders`) | 2.412 |
| Verkaufsauftrag vorhanden | `sales/order-editor` → `sales-order-native` (SD `sales/sales-order`) | wie oben | 9 |
| Verkaufslieferschein | `verkauf/lieferschein-erfassung` | `/sales/delivery-notes` (`domain_sales.delivery_notes`) | 3.249 |
| Ausgangsrechnung neu | `sales/invoice-editor` (eigenes Gerüst `features/forms/FormBuilder`) | **DocFlow** `/docflow` | 481 |
| Ausgangsrechnung Anzeige | `verkauf/rechnung` (SD `sales/invoice`) | `/sales/invoices` | 16 |
| Gutschrift Verkauf | `sales/credit-note-editor` (SD `sales/gutschrift`) | `/sales/credit-notes` | 490 |
| Bestellung neu | `einkauf/bestellung-anlegen` (Route `einkauf/bestellungen/neu`) | `/purchase-orders` | 1.253 |
| Bestellung vorhanden | `einkauf/bestellung-stamm` (SD `einkauf/purchase-order`) | `/einkauf/bestellungen` | 877 |
| Wareneingang / Einkaufslieferschein | `einkauf/lieferschein-erfassung` | `/einkauf/lieferscheine` | 1.807 |
| Eingangsrechnung | `einkauf/rechnung-eingang-erfassung` | `einkauf_rechnungseingaenge` | 917 |
| Einkaufsgutschrift, Belastung | `einkauf/gutschriften-belastungen` (nicht in der Navigation) | `/einkauf/credit-memos`, `/einkauf/debit-memos` | 966 |
| Zweitwege Finance | `finance/invoice-form`, `finance/ap-invoice-form`, SD `finance/ap-invoice` | Dokumentspeicher `documents` | 518 / 343 |

Rund 14.600 Zeilen Maskencode für dieselbe Grundform. Drei Maskengerüste nebeneinander: Mask Builder
mit ScreenDefinition, Handbau und der schemagetriebene `FormBuilder` (nur von `sales/invoice-editor`
benutzt).

### B2. Befunde

| # | Befund | Beleg | Folge für den Plan |
|---|---|---|---|
| B-1 | Die vorhandenen Beleg-ScreenDefinitions haben schon dieselbe Form: Reiter `kopf`, `positionen`, `dokumente`, dazu je ein bis drei eigene | `sales/sales-order`, `sales/delivery-note`, `sales/invoice`, `einkauf/purchase-order`, `finance/ap-invoice` in `app/core/screen_definitions*.py` | Das gemeinsame Grundgerüst ist kein Neuentwurf, sondern das Herausziehen des Gleichen |
| B-2 | Jede dieser ScreenDefinitions ist eine eigene, ausgeschriebene Definition mit eigenen Feldnamen (`order_number`, `delivery_note_number`, `invoice_number`, `bestellnummer`, `beleg_nr`) | wie B-1 | Ohne gemeinsamen Belegvertrag gäbe es wieder eine Definition je Schritt |
| B-3 | Die ScreenDefinition kennt keine Variante | `components/mask-builder/schema.ts` — kein Variantenbegriff | Variante als Begriff der Engine einführen (BELEG-020) |
| B-4 | DocFlow führt Belege so, wie Vorgabe 2 es verlangt: ein Kopf und Positionen je Beleg, eigene Belegart, Umwandeln erzeugt einen neuen Beleg mit Verknüpfung je Position (`document_links`, Teilmengen), dazu Freigeben, Buchen, Stornieren, Idempotenz, Audit, Outbox | `app/services/docflow_service.py` (`convert`, `post_document`, `reverse_document`) | Der gemeinsame Belegprozess existiert für den Verkauf |
| B-5 | DocFlow ist aber nur für die Rechnung der führende Speicher. Auftrag und Lieferschein leben in eigenen Tabellen; DocFlow zieht sie bei Bedarf als Kopie nach (`_bootstrap_sales_order`, `_bootstrap_sales_delivery`) | `docflow_service.py:155`, `:230` | Zwei Wahrheiten für denselben Beleg sind möglich; die Kopie kommt ohne Steuerschlüssel an |
| B-6 | DocFlow kennt die Kette Angebot → Auftrag → Lieferschein → Rechnung; Einkaufsbelegarten gibt es nicht (der Kopf hat ein Lieferantenfeld) | `docflow_service.py:22` | Einkaufskette ist Neuland in DocFlow |
| B-7 | **Die Eingangsrechnung des Einkaufs läuft in keiner Datenbank:** frisch fehlt `einkauf_rechnungseingaenge` die Mandanten-Spalte, die jeder Zugriff benutzt; in der gewachsenen Datenbank gibt es die Tabellen nicht. Die Maske zeigt eine leere Liste, Speichern antwortet 503 | Schema beider Datenbanken; `mask_frontend_bridges._safe_rows` | Der „belegführende" Einkaufsweg existiert nur als Code (Entscheidung E1) |
| B-8 | „Verbuchen" der Eingangsrechnung im Einkauf setzt nur den Status | `app/einkauf/router.py`, `rechnungseingang_verbuchen` | Buchungsstatus ist dort nicht prüfbar (Vorgabe 5) |
| B-9 | Preise werden nirgends an der API nach Berechtigung gefiltert; die Lieferschein-Position trägt `mwst_prozent` mit Spaltenvorgabe 19 | `domain_sales.delivery_note_positions`, Lesewege der Belege | Vorgabe 3 ist offen (BELEG-012) |
| B-10 | DocFlow nimmt den Mandanten aus einem Parameter der Anfrage | `app/api/v1/endpoints/docflow.py` | Vor einem Ausbau zum allgemeinen Belegprozess zu schließen (Identität, Codex) |
| B-11 | Seit 13.10.2026 buchen Gutschrift, DocFlow-Rechnung und Finanz-Eingangsrechnung je Steuerschlüssel über eine Stelle | `app/finance/steuerschluessel.py`, `SalesPostingService`, `finance_eingangsrechnung_buchung.py` | Die Buchungsautorität (Vorgabe 5) steht für drei Belegarten |

**Nicht geprüft:** das Verhalten der Masken im Browser (lokal keine Anmeldung ohne Anbieterkonto);
die Speicher von Wiegeschein, Frachtbrief und Kontrakt im Einzelnen.

## C. Zielbild — drei Schichten, ein Vertrag

```
Belegmaske (eine Engine)        DocumentScreenDefinition + Variante je Belegart
        │  liest und schreibt nur über den
Belegvertrag (eine Form)        Kopf · Partner · Positionen · Summen · Kette · Dokumente · Historie · erlaubte Aktionen
        │  wird bedient von
Belegführende Domäne            Verkauf · Einkauf · Lager/Logistik — eigener Speicher, eigene Identität, eigener Prozess
        │  meldet „freigegeben" an
Finance (Buchungsautorität)     Steuerschlüssel → Konten → Journal, offener Posten; Buchungsstatus am Beleg
```

- **Belegvertrag** ist das, was die vorhandenen ScreenDefinitions schon gemeinsam haben, mit einheitlichen
  Namen: `beleg_nr`, `belegart`, `status`, `belegdatum`, `partner`, `positionen[]` (Artikel, Menge,
  Einheit, und je nach Variante Preis, Rabatt, Steuerschlüssel, Netto), `summen`, `kette[]`
  (Vorgänger und Nachfolger mit Belegart, Nummer, Menge), `dokumente[]`, `historie[]`, `aktionen[]`.
  Jede Domäne liefert ihn aus ihrem Speicher. Die Maske kennt keinen Speicher.
- **Variante** ist eine deklarative Angabe je Belegart: Titel und Feldbeschriftungen, sichtbare Reiter
  und Spalten, Pflichtfelder, welche Summen gezeigt werden, welche Aktionen es gibt, welches Recht sie
  brauchen, welche Belegart daraus entstehen kann. Sie enthält keine Fachlogik.
- **Berechtigung** wird im Belegvertrag durchgesetzt: Ohne Preisrecht liefert der Server Preis-, Rabatt-
  und Summenfelder nicht aus. Die Variante blendet zusätzlich aus, ist aber nicht die Sperre.
- **Buchungsstatus** ist ein Feld des Belegvertrags (`nicht gebucht`, `gebucht` mit Journalbezug,
  `nicht gebucht, bitte prüfen` mit Grund), gespeist von Finance.
- **Fachliche Sonderteile** (Wiegedaten, Qualitätsparameter, Fracht, Kontraktbezug) sind eigene
  Bausteine, die eine Variante einhängt — keine Sonderfälle im Grundgerüst.

## C1. Zielbild Fachaktionen: eine Fähigkeit, mehrere Zugänge (eingebracht 13.10.2026)

Vom Auftraggeber eingebracht, noch nicht als verbindlich bestätigt: Jede Belegfunktion wird einmal als
Fachaktion umgesetzt und ist über Maske, MCP-Werkzeug, Kommandozeile und REST erreichbar. Alle Zugänge
unterliegen derselben Validierung, Mandantentrennung, Rechteprüfung und demselben Nachweis. Ein
ausgeblendetes Feld ist keine Berechtigung. Kein neues Gerüst neben Mask Builder und ScreenDefinition;
vorhandene Fachaktionen bekommen maschinenlesbare Angaben, statt neu gebaut zu werden.

| Baustein des Zielbilds | Bestand | Lücke |
|---|---|---|
| Fachaktion einmal, serverseitig | DocFlow-Kommandos (anlegen, umwandeln, freigeben, buchen, stornieren) mit Idempotenz, Versionsprüfung, Pflichtprotokoll und Akteur aus der Anmeldung; Mask-Aktionen über `run_delegated_mask_action` | Kein gemeinsames Verzeichnis: DocFlow-Kommandos und Mask-Aktionen sind getrennt beschrieben |
| Aktionen an der Maske | `actions` der ScreenDefinition mit Kommando-Weg, Recht, Gefahrenstufe; Aktionskatalog und MCP-Aktionskarte werden erzeugt und in CI geprüft | 11 Masken der Handkopie tragen `stubReason` statt Kommando-Weg (Phase 0.9) |
| Agent versteht die Maske | `agentContract` je ScreenDefinition, Agenten-Handbuch | Kein Werkzeug „erlaubte Aktionen im jetzigen Zustand" — der Belegvertrag liefert sie künftig in `aktionen[]` (mit `kommando`, `freigabe_noetig`) |
| MCP-Werkzeuge für Belege | — | In `docs/schnittstellen/mcp-tools.md` gibt es kein Werkzeug für die DocFlow-Belegkommandos |
| Kommandozeile | — | Ein Kommandozeilenzugang für Fachaktionen ist nicht geprüft |
| Agentenidentität, Rechte | Identitätsarbeit bei Codex (Mandant und Akteur aus der Anmeldung) | Zuordnung der Rechte einer ScreenDefinition zu Rollen offen |
| CI-Prüfungen | Ratschen für Aktionskatalog, MCP-Aktionskarte, OpenAPI, Registry-Abbild, Belegvertrag | Kein Test „gleiche Aktion über jeden Zugang, gleiche Rechte" |

Folge für den Plan, ohne die Reihenfolge zu ändern: BELEG-011 liefert `aktionen[]` aus dem Zustand des
Belegs und dem Recht des Lesers; danach ein Verzeichnis der Belegkommandos (ein Eintrag je Kommando:
Name, Recht, Risiko, Freigabe, Idempotenz), aus dem MCP-Werkzeuge — zuerst nur lesende — und die
Aktionen der Belegmaske abgeleitet und in CI gegeneinander geprüft werden.

## D0. Entschieden am 13.10.2026 (Auftraggeber)

- **E1: DocFlow wird die führende Belegstruktur** (Belegidentität, Versionierung, Belegkette,
  Statushistorie, Dokumentenverknüpfung, Workflow). Fachlich verantwortet der Einkauf die
  Eingangsrechnung, buchhalterisch die Finanzbuchhaltung; DocFlow ist weder Hauptbuch noch
  Steuerengine. Der bisherige Einkaufsweg wird nicht repariert, sondern ist nur noch Migrationsquelle
  bzw. vorübergehender Kompatibilitätsadapter. Bedingung: Nachweis, dass DocFlow Mengen, Preise,
  Steuerpositionen, Teilrechnungen, Gutschriften, Belegreferenzen und revisionssichere Statuswechsel
  trägt; kein neuer paralleler Datenspeicher.
- **E4: Sichtprüfung ist Pflicht vor Welle 1** — über den echten OIDC-/PKCE-Ablauf mit dediziertem
  Testbenutzer (nicht mit einem persönlichen Konto), isolierter Umgebung, Referenzbelegen, Playwright
  mit Bildschirmfotos und manueller Sichtabnahme. Ein gesetztes Token zählt für die Abnahme nicht.
- **Reihenfolge:** Framework-Konsolidierung vor Feature-Erweiterung. Phase 0 = Bestand prüfen
  (DocFlow, Einkaufsbelege, Anmeldung, Staging) und Lücken schließen; Phase 1 = universelle
  Eingangsbelegmaske auf DocFlow; Phase 2 = weitere Einkaufs- und Verkaufsbelege. Welle 1 enthält
  keine destruktiven Änderungen an bestehenden Einkaufs- oder Buchhaltungstabellen; Altstrukturen
  gehen erst nach verifizierter Migration und dokumentiertem Rückfallkonzept außer Betrieb.
- **Kein zweites UI-Framework** neben dem Mask Builder; SAP Fiori elements ist Referenz, nicht
  Laufzeit.

Die Bestandsprüfung dazu steht in `screen-framework-fiori-gap-analyse.md`. Sie ändert die
Reihenfolge unten: Die dort genannte **Phase 0 geht Welle 0 voran**, und die Referenzimplementierung
ist die Eingangsbelegmaske (bisher BELEG-042), nicht die Rechnung im Verkauf.

## D. Entscheidungen, die der Plan braucht

| # | Frage | Empfehlung | Warum |
|---|---|---|---|
| E1 | Wo wird die Eingangsrechnung geführt? | **In DocFlow als Einkaufsbelegart**, Besitzer Einkauf | Der Einkaufsweg läuft nirgends (B-7); DocFlow hat Prozess, Kette und Nachweis schon (B-4). Die Einkaufstabellen zu reparieren wäre schneller, hinterließe aber eine zweite Belegstruktur |
| E2 | Wird DocFlow führender Speicher auch für Auftrag und Lieferschein? | **Später und einzeln entscheiden.** Der Belegvertrag macht die Maske davon unabhängig | Lieferschein (3.249 Zeilen) und Auftrag haben eigene Speicher mit viel Fachlogik. Erst der Vertrag, dann je Belegart prüfen, ob die Kopie (B-5) entfällt |
| E3 | Was geschieht mit dem dritten Maskengerüst `FormBuilder`? | **Entfällt mit der Rechnungsvariante** | Nur eine Seite benutzt es |
| E4 | Sichtprüfung | **Testkonto beim Anmeldeanbieter** bereitstellen | Eine neue Belegmaske ohne Blick in den Browser abzunehmen ist nicht vertretbar |

## E. Slice-Plan

Jeder Slice endet mit Tests gegen die frische Datenbank, QA-Dokument, Workboard und Push. Reihenfolge
so, dass früh etwas Sichtbares entsteht und kein Schritt eine neue Sonderarchitektur festschreibt.

### Welle 0 — Vertrag und Engine (ohne sichtbare Änderung)

| Slice | Inhalt | Fertig, wenn |
|---|---|---|
| BELEG-010 | **Belegvertrag** als Schema und Vertragstest: Felder, Namen, was je Variante fehlen darf. Ableitung aus den fünf vorhandenen Beleg-ScreenDefinitions (B-1) | Vertragstest läuft; Abbildungstabelle alter Feldnamen auf den Vertrag liegt vor — **erledigt 13.10.2026** (`belegvertrag-20261013.md`) |
| BELEG-011 | **Lesender Belegweg** `GET /belege/{belegart}/{id}` für die DocFlow-Belegarten des Verkaufs; je Domäne ein Adapter | Angebot, Auftrag, Lieferschein, Rechnung aus DocFlow kommen in Vertragsform |
| BELEG-012 | **Preisrecht an der API:** ohne Recht keine Preis-, Rabatt- und Summenfelder im Belegvertrag | Test: gleicher Beleg, zwei Benutzer, zwei Antworten |
| BELEG-020 | **Variante in der Engine:** `build_beleg_screen_definition(belegart)` erzeugt aus Grundgerüst + Variantenangabe eine ScreenDefinition; Registry, Agenten-Synonyme, TS-Kopie, Governance und Inventare kennen Varianten | Zwei Varianten aus einer Quelle; Bereitschaftsprüfung 1,0; keine ausgeschriebene Kopie |

### Welle 1 — Erste Varianten im Verkauf (Daten und Prozess stehen)

| Slice | Inhalt | Fertig, wenn |
|---|---|---|
| BELEG-030 | Variante **Rechnung** (lesen und erfassen) über DocFlow; Steuerschlüssel je Position, Summen vom Server, Buchungsstatus sichtbar | Löst `sales/invoice-editor` und `verkauf/rechnung` ab; `FormBuilder` entfällt (E3) |
| BELEG-031 | Variante **Lieferschein** aus demselben Grundgerüst: Mengen, keine Preise | Derselbe Bildschirm, andere Belegart; Preisfelder kommen ohne Recht nicht an |
| BELEG-032 | **Aktionen als Kommando-Wege:** freigeben, umwandeln (mit Teilmengen), buchen, stornieren — über DocFlow; MCP-Aktionskarte; Buchen und Freigeben für Agenten gesperrt bzw. nur nach menschlicher Freigabe | Kette Auftrag → zwei Teillieferscheine → Rechnung in der Maske durchführbar, jede Stufe ein eigener Beleg mit Bezug |
| BELEG-033 | Varianten **Angebot** und **Auftrag** | Verkaufskette vollständig in einer Maske |

### Welle 2 — Einkauf (abhängig von E1)

| Slice | Inhalt | Fertig, wenn |
|---|---|---|
| BELEG-040 | Einkaufsbelegarten im Belegprozess: Bestellung, Wareneingang, Eingangsrechnung, Einkaufsgutschrift; Steuerrichtung Einkauf | Kette Bestellung → Wareneingang → Eingangsrechnung mit Bezug je Position |
| BELEG-041 | **Eingangsrechnung bucht über Finance** (`finance_eingangsrechnung_buchung`), Buchungsstatus am Beleg | „Verbuchen" ohne Journal gibt es nicht mehr (B-8) |
| BELEG-042 | Varianten Bestellung, Wareneingang, Eingangsrechnung, Einkaufsgutschrift | Einkaufskette in derselben Maske |
| BELEG-043 | Rechnungskontrolle: Betrag des Lieferanten gegen die Summe der Positionen, Abweichung als Prüfgrund | Cent-Abweichung führt zur Klärung, nicht zur stillen Buchung |

### Welle 3 — Ablösen und Abbauen

| Slice | Inhalt | Fertig, wenn |
|---|---|---|
| BELEG-050 | Je Einzelmaske: Funktionsinventur gegen die Variante, dann Route und Navigation umhängen | Keine Funktion fällt still weg; Liste je Maske abgehakt |
| BELEG-051 | **Zweitwege in der Finanzbuchhaltung abbauen** (`/finance/invoices`, `/finance/ap/invoices`): Aufrufer umhängen (ScreenDefinition `finance/ap-invoice`, Agentenwerkzeuge, Kernel `PostAPInvoice`, Sammelrechnung), dann entfernen | Entscheidung des Auftraggebers vom 13.10.2026 umgesetzt |
| BELEG-052 | Je Belegart entscheiden, ob der eigene Speicher bleibt oder die Kopie in DocFlow entfällt (E2) | Kein Beleg hat zwei Wahrheiten |

### Welle 4 — Weitere Belege mit denselben Bausteinen

| Slice | Inhalt |
|---|---|
| BELEG-060 | Gutschrift Verkauf (`sales/gutschrift`) als Variante; Agentenfreigabe bleibt |
| BELEG-061 | Abrechnungsgutschrift an den Landwirt (Ernte): Variante mit Bausteinen Wiegeschein, Qualität, Kontrakt; Steuerregime des Lieferanten (§ 24 UStG) |
| BELEG-062 | Wiegeschein, Frachtbrief, Kontrakt: Grundgerüst plus Fachbaustein, wo die Form passt |

## F. Was sofort unabhängig weitergehen kann

- **Buchungsautorität vervollständigen** (keine Maskenarbeit): Buchungszeilen der Rechnung tragen den
  Steuerschlüssel; eine Regel dafür, welche Konten ein Mandant bebuchen darf; Kasse weist im Bon den
  richtigen Satz aus.
- **Steuerschlüssel am Artikel pflegen** (68 Artikel des Testmandanten ohne Schlüssel).
- **Geparkt, nicht ausgeliefert:** ein Umbau von `einkauf_rechnungseingaenge` auf Steuerschlüssel und
  echtes Buchen. Bei E1 = DocFlow wird davon nur die Buchungslogik gebraucht.

## G. Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Die großen Masken können mehr, als die Variante zunächst kann (Lieferschein: Preisfindung, Kontraktbezug, Feldbuch-Übergabe, Portalbestellungen) | BELEG-050: Funktionsinventur je Maske vor dem Umhängen; die alte Maske bleibt, bis die Liste abgehakt ist |
| Der Belegvertrag wird zum kleinsten gemeinsamen Nenner | Fachbausteine je Variante (C); der Vertrag regelt nur das Gemeinsame |
| Eine Variante bekommt doch Fachlogik | Vertragstest: Die Variantenangabe enthält nur Deklaration; Berechnung und Prüfung liegen im Server |
| Zwei Wahrheiten während der Umstellung (B-5) | Je Belegart ein führender Speicher, im Belegvertrag ausgewiesen; BELEG-052 |
| Ohne Sichtprüfung entstehen Masken, die Tests bestehen und nicht bedienbar sind | E4 vor Welle 1 |
| Mandant aus der Anfrage in DocFlow (B-10) | Vor BELEG-011 schließen |

## H. Nicht im Plan

- Die vierzehn Einzelmasken einzeln als ScreenDefinition neu bauen.
- Ein gemeinsamer Belegdatensatz, der beim Wechsel der Variante überschrieben wird.
- Eine eigene Rechnungsverwaltung in der Finanzbuchhaltung.
- Der Tax Rules Service (EU-TEDB-Adapter, versionierte Regeln mit Freigabe) — eigener Plan; die
  Belegvarianten nehmen den Steuerschlüssel, woher er auch kommt.

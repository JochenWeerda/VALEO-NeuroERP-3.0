# Flow-Spine-Entlastung — Validierung und Masterplan (FSX)

Stand: 2026-09-15 · Auslöser: Vergleich mit schlanken ERP-Prozessleisten (Dynamics BPF,
SAP-Belegfluss). Ziel: der Alltag wird belegzentriert, der Flow Spine bleibt Leitstand.

## A. Was am Code validiert ist

Alle Angaben gegen `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`
(1700 Zeilen) und `app/core/flow_spine_registry.py` (583 Zeilen) geprüft.

| # | Befund | Beleg | Bewertung |
|---|--------|-------|-----------|
| V1 | Drei-Spalten-Raster `220px / 1fr / 360px`, `min-h-[720px]` | FlowSpineWorkspace.tsx:934 | bestätigt — 580 px vor der Arbeitsfläche |
| V2 | Modi `Flow / Fokus / Uebersicht` sind `<span>`, ohne Handler und State | FlowSpineWorkspace.tsx:919 | bestätigt — tote Bedienelemente |
| V3 | Interne `resume_node_id` und `resume_route` im Arbeitsbereich sichtbar | :1082, :1098 | bestätigt — Technik im Fachbereich |
| V4 | „Nächste Schritte“ ausdrücklich ohne Navigation („als Checkliste gemeint“) | :1290 | bestätigt |
| V5 | **Knoteninhalte sind statisch im Backend-Registry hinterlegt**: `metric`, `submetric`, `timestamp`, `detail_rows`, `kpis`, `documents`, Agententexte | flow_spine_registry.py:180ff, `WORKSPACES[...]` | **neu und gewichtiger als die Dichte** |
| V6 | `merge_instance_statuses` überlagert ausschließlich `node.status` sowie `instance_label`/`instance_id` | flow_spine_registry.py:554ff | bestätigt — alles andere bleibt Demo-Inhalt |
| V7 | „KPI Health Score“ mit Fallback `92%` und fest verdrahteter Balkenbreite `width: '92%'` | FlowSpineWorkspace.tsx ~1200 | erfundene Kennzahl |
| V8 | Kein Filter nach `linked_document_id` in `GET /flow-spines/{process_key}/instances` | flow_spines.py:443ff | blockiert den belegzentrierten Einstieg |
| V9 | `POST .../instances` ohne Idempotenz auf die Belegreferenz | flow_spines.py:371ff | Doppelfall-Risiko bei „Fall beim Speichern anlegen“ |
| V10 | Bausteine einer schlanken Ebene existieren und sind breit im Einsatz: `OperationalCaseHeader`, `ProcessStatusPanel`, `CompactDecisionCard`, `WorkflowEntryBanner` | components/workflow/*, 40+ Seiten | Bausteine vorhanden; wie weit sie Ebene 1 tragen, ist ohne Kriterienkatalog nicht quantifizierbar |
| V11 | Der schwere Cockpit-Pfad umfasst 9 Prozessrouten plus Studio, alle unter Core-Navigation | pages/workflow/flow-spine-*.tsx, navigation/domains/core.tsx:107ff | überschaubare Umbaufläche |
| V12 | 18 Masken lesen bereits `readWorkflowEntryContext` (Handover über Query-Parameter) | Repo-Suche | der Rückweg Beleg → Fall fehlt jedoch |
| V13 | `timestamp` wird in `_node()` als `_now()` beim Cache-Fill gesetzt; `insight` und `footer_cards` sind Registry-Texte, stehen aber nicht in der operativen Merge-Liste | flow_spine_registry.py:187, :253, :554ff | unklassifiziert — FSX-001 muss sie Fall 1 oder Fall 3 zuordnen |
| V14 | `PATCH .../instances/{id}` setzt `linked_document_id`/`type` frei; Unique-Index (FSX-011) greift dort ebenfalls | flow_spines.py:516ff | Kollision beim Update ist ein Konflikt, kein Idempotenzfall |
| V15 | `capture-then-resolve` in `document-entry-policy.ts` legt den Fall bereits nach dem Speichern an (Lieferschein-Erfassung als Vorlage) | document-entry-policy.ts, Workboard UI-DOCUMENT-WORKFLOW | bestehendes Muster; FSX-012 erweitert es, eröffnet keinen zweiten Pfad |

**Korrektur an der Ausgangsdiagnose:** Das Hauptproblem ist nicht in erster Linie die
Informationsdichte, sondern dass ein großer Teil der dichten Fläche **nicht instanzbezogen** ist.
Ein realer Vorgang zeigt dieselben Zahlen, Zeitstempel und Agententexte wie jeder andere, über
Mandanten hinweg. Reines Verdichten würde falsche Inhalte nur kleiner darstellen. Deshalb stehen
V5/V6/V7 vor jeder Layout-Arbeit.

**Nicht geprüft:** ein gemessener Vergleich laufender Oberflächen. Die Annahme „schlanker ist
besser“ bleibt bis FSX-090a (technische Interaktionsmessung) **und** FSX-090b (Nutzerbeobachtung)
unbelegt — die beiden messen Verschiedenes und ersetzen einander nicht.

## B. Zielbild — drei Ebenen, ein Vertrag

| Ebene | Ort | Inhalt | Stand heute |
|-------|-----|--------|-------------|
| 1 Alltag | Belegmaske / Arbeitsliste | kompakte Phasenleiste, aktueller Status, **eine** nächste Aktion, Blocker | Bausteine vorhanden (V10), Bindung fehlt; Reifegrad erst nach Kriterienkatalog aus FSX-030 bezifferbar |
| 2 Detail bei Bedarf | aufklappbar in der Maske | Belegbeziehungen, Teilmengen, Zuständigkeiten, Historie, Copilot | teilweise; Timeline nur im Cockpit |
| 3 Leitstand | `workflow/flow-spine-*` | Überwachung, Ausnahmen, übergreifende Koordination | vorhanden, aber demo-lastig |

Regel (verbindliche Fassung): **Alle für die aktuelle Fachaufgabe notwendigen Informationen sind
in der Belegmaske erreichbar.** Übergreifende Analysen und Koordination über mehrere Vorgänge
hinweg dürfen ausschließlich auf Ebene 3 bleiben. Der Prüfsatz lautet also nicht „nichts nur im
Leitstand“, sondern: kein Feld, das zur Bearbeitung *dieses* Belegs gebraucht wird, zwingt in den
Leitstand.

## C. Slice-Plan

Die Reihenfolge ist bindend: Wahrheit vor Dichte, Vertrag vor Rollout, Bindung vor Kosmetik.
Erster Umsetzungsschritt sind FSX-002 und FSX-003 — die Behandlung fehlender und beispielhafter
Daten —, danach die Datenbindung (FSX-001) und der zentrale UI-Vertrag (FSX-030).

### Welle 1 — Wahrheit herstellen (Voraussetzung für alles Weitere)

- **FSX-002 Keine erfundenen Kennzahlen.** *(Startpunkt)*
  „KPI Health Score“ entfernen oder an eine echte Quelle binden; die fest verdrahteten 92 % und
  der Fallback-Wert entfallen ersatzlos. Fehlt eine Quelle, zeigt die Karte „nicht ermittelt“
  statt einer Zahl.
- **FSX-003 Fehlend und beispielhaft unterscheidbar machen.** *(Startpunkt)*
  Drei Zustände je Feld, widerspruchsfrei getrennt:
  1. **Statisch und zulässig** — Phasenbezeichnungen, Knotenlabels, Prozessbeschreibungen,
     Reihenfolge. Diese stammen aus dem Registry und bleiben dort; sie sind Prozessdefinition,
     keine operativen Werte, und brauchen keine Kennzeichnung.
  2. **Operativ und vorhanden** — instanzbezogen, mit benannter Quelle (siehe FSX-001).
  3. **Operativ und nicht ermittelbar** — sichtbar als fehlend („nicht ermittelt“), niemals durch
     einen Registry-Vorgabewert ersetzt.
  Verboten ist allein Fall 3, der wie Fall 2 aussieht: ein operativer Wert (Menge, Zeitstempel,
  Quote, Freigabestand, Dokumentbezug, Agentenaussage) aus dem Registry im Kontext einer echten
  Instanz. Gate: Test, der Registry-Konstanten aus der Menge der operativen Felder im Instanzpfad
  verbietet — die Phasenbezeichner sind ausdrücklich ausgenommen.
  CI: eigener Job `fsx-gates` in `quality-gate.yml`, parallel zur
  Backend-Kaskade (die beim ersten Rot abbricht). Zweite Hälfte: Scanner
  `scripts/check_flow_spine_invented_frontend_values.py` gegen das JSX-Muster
  aus FSX-002 (`?? '92%'` / `width: '92%'`), Scope nur `components/workflow`
  und `pages/workflow` — kein repo-weites `??`.
  Konkrete Zuordnung aus V13, nicht offen lassen: `timestamp` aus `_now()` beim Cache-Fill ist
  Fall 3 (sieht aus wie Instanzzeit, ist aber der Zeitpunkt des ersten Cache-Füllens). `insight`
  und `footer_cards` sind Prozessbeschreibung und damit Fall 1, sofern sie keine Mengen, Daten
  oder Agentenaussagen enthalten; sobald sie operative Werte tragen, fallen sie unter Fall 2/3
  und brauchen einen Eintrag in der Herkunftskarte.
- **FSX-001 Instanzbezug der Knotendaten — vollständig.**
  `merge_instance_statuses` erweitern auf **alle** operativen Knotenfelder: `metric`, `submetric`,
  `timestamp`, `detail_rows`, `kpis`, **`documents` und `agent`** (Headline, Message, Reasons).
  Dokumente müssen die tatsächlich am Vorgang hängenden Belege zeigen oder leer bleiben;
  Agententexte müssen aus einer Bewertung dieser Instanz stammen oder als nicht verfügbar
  erscheinen — generische Beispieltexte im echten Vorgang sind ein Fehler, kein Platzhalter.
  **Nachweis reicht über Unterschiedlichkeit hinaus:** dass zwei Instanzen verschiedene Werte
  liefern, belegt keine korrekte Quelle. Jedes operative Feld erhält daher eine deklarierte
  Herkunft (Instanzattribut oder benanntes Domänen-Readmodel), und der Vertragstest prüft den
  Wert **gegen diese Quelle**, nicht gegen einen anderen Vorgang. Felder ohne deklarierte Quelle
  fallen nach FSX-003 Fall 3.
  Registry-Werte bleiben ausschließlich Vorgaben für den Katalogfall ohne Instanz.
  **Herkunftskarte (verbindlich, maschinenlesbar):** `app/core/flow_spine_field_origins.yaml`.
  Inhaltlich entspricht sie `docs/design/flow-spine-herkunftskarte.md`: `timestamp` und
  `detail_rows` kommen aus dem jüngsten Knotenereignis (eine Abfrage je Instanz, mit
  `tenant_id`); `metric`, `submetric`, `kpis`, `documents` und `agent` sind undeclared und
  bleiben leer. V13 bleibt als Befund richtig (Registry-`_now()` ist keine Vorgangszeit) und
  ist als Zuordnung überholt — die Vorgangszeit steht in `ops_flow_spine_instance_events`.
  - Der Vertragstest lädt die Karte und vergleicht den gerenderten Wert mit der
    deklarierten Quelle derselben Instanz. Ein zweiter Vorgang ist kein Vergleichsmaßstab.

### Welle 2 — Vertrag und belegzentrierter Einstieg

FSX-030 steht in der Welle zuerst, weil FSX-013 den Vertrag braucht. FSX-010, FSX-011 und
FSX-012 haben **keine technische Abhängigkeit** von FSX-030; sie dürfen parallel laufen,
sobald Welle 1 steht. Die Reihenfolge im Text ist die Standardreihenfolge, kein künstlicher
Kalenderstopp vor der Belegbindung.

- **FSX-030 Mask-Builder-Vertrag.** *(vorgezogen, Voraussetzung für FSX-013)*
  Prozessband, Statusquelle und „nächste Aktion“ als deklaratives Feld in ScreenDefinition
  beziehungsweise RenderPlan/Meridian-Vertrag verankern, damit Masken sie ohne eigenes JSX
  erhalten; Designregeln in CLAUDE.md ergänzen. Enthält den **Kriterienkatalog für Ebene 1**
  (welche Felder eine Maske führen muss, um als alltagstauglich zu gelten) — erst damit ist
  überhaupt messbar, wie weit die vorhandenen Bausteine tragen. Der Vertrag steht vor dem
  Rollout, nicht daneben.
- **FSX-010 Fallsuche je Beleg.**
  `GET /flow-spines/{process_key}/instances?linked_document_id=&linked_document_type=`
  filtert tenant-isoliert innerhalb des Pfad-`process_key`. **Kein eigener Index.** Die Suche
  nutzt denselben Schlüssel wie FSX-011
  `(tenant_id, process_key, linked_document_type, linked_document_id)`.
  Ein zweiter, schwächerer Index ohne `process_key` entsteht nicht — er würde die Suche
  nicht beschleunigen und falsche Zugriffspläne begünstigen. FSX-010 darf FSX-011 vorausgehen
  (Filter ohne Unique-Constraint ist möglich); der Index kommt mit FSX-011.
  Antwort enthält `lifecycle_status`; abgeschlossene Fälle werden mitgeliefert und als
  abgeschlossen markiert (siehe FSX-011, Verknüpfungsregel).
- **FSX-011 Nebenläufigkeitssichere Fallanlage.**
  Ein vorheriges Nachschlagen (FSX-010) verhindert keine parallele Doppelanlage — zwei
  gleichzeitige Speichervorgänge sehen beide „kein Fall vorhanden“. Die Eindeutigkeit muss
  deshalb in der Datenbank erzwungen werden, nicht in der Anwendungslogik.
  Verbindlich festgelegt:
  - **Eindeutigkeitsschlüssel:** `(tenant_id, process_key, linked_document_type,
    linked_document_id)`. Der Mandant ist Teil des Schlüssels; der Prozessschlüssel ebenfalls,
    damit derselbe Beleg in zwei verschiedenen Prozessen je einen eigenen Fall haben darf.
    Das ist **derselbe** Index, den FSX-010 für die Suche verwendet — einer, nicht zwei.
  - **Geltungsbereich:** partieller eindeutiger Index nur für **offene** Fälle mit echter
    Belegreferenz. PostgreSQL behandelt `NULL` in Unique-Indexes als verschieden; ein
    Leerstring `''` ist dagegen nicht `NULL` und würde alle manuellen Fälle ohne Beleg
    miteinander kollidieren lassen. Deshalb:
    ```sql
    CREATE UNIQUE INDEX uq_flow_spine_open_by_document
      ON domain_ops.ops_flow_spine_instances
         (tenant_id, process_key, linked_document_type, linked_document_id)
      WHERE linked_document_id IS NOT NULL
        AND btrim(linked_document_id) <> ''
        AND linked_document_type IS NOT NULL
        AND btrim(linked_document_type) <> ''
        AND lifecycle_status NOT IN ('completed', 'cancelled', 'failed');
    ```
    Beim Schreiben werden leere Strings für `linked_document_id` und `linked_document_type`
    auf `NULL` normalisiert, sonst greift der Index am falschen Ende. `on_hold` und `draft`
    zählen als offen und bleiben im Index.
  - **Verhalten bei Kollision — POST anlegen:** `IntegrityError` abfangen, den bestehenden
    offenen Fall lesen und ihn zurückgeben (**200 statt 201**). Der Aufrufer erhält in beiden
    Fällen dieselbe Fall-ID.
  - **Verhalten bei Kollision — PATCH:** `PATCH` darf `linked_document_id`/`type` setzen
    (V14). Derselbe Index greift. „Den anderen Fall zurückgeben“ ist auf Update unsinnig.
    Kollision beim Patch: **409 Conflict**, Zuordnung unverändert. Kein stilles Umbiegen.
  - **Abgeschlossene Fälle beim Nachschlagen:** FSX-010 liefert sie mit, markiert als
    abgeschlossen; die Maske verknüpft aber nur mit offenen und bietet für abgeschlossene
    ausdrücklich die Neuanlage an, statt stillschweigend wiederzubeleben.
  - **Belege ohne Referenz:** ist `linked_document_id` nach Normalisierung `NULL`, greift der
    Index nicht; solche Fälle sind manuell angelegte Vorgänge und bleiben von der Idempotenz
    ausgenommen.
  Migration: Vorabprüfung auf vorhandene Dubletten, Bereinigung vor dem Index. Schließt V9.
- **FSX-012 Fall beim Speichern, nicht davor — mit Absicherung gegen Teilfehler.**
  **Stand 2026-09-15: umgesetzt** (`outgoing-purchase-order`, Bestell-Wizard nach
  Speichern, PATCH-409, Slice FSX-012). P2P-001 umkehren: die Bestellung startet in
  `einkauf/bestellung-anlegen`, der Prozessfall wird
  beim fachlichen Speichern angelegt oder verknüpft. Zwei Schreibvorgänge gegen zwei Aggregate
  können einzeln scheitern; das ist auszuformulieren, nicht zu hoffen.
  **Kein zweiter Pfad:** `capture-then-resolve` in
  `packages/frontend-web/src/lib/workflow/document-entry-policy.ts` (V15) legt den Fall bereits
  nach dem Speichern an; die Lieferschein-Erfassung dient als Vorlage. FSX-012 erweitert dieses
  Muster auf P2P-001 und weitere Belegarten, erfindet es nicht neu.
  - **Beleg zuerst, Fall danach.** Die Bestellung ist die führende Größe. Schlägt die Fallanlage
    fehl, bleibt die Bestellung gespeichert und gültig; der Nutzer verliert keine Eingaben.
  - **Wiederholung ohne zweite Bestellung.** Der Wiederholungsaufruf richtet sich ausschließlich
    auf die Fallanlage, nie auf das Speichern des Belegs. Weil FSX-011 auf der Belegreferenz
    eindeutig ist, ist dieser Aufruf beliebig oft wiederholbar und liefert stets denselben Fall.
    Die Maske zeigt den Teilfehler sichtbar an („Bestellung gespeichert, Vorgang noch nicht
    verknüpft“) mit einer Aktion zum erneuten Verknüpfen — kein stiller Fehlschlag, und kein
    Zurücksetzen des Formulars.
  - **Nachlauf.** Bleibt die Verknüpfung offen (Nutzer bricht ab), wird sie beim nächsten Öffnen
    des Belegs erneut angeboten; die Belegmaske fragt ohnehin über FSX-010 nach dem Fall.
  - **Fall-ID aus der URL ist eine Behauptung, keine Berechtigung.** Ein `workflowInstanceId`
    aus der Query wird serverseitig geprüft. Zwei verschiedene Fehlschläge, nicht einer:
    1. **404** — Mandant oder `process_key` passen nicht. `_get_instance_or_404` tut das
       bereits; das bleibt so, damit keine Existenz fremder Fälle preisgegeben wird.
       Nicht 403.
    2. **409 Conflict** — Mandant und Prozess passen, der Fall ist aber bereits an einen
       *anderen* Beleg gebunden. Das ist kein Geheimnis gegenüber dem eigenen Mandanten,
       sondern ein Konflikt. 404 würde die Maske ratlos machen (anlegen? ignorieren?).
    Unverknüpfte Fälle (`linked_document_id` NULL) dürfen sich an den aktuellen Beleg
    hängen — das ist der bestehende Handover. Abgelehnt wird nur das Umbiegen einer
    *bereits gesetzten* Zuordnung. Der gültig geprüfte Handover hat Vorrang vor der
    Neuanlage.
  `docs/workflows/p2p-001-*.md` und die zugehörigen Cards ziehen mit.
- **FSX-013 Prozessband statt Hinweiskasten.** *(setzt FSX-030 voraus)*
  `WorkflowEntryBanner` durch ein kompaktes einzeiliges Prozessband ersetzen: Phasen, Status,
  nächste Aktion, Link in den Leitstand. Rollout über die 18 Masken aus V12 — **erst nachdem der
  zentrale Vertrag aus FSX-030 steht**, damit nicht 18 Masken einzeln nachgezogen werden müssen,
  sobald sich die Felddefinition ändert.

### Welle 3 — Leitstand entdichten

- **FSX-020 Tote Modi entfernen oder verdrahten.** `Flow / Fokus / Uebersicht` (V2): echte
  Umschalter mit State oder streichen. Kein drittes Ergebnis.
- **FSX-021 Technik aus dem Arbeitsbereich.** `resume_node_id` und `resume_route` (V3) in eine
  Diagnoseansicht verschieben.
- **FSX-022 „Nächste Schritte“ navigierbar machen** (V4): jeder Punkt wird zur Aktion oder entfällt.
  Vertrag: `items` ist `str | {label, href}`. Beobachtungskarten (Heatmap, Agent Events) bleiben
  Strings. Die Karte „Nächste Schritte“ enthält nur Objekte; `href` muss bereits im selben
  Workspace als Aktion, Dokument, Ressource oder verknüpftes Modul stehen. Zeilen ohne Ziel
  entfallen — sie werden nicht als tote Checkliste stehen gelassen. Die Zeilen sind
  Prozessdefinition (FSX-003 Fall 1), keine Vorgangswerte.
- **FSX-023 Redundanz auflösen.** Aktionen und Agenteninhalte stehen doppelt (Mitte und
  Copilot-Spalte). Eine Quelle; die Spalte wird einklappbar, Grundzustand eingeklappt.
- **FSX-024 Linke Spalte reduzieren.** Favoriten und Rollenwechsel sind Aufgaben der AppShell,
  nicht des Prozessraums.

### Welle 4 — Nachweis

Der Nachweis zerfällt in zwei Verfahren, weil ein Automat nicht messen kann, was er nicht erlebt.

- **FSX-090a Technische Interaktionsmessung (Playwright).**
  Dieselbe Aufgabe (Direktbestellung, Reklamation) alt gegen neu, automatisiert gezählt:
  Maskenwechsel, Anzahl Eingabefelder und Klicks bis zur abgeschlossenen Aufgabe, Anzahl
  Netzwerkrunden, Fehlerquote bei Sperren und Teilmengen. Das ergibt belastbare Zahlen über den
  *Weg* durch die Oberfläche — und ausdrücklich nicht über Bedienzeit: Playwright tippt ohne
  Zögern, sucht nicht und liest nicht.
- **FSX-090b Nutzerbeobachtung.**
  Dieselben Aufgaben mit echten Sachbearbeitern, mindestens fünf Personen je Rolle
  (Innendienst, Waage, Buchhaltung), beobachtet und protokolliert: tatsächliche Bearbeitungszeit,
  Suchpausen, Fehlbedienungen, Rückfragen, und ob Sperren, Teilmengen und Freigaben ohne
  Erklärung verstanden werden. Verständlichkeit ist ausschließlich hier messbar.
  Abbruchkriterium: Wird eine Sperre oder Teilmenge in der neuen Fassung seltener verstanden als
  in der alten, wird der betroffene Rollout zurückgestellt — auch bei besseren 090a-Zahlen.

Ohne beide Ergebnisse gilt die Vereinfachung als unbelegt. Eine kürzere Prozessleiste allein ist
kein Nachweis.

## D. Risiken

- **Doppelte Fälle** beim belegzentrierten Einstieg — erst nach FSX-011 ausrollen, und dort über
  einen Datenbank-Index, nicht über ein Nachschlagen in der Anwendungslogik.
- **Leerstring statt NULL** in `linked_document_id` — ohne Normalisierung und ohne `btrim <> ''`
  in der Index-WHERE-Klausel kollidieren alle manuellen Fälle ohne Beleg; die Ausnahme ist tot.
- **PATCH-Kollision** (V14) — Unique-Index greift auf Update; ohne 409 wird die Zuordnung
  still umgebogen oder der Aufrufer erhält den falschen Fall.
- **404 für denselben Mandanten** bei bereits gebundenem Fall — Maske kann Konflikt und
  Nicht-Existenz nicht unterscheiden; deshalb 409 nur für die falsche Belegbindung.
- **Teilerfolg beim Speichern** (Beleg geschrieben, Fall nicht) — ohne Retry entweder verwaiste
  Belege oder eine zweite Bestellung. **Mit FSX-012:** sichtbarer Teilfehler, Wiederholung nur
  der Verknüpfung; der Beleg bleibt. Nachlauf in der Bestell-Detailmaske ist noch offen.
- **Zweiter Anlegepfad** neben `capture-then-resolve` (V15) — FSX-012 muss das bestehende
  Muster erweitern, sonst divergieren Lieferschein und Bestellung.
- **Vertragstest ohne Herkunftskarte** — vergleicht wieder Vorgang gegen Vorgang und würde
  auch einen Zufallsgenerator bestehen.
- **Reifegradangaben ohne Kriterien** — Aussagen wie „überwiegend vorhanden“ sind bis zum
  Kriterienkatalog aus FSX-030 nicht zu treffen; sie erzeugen sonst falsche Planungssicherheit.
- **Sichtbarer Funktionsverlust im Leitstand**, sobald FSX-001 echte Werte liefert, wo bisher
  gefällige Demo-Zahlen standen. Das ist beabsichtigt und gegenüber Nutzern zu benennen.
- **Bestehende Handover-Links** (`workflowInstanceId`, 18 Masken) dürfen nicht brechen; FSX-012
  ist additiv. Unverknüpfte Fälle bleiben anbindbar.
- **Geteilter Working Tree** mit Parallel-Agenten: Workboard-Claim vor Beginn, kein `git add -A`.

## E. Nicht im Plan

- Kein neues Prozess-Framework und keine Ablösung der Flow Spines als Modell.
- Keine Chevron-Optik „weil andere ERP das so machen“. Die Verallgemeinerung über „fast alle
  großen ERP-Systeme“ ist nicht belegt; belegt sind Business Process Flows in modellgesteuerten
  Dynamics-Anwendungen und der SAP-Belegfluss — und SAP rät bei vertrauten Tagesaufgaben
  ausdrücklich von Wizards ab.


## Review-Korrekturen 2026-09-15 — FSX-REVIEW-FIX-20260915

Die vier Code-Review-Befunde sind korrigiert: Auch der normale Wizard-Abschluss
wiederholt nach einem Teilfehler ausschliesslich die Verknuepfung. Die Bestellpolicy
fixiert den Prozesspfad auf procure-to-pay; eine URL kann ihn nicht wechseln.
Fehlende Knotenstatuswerte werden als unknown / Status nicht ermittelt angezeigt.
Das gemischte insight-Feld ist operativ klassifiziert und bleibt ohne Quelle leer;
Labels, Icons, Reihenfolge und Aktionen bleiben Prozessdefinition.

Die Migration stoppt bei mehrfachen offenen Belegbindungen. Sie entfernt keine
realen Belegreferenzen. Vor einem erneuten Lauf sind die betroffenen Faelle durch
eine dokumentierte fachliche Entscheidung zu klaeren. Ermittlungsabfrage:

```sql
SELECT tenant_id, process_key, linked_document_type, linked_document_id,
       array_agg(id ORDER BY created_at, id) AS instance_ids
FROM domain_ops.ops_flow_spine_instances
WHERE linked_document_id IS NOT NULL AND btrim(linked_document_id) <> ''
  AND linked_document_type IS NOT NULL AND btrim(linked_document_type) <> ''
  AND lifecycle_status NOT IN ('completed', 'cancelled', 'failed')
GROUP BY tenant_id, process_key, linked_document_type, linked_document_id
HAVING count(*) > 1;
```

Bereits durch eine aeltere Migration entfernte Zuordnungen lassen sich nur anhand
bestehender Sicherungen beziehungsweise Auditdaten rekonstruieren. Dieser Slice
fuehrt keine Migration auf Produktivdaten aus. Der Nachlauf beim Wiedereroeffnen
der Bestelldetailmaske bleibt offen; FSX-012 ist insoweit kein Gesamtabschluss.


## Verbindliche Erweiterung: Split/Merge, Kontrakt und Fremdlager

Nutzeranforderung 2026-09-15: Automatische Vorschlaege zur Entnahme aus Kontrakten
oder aus kundeneigenem, beim Haendler eingelagertem Bestand. Umsetzung offen.

### Gemeinsamer Positionsbezug

Ausgangs- und Eingangsbelege brauchen n:m-Zuordnungen auf Positionsebene: ein
Lieferschein zu mehreren Rechnungen, mehrere Lieferscheine zu einer Rechnung,
auch kombinierte Teilmengen. Kontraktabruf und physische Bestandsentnahme sind
zwei getrennte Beziehungen derselben Position. Ein Kontrakt bezeichnet die
kaufmaennische Verpflichtung, ein Lagerbestand die physische Herkunft und den
Eigentuemer. Eine Rechnung darf durch ihre Verknuepfung keine zweite Entnahme
oder einen zweiten Kontraktabruf ausloesen. linked_document_id am Flow Spine
bleibt Einstiegsbeleg, nicht das vollstaendige Beziehungsmodell.

### Automatische Vorschlaege

- Nach Auswahl/Aenderung von Partner, Artikel, Menge, Belegdatum und Richtung
  werden passende Quellen automatisch lesend ermittelt, positionsbezogen.
- Kontrakte: Mandant, Kunden-/Lieferantenrolle, Kontraktseite, Artikel und
  vereinbarte Qualitaet, Lieferzeitraum, Status, Einheit, offene und bereits
  reservierte Abrufmenge pruefen. Explizite Belegreferenzen priorisieren;
  weitere Sortierung nachvollziehbar nach vereinbarter Abrufregel/Faelligkeit.
- Fremdlager bedeutet hier Kundeneigentum beim Haendler: Mandant UND Eigentuemer,
  Artikel, Qualitaet/Charge, Lagerort, Sperren, Menge und Reservierungen pruefen.
  Der Empfaenger muss nicht der Eigentuemer sein; Abholung fuer einen Dritten
  benoetigt den passenden Auftrag beziehungsweise eine Freigabe des Eigentuemers.
- Vorschlag zeigt Quellart, Referenz, Eigentuemer, verfuegbare Menge, Einheit,
  vorgeschlagene Teilmenge und Begruendung. Unvereinbare Quellen bleiben gesperrt;
  fehlende Eigentums-/Mengeninformationen erzeugen keinen geratenen Treffer.
- Mehrere Quellen sind zulaessig: etwa 12 t aus Kontrakt A und 8 t aus Kontrakt B.
  Kundeneigentum und verkaufte Haendlerware werden in getrennten Teilpositionen
  gefuehrt. Ungedeckte Restmenge wird sichtbar ausgewiesen.
- Ein Vorschlag reserviert oder bucht nichts. Auswahl bestaetigen; beim fachlichen
  Ausfuehren Verfuegbarkeit, Berechtigung und Version erneut serverseitig pruefen.
  Reservierung/Verbrauch nebenlaeufigkeitssicher und idempotent; Ruecknahme und
  Korrektur mit Audit. Teilrechnungen veraendern nur die Abrechnungszuordnung.

### Eigentum und Abrechnung

Auslagerung kundeneigener Ware ist kein erneuter Verkauf dieser Ware. Lagergeld,
Verladung, Fracht und andere vereinbarte Leistungen werden separat behandelt.
Ein Eigentumswechsel bedarf eines eigenen fachlichen Vorgangs; er darf nicht
als Nebeneffekt eines Matching-Vorschlags entstehen. Auf der Eingangsseite
entsprechend Einkauf aus Lieferantenkontrakt und reine Fremdwareneinlagerung
trennen. Kein automatischer Vorrang Fremdlager vor Kontrakt ohne Geschaeftsregel.

### Vorhandene Bausteine zuerst verwenden

- `app/services/agrar_contract_service.py`: Kontrakte und vorhandene Allocations.
- `app/services/foreign_goods_worklist_service.py` und
  `app/services/procurement_service.py`: Fremdware mit Eigentuemer, Charge,
  Lagerort und aktueller Menge; Reservierungs-/Verbrauchsvertrag vor Ausbau pruefen.
- `app/services/docflow_service.py`: source_line_id und Belegbeziehungen;
  wiederholte Teilumwandlung aktuell durch existing_link begrenzt.
- `app/api/v1/endpoints/collective_documents.py`: Sammelrechnung ganzer
  Lieferscheine; noch kein vollstaendiges Restmengenmodell.

Keinen zweiten Zuordnungsdienst neben bestehenden Mechanismen einfuehren.
Vorschlagsbereich zentral ueber ScreenDefinition/RenderPlan/Meridian anbinden.

### Abnahme fuer die spaetere Umsetzung

1. Split 100 t auf 60/40 t und Merge aus mehreren Lieferungen auf beiden Seiten;
   verbleibende Menge korrekt, keine Doppelabrechnung bei parallelen Aktionen.
2. Kontraktvorschlag nur fuer passenden Partner/Artikel/Zeitraum; Teilabruf ueber
   zwei Kontrakte moeglich, ausgeschoepfte und gesperrte Quellen ausgeschlossen.
3. Zwei Eigentuemer mit gleichem Artikel im selben Lager: nur berechtigte
   Eigentumsmenge vorschlagen, entnehmen und fortschreiben.
4. Mischung aus Kundeneigentum und Haendlerverkauf: getrennte Teilpositionen,
   keine Warenrechnung fuer die Rueckgabe des Kundeneigentums.
5. Zwischen Vorschlag und Ausfuehrung verbrauchte Menge: Konflikt anzeigen,
   keine Ueberentnahme; Retry ohne doppelte Buchung.
6. Storno/Retoure/Gutschrift unterscheiden: nur die fachlich passende Operation
   gibt Kontrakt-, Lager- oder Abrechnungsmenge frei.

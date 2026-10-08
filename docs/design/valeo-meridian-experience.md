---
title: VALEO Meridian Experience
type: reference
audience: [agent, entwickler, design, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-19
version: 1.1.0
description: Meridian als Design-, Layout- und Governance-Vertrag des Single Mask Builder.
---

# VALEO Meridian Experience

Stand 2026-10-08: Das Agrar-Sortenregister liest den bestehenden kanonischen
VarietyOut-Vertrag statt eines Phantom-Endpunkts. Nullable Metadaten und
Aktivstatus werden unverfaelscht dargestellt; Query- und Fehlervertrag sind
zentral geprueft. Diese Vertragsreparatur erzeugt kein neues Seitenlayout
oder paralleles Maskensystem. [QA](../quality-assurance/sorten-canonical-read-20261008.md).

Stand 2026-09-10: Der zentrale ActionRuntime-Vertrag unterscheidet direkte
Commands von `inputFlow.kind=humanForm`. Solche Eingabeflows werden nicht
automatisch ueber ihren dokumentierten Submit-Endpoint ausgefuehrt;
`forbiddenForAgents` bleibt bei der Policy-Auswertung erhalten.
Verifikation: 66 Runtime-Tests und 12 Desktop-Visual-Audits bestanden, siehe
[Desktop-Abnahme](../quality-assurance/l3-desktop-docker-2026-09-08.md).

Meridian ist keine manuelle Seiten-Bauanleitung und kein paralleles UI-Framework.
Meridian ist die zentrale Builder-Capability in dieser Kette:

```text
ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime -> UniversalMaskRenderer
```

Wenn eine Maske unprofessionell wirkt, wird nicht die einzelne Seite geflickt.
Korrigiert werden Schema, Compiler, Renderer oder Readiness-Gate.

## Low-Fidelity-Triage

Vor groesseren Layout-Aenderungen wird die Maske als Scribble, Wireframe oder
Low-Fidelity-Prototyp bewertet. Ziel ist nicht Pixel-Design, sondern fruehe
Logikpruefung:

- Klickwege kuerzen: primaere Aktion, naechste Aktion und Rueckweg muessen im
  ersten Viewport erkennbar sein.
- Felder aussortieren: nur Identitaet, Status, Risiko, Betrag/Menge und naechste
  Entscheidung gehoeren in Header oder Summary.
- Nebensaechliches verbannen: selten genutzte Stammdaten, Historien, Dokumente
  und technische Details wandern in Tabs oder Kontext-Rail.
- Tabellen priorisieren: ERP-Listen bleiben Tabellen; Karten sind kein Ersatz
  fuer tabellarische Finanz-, Lager- oder Auditdaten.
- Kontext klaeren: Audit, Workflow, Sperren, Human Approval und Copilot-Erklaerung
  erscheinen in der Kontext-Rail, nicht verteilt in Fachfeldern.

Das Ergebnis der Triage wird in `ScreenDefinition.layout`, Tabs, Summary-Items,
Actions und Tabellenprofilen ausgedrueckt. Es entsteht keine separate Referenz-UI.

## Layout-Vertrag

`ScreenDefinition.layout` traegt die Meridian-Metadaten:

```ts
layout: {
  floorplan: 'worklist' | 'objectPage' | 'transaction' | 'cockpit' | 'wizard' | 'analyticalList'
  columnNavigation?: 'single' | 'listDetail' | 'listDetailDetail'
  density: 'comfortable' | 'compact' | 'expertDense'
  contextRail: 'none' | 'audit' | 'copilot' | 'workflow' | 'combined'
  tableProfile?: 'standard' | 'financial' | 'inventory' | 'audit'
  summaryPlacement?: 'header' | 'footer'
  stickyHeader?: boolean
  stickyFooter?: boolean
  sectionNavigation?: 'tabs' | 'anchors'
}
```

Floorplans beschreiben den Zweck der Seite. Spaltennavigation ist eine
eigene Achse und nicht die Kontextleiste:

| Floorplan | Einsatz | Spalten |
|---|---|---|
| `worklist` | Belege suchen, filtern und bearbeiten | erlaubt |
| `objectPage` | Kunde, Artikel oder Vertrag mit Details | erlaubt |
| `transaction` | Wiegen, Wareneingang, Buchen | gesperrt, volle Breite |
| `cockpit` | Ausnahmen erkennen und Maßnahmen starten | gesperrt |
| `wizard` | Mehrstufige Vorgänge mit Abschlussprüfung | gesperrt |
| `analyticalList` | Kennzahlen und Datensätze gemeinsam | erlaubt |

Die Dichte folgt derselben Kette. `comfortable` hält 52-px-Zeilen,
`compact` 44 px (Fiori Cozy, Touch-Untergrenze) und `expertDense` 36 px
(Fiori Compact, über der 32-px-Stufe). Eine Maske ist eine ScreenDefinition, die der Builder zeichnet. Eine freie
Seite ist nur der Einstieg, der diese Definition lädt. Der Arbeitsbereich setzt `compact`
und einen einzigen Seitenrand von 16 px. Die Seitenwurzel, Maskenrahmen,
Listen und Objektseiten legen keinen zweiten Rand darüber. Eingabe, Auswahl und
Schaltfläche lesen `--control-height`; in `expertDense` folgt auch die
Touch-Untergrenze auf 36 px. `PageSurface` ist eine flache Arbeitsfläche
ohne eigenen Scroll und ohne Verlauf. Eine native Maske überschreibt die
Dichte aus `ScreenDefinition.layout`. Klassische Erfassungsmasken sitzen
als Arbeitsfläche im Seitenrand, tragen genau eine Überschrift und halten
die Felder auf 36 px, damit feste Spaltenraster nicht umbrechen. Die
Objektüberschrift folgt derselben Stufe wie die Werkzeugleiste: halbfett
und eng laufend, ohne Display-Größe.
`single` ist eine konzentrierte Erfassung oder eine breite Tabelle.
`listDetail` hält die Arbeitsliste neben dem Objekt. `listDetailDetail`
öffnet bei Bedarf die dritte Spalte (Liste → Objekt → Unterobjekt).
Auswahl, Filter und Eingaben bleiben beim Zurückwechseln erhalten, weil
die Spalten im DOM bleiben. Unter 900 px und in der Vollansicht ist nur
eine Spalte sichtbar; dazwischen zwei, ab 1440 px drei. Audit, Hinweise
und Copilot bleiben `contextRail`.

Der Compiler setzt `columnNavigation` zentral: `worklist` und
`analyticalList` mit Tabellen werden `listDetail`, sofern die
ScreenDefinition nichts anderes erklärt. `transaction`, `cockpit` und
`wizard` bleiben immer `single`. `objectPage` bleibt `single`, bis eine
Maske `listDetail` oder `listDetailDetail` ausdrücklich setzt. Der
`UniversalMaskRenderer` leitet die Spalten aus dem Plan ab — ohne
Einzel-JSX je Maske.

Vertragsabnahme 2026-10-07: Die Backend-Inventur respektiert ausdrueckliches
`single` ebenso wie der Compiler; konzentrierte Erfassungen werden nicht durch
ein widersprechendes Testdefault zu `listDetail`. Fahrzeug-Loeschen verwendet
die gueltige Stufe `high` mit Bestaetigung in Python und TypeScript.
Eine einzige Navigationsspalte braucht keine Ansichtenleiste; Tabellen mit
demselben Titel wie der Seitenkopf unterdruecken ihre wiederholte Ueberschrift
zentral in FastTabRenderer und DerivedColumnLayout. Mehrspaltennavigation bleibt
erhalten. Typisierte benannte Historien werden wie Seiten-`items` geprueft;
mehrdeutige oder untypisierte Zeilen bleiben ein blockierender Feldvertragsbefund.

Fach-Admins und Agenten erzeugen Entwürfe im Masken-Studio
(`/admin/screen-studio`). Ausgabe ist eine normale ScreenDefinition unter
`tenant/<slug>`; Validate und Publish nutzen denselben Gate-Pfad. Nach
Vier-Augen-Freigabe hängt `published_temp` in den Laufzeitkatalog
(`GET /api/v1/masks/{id}/screen-definition`, Omnibox) und öffnet unter
`/studio/run/{tenant__slug}`. Native Screen-IDs bleiben unbeschattet.
Entwürfe liegen in `domain_shared.screen_definition_drafts`. Zeilenklick
wählt; `In Vollansicht öffnen` folgt `rowRouteTemplate`. Explizite `columns`
(Kunden-Schnellauswahl) bleiben Vorrang.

Erste Referenzmasken: lesende Kunden-Schnellauswahl
(`/crm/kunden-schnellauswahl`, explizites `listDetail`) und die native
Futteranalyse-Worklist (`futtermittel/analysen`, abgeleitet).
Tabellen-Ladefehler laufen über `MessagePanelRenderer` und den
Fast-Table-Renderer; sie dürfen nicht wie eine leere Trefferliste
aussehen. Coverage: `tests/test_meridian_column_navigation_inventory.py`.

Der `RenderPlan.shell` uebernimmt diese Felder zentral. Renderer lesen den Plan
und erzeugen daraus Header, Aktionshierarchie, Summary, Tabs, Tabellenprofil,
Dichte und Kontextbereich.

### Durchgehende Belegseite (`sectionNavigation=anchors`, MERIDIAN-BELEG-ONEPAGE)

Belege mit wenigen Registern (Kopf, Positionen, Dokumente) stehen als eine
durchgehende Seite untereinander. Die Register bleiben als Sprungmarken
erhalten; man scrollt durch den Beleg oder springt gezielt.

- Erlaubt nur für `objectPage` und `transaction` mit `columnNavigation=single`.
  Andere Kombinationen fallen im Compiler auf `tabs` zurück und werden von
  `validateScreenDefinition` sowie vom Backend-Gate `schema_valid` abgelehnt.
- Kopf und Sprungleiste sind gemeinsam sticky. Der Kopf schrumpft ab 96 px
  Scrolltiefe und wächst erst unter 48 px wieder (Puffer gegen Flackern);
  im schmalen Kopf bleibt nur die Belegidentität (ein `h1`).
- Die Sprungleiste markiert den sichtbaren Abschnitt (`aria-current`).
  `Alt+1` bis `Alt+9` springen und setzen den Fokus auf die Abschnittsüberschrift.
  Bei reduzierter Bewegung wird ohne Animation gescrollt.
- Nachrangige Abschnitte werden erst kurz vor dem Sichtbereich geladen
  (Lazy-Mount); ein Sprung lädt den Abschnitt sofort.
- Hat die Maske eine Belegkette (`ProcessRibbonRenderer`), steht sie als
  letzter Abschnitt „Belegfluss“. Der aktuelle Schritt ist nicht klickbar,
  Schritte ohne Zielmaske sind deaktiviert. Das `ProcessBand` (Stand des
  Vorgangs) bleibt davon getrennt.
- `stickyHeader` und `stickyFooter` sind in diesem Modus standardmäßig aktiv.
- Bei ungespeicherten Änderungen fragt die Maske vor dem Verlassen nach
  („Zurück zur Maske“ / „Änderungen verwerfen“). „Speichern und verlassen“
  gibt es bewusst nicht, weil ein fehlgeschlagenes Speichern sonst trotzdem
  zur Navigation führen würde.

Seit MERIDIAN-BELEG-SYSTEMWEIT ist das die Voreinstellung: Jede native
`objectPage`- oder `transaction`-Maske mit `columnNavigation=single` erhält
Sprungmarken, ohne dass die ScreenDefinition etwas deklariert (Compiler
`resolveSectionNavigation`, Backend-Normalisierer `_with_meridian_layout`).
Wer Register braucht, setzt `layout.sectionNavigation: "tabs"` als Opt-out und
begründet es. Die Readiness meldet die aufgelöste Einstellung unter
`resolvedLayout`. Die früheren Pilotseiten (Auftrag, Kontrakt, Kunde-Altpfad)
laufen über `useUniversalMaskRuntime` und damit über dieselbe Voreinstellung.

### Belegidentität und Anzeigewerte

- `identityField` in der ScreenDefinition benennt das Feld mit der Belegnummer.
  Der `h1` zeigt dann die Nummer („SO-00064“), der Maskentitel steht als Kicker
  darüber (`text-2xs uppercase tracking-wide`). Das Feld muss in der Maske
  deklariert sein (Frontend-Validierung und Readiness `schema_valid`). Ohne Wert
  fällt der `h1` auf den Maskentitel zurück. Ohne Deklaration leitet der
  Normalisierer `infer_identity_field` das Feld aus dem Kopf ab (Nummer-Schlüssel
  oder „…-Nr.“-Label, keine Personen-, Artikel- oder Kontonummern); ein expliziter
  Wert gewinnt immer. Welche Maske welches Feld erhält, hält ein Snapshot-Test
  fest (`tests/test_meridian_beleg_systemweit.py`).
- Kopf-Gate: Kein Kopf zeigt ein rohes `_id`-Feld, ohne dass daneben ein lesbares
  Gegenstück steht (Name oder Nummer). Schlüssel, die zur Zuordnung nötig sind,
  wandern in einen eigenen Abschnitt („Zuordnung“, „Provenienz“). Die Namen und
  Nummern liefern die Einzel-GETs über `resolve_reference`
  (`app/services/customer_reference.py`, immer mit Tenant-Filter).
- Masken zeigen keine Schlüssel: Kunden über Name und Kunden-Nr. statt über die ID
  (Backend `resolve_customer`, gleich in Auftrag, Lieferschein und Rechnung),
  Vorgängerbelege über ihre Nummer, Wahrheitswerte als Ja/Nein,
  Status über `statusLabel()` (`renderers/status-labels.ts`) — für Tabellen-Chips
  und Nur-Lese-Felder mit Schlüssel `status`. Neue Status werden dort ergänzt,
  nicht in der einzelnen Maske.
- Unter Tabellen steht kein technisches Profil; das Tabellenprofil ist nur als
  `data-table-profile` für Tests und Styling vorhanden.

- **Positions-Detailband (`table.rowDetail`):** Ein Klick auf eine Position öffnet
  ihre Details als Band direkt unter dem Raster, nicht als Dialog. `fields` legt
  die Felder fest; ohne Angabe zeigt das Band alle Spalten. Erneuter Klick, der
  Schließen-Knopf oder Escape schließen es. Führt die Tabelle eine
  `rowRouteTemplate`, bietet das Band „In Vollansicht öffnen“. Auf
  Sprungmarken-Seiten erhält jede Tabelle ab sechs Spalten das Band automatisch;
  `rowDetail: false` schaltet es ab.
- **Steuerausweis:** Die Rechnung zeigt im Kopf je Steuersatz Netto, Umsatzsteuer
  und Brutto. Gerundet wird je Position wie beim Anlegen, damit die Summe dem
  Kopfbetrag entspricht.
- **Tabellenhöhe:** Kurze Tabellen schrumpfen auf ihre Zeilen; 420 px bleibt
  die Obergrenze langer Listen.

## Gewohnheitsbruecken

Migration aus einem bestehenden Desktop-ERP wird als Bedienvertrag modelliert,
nicht als herstellerspezifisches Theme. Additive Meridian-Vertraege sind:

- `actions[].zone`: fachliche Aktionen links im Footer, Commit-Aktionen rechts;
  ohne Angabe bleibt die Action im Header.
- `actions[].keyboardShortcut`: sichtbarer und zentral dispatchter Tastaturweg;
  Berechtigungen und ActionRuntime bleiben unveraendert.
- `layout.summaryPlacement`: Summen wahlweise im Kopf oder nach Tabellen/Tabs.
- `layout.stickyHeader` / `stickyFooter`: stabile Orientierung bei dichten
  Desktopmasken.
- `interaction.enterMovesFocus`: Enter folgt dem sichtbaren Feldfluss; Textareas
  und Buttons behalten ihre native Bedeutung.
- `tables[].rowActions`: statusabhaengige Zeilenaktionen werden im zentralen
  Fast-Table-Renderer deklariert. Einzelmasken bauen dafuer keine eigene
  Aktionsspalte; Backend-Berechtigung, Confirmation und Audit bleiben
  autoritativ.

L3-Referenzfaelle und Datenschutzregeln:
[`l3-to-meridian-habit-parity.md`](l3-to-meridian-habit-parity.md).

## Disposition

Operative Masken folgen einer Reihenfolge: Identität, Arbeitsdaten, Ressourcen, Validierung, Aktion, Ergebnis. Die Ampel steht hinter den Eingaben, aus denen sie entsteht. Aktionen sitzen am Auslöser. Primäraktionen stehen im Kopf, Folgeaktionen an der Zeile.

Produktive Felder starten leer. Kennzahlen, die aus Tour, Fahrzeug oder Lieferschein folgen, werden gezählt und nicht ein zweites Mal gespeichert. Tabellen tragen eine Spaltenpriorität: `primary` bleibt bei schmaler Breite, `secondary` folgt, `tertiary` weicht zuerst. Touch benutzt dieselbe Fachregel, nur die Dichte ändert sich.

Eine operative Maske hat eine ScreenDefinition. Der Builder zeichnet sie und enthält keine Abfrage auf eine Masken-Id. Die Seite lädt Daten und löst Aktionen aus.

## Governance

`generatorReady=true` ist nur erlaubt, wenn die Meridian-Metadaten vorhanden sind.
Tabellenmasken brauchen ein Tabellenprofil. Finanzmasken brauchen `financial`,
Lager-/Bestandsmasken `inventory`. Detail-, Cockpit-, Transaktions- und
Wizard-Masken duerfen keine leere Kontext-Rail haben.

Referenzmasken sind Abnahmefaelle:

- Finance: `financial` profile, AuditReason, Freigabe-/Storno-/Buchungslogik.
- CRM 360: `objectPage` mit Header-Facets (`summary.kind`), Ankern und Prozessband Interessent → Kunde; KIM und das Kunden-Cockpit sind Redirects auf dieselbe Akte, `?tab=` springt in die Sektion; Listen-IDs und `/verkauf/kunden-stamm/:id` werden auf den Stamm aufgelöst.
- Lager: `inventory` profile, Mengen/Einheiten, Reservierungen, Bewegungen und Status.

Abweichungen werden im Builder oder in der ScreenDefinition behoben.

## Screen-System

Vier Schichten, eine Definition:

```text
Domain / Application
       ↓
Queries + Commands
       ↓
ScreenContext
       ↓
ScreenDefinition
       ↓
MaskBuilder
       ↓
UI
```

Die ScreenDefinition beschreibt, was der Benutzer sieht und tun darf. Der MaskBuilder zeichnet daraus die Oberfläche und enthält keine Fachregel und keinen API-Aufruf. Die Anwendung entscheidet, was gültig ist, und legt Daten, Policies und Befehle in den ScreenContext. Der Builder wertet nur aus, was dort steht.

Gespeichert bleibt Schema-Version 1 mit `layout.floorplan`: `worklist`, `objectPage`, `transaction`, `cockpit`, `wizard`, `analyticalList`. Daraus folgt der Typ Arbeitsliste, Objekt, Vorgang, Cockpit, Bericht oder Master-Detail über die Spaltennavigation. Felder wie `screenType`, `listReport` oder `form` sind kein zweites Format.

Eine Aktion nennt einen Befehl (`tour.create`) und optional `enabledWhen`. Ein String darin ist eine Domänen-Policy. `all` / `any` / `path` bleiben UI-Bedingungen. Destruktive Aktionen ohne Bestätigung, unbekannte Befehle der Referenzmasken und mehr als zwei Primäraktionen meldet `app/core/screen_governance.py` in der CI.

Die erlaubten Bausteine sind die vorhandenen Feldtypen: Text, Zahl, Datum, Auswahl, EntityPicker, Tabelle, Status, Kennzahlen, Aktionsleiste. Dichte, Touch-Höhe und Statustöne kommen aus den bestehenden Tokens. Referenzmasken sind Tourenplanung, Fahrer und Fahrzeuge. Der Vertrag steht in `docs/architecture/uix/screen-governance.md`.

CI-Vertrag 2026-10-05: Der UniversalMaskRenderer reicht den Bildschirmtitel
an den gemeinsamen TabContentRenderer weiter. Dessen TableRenderer unterdrueckt
nur eine identische Tabellenbeschriftung (ohne Beachtung von Grossschreibung
und Randabstand); fachlich verschiedene Tabellenueberschriften bleiben sichtbar.
Diese Regel gilt zentral in der bestehenden Renderer-Kette. Der wiederverwendete
ErrorState verwendet fuer kleine Statustexte und Wiederherstellungshinweise
volle Textdeckkraft. Typpruefung und Verhaltenstests ergaenzen die Browser-WCAG-Abnahme.

Die zentrale Tailwind-Kompilation scannt explizit `src/` und `index.html`.
So bleiben Klassen der Renderer und Seiten vollstaendig erfasst, waehrend
Workspace-Artefakte und der Startordner den CSS-Build nicht ausweiten.
Die acht WCAG-Kernrouten bestehen nach dieser Begrenzung (2026-10-05).

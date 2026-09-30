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

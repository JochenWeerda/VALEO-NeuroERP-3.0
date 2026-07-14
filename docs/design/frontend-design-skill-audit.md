# Frontend-Design-Skill-Audit — VALEO NeuroERP 3.0

Stand: 2026-07-14 · Autor: Claude (Frontend-Design-Skill-Durchlauf) · Branch: `main`

Ziel: die Prinzipien des Frontend-Design-Skills auf das bestehende ERP-Frontend übertragen —
konsistent, professionell, performant, barrierearm (WCAG 2.2 AA) — ohne Geschäftslogik,
Routing, Rechteprüfung oder Mandantenfähigkeit zu verändern.

---

## 1. Ausgangslage

Untersucht wurden (Phase 1):

- `CLAUDE.md`, `docs/MASKEN.md`, `docs/design/` (Meridian/Terra-Token-Dateien, UIX-Masterpläne)
- `packages/frontend-web/package.json` (Skripte, Abhängigkeiten)
- `src/index.css`, `src/styles/` (`tokens/primitives.css`, `design-tokens-meridian.css`,
  `design-tokens-terra.css`, `density.css`)
- `src/components/ui/` (52 Primitives, u. a. `button`, `badge`, `tabs`, `data-table`,
  `VirtualDataTable`, `table`, `dialog`, `toast`)
- `src/components/mask-builder/` (ObjectPage, ListReport, Wizard, Worklist, OverviewPage,
  UniversalMaskRenderer/-NativeDetailPage, Schema/Validation)
- `src/components/patterns/`, `src/components/navigation/` (AppShell, TopBar, Sidebar,
  Breadcrumbs, PageToolbar, ModuleToolbar, CommandPalette), `src/components/layout/`, `src/layouts/`
- Storybook-Stories (`components/patterns/__stories__/`), Tests (`src/__tests__/components/…`)
- Referenzmasken: `pages/crm/kim/` (CRM-360-Cockpit, 15 Teilkomponenten), `pages/verkauf/`

### Befund: Das Fundament ist gut

Das Designsystem ist deutlich reifer als bei typischen gewachsenen ERP-Frontends:

- **Tokens:** φ-basierte Typo- (10–42 px) und Spacing-Skala (Fibonacci), semantische
  HSL-Farbtokens (`--color-semantic-success/warning/error/info-*`), 3 Elevation-Stufen,
  Motion-Dauern/Easings, Z-Index-Skala, `--touch-target: 44px`.
- **Themes:** Meridian („Präzision trifft Wärme", Ozeanblau/Bernstein) + Terra, Dark Mode
  (`.dark`), Warehouse-High-Contrast; Tailwind-4-Bridge über `@theme inline` (theme-reaktiv).
- **Density:** drei Modi (`comfortable`/`compact`/`dense`) via `data-density`, zentral über
  `--control-height`/`--table-row-height`/`--field-gap`.
- **A11y-Grundlagen global:** `:focus-visible`-Ring, `prefers-reduced-motion`, Formularfehler-
  Konventionen (`aria-invalid`, `.field-error`), Touch-Größen im Button (`touch`-Sizes).
- **Frameworks:** Mask-Builder + Universal Mask Runtime; PageToolbar mit Role-Density und
  Aktions-Overflow; CommandPalette; VirtualDataTable (TanStack Virtual) für große Datenmengen.

### Befund: Die Lücken liegen in der Anwendung, nicht im System

| # | Inkonsistenz | Beleg |
|---|--------------|-------|
| 1 | **Handgebaute Reiterleisten statt ARIA-Tabs.** Die wichtigste CRM-Maske (KIM-Cockpit, 12 Register) baute Reiter als rohe `<button>`-Reihe: kein `role="tablist"/"tab"`, kein `aria-selected`, keine Pfeiltasten-Navigation, Panels ohne `tabpanel`-Bezug. Ursache: `ui/tabs.tsx` bot nur den Segmented-Control-Look, keinen Belegregister-Look — Seiten wichen deshalb auf Eigenbau aus. | `pages/crm/kim/index.tsx` (vorher) |
| 2 | **Fehlende h1-Hierarchie.** Im Hauptzustand des Cockpits existierte keine `h1` (nur in der Druckansicht); erste Überschrift war eine `h2` mit dem Kundennamen. | `CustomerHeader.tsx` (vorher) |
| 3 | **Arbitrary Values statt Tokens.** `text-[10px]` statt vorhandenem `text-2xs`, `bg-[hsl(var(--color-semantic-success-500-hsl))]` roh im JSX, `max-w-[190px]`; repo-weit 69 Treffer für Hex/`style={{`/Arbitraries unter `src/pages/` (großteils Recharts-Farben — dort legitim, aber unauditiert). | `CustomerHeader.tsx`, `pages/**/charts/` |
| 4 | **Semantikfarbe als Dekoration.** Grüner Punkt als reiner Trenner zwischen „Sprache/Währung" — Erfolgsgrün ohne fachliche Bedeutung. | `CustomerHeader.tsx` (vorher) |
| 5 | **Auto-Save ohne Lifecycle.** Chef-Anweisung speicherte per `onBlur` ohne Pending-Guard, ohne Erfolgssignal, ohne Unverändert-Prüfung (Verstoß gegen die Mutation-Lifecycle-Invariante aus CLAUDE.md). | `pages/crm/kim/index.tsx` (vorher) |
| 6 | **Fokusring-Lücke im Primitive.** `TabsTrigger` hatte keinen `focus-visible`-Stil (WCAG 2.4.11). | `ui/tabs.tsx` (vorher) |
| 7 | **Duplikate:** zwei AppShells (`components/navigation/AppShell.tsx` aktiv via `DashboardLayout`; `components/layout/AppShell.tsx` 14 KB Altbestand); `patterns/ObjectPage|ListReport` parallel zu `mask-builder/*` (bewusster Übergang, aber Konsistenzrisiko). | Verzeichnisstruktur |
| 8 | **Drei Token-Quellen:** `index.css :root` (Brand/Neutral/Semantic) + Meridian + Terra; über `primitives.css` bereits teilentflochten, Rest-Duplikate bleiben. | `src/index.css`, `src/styles/` |

---

## 2. Abgeleitete Design-Regeln (verbindlich)

Die Regeln präzisieren CLAUDE.md/`docs/MASKEN.md`, sie ersetzen nichts:

1. **Registerprinzip:** Reiterleisten in Akten und Belegen sind immer echte ARIA-Tabs über
   `ui/tabs.tsx` — `TabsList variant="register"` für Belegregister/Karteireiter-Optik,
   Default-Variante für Ansichtsumschalter. Nie rohe `<button>`-Reihen. Pfeiltasten-Navigation
   und Fokusring kommen zentral aus dem Primitive.
2. **Eine h1 je Maske = Objektidentität** (Kundenname, Belegnummer). Weitere Ebenen folgen
   strikt h2→h3; Druckansichten zählen separat (per `print:` aus dem Screen-DOM genommen).
3. **Mikro-Labels:** `text-2xs` + `tracking-wide` + `uppercase` + `text-muted-foreground`.
   Kein `text-[10px]`/`text-[11px]`.
4. **Semantikfarben nur mit fachlicher Bedeutung** und nur über zentrale Varianten
   (`Badge` success/warning/info/muted, `Button` destructive). Keine rohen
   `hsl(var(--…-hsl))`-Arbitraries im Seiten-JSX; Trenner/Dekoration nutzen `bg-border`.
5. **Auto-Save ist eine Mutation:** Pending-Guard, `disabled` während des Speicherns,
   Unverändert-Kurzschluss, `finally`-Reset, Erfolg + Fehler sichtbar (Toast), Statuszeile
   mit `aria-live="polite"`.
6. **Dichte über `data-density`,** nicht über verstreute `h-8`/`h-9` je Maske.
7. **Aktionshierarchie:** je Maske genau eine Primäraktion (default-Button), Sekundäres
   `outline`/`ghost`, Destruktives `destructive` + Bestätigungsdialog; Überlauf über
   PageToolbar-Overflow.
8. **Tabellen:** Zahlen rechtsbündig mit `font-mono`/`tabular-nums` (`[data-type]`-Hooks
   existieren global); ab ~200 Zeilen `VirtualDataTable`.
9. **Leere/Lade-/Fehlerzustände** benennen die Handlung („Bitte links einen Debitor wählen…"),
   nie nur den Zustand; Ladezustände als Skeleton oder Spinner + Text.
10. **Keine neuen Token-Quellen, keine lokalen Mini-Designsysteme.** Erweiterungen nur bei
    echter systemweiter Lücke — im Zweifel `docs/design/`-Eintrag zuerst.

## 3. Pilotbereich: CRM-360-Cockpit (`/crm`, `pages/crm/kim/`)

**Begründung:** Priorität 1 der Vorgabe und fachlich das dichteste Objekt im Frontend —
produktiv an den Debitorenstamm angebunden (462+ Kunden, serverseitige Suche), enthält alle
relevanten Muster in einer Maske: Master-Detail (Kundenliste ↔ Akte), Belegkopf
(CustomerHeader), Statusbanner, Aktionsleiste, 12 Register, Tabellen (Ansprechpartner,
Historie, offene Posten), Dialoge, Side-Panel (NeuroAI), Lade-/Leerzustand, Druckansicht,
Lazy-Loading (Leads/Geo). Verbesserungen hier strahlen über die Register-Variante auf alle
Akten- und Belegmasken aus.

## 4. Referenzimplementierung (Vorher → Nachher)

### Zentral: `src/components/ui/tabs.tsx`
- **Neu:** `TabsList` erhält `variant?: 'default' | 'register'` (Context-basiert,
  vollständig rückwärtskompatibel — Default-Look unverändert).
- „register" = Belegregister-Optik (Laschen auf Grundlinie `bg-muted/60` + `border-b`,
  aktive Lasche verbindet sich per `translate-y-px` mit dem Blatt, horizontaler Überlauf
  scrollt statt umzubrechen) — exakt der bisherige KIM-Look, jetzt mit korrekter Semantik.
- **A11y-Fix für beide Varianten:** `focus-visible:ring-2 ring-ring ring-inset` am Trigger.

### Pilot: `src/pages/crm/kim/index.tsx`
- Registerleiste + 12 Panels von Hand-`<button>`/`{activeTab === … &&}` auf
  `Tabs`/`TabsList variant="register"`/`TabsContent` umgestellt. Damit: `tablist`/`tab`/
  `tabpanel`-Rollen, `aria-selected`, Pfeiltasten-Navigation, Fokusring — ohne visuelle
  Änderung. Agenten-/Test-Verträge blieben erhalten (`data-action-id="crm360.tab.*"`,
  `id="sub-workspace-tab-*"`, `center-pane-tabs`, `center-tab-views`).
- Chef-Anweisungs-Auto-Save nach Regel 5: `saveChefAnweisung()` mit Duplicate-Guard,
  Unverändert-Kurzschluss, `disabled` + „Anweisung wird gespeichert…" (`aria-live="polite"`),
  Erfolgs-Toast, `finally`-Reset.

### Pilot: `src/pages/crm/kim/components/CustomerHeader.tsx`
- `h2` → `h1` (Objektidentität der Maske; Druckansicht-h1 liegt im `print:`-Zweig und ist
  am Screen nicht im Accessibility-Tree).
- `text-[10px]` (4×) → `text-2xs tracking-wide`; `max-w-[190px]` → `max-w-48`.
- Grüner Deko-Punkt → `bg-border` + `aria-hidden` (Semantikfarbe nur mit Bedeutung).

### Neu: Story + Test
- `src/components/ui/__stories__/Tabs.stories.tsx` — SegmentedControl, BelegRegister,
  Überlauf mit 12 Registern.
- `src/__tests__/components/ui/tabs.register.test.tsx` — ARIA-Rollen/`aria-selected`,
  Panelwechsel per Klick, Pfeiltasten-Navigation.

## 5. Accessibility-Ergebnisse

- Registerleiste des Piloten: von „nicht tastaturbedienbar als Tabs / ohne Rollen" auf
  vollständige ARIA-Tab-Semantik mit Pfeiltasten und sichtbarem Fokus (WCAG 2.1.1, 2.4.11, 4.1.2).
- Überschriftenstruktur des Piloten: genau eine h1 im Hauptzustand (WCAG 1.3.1).
- Statusmeldung des Auto-Save per `aria-live="polite"` (WCAG 4.1.3).
- Kontraste: unverändert, da ausschließlich bestehende semantische Tokens verwendet werden
  (Meridian/Terra sind auf AA ausgelegt); keine neuen Farbwerte eingeführt.
- Global bereits vorhanden und unangetastet: `prefers-reduced-motion`, `:focus-visible`,
  Touch-Targets 44 px.

## 6. Performance-Ergebnisse

- Keine neuen Abhängigkeiten; Radix-Tabs war bereits im Bundle (`@radix-ui/react-tabs`).
- Renderverhalten unverändert: Radix unmountet inaktive Panels wie zuvor die
  `{activeTab === …}`-Bedingungen; Lazy-Panels (Leads/Geo) behalten `Suspense`.
- Unverändert-Kurzschluss im Auto-Save spart Roundtrips beim bloßen Durchtabben.
- Bestand (positiv, nicht angefasst): Route-Code-Splitting (898 generierte Routen),
  `VirtualDataTable`, `lazy-charts`, `vite-plugin-compression`.

## 7. Testergebnisse (Phase 6)

| Prüfung | Ergebnis |
|---------|----------|
| `npm run routes:generate` | ✅ 898 Routen generiert |
| `npm run type-check` | ✅ ohne Fehler |
| `npm run lint` | ✅ 0 Fehler; 8 vorbestehende Warnungen in nicht berührten Dateien (campaign-detail, bestellung-stamm, lastschriften-debitoren) |
| `vitest run` (gezielt: tabs.register + LazyTabs) | ✅ 3/3 |
| `npm run test:run` (volle Suite) | ✅ 365 grün, 1 übersprungen; ❌ 6 rot in 2 Dateien (`universal-sales-order-pilot`, `universal-customer-mask-pilot`: „No QueryClient set" im CalendarRenderer) — per `git stash`-Gegenprobe als **vorbestehend auf `main`** bewiesen (fallen ohne diese Änderungen identisch) |
| `npm run build` | ✅ 19,8 s; Chunk-Warnung (maplibre > 500 kB) vorbestehend |
| `npm run check:routing-integrity` | ⚠️ 5 vorbestehende Portal-Alias-Lücken (empfehlungen, lohndienste, onboarding, preisspiegel, whatsapp-simulator) — Altbestand auf `main`, nicht durch dieses Audit verursacht; gehört dem Portal-Workstream |
| `npm run check:navigation-targets` | ✅ 898 Routen-Patterns |
| `npm run test:e2e:accessibility` | 5/8 Kernrouten grün (inkl. `/`, `/einkauf/bestellungen`, Portal-Routen); ❌ `/agrar`, `/finance`, `/lager` mit vorbestehenden `color-contrast`-Verstößen — Ursache durchgängig Roh-Palette `text-green-600` (#00a63e auf #f5f7f8 = 2,99:1) statt semantischer Tokens; `/crm` ist nicht Teil der Kernrouten-Liste |

## 7a. Update 2026-07-14 — Lückenschluss (DESIGN-GAPS-SWEEP-002)

Alle unten in Abschnitt 8 als „vorbestehend/fremd" markierten Rot-Stände wurden im
Folge-Slice **DESIGN-GAPS-SWEEP-002** geschlossen:

- **Statusfarben:** Neue theme-bewusste Utilities `text-status-success|warning|error|info`
  (`@theme inline` → `--status-*-hsl`; `:root` = 700er-Stufe für hellen Grund,
  `.dark`/`.theme-warehouse` = 500er-Stufe; eigener Namensraum ohne Kollision mit
  Meridian-`--color-success`). Mechanischer Sweep `text-(green|emerald|red|amber|yellow|
  orange)-(500|600)` → Status-Utilities über 298 Dateien in `src/`.
  **axe-E2E danach 8/8 Kernrouten grün** (vorher 5/8).
- **Portal-Aliase:** 5 fehlende Einträge ergänzt (`empfehlungen`, `lohndienste`,
  `onboarding`, `preisspiegel`, `whatsapp-simulator`) → `check:routing-integrity` grün
  (17 Portal-Aliase, 649 gesamt).
- **Vitest-Harness:** `renderPage()`-Wrapper mit `QueryClientProvider` in
  `universal-sales-order-pilot.test.tsx` + `universal-customer-mask-pilot.test.tsx`
  (CalendarRenderer nutzt `useQuery`) → **Vitest 88/88 Dateien, 371 grün**.
- **Alt-AppShell:** `components/layout/AppShell.tsx` (0 Referenzen) entfernt.

Validierung nach dem Sweep: tsc ✅ · eslint 0 Fehler ✅ · Vitest 371/371 ✅ ·
Build 45,8 s ✅ · routing-integrity ✅ · navigation-targets 898 ✅ · axe 8/8 ✅.

Restrisiko des Sweeps: `text-red-500` u. ä. auf lokal dunklen Flächen im Light-Mode
(seltene Spezialpanels) wird minimal dunkler dargestellt; `dark:`-Overrides blieben
unangetastet und greifen weiterhin.

## 7b. Update 2026-07-14 — Register-Rollout (DESIGN-ROLLOUT-REGISTER-003)

Rollout-Plan-Positionen 1, 2, 3 und 6 sind umgesetzt:

- **Universal Mask Runtime + ObjectPage:** `LazyTabs` reicht die Tab-Variante durch;
  `UniversalMaskRenderer` und die Mask-Builder-`ObjectPage` rendern `variant="register"` —
  **alle nativen SD-Masken und alle Konfigmasken erben den Belegregister-Look** ohne
  Konfigurationsänderung (das starre `grid-cols-4` der ObjectPage entfiel).
- **Belegketten-Köpfe vereinheitlicht:** Auftrag (`OrderEditorLegacyPage`), VK-Lieferschein,
  EK-Lieferschein und Ernte-Annahmebeleg tragen dieselbe Belegkopf-Registerleiste.
  Dabei behoben: zwei getrennte `TabsList`-Reihen pro Belegkopf zerschnitten die
  Pfeiltasten-Navigation (Arrow-Keys wechselten nur innerhalb je einer 4er-Reihe).
- **KIM-Rest:** SalesDocumentsPanel-Kategorien sind bewusst **kein** Register, sondern eine
  `aria-pressed`-Toggle-Gruppe (Filter über einer gemeinsamen Tabelle — Struktur ist
  Information); Forderungsspalte mit `tabular-nums`. InformationPanel-Sektionen werden nur
  programmatisch gesetzt (kein Umschalter vorhanden).
- **Bewusst unverändert:** Ansichtsumschalter regulärer Seiten (compliance, fibu, pos,
  inventory-reports u. a.) behalten den Segmented-Look gemäß Regel R1.

Validierung: Vitest 371/371 ✅ · tsc ✅ · eslint 0 Fehler ✅ · Build 19,0 s ✅ · axe-E2E 8/8 ✅.

## 7c. Update 2026-07-14 — Density + Finanz-Audit (DESIGN-ROLLOUT-DENSITY-FIN-004)

Rollout-Plan-Positionen 4 und 5:

- **Lager/Disposition dense:** `data-density="dense"` am Maskenwurzel von
  `lager/bestandsuebersicht`, `lager/lagerbewegungen`, `lager/kommissionierung`,
  `disposition/liste` — Tabellenzeilen 32 px über den zentralen Scope
  (`ui/table.tsx` konsumiert `--table-row-height`). Weitere Lager-Masken folgen
  demselben 1-Zeilen-Muster bei Bedarf.
- **Finanzen-Mutation-Audit:** `zahlungslauf-kreditoren.tsx` und
  `lastschriften-debitoren.tsx` erfüllen die Mask-Builder-Action-Invariante bereits
  (`useMaskActions` + `loadingActionKey` an ObjectPage) — kein Handlungsbedarf.
  **Befund:** `mahnwesen/mahnlauf.tsx` sendet beim Wizard-Abschluss keine
  Backend-Mutation (`onFinish` navigiert nur), obwohl der Erfolgstext Versand
  suggeriert — fachliches Gap, braucht einen eigenen Slice mit API-Vertrag
  (hier bewusst keine Geschäftslogik erfunden).

## 8. Verbleibende Risiken & Folgearbeiten

> **Stand nach Slices 002–004:** Punkte 1–4 sind erledigt (1 → 7b, 2/3/4 → 7a);
> Rollout-Prios 1/2/3/6 → 7b, Prios 4/5 → 7c. **Offen bleiben:** Punkt 5
> (Chart-Palette aus Tokens — eigener Slice mit visueller QA je Chart), Punkt 6
> (`patterns/`-Konsolidierung — Großvorhaben im Zuge der Universal-Mask-Promotion),
> Punkt 7 (Token-Quellen — Koordination mit Codex/TW4-Dateibesitz nötig), der
> `text-*-400`-Nachzug (dunkle Spezialflächen, gezielt statt mechanisch) sowie neu:
> **Mahnlauf ohne Backend-Mutation** (fachlicher Slice mit API-Vertrag, siehe 7c).

1. **Weitere Eigenbau-Reiterleisten** (z. B. `SalesDocumentsPanel`-Kategorien,
   `InformationPanel`-Sektionen, Sidebar-Alphabetregister) auf die Register-/Default-Variante
   umstellen.
2. **`components/layout/AppShell.tsx`** (Altbestand, ungenutzt) nach Bestätigung entfernen.
3. **Portal-Alias-Lücken** (5) im Portal-Workstream schließen.
4. **Statusfarben-Sweep (WCAG-kritisch, eigener Slice):** 154+ Treffer `text-green|red|amber-*`
   in 40+ Seiten; verursacht die drei roten axe-Kernrouten (`/agrar`, `/finance`, `/lager`,
   Kontrast 2,99:1). Saubere Lösung: theme-bewusste Utilities `text-status-success|warning|
   error|info` über `@theme inline` + `:root`/`.dark`-Indirektion (Vorsicht: keine
   Namenskollision mit Meridian-`--color-success` — TW4-Zirkularitätsfalle, vgl. Commit
   `8a6f6b945`), danach mechanischer Sweep. Kein Drei-Dateien-Schnellfix, der der
   Token-Lösung vorgreift.
5. **Arbitrary-Value-Sweep** über `src/pages/` (69 Treffer): Chart-Farben auf eine zentrale
   Recharts-Palette aus Tokens heben, UI-Arbitraries auf Utilities.
6. **`patterns/` vs. `mask-builder/`**-Konsolidierung im Zuge der Universal-Mask-Promotion.
7. **Token-Quellen konsolidieren:** `index.css`-`:root`-Brandtokens vollständig in
   `primitives.css`/Themes aufgehen lassen.

## 9. Rollout-Plan (priorisiert)

| Prio | Bereich | Maßnahme |
|------|---------|----------|
| 1 | Restliche KIM-Teilkomponenten | Kategorien-/Sektions-Umschalter auf Tabs-Varianten; Tabellen-Zahlenspalten auf `tabular-nums` |
| 2 | Verkaufs-Belegkette (`lieferschein-erfassung`, Auftrag, Rechnung) | Register-Variante für Kopf-Tabs (KUNDE/LIEFER-ANSCHR. …) → Gewohnheits-Prinzip `docs/MASKEN.md` wird zum ersten Mal technisch erzwungen |
| 3 | Einkauf (Bestellung → Wareneingang → Rechnung) | identisches Registerlayout wie Verkauf (Belegfolgen-Konsistenz) |
| 4 | Lager/Disposition | Density `dense` konsequent; VirtualDataTable-Schwellen prüfen |
| 5 | Finanzen (OP-Listen, Mahnwesen) | Mutation-Lifecycle-Audit der Massenaktionen; Statusfarben-Audit |
| 6 | Mask-Builder-`ObjectPage` | Register-Variante als Standard-Tab-Look der ObjectPage → alle nativen SDs erben den Look konfigurationsfrei |

Jede Welle als eigener Slice (Claim → YAML → Code → Abschluss) gemäß AI-Harness-Governance.

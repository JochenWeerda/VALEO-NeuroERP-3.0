# UX-Konzept: Schließen, Navigation, Startseite, Modul-Toolbar

## 1. Schließen einer Seite

**Regel:** „Schließen“ führt immer zu einem definierten Ziel pro Modul/Kontext.

- **Detail-/Erfassungsmaske:** Schließen → Modul-Liste oder Modul-Start (z. B. `/agrar/ernte`, `/einkauf/lieferschein-liste`).
- **Liste ohne übergeordnete Ebene:** Schließen → Modul-Dashboard oder Startseite (`/`).
- **Einheitliche Umsetzung:** Jede Maske kennt ein `closeTarget` (z. B. aus Modul-Konfiguration oder Props). Kein generisches `navigate(-1)` ohne Fallback, da das Ziel sonst unklar ist (z. B. externe Herkunft → Verlust der App-Kontexts).

**Technik:** `ModuleToolbar` bzw. Modul-Layout liefert `closeTarget`; Buttons „Schließen“/„Abbrechen“ navigieren dorthin. Optional: `useUnsavedChanges` vor Navigation prüfen (siehe unten).

---

## 2. Speichern / Verwerfen beim Verlassen

**Regel:** Beim Verlassen einer Maske mit ungespeicherten Änderungen wird gefragt: **Speichern**, **Verwerfen** oder **Abbrechen** (im Modul bleiben).

- **Wo:** Beim Klick auf Schließen/Zurück/Abbrechen, beim Wechsel per Sidebar/Nav und (optional) beim Browser-Tab schließen/Refresh.
- **Technik:**
  - React: `useBlocker` (react-router-dom) oder eigener „blocker“, der bei Programmnavigation (z. B. `navigate(closeTarget)`) einen Dialog anzeigt.
  - Dialog: drei Buttons – „Speichern“ (speichern + dann navigieren), „Verwerfen“ (navigieren ohne Speichern), „Abbrechen“ (Dialog schließen, bleiben).
  - Optional: `beforeunload` für Tab-Close/Refresh (nur Hinweis, kein eigener Dialog).

**Komponenten:** `useUnsavedChanges(hasDirtyState, options)` + `LeaveConfirmDialog`. Masken setzen `hasDirtyState` aus Form-State; bei blockierter Navigation wird der Dialog geöffnet.

---

## 3. Vor/Zurück innerhalb eines Moduls

**Regel:** Wo fachlich sinnvoll (z. B. Beleg zu Beleg, Datensatz zu Datensatz), gibt es eine einheitliche Vor/Zurück-Logik.

- **Umsetzung:** Entweder in der **Modul-Toolbar** („Nächster“/„Vorheriger“) mit Modul-spezifischer Logik (z. B. ID-Liste, Reihenfolge aus Liste) oder in der jeweiligen Maske (z. B. Lieferschein „vorheriger/nächster“).
- **Modul-Toolbar:** Ein Ort für „Zurück“, „Schließen“, „Startseite“, optional „Vor“/„Zurück“ (wenn die Maske sie anbietet).

---

## 4. Zurück zur Startseite

**Regel:** Ein klares, immer sichtbares Element führt zur Startseite (Route `/` = Start-Dashboard).

- **Umsetzung:**
  - **Logo:** Sidebar und (falls sichtbar) TopBar: Logo klickbar → Link zu `/`.
  - **TopBar:** Optional zusätzlicher Link/Button „Startseite“ oder „Dashboard“ (Icon Home) für bessere Auffindbarkeit.
- **404-Seite:** Button „Zur Startseite“ verweist auf `/` (bereits „Zum Dashboard“; einheitlich als „Zur Startseite“ bezeichnen, wenn die Startseite das Dashboard ist).

---

## 5. 404-Fehler vermeiden

**Ursachen:** Falsche oder veraltete Links (`to`/`href`/`navigate()`), fehlende Routen, Tippfehler in Pfaden.

**Maßnahmen:**
- Alle programmatischen Navigationen (`navigate(...)`) und alle `to=`/`href=` gegen die tatsächlichen Routen (inkl. `route-aliases.json` und Auto-Routen) prüfen.
- Wo möglich zentrale Pfad-Konstanten oder `resolveRoutePathFromModule` nutzen statt Hardcodierte Strings.
- 404-Seite: klare Hinweise und „Zur Startseite“-Button (Link zu `/`).

---

## 6. Durchgängige Toolbar pro Modul (optional Autohide)

**Regel:** Pro Modul eine einheitliche **Modul-Toolbar** mit festen Aktionen.

- **Inhalte (minimal):**
  - **Zurück:** Zur vorherigen Ebene (Liste/Übersicht), nicht Browser-Back.
  - **Schließen:** Wie unter 1. (definiertes Ziel).
  - **Startseite:** Link zu `/`.
- **Optional:** Vor/Zurück (Nächster/Vorheriger), wenn die Maske das anbietet; weitere Modul-Aktionen.
- **Optional Autohide:** Beim Scrollen nach unten ausblenden, beim Scrollen nach oben einblenden (z. B. mit `IntersectionObserver` oder Scroll-Delta), um Platz zu sparen und Fokus auf Inhalt zu legen.

**Platzierung:** Unter der TopBar, oberhalb des Seiteninhalts; entweder im AppShell/Layout pro Modul oder als feste Komponente in den Modul-Masken (z. B. `ModuleToolbar`).

**Technik:** Wiederverwendbare Komponente `ModuleToolbar` mit Props wie `backTarget`, `closeTarget`, `showHome`, `onPrev`/`onNext` (optional), `autohide` (optional). Integration in DashboardLayout oder pro Modul-Route.

---

## Umsetzungsstatus (Kurz)

| Thema                    | Status   | Anmerkung |
|--------------------------|----------|-----------|
| Schließen-Ziel pro Modul | Konzept  | In Masken schrittweise `closeTarget` nutzen |
| Speichern/Verwerfen      | umgesetzt| `useUnsavedChanges` + `LeaveConfirmDialog` (siehe unten) |
| Vor/Zurück Modul         | Konzept  | In ModuleToolbar oder Masken |
| Startseite-Link          | umgesetzt| Logo → `/`, TopBar „Startseite“ (Home-Icon) |
| 404-Vermeidung           | laufend  | Link-Check, NotFound → „Zur Startseite“ |
| Modul-Toolbar            | umgesetzt| Komponente `ModuleToolbar`; eingebaut in allen relevanten Erfassungs-/Stamm-/Detail-Masken (u.a. Buchungserfassung, Bankkonten/Debitoren/Kasse/Mahnwesen/Lastschriften/Dunning/Zahlungslauf, Einkauf Lieferschein/Anfrage/Auftragsbestaetigung, Verkauf Lieferschein/Kunde-neu, Agrar Ernte/Saatgut/Dünger/PSM-Abgabe, Futtermittel/Charge-Stamm, CRM Kontakt/Aktivität/Segment, Lager Auslagerung, Annahme LKW/Qualität, Verladung LKW-Beladung, Compliance PCN, Personal Schulung, Förderung Antrag, Finance Invoice-Form, Sales Delivery-Editor) |

---

## Verwendung der umgesetzten Bausteine

### Startseite
- **Sidebar:** Logo klickbar → Link zu `/`.
- **TopBar:** Home-Icon (Desktop) und Logo (Mobile) → Link zu `/`.
- **404-Seite:** Primärer Button „Zur Startseite“ → `/`.

### ModuleToolbar
- **Datei:** `packages/frontend-web/src/components/navigation/ModuleToolbar.tsx`
- **Props:** `backTarget`, `closeTarget`, `showHome`, `onPrev`/`onNext`, `prevDisabled`/`nextDisabled`, `autohide`, `title`, `actions`.
- **Beispiel:** In einer Erfassungsmaske oben einbinden, z. B.  
  `<ModuleToolbar backTarget="/agrar/ernte" closeTarget="/agrar/ernte" title="Ernte erfassen" />`

### Ungespeicherte Änderungen (Speichern/Verwerfen)
- **Hook:** `useUnsavedChanges(hasDirtyState)` aus `@/hooks/useUnsavedChanges` (nutzt React Router `useBlocker`).
- **Dialog:** `LeaveConfirmDialog` aus `@/components/LeaveConfirmDialog` mit Props `blocker`, `onSave`, optional `title`/`description`.
- **Beispiel in einer Maske:**
  ```tsx
  const blocker = useUnsavedChanges(formState.isDirty ?? false)
  return (
    <>
      <LeaveConfirmDialog blocker={blocker} onSave={handleSubmit} />
      {/* Seiteninhalt */}
    </>
  )
  ```
- Beim Verlassen (Link/Navigation) erscheint der Dialog mit **Speichern** (führt `onSave` aus, dann Navigation), **Verwerfen** (Navigation ohne Speichern), **Abbrechen** (bleiben).

Dieses Dokument dient als Referenz für zukünftige Anpassungen und für die schrittweise Einführung der Modul-Toolbar und der Schließen-/Verlassen-Logik in allen Modulen.

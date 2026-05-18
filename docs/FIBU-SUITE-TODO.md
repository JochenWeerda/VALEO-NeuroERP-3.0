# FIBU SUITE – TODOs für Masken-Design & Funktionsumfang (Cursor)

> Ziel: Die zentralen WinFibu-Funktionen als **FIBU SUITE** neu entwerfen (UI/UX + notwendige Backend-/Workflow-Anforderungen), basierend auf den gezeigten Masken (Ribbon + Filterleiste + Baum links + Monats-Grid) und der Funktionsbeschreibung.

---

## 0) Scope & Leitplanken

- **Integriert**: Gemeinsame Datenbank mit **VALEO NeuroERP** bzw. **VALEO ERP** (Single Source of Truth), aber **optional standalone**.
- **GoBD/Revision**: Protokollierung, Nachvollziehbarkeit, Berechtigungen, Exportfähigkeit (Prüferzugriff).
- **Prinzip**: Draft/Workflow-gesteuert, keine „stillen“ Änderungen, klare Status.
- **UI-Pattern**:
  - Ribbon/Toolbar (oben)
  - Filter/Parameterzeile (Mandant, Zeitraum, Berichtstyp, Kostenstelle …)
  - Navigation/Gliederung links (Kontenbaum/BWA-Struktur)
  - Haupttabelle rechts (Monate/Spalten, Summen, Vorjahr)
  - Footer (Summen, Druck/Export)

---

## 0.1) Ribbon-Band: Zeitgemäßheit und Empfehlung

**Frage:** Passt das Ribbon-Band in der FIBU Suite noch (noch zeitgemäß)?

### Aktueller Einsatz (zwei Ebenen)

1. **Suite-Ebene** (`FibuSuiteLayout.tsx`): Ein **horizontaler Navigationsstreifen** mit „START“ + Links zu allen FiBu-Masken (Hauptbuch, Debitoren, Kreditoren, Buchungsjournal, …). Das ist faktisch eine **Tab- bzw. Modul-Navigation**, kein klassisches Office-Ribbon.
2. **Masken-Ebene** (z. B. `buchhaltungsuebersicht.tsx`, `monatswerte.tsx`): **Office-artiges Ribbon** mit Registerkarten (DATEI, ALLGEMEIN, POSTBEARBEITUNG, SCHNITTSTELLEN, ABSCHLUSS, AUSWERTUNGEN, FENSTER/REGISTER). Pro Register Buttons (Drucken, Export, BWA, Bilanz/GuV, Umbuchen, …). Entspricht der WinFibu-Referenz.

### Bewertung

| Aspekt | Ribbon (mask-level) | Moderne Alternative (PageToolbar + Command Palette) |
|--------|----------------------|-----------------------------------------------------|
| **Zeitgemäßheit** | Office-Ribbon (ca. 2007+) ist in Web-ERP kaum noch Standard; Moderne ERP-Oberflächen setzen auf **kontextuelle Page Toolbar** + Overflow, keine Registerbänder. | Moderne SaaS: eine schlanke Toolbar pro Seite, wenige Primäraktionen, Rest im ⋯-Menü oder per Ctrl+K. |
| **Platz** | Zwei Zeilen (Register + Gruppen) pro Maske kosten vertikalen Platz; auf kleinen Viewports starker Druck. | Eine kompakte Toolbar-Zeile, mehr Platz für Inhalt und Grid. |
| **Kontext** | Viele Register zeigen immer dieselben oder ähnlichen Aktionen (Export, BWA, Bilanz) – **redundant** über Masken. | Aktionen nur für die aktuelle Maske/kontextabhängig; weniger Wiederholung. |
| **Mobile / Responsive** | Ribbon mit vielen Tabs ist auf schmalen Screens schwer nutzbar (Overflow, Verstecktes). | PageToolbar + Overflow + Command Palette (Ctrl+K) ist responsive bereits im Projekt vorgesehen (`orders-modern.tsx`). |
| **Konsistenz im Produkt** | Andere Bereiche (z. B. Sales „modern“) nutzen ausdrücklich **kein Ribbon** (`PageToolbar`, „KEIN Ribbon“, spart Platz). | Ein einheitliches Pattern (PageToolbar + Sidebar + Command Palette) über alle Domänen. |

**Fazit:** Das Ribbon auf **Masken-Ebene** (DATEI/ALLGEMEIN/AUSWERTUNGEN/…) ist **nicht mehr zeitgemäß** im Sinne von modernem Web-ERP: Es kostet Platz, wirkt redundant und weicht vom bereits eingeführten Pattern (PageToolbar, Command Palette) ab. Die **Suite-Navigation** (START + Masken-Links) ist dagegen ein klares, nützliches Navigationspattern und kann beibehalten werden (evtl. als „Tab Bar“ oder „Suite-Nav“ bezeichnen, um Verwechslung mit Office-Ribbon zu vermeiden).

### Empfehlung

- **Suite-Ebene:** Beibehalten. Optional: Begrifflichkeit „Ribbon“ durch „Suite-Navigation“ oder „Tab-Leiste“ ersetzen, um Klarheit zu schaffen.
- **Masken-Ebene:** Für **neue und neu zu bauende** FiBu-Masken **kein** Office-Ribbon mehr; stattdessen:
  - **PageToolbar** mit 2–4 Primäraktionen (z. B. Drucken, Export, Aktualisieren) + Overflow-Menü (⋯) für weitere Aktionen,
  - **Command Palette** (Ctrl+K) für Befehle und Navigation,
  - Filter/Parameter in einer **Filterzeile** unter der Toolbar (unverändert sinnvoll).
- **Bestehende Masken** (Buchhaltungsübersicht, Monatswerte, …): Ribbon nicht sofort entfernen (Akzeptanz, Schulung), aber bei **Rebuild oder größeren Refactorings** auf PageToolbar umstellen und in der Design-System-Dokumentation festhalten, dass neuer Standard „PageToolbar + Overflow + Command Palette“ ist.

Damit bleibt die FIBU Suite konsistent mit dem Rest von VALEO (z. B. Sales modern) und mit aktuellen UX-Standards (Web-ERP-Standard, Enterprise Web).

---

## 1) Globale UX/Design-System TODOs

- [ ] **Design System** definieren (Typografie, Abstände, Icons, Tabellenstil, Zustände: hover/selected/disabled)
- [ ] **Ribbon-Komponente** (gruppenweise Buttons, Tooltips, Shortcuts, Overflow) – nur für Legacy-Masken; **Neustandard:** PageToolbar + Overflow + Command Palette (siehe Abschnitt 0.1)
- [ ] **Filterbar-Komponente** (Dropdowns, Zeitraum-Picker, Mandant, Suchfeld, „Aktualisieren“)
- [ ] **Tree/Nav-Komponente** für Konten/BWA-Struktur (expand/collapse, search, select)
- [ ] **DataGrid-Komponente** (frozen columns, sticky header, column resize, export)
- [ ] **Drilldown-Pattern** (Klick in Zahl → Buchungsjournal/Belege)
- [ ] **Status/Feedback**: Toast, Inline-Errors, Ladezustände, „letztes Update“ Anzeige
- [ ] **Barrierefreiheit** (Tastatur, Fokus, Kontraste, Screenreader Labels)
- [ ] **Mehrmandantenfähigkeit** (Mandantenwechsel ohne "State-Leaks")

---

## 2) Maskenliste (Screens) – Priorität

### P0 (MVP)
1. **Cockpit/Dashboard**
2. **Buchungsjournal & Buchungserfassung**
3. **Bank/CAMT.053 Import + Vorkontierung**
4. **OP-Verwaltung (Debitor/Kreditor)**
5. **Mahnwesen (Vorschlag → Versand → Archiv)**
6. **Auswertungen: BWA/BAB/Saldenliste** *(Masken-Rebuild nach Screenshot)*
7. **UStVA (ELSTER)**
8. **E-Banking: Zahlvorschlag + SEPA Export + Mandatsarchiv**
9. **Schnittstellen-Center (Import/Export)**
10. **Stammdaten: Kontenplan, Steuerschlüssel, Kostenstellen**

### P1 (Erweiterung)
11. **Planwerte & Kostenstellen-Controlling**
12. **Anlagen (VALEO Suite Anlagen / Asset Ledger) Integration** (Backlog: AfA-Lauf, Umbuchung/Abgang, Buchwert-/AfA-Reports)
13. **Dokumentenarchiv (Belege, Mahnungen, Protokolle)**

---

## 3) Detaillierte TODOs pro Maske

*(Vollständiger Inhalt wie in der Nutzeranfrage – 3.1 bis 3.9, 4–7.)*

---

## Nachtrag: Laborbuch (Ernteerfassung)

- Maske für das **Laborbuch** (Ernteerfassung) in der Agrar-Domäne – Referenzbild: Laborbuch_Argraspezial (Schnittstellen/Export-Ansicht kann als UI-Pattern übernommen werden).

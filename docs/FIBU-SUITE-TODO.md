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

## 1) Globale UX/Design-System TODOs

- [ ] **Design System** definieren (Typografie, Abstände, Icons, Tabellenstil, Zustände: hover/selected/disabled)
- [ ] **Ribbon-Komponente** (gruppenweise Buttons, Tooltips, Shortcuts, Overflow)
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

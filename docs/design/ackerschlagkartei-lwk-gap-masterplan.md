# Ackerschlagkartei — Gap-Analyse & Masterplan (LWK-Standard)

Stand: 2026-07-13 · Autor: Codex · Fachliche Grundlage: **Benutzerhandbuch
Ackerschlagkartei der Landwirtschaftskammer Niedersachsen** (QS-Acker, Stand 2017)
sowie geltende **Düngeverordnung (DüV 2017/2020)**, **Stoffstrombilanzverordnung (StoffBilV)**
und **Pflanzenschutz-Anwendungsdokumentation (PflSchG / CC)**.

Ziel: die Portal-Ackerschlagkartei vom einfachen Maßnahmen-Logbuch auf den heute von
Landwirtschaftskammer und Praxis geforderten Mindestumfang heben (rechtssichere Dünge- und
Pflanzenschutzdokumentation, Düngebedarfsermittlung, Nährstoff-/Stoffstrombilanz).

---

## 1. IST-Stand (vorhanden)

Datenmodell `app/infrastructure/models/agrar_models.py`, Endpunkte
`app/api/v1/endpoints/portal_feldbuch.py` / `agrar_feldbuch.py`, UI `pages/portal/feldbuch.tsx`.

- **Schlag** (`FeldbuchSchlag`): Name, FLIK, Fläche (ha), Kultur, Vorkultur, Gemeinde/Gemarkung,
  Bodenart, Ackerzahl, Status, GeoJSON-Geometrie.
- **Maßnahme** (`FeldbuchMassnahme`): Datum, generischer Typ (psm/aussaat/ernte/bodenbearbeitung),
  Mittel + Menge/Einheit, behandelte Fläche, Anwender, Quelle (portal/erp), PSM-Auflagen (JSONB),
  Wartezeit, Wind/Temperatur, compliant-Flag, Export-Flag.
- **Maschinen** (`AgrarMaschine`).
- Portal-CRUD, CSV-Export „ackerschlagkartei".

**Bewertung:** guter Rohbau (Schlag + generische Maßnahme + PSM-Wetter/Auflagen), aber ohne
strukturierte Stammdaten, ohne Reinnährstoff-/Bedarfslogik, ohne DüV-Pflichtauswertungen.

---

## 2. SOLL (LWK-Handbuch + heutige Rechtslage)

### Stammdaten (CC-relevant, Voraussetzung für Auswertungen)
- **Düngemittel** mit Reinnährstoffen (N, P₂O₅, K₂O, MgO, S, CaO), Düngerform mineralisch/organisch,
  Preis; org. Dünger mit Nutzbarkeitsfaktor.
- **Pflanzenschutzmittel** mit Wirkstoff(en), Wirkungsbereich (Herbizid/Fungizid/Insektizid/Sonstiges),
  Wartezeit je Kultur, Auflagen (NW/NT/…), Preis.
- **Kulturen** mit N-Sollwert/Düngebedarf, ANDI-Code, Ertragsniveau.
- **Anwender** (Sachkundenachweis) — Pflicht je Dünge-/PSM-Maßnahme (CC/PflSchG).
- **Technik** (Ausbringgeräte).
- **Maßnahmen-Begründungen** (PSM-Notwendigkeit/Schadschwelle, Dropdown).

### Anbauplanung
- Anbauplan je Wirtschaftsjahr, manuell **oder ANDI-Import (XML)**; Schlag-Nr. aus Agrarförderantrag;
  Sammelbuchung; **Jahreswechsel** (Fortführung); Zwischenfrüchte (Aussaat/Verbleib/Menge).

### Schlag-Register (je Schlag)
1. **Aussaat** (Sorte, Termin, Menge; QS-Vorkeimung).
2. **Nmin** (Frühjahr in Bedarf einbeziehen ja/nein; Herbst/Mai nur erfassen).
3. **Bodenuntersuchung** (P/K/Mg/pH, Datum, Versorgungsstufe A–E; QS-Risikoanalyse).
4. **Düngung** — je Maßnahme automatische **Reinnährstoffe** + Düngerkosten; org./min. getrennt;
   Warnung **170 kg N/ha org.** (rote Gebiete strenger).
5. **Düngebedarfsermittlung (DüV)**: Sollwert − Nmin − Zu-/Abschläge (Vorkultur, org. Düngung,
   Ertragsdifferenz) → zulässiger N-Bedarf; kontinuierlich gegen ausgebrachte N fortgeführt.
6. **Pflanzenschutz** — Kostensplit Herbizide/Fungizide/Insektizide/Sonstiges; **Wartezeit-Hinweis**
   vs. geplante Ernte; Begründung; Rand-/Teilbehandlung; Anwender-Pflicht.
7. **Beregnung** (Art, Datum, Wassermenge, Stadium — QS/GLOBALGAP).
8. **Ernte** (Ertrag dt/ha, Qualität, Verkaufserlös, Nebenleistung/Stroh, mehrere Schnitte/Termine).
9. **QS / GLOBALGAP-Zusatzfelder**; **AUM/Umweltmaßnahmen**.
10. **Schlaginfo**: Zusammenfassung + **Direktkostenfreie Leistung** (Erlös − Direktkosten), druckbar.

### Auswertungen
- Übersicht Anbauplan (Schläge; Hauptfrüchte nach Umfang).
- **Nährstoffvergleich / Stoffstrombilanz** (Zufuhr vs. Abfuhr, N-/P-Saldo, StoffBilV).
- Direktkostenfreie Leistung; Dünge-/PSM-Kosten je Schlag/Kultur.
- Export/Druck je Schlag & Bereich.

---

## 3. Wellen (priorisiert; rechtlich Pflichtiges zuerst)

| Welle | Titel | Rechtsbezug | Prio | Aufwand |
|-------|-------|-------------|------|---------|
| **AS-W1** | Düngemittel-Stammdaten + Reinnährstoff-Düngung + 170-kg-N-Grenze | DüV | P0 | L |
| **AS-W2** | Düngebedarfsermittlung (Sollwert/Nmin/Zu-Abschläge) | DüV §3/§4 | P0 | L |
| **AS-W3** | Nährstoffvergleich → Stoffstrombilanz | DüV/StoffBilV | P0 | L |
| **AS-W4** | PSM-Stammdaten + PSM-Doku (Wartezeit-Hinweis, Wirkungsbereich, Begründung, Anwender) | PflSchG/CC | P0 | L |
| **AS-W5** | Nmin + Bodenuntersuchung (P/K/Mg/pH, Versorgungsstufe) | DüV | P1 | M |
| **AS-W6** | Ernte (Ertrag/Qualität/Erlös/Nebenleistung) + Direktkostenfreie Leistung | betriebswirtschaftlich | P1 | M |
| **AS-W7** | Kulturen-Stammdaten (N-Sollwert, ANDI-Code) + Anbauplan/Fruchtfolge + Zwischenfrüchte | DüV/GAP | P1 | M |
| **AS-W8** | ANDI-Import (XML) + GIS-Schlaggeometrie/Karte | GAP/ANDI | P2 | L |
| **AS-W9** | Beregnung + QS/GLOBALGAP-Zusatzfelder + AUM | Zertifizierung | P2 | M |
| **AS-W10** | Auswertungen/Berichte/Export (Schlaginfo-Druck, Übersicht, Nährstoffbericht-PDF) | Doku | P1 | M |

Empfohlene Reihenfolge: **AS-W1 → AS-W4 → AS-W2 → AS-W5 → AS-W3 → AS-W6 → AS-W7 → AS-W10 → AS-W9 → AS-W8**
(erst die täglich genutzte, rechtssichere Dünge-/PSM-Erfassung, dann Bedarf/Bilanz, dann Ernte/Auswertung,
zuletzt ANDI/GIS).

**Update 2026-07-16:** AS-W1…W10 abgeschlossen. Weiterführung über Lastenheft-Inkremente
unter `docs/specs/agrar/` — Slice `ACKER-INK1-GAPS-008` (Arbeitskontext, Schlaginfo,
Jahreswechsel, Sammeldüngung) testgetrieben umgesetzt.

---

## 4. Leitprinzipien

- **Rechtssicherheit vor Komfort**: DüV-/PflSchG-Pflichtfelder sind harte Validierungen, keine Optionen.
- **Stammdaten einmal, Auswahl überall** (LWK-Muster: nur betriebseigene Mittel in Folgelisten).
- **Automatische Ableitung**: Reinnährstoffe/Kosten aus Stammdaten, Bedarf/Bilanz aus Maßnahmen —
  keine Doppeleingabe.
- **Vertikaler Agrarhandel-Nutzen**: Übernahme aus VALEO-Lieferscheinen/Dienstleistungen bleibt Quelle
  (`quelle='erp_*'`), Portal ergänzt Selbsterfassung.
- Kanonisches Datenmodell zuerst; jede Welle als AI-Harness-Slice (Claim→YAML→Code→Abschluss).

---

## 5. Nicht-Ziele / Grenzen
- Keine amtliche ANDI-/Meldeportal-Zertifizierung; ANDI-Import ist Datenübernahme, keine Antragstellung.
- Regionale Sollwert-/Nmin-Tabellen sind konfigurierbar (LWK-Landesdaten), nicht hart kodiert.
- Rote-Gebiete-Logik als Flag/Parameter, Geodaten-Verschnitt ist Folgeausbau.

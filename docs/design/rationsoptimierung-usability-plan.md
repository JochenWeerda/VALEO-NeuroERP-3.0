# Optimierungsplan Rationsoptimierung Milchkühe — Usability & Nutzen

Stand: 2026-07-10 · Autor: Codex · Bezug: `/portal/rationsoptimierung`,
Service `rationsoptimierung/`, Frontend `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`

Vergleichsmaßstab: **Fodjan smart feeding**. Ziel ist **kein 1:1-Nachbau**, sondern die
Übernahme der Einfachheit und der durchdachten Bedien-Kleinigkeiten bei Erhalt unserer
fachlichen Tiefe (GfE-2023, HiGHS-Solver, DLG-2025-Daten).

Wissensgrundlage: `docs/futterwerte_dlg_2025_gfe2023.md` und Paperless-Dokument
„Rationsoptimierung Wissensbasis Fodjan+DLG 2025 (2026-07-10)".

---

## 1. Ausgangsbefund

**Fachlich sind wir stark, teils stärker als Fodjan.** Vorhanden: Wizard→Workbench→Review,
Grundfutterleistung (Milch aus Energie/Protein), Weide-Risiko, Konzentrat-Abrufstaffel,
Misch-/Fütterungsprotokoll, DLG-2025-Datenbank, GfE-2023-Solver.

**Formeln sind auf aktuellem Stand** (verifiziert): GfE-2023-ME-System korrekt umgesetzt,
Futterwerte exakt aus DLG 2025 (Stichprobe Ackerbohne MEFAN1/SIDP deckungsgleich).

**Das Defizit ist Einfachheit und Zugänglichkeit**, gemessen an Fodjan:
1. **Kein TS/Frischmasse-Umschalter** am Mengen-Eingabefeld — Fodjans größte Einzelstärke.
2. Zielsteuerung über **5 abstrakte Prioritäts-Schieberegler** statt benannter
   Intent-Vorschläge mit sofortigem Vorschau-Delta.
3. **Kein persistentes Live-Kennzahlen-Trio** (Kosten/IOFC/Gesundheit) beim Editieren.
4. **Keine echte Mobile-/Tablet-Ansicht** (Grund-Responsive vorhanden, aber die dichte
   Desktop-Workbench ist am Handy schwer bedienbar) — Fodjan ist app-first.
5. Fachliche Reserve ungenutzt: DLG-2025 liefert **sid-Aminosäuren** und **RMD (ruminale
   N-Bilanz)** je Futtermittel — wir bilanzieren bisher nur sidP-Menge.

---

## 2. Leitprinzipien

- **Einfachheit als Default, Tiefe auf Abruf** (Progressive Disclosure). Landwirt sieht
  wenig; Berater klappt „Feinsteuerung" auf.
- **Am Eingabefeld entscheiden, nicht im Einstellungsmenü** (TS/FM-Toggle direkt an der
  Zeile, wie Fodjan).
- **Benannte Absichten statt abstrakter Gewichte** („Günstiger", „Mehr Milch",
  „Weniger Stickstoff", „Gesünder") mit Vorschau-Delta vor Übernahme.
- **Kennzahlen immer sichtbar** beim Rechnen (Kosten · IOFC · Futtergesundheit).
- **Mobil zuerst dokumentieren, am Desktop optimieren** (Rollentrennung wie App vs. Pro).
- Keine UI-Logik außerhalb des Designsystems; Mask-Builder-Muster wo möglich.

---

## 3. Maßnahmen (priorisiert)

### P0 — Schnelle, hohe Wirkung (Sprint 1–2)

**M1. TS/Frischmasse-Umschalter an der Rationszeile**
- Toggle-Chip `kg TM ⇄ kg FM` pro Zeile + globaler Master-Toggle für die ganze Ration
  (unten rechts, wie Fodjan).
- Umrechnung über `dm_frac` je Futtermittel (bereits im Datenmodell: `buildFeedDmById`).
  Eingabe in FM → intern kg TM für Solver; Anzeige folgt dem Toggle.
- Persistenz der Einstellung (localStorage, analog `LS_FEED_SELECTION`).
- Akzeptanz: Wechsel FM↔TM rechnet Werte konsistent um, Solver-Ergebnis unverändert;
  Y-Achse/DMI-Anzeige folgt dem Modus.

**M2. Benannte Intent-Vorschläge mit Vorschau-Delta**
- Aus den 5 Schiebereglern werden 5 Buttons mit fester `objective_strategy`-Ableitung
  (Mapping existiert: `deriveObjectiveStrategy`): **Günstiger · Mehr Milch · Weniger
  Stickstoff · Gesund & Günstiger · Gesünder**.
- Jeder Button rechnet im Hintergrund und zeigt **vor Übernahme** das Delta
  (Kosten, IOFC, Milch, Futtergesundheit) — „Vorschlag übernehmen" oder verwerfen.
- Schieberegler bleiben unter „Feinsteuerung" für Berater erhalten.
- Akzeptanz: ein Klick erzeugt einen Vorschlag inkl. sichtbarem Delta; Übernahme
  ist ein zweiter, bestätigter Schritt (Mutation-Lifecycle-Invariante: Guard + Delta + Freigabe).

**M3. Persistentes Kennzahlen-Trio in der Workbench**
- Sticky-Leiste (oben/rechts, mobil unten fix): **Kosten/Kuh/Tag · IOFC · Futtergesundheit**
  mit Ampel (grün/gelb/rot), live bei jeder Mengenänderung.
- Reuse vorhandener KPI-Kacheln; nur Sticky-Positionierung + Ampellogik ergänzen.

### P1 — Mobile Tauglichkeit (Sprint 3–4)

**M4. Mobile Dokumentationsansicht („VALEO-App-Modus")**
- Reduzierte Route/Ansicht für Endkunden: aktive Ration ansehen, „jetzt füttern",
  Ist-Mengen erfassen (nur aufgenommene Menge, Rest automatisch) — Fodjan-App-Analogon.
- Kein Solver-Editieren am Handy; Optimierung bleibt Tablet/Desktop.
- Umsetzung: eigener schlanker View + Breakpoint-Weiche, kein neuer Datenpfad.

**M5. Tablet-Workbench-Layout**
- Umbruch der 3-Spalten-Workbench in gestapelte Karten mit Tab-Wechsel
  (Tabelle | Kennzahlen | Hinweise) bei Tablet-Breite; horizontale Scroll-Container
  für Tabellen (`overflow-x` bereits vorhanden, konsequent kapseln).

### P2 — Fachlicher Mehr-Nutzen aus DLG 2025 (Sprint 4–6)

**M6. Aminosäuren-Bilanzierung (sidLys / sidMet)**
- DLG-2025-Felder `SIDLYSFAN1`, `SIDMETFAN1` in Loader (`dlg_merged_csv`) übernehmen.
- Bedarf/Restriktion + Kennzahl „sidLys:sidMet ≈ 3:1" ergänzen — bewertet Protein**qualität**
  statt nur -menge (hebt uns über Fodjan hinaus).

**M7. Ruminale N-Bilanz (RMD) als eigene Kennzahl + „Weniger Stickstoff"-Intent**
- `RMDFAN1` je Futtermittel als N-Effizienz-Kennzahl und optionale Restriktion;
  speist M2-Intent „Weniger Stickstoff" fachlich exakt.

**M8. Mineralbilanz + DCAB exakt aus DLG 2025**
- Ca/P/Na/Mg/K/S und DCAB je Futtermittel aus DLG-Tabelle statt Näherung;
  DCAB-Steuerung besonders für Trockensteher-Gruppe.

### P3 — Komfort (fortlaufend)

- **M9.** Ration teilen (PDF/Link an Landwirt) — Review-Schritt existiert, Export ergänzen.
- **M10.** Bestandsbezug-Icon (Stall-Symbol) für nicht-inventarisierte Futtermittel.
- **M11.** „Letzte Ration kopieren" / Vorlagen als Startpunkte statt leerer Maske.

---

## 4. Umsetzungsreihenfolge & Slices

| Slice | Inhalt | Prio | Aufwand |
|-------|--------|------|---------|
| RATIONS-UX-TSFM-001 | M1 TS/FM-Umschalter | P0 | S |
| RATIONS-UX-INTENT-002 | M2 Intent-Vorschläge + Delta | P0 | M |
| RATIONS-UX-KPI-003 | M3 Kennzahlen-Trio sticky | P0 | S |
| RATIONS-UX-MOBILE-004 | M4 Mobile Doku-Ansicht | P1 | M |
| RATIONS-UX-TABLET-005 | M5 Tablet-Layout | P1 | M |
| RATIONS-SCI-AA-006 | M6 sid-Aminosäuren | P2 | M |
| RATIONS-SCI-RMD-007 | M7 RMD/N-Bilanz | P2 | S |
| RATIONS-SCI-MIN-008 | M8 Mineral/DCAB exakt | P2 | M |

Jeder Slice nach AI-Harness-Workflow: Claim → YAML → Code → Abschluss
(vgl. `docs/agent-ops/`). Frontend-Änderungen halten Mutation-Lifecycle- und
Async-Handler-Invarianten aus `CLAUDE.md` ein.

---

## 5. Erfolgsmessung

- **TS/FM-Umschalter** in Nutzungstest ohne Erklärung bedienbar (Landwirt-Proband).
- Rationsanpassung **mit ≤ 3 Klicks** vom Ziel zum übernommenen Vorschlag (M2).
- Kern-Workflow **auf Tablet vollständig** ohne horizontales Body-Scrollen.
- Fachlich: A­S- und N-Bilanz erscheinen als Kennzahl; DLG-2025-Mineralwerte statt Näherung.

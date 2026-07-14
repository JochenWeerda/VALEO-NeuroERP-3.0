---
title: Fuetterungsberatung Experience Architecture
type: design
audience: [produkt, fachlich, ux, entwickler, qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-14
version: 1.0.0
---

# Fuetterungsberatung Experience Architecture

## Entscheidung in einem Satz

VALEO nutzt eine eigenstaendige hybride Aufgabenarchitektur: Native Meridian-
Masken tragen Orientierung, Worklists, Lebenszyklus und Controlling; nur die
gleichzeitige Bearbeitung einer mathematischen Ration bleibt ein spezialisierter,
bei Bedarf geladener Facharbeitsplatz.

## Offene Bewertung der bestehenden Spezialmaske

Die bisherige Portalroute exportierte dieselbe 242-kB-TSX-Datei wie die interne
Expertenroute. Darin waren Dashboard, Wizard, Solver-Workbench, Diagnose, Review,
Mischprotokoll und Controlling als lokaler View-Automat gekoppelt. Das bot hohe
Fachtiefe, machte aber jede Rolle mit derselben Komplexitaet, demselben Bundle und
derselben Navigation bekannt. Statische Tiergruppen und eine eigene Rohfarbpalette
verstaerkten die Abweichung vom produktweiten Laufzeitvertrag.

Die Spezialmaske ist deshalb kein Zielbild. Sie bleibt vorlaeufig nur fuer jene
Interaktion erhalten, bei der Rationszeilen, harte Grenzen, Solverzustand,
Naehrstoffbilanz und Vorschau-Delta gleichzeitig sichtbar sein muessen.

## Variantenvergleich

Bewertung: 1 schlecht, 5 sehr gut. Wartbarkeit und Fehlersicherheit sind doppelt
gewichtet, weil fachliche Grenzwerte und Freigaben sicherheitsrelevant sind.

| Kriterium | Monolith behalten | Alles generisch | Hybrid | Gewicht |
|---|---:|---:|---:|---:|
| Taeglicher Einstieg und Rollenfokus | 2 | 5 | 5 | 1 |
| Solver-Aufgabeneffizienz | 5 | 2 | 5 | 1 |
| Progressive Disclosure | 2 | 4 | 5 | 1 |
| Fehlerpraevention und Freigabeklarheit | 2 | 4 | 5 | 2 |
| Tastatur, Touch und Barrierefreiheit | 2 | 4 | 4 | 1 |
| Initiale Performance | 1 | 5 | 5 | 1 |
| Zentrale Wartbarkeit | 1 | 5 | 4 | 2 |
| Fachliche Erweiterbarkeit | 3 | 3 | 5 | 1 |
| Gewichtete Summe | 20 | 41 | **47** | 10 |

„Alles generisch“ verliert trotz guter Plattformwerte, weil eine normale
ObjectPage oder Tabelle den engen Rechenzyklus aus Mengeneditierung,
Restriktionsdiagnose und sofortiger Vorschau unnoetig zerlegt. Der Hybrid gewinnt,
wenn seine Grenze technisch erzwungen wird.

## Zielmodell

```text
Portal / Fuetterungsberatung
  -> native ScreenDefinition agrar/feed-advice
  -> RenderPlan
  -> useUniversalMaskRuntime
  -> UniversalMaskRenderer
      -> Ration planen: lazy spezialisierter Solver-Arbeitsplatz
      -> Rationen/Freigaben: native Worklist und ObjectPage
      -> Heute fuettern: schlanker mobiler Ausfuehrungsdialog
      -> Bestand/Analysen: vorhandene native Fachmasken
      -> Controlling: native Cockpit-/Zeitreihenansicht
```

Der Portal-Einstieg liefert maximal sechs aufgabenorientierte Ziele. Keine Rolle
muss zuerst zwischen internen Ansichten wie „Dashboard“, „Diagnose“ oder „Review“
waehlen. Der Expertenarbeitsplatz hat einen stets sichtbaren Rueckweg.

## Eigenstaendigkeit und Rechteabstand

- Keine fremden Texte, Screenshots, Icons, Markenassets oder Seitenstruktur werden
  uebernommen.
- Anforderungen werden als betriebliche Aufgaben formuliert, nicht als Nachbau
  eines Produktmenues.
- Das visuelle System nutzt Meridian/Terra-Semantiktokens statt einer extern
  referenzierten Palette.
- Wissenschaftliche Werte stammen aus den dokumentierten GfE-/DLG-Vertraegen;
  Providerdaten laufen nur ueber lizenzierte, konfigurierbare Connector-Vertraege.

## UX-Abnahmekriterien

- Portalstart rendert ohne Solver-Bundle und mit mindestens 44 px Touch-Zielen.
- Planung ist vom Einstieg mit einer Zielwahl erreichbar; Rueckkehr ebenfalls mit
  einer Aktion.
- Mobile Stallarbeit laedt keinen Solver.
- Lifecycle-Mutationen zeigen Status, Delta, Guard und Ergebnis.
- Keine horizontale Body-Scrollflaeche bei 390 px; Expertentabellen duerfen einen
  lokal begrenzten horizontalen Scrollcontainer besitzen.
- ScreenDefinition, RenderPlan, Runtime und Renderer sind in Tests nachweisbar.

## Migrationsschritte

1. Nativen Einstieg und Lazy-Grenze liefern. **Erledigt in FEED-ADVICE-UX-011.**
2. Persistente Rationsworklist und Rations-ObjectPage liefern.
3. Bestand/Analyse/Preis als Solver-Readiness in Einstieg und Workbench spiegeln.
4. Controlling als eigenstaendige native Aufgabe liefern.
5. Spezialdatei entlang ihrer Fachpanels modularisieren; keine neue Portal- oder
   Lifecycle-Funktion mehr direkt in den Monolithen einbauen.


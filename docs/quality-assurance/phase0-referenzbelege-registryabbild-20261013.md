# Phase 0.7 und 0.9: Referenzbelege, eine Quelle für ScreenDefinitions

Stand: 2026-10-13 · Slice `PHASE0-REFERENZBELEGE-REGISTRYABBILD-20261013` ·
aus [Bestandsprüfung Screen Framework](../design/screen-framework-fiori-gap-analyse.md)

## 0.7 Referenzbelege

`scripts/referenzbelege_anlegen.py --tenant <id> [--apply]` legt einen festen Satz von 17 Belegen an —
über DocFlow, denselben Weg, den die Masken benutzen. Statushistorie, Protokoll, Belegkette und
Buchungen sind echt, nichts ist per SQL gesetzt.

| Bereich | Belege |
|---|---|
| Verkauf | Angebot → Auftrag → zwei Teillieferscheine → Rechnung 1 (gebucht) mit Gutschrift (gebucht), Rechnung 2 (offen) |
| Verkauf, Sonderfälle | Rechnung ohne Steuerschlüssel (Entwurf, nicht buchbar); Rechnung gebucht und storniert |
| Einkauf | Bestellung → zwei Wareneingänge → Eingangsrechnung 1 (gebucht) mit Einkaufsgutschrift (gebucht), Eingangsrechnung 2 (offen) |
| Einkauf, Sonderfälle | Eingangsrechnung ohne Steuerschlüssel (offen, nicht buchbar); Eingangsrechnung gebucht und storniert |

Damit liegen vor: zwei Steuersätze je Richtung, Teilmengen, vier Belegstände (Entwurf, offen, gebucht,
storniert), Gutschriften mit gemindertem offenen Posten und je ein Beleg, den Finance nicht bucht.

- **Wiederholbar:** Jeder Schritt hat einen festen Idempotenzschlüssel. Ein zweiter Lauf legt nichts
  doppelt an und bucht nichts doppelt.
- **Voraussetzungen werden vorab geprüft:** Steuerschlüssel 2, 3, 8, 9 mit Konten, die dem Mandanten
  gehören, dazu 1400 und 1600. Fehlt etwas, nennt das Skript es und legt nichts an.
- Ohne `--apply` zeigt es nur, was es anlegen würde.
- Akteur in Statushistorie und Protokoll ist `referenzbelege`.

**Grenze:** Der Satz deckt keine Berechtigungsfälle ab (zwei Benutzer mit und ohne Preisrecht); das
Preisrecht an der API gibt es noch nicht (BELEG-012). Kunde und Lieferant sind Platzhalter
(`REF-KUNDE`, `REF-LIEFERANT`), keine Stammdatensätze.

## 0.9 Eine Quelle für ScreenDefinitions

Die kanonische Quelle ist die Python-Registry. Daneben stehen 31 Definitionen ein zweites Mal von Hand
in `packages/frontend-web/src/masks/capture-screens.ts`.

### Gemessen

| | Anzahl |
|---|---:|
| Kopien gleich der Quelle | 5 |
| Kopien mit Abweichung | 26 |
| davon nur `performance` fehlt in der Kopie | 14 |
| davon zusätzlich abweichende Aktionen | 11 |
| davon `performance` und `noProcessChainReason` | 1 |

In den elf Masken mit abweichenden Aktionen nennt die Registry Kommando-Weg, Methode und ein Recht; die
Kopie trägt stattdessen `stubReason` („wird lokal erledigt"). Betroffen: Fuhrpark (ausgehende
Dokumente, Fahrzeugstamm, Rechnungen, Terminarten), Logistik (Frachttabellen, Tourenplanung), Personal
(Bewerbungen, Einwilligungserklärungen, Onboarding, Qualifikationen, Schulungen).

### Warum die Kopie nicht einfach erzeugt wird

18 der 21 Seiten, die die Kopie benutzen, zeichnen sie selbst und **ohne Rechte**
(`compileRenderPlanFromScreenDefinition(schema)`). Der Compiler blendet Aktionen mit einem Recht aus,
das nicht gewährt ist. Käme die Kopie aus der Registry, verschwänden in den elf Masken die
Aktionsknöpfe. Die Umstellung ist deshalb je Maske eine eigene Arbeit mit Sichtprüfung — und sie hängt
an einer offenen Frage: Die Rechte der Definitionen (`logistik.tour.create`, `logistics:write`,
`finance.steuerschluessel.write` …) sind keine Rollen der Anmeldung; `useScreenPermissions` kennt sie
nur für Administratoren und einzelne Bereiche. Wie ein Recht einer Definition aus den Rollen folgt,
ist nicht einheitlich geregelt (Identität).

### Was jetzt gilt

- `scripts/generate_screen_registry_snapshot.py [--check]` schreibt das Abbild der 31 Definitionen aus
  der Registry nach `masks/screen-registry.snapshot.json` (ohne Agentenvertrag).
- `tests/test_screen_registry_snapshot.py`: Das Abbild ist aktuell — wer eine ScreenDefinition ändert,
  muss es neu erzeugen.
- `src/__tests__/masks/capture-screens-sync.test.ts`: Jede Kopie wird mit dem Abbild verglichen; zulässig
  sind nur die 26 einzeln benannten Abweichungen. **Eine neue Handkopie oder eine neue Abweichung macht
  den Test rot; eine behobene muss aus der Liste.** Ziel ist die leere Liste.
- Neue Masken lesen die Definition aus der Registry (`useScreenDefinition`) oder aus dem Abbild.

**Nicht umgesetzt:** die Variante als Begriff des Schemas. Sie gehört zu BELEG-020 und setzt den
Belegvertrag (BELEG-010) voraus; ein Feld ohne Wirkung wollte ich nicht einführen.

## Nachweis

- `tests/test_referenzbelege.py`: 3 bestanden gegen `valeo_probe` — ohne Voraussetzungen entsteht
  nichts; der Satz ist vollständig (17 Belege, 8 Buchungen einschließlich zweier Stornobuchungen,
  4 offene Posten, erwartete Stände); ein zweiter Lauf liefert dieselben Belege und ändert keine Zahl.
- `tests/test_screen_registry_snapshot.py`: 2 bestanden.
- Vitest `capture-screens-sync.test.ts`: 33 bestanden. `tsc --noEmit` ohne Befund.

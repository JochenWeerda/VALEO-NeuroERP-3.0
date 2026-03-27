# Workflow Analysis Master Prompt

## Zweck

Dieser Prompt ist die repo-konforme Arbeitsanweisung fuer Codex, Claude Code und vergleichbare Agents zur vollstaendigen Analyse von End-to-End-Workflows in VALEO NeuroERP.

## Rollenbild

Du arbeitest als Kombination aus:

- ERP-Prozessanalyst fuer Landhandel und Agrargenossenschaften
- QA-Testingenieur fuer End-to-End-Workflows
- Senior Software Engineer
- UI-/CRUD-Pruefer im Browser-Use-Kontext

## Ziel

Analysiere die in VALEO NeuroERP implementierten End-to-End-Workflows vollstaendig auf:

- fachliche Vollstaendigkeit
- praktische Einsatzfaehigkeit
- technische Durchgaengigkeit
- UI-/CRUD-Tauglichkeit

## Dokumentationsbasierte Arbeitsweise

Vor jeder Analyse, Umsetzung, UI-Pruefung oder Fehlerbehebung:

1. lies [docs/README.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/README.md)
2. lies die relevanten Dateien unter `docs/project-context/`
3. lies die passende Workflow-Dokumentation unter `docs/workflows/`
4. pruefe den aktuellen Umsetzungsstand in `docs/architecture/process-kernel/STATUS.md` und den relevanten `wave-*/STATUS.md`
5. pruefe bekannte Fehler und QA-Hinweise unter `docs/quality-assurance/`

Wenn Informationen fehlen, unklar sind oder noch nicht umgesetzt wurden:

- triff realistische und fachlich plausible Annahmen auf Basis typischer Landhandels- und Agrargenossenschaftsablaeufe
- kennzeichne Annahmen explizit
- dokumentiere die Luecke

## Hauptaufgabe

Zerlege jeden Workflow in kleinste pruefbare Einheiten (`Cards`) und nutze diese fuer:

- Soll-Ist-Vergleich
- Prozesslueckenanalyse
- Edge-Case-Analyse
- UI-/CRUD-Pruefung
- Browser-Use-Pruefung
- Validierung gegen reale Praxisprozesse

## Verbindliche Umsetzungsregeln

### 1. Dokumentationspflicht

Bei jedem bearbeiteten Prozess muss die zugehoerige Dokumentation geprueft und bei Bedarf aktualisiert werden.

### 2. Standardmaske vor Spezialmaske pruefen

Wenn Luecken in bestehenden Standardmasken sichtbar werden, pruefe zuerst die saubere Erweiterung der Standardmaske.

### 3. Spezialmaske nur bei echtem Bedarf

Wenn eine Standardmaske fachlich, UX-seitig oder wartungstechnisch nicht sinnvoll erweitert werden kann, entwerfe eine Spezialmaske.

### 4. Fehler sofort beheben

Werden bei Analyse, Tests, Browser-Use, CRUD-Pruefung oder Validierung Fehler gefunden, sind diese unmittelbar zu beheben, wenn sie aktuellen oder angrenzenden Prozessfluss beeintraechtigen.

### 5. Dokumentation nach Fehlerbehebung aktualisieren

Nach jeder relevanten Fehlerbehebung:

- Ursache und Loesung dokumentieren
- Umsetzungsstand aktualisieren
- QA-Hinweise oder Regressionstests ergaenzen

## Vorgehen

### 1. Workflow vollstaendig zerlegen

Beruecksichtige:

- fachliche Einzelschritte
- Alternativpfade
- Abbrueche
- Rueckspruenge
- Schleifen
- Teilprozesse
- Sonderfaelle
- automatische und manuelle Uebergaenge
- externe Trigger
- Folgeprozesse

### 2. Soll-Ist-Vergleich

Vergleiche jede Card mit:

- realen Ablaeufen im Landhandel
- typischen Praxisfaellen
- Sonderfaellen
- Abkuerzungen im Tagesgeschaeft
- manuell ausgeloesten Direktprozessen
- vorgezogenen Folgebelegen
- externen Uebernahmen
- Ausnahmen und Korrekturen

### 3. UI-/CRUD-Pruefung

Pruefe pro Card:

- Create
- Read / Suchen / Auffinden
- Update
- Delete oder fachlich zulaessiges Storno / Abschluss / Ruecknahme
- Pflichtfelder
- Validierungen
- Statuswechsel
- Maskenuebergaben
- Sackgassen

### 4. Iterative Selbstpruefung

Arbeite in mindestens drei Durchlaeufen:

1. vollstaendige Zerlegung
2. kritische Nachpruefung auf fehlende Sonderfaelle und Rueckspruenge
3. Praxisschaerfung und Priorisierung

## Ausgabeformat

### A. Workflow-Uebersicht

Kurze Beschreibung des geprueften Workflows.

### B. Vollstaendige Card-Liste

Alle Cards in logischer Reihenfolge.

### C. Mermaid-Diagramm

Mit:

- Startpunkten
- Hauptfluss
- Alternativpfaden
- Schleifen
- Rueckspruengen
- Abbruechen
- externen Triggern

### D. Soll-Ist-Abweichungen

### E. UI-/CRUD-Befunde

### F. Risiken

- kritisch
- hoch
- mittel
- niedrig

### G. Konkrete Empfehlungen

## Kompakter Folgeprompt fuer Einzel-Workflow

```text
Analysiere jetzt ausschliesslich den folgenden Workflow:

[HIER WORKFLOW ODER SEITE EINSETZEN]

Erstelle:

1. vollstaendige Zerlegung in Cards
2. Mermaid-Diagramm
3. Soll-Ist-Abweichungen
4. UI-/CRUD-Pruefung
5. Praxisluecken
6. priorisierte Empfehlungen

Beruecksichtige insbesondere:

- alternative Einstiege
- direkte Spruenge
- Teillieferungen
- Ruecknahmen
- Storno
- Korrekturen
- externe Uebernahmen aus Agrarportal oder Online-Shop
- noch nicht umgesetzte, aber fachlich notwendige Pfade
```

## Vertiefungsprompt

```text
Vertiefe jetzt die Analyse.
Finde fehlende Mikroprozesse, alternative Startpunkte, Rueckspruenge, Schleifen und Sonderfaelle, die im bisherigen Ergebnis noch nicht ausreichend beruecksichtigt wurden.
Zerlege zu grobe Cards weiter.
Pruefe zusaetzlich alle Cards auf praktische Durchfuehrbarkeit in der UI und auf vollstaendige CRUD-Faehigkeit.
Ergaenze das Mermaid-Diagramm entsprechend.
```

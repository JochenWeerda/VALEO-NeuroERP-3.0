# Markdown Governance fuer lebende Projektdokumentation

Stand: 2026-03-19

## Ziel

Dieses Dokument definiert, wie Markdown-Dateien im Repository fachlich eingeordnet werden und welche Dokumenttypen verbindliche Strukturen erhalten.

Es adressiert vor allem die agentenuebergreifende Zusammenarbeit mit mehreren LLMs und Coding-Agents. Ziel ist nicht, alle `.md`-Dateien identisch zu machen, sondern die lebende Steuerungsdoku konsistent, belastbar und maschinenpruefbar zu halten.

## Grundsatz

Nicht alle Markdown-Dateien haben denselben Governance-Bedarf.

Es gibt im Repository mindestens fünf unterschiedliche Dokumentklassen:

1. Steuerungsdokumente
2. Architektur- und Normdokumente
3. Arbeits- und Agentendokumente
4. Modul-/Service-Dokumentation
5. Archiv / historische Reports

Harte Struktur- und Sync-Regeln sollen nur fuer Dokumente gelten, die den laufenden Projekt- oder Lieferstatus steuern.

## Dokumentklassen

### A. Steuerungsdokumente

Diese Dokumente sind Source-of-Truth oder direkt davon abgeleitet:

- `docs/architecture/process-kernel/STATUS.md`
- `docs/architecture/process-kernel/wave-*/STATUS.md`
- `PLAN_GAPS_*.md`
- `docs/architecture/process-kernel/DELIVERY-MAP.md`
- `docs/roadmap/status/*.md`
- `DEVELOPMENT-MAP.md`

Eigenschaften:

- lebend
- statusrelevant
- referenzieren Code, Tests, Gaps und Waves
- duerfen nicht frei-form ohne Struktur veraendert werden

Governance-Level:

- streng

### B. Architektur- und Normdokumente

Beispiele:

- `docs/architecture/**`
- `docs/adr/**`
- `docs/AI-VISION.md`
- `docs/AGENT-INTEGRATION.md`

Eigenschaften:

- konzeptionell
- langlebig
- nicht zwingend release- oder sprintaktuell

Governance-Level:

- mittel

### B2. ADR-Dokumente

Diese Untergruppe umfasst:

- `docs/adr/*.md`

Governance-Level:

- mittel

### B1. Zentrale Referenzdokumente

Diese Untergruppe innerhalb der Architektur- und Normdokumente dient als Einstieg oder Querverweis fuer Menschen und Agenten:

- `README.md`
- `docs/architecture/index.md`
- `docs/AI-VISION.md`
- `docs/AGENT-INTEGRATION.md`

Governance-Level:

- mittel bis streng

### C. Arbeits- und Agentendokumente

Beispiele:

- `swarm/status/**`
- `swarm/handoffs/**`
- `swarm/missions/**`
- `swarm/standups/**`

Eigenschaften:

- operativ
- oft kurzfristig
- mehrere Autoren / Agenten

Governance-Level:

- leicht

### D. Modul-/Service-Dokumentation

Beispiele:

- `packages/**/README.md`
- `services/**/README.md`
- `docs/setup/**`

Eigenschaften:

- technisch
- teilweise onboarding-orientiert
- lokal gueltig fuer ein Modul

Governance-Level:

- mittel

### E. Archiv

Beispiele:

- `docs/archive/**`

Eigenschaften:

- historisch
- nicht Source-of-Truth
- darf inkonsistente Altformate enthalten

Governance-Level:

- minimal

## Source-of-Truth-Regel

Fuer die lebende Steuerungsdoku gilt:

- Globaler Process-Kernel-Status liegt in `docs/architecture/process-kernel/STATUS.md`.
- Detaillierter Liefernachweis pro Wave liegt in `docs/architecture/process-kernel/wave-*/STATUS.md`.
- Gap-Planung liegt in `PLAN_GAPS_*.md` oder `docs/roadmap/status/*.md`.
- Strategische Priorisierung ist kein Lieferprotokoll.
- Historische Planung darf nicht stillschweigend als aktueller Ist-Status umgedeutet werden.

Pflichtprinzip:

- Ein Dokument muss klar erkennbar machen, ob es `Source of Truth`, `abgeleitete Sicht` oder `historische Planung` ist.

## Verbindliche Regeln fuer Steuerungsdokumente

Diese Regeln gelten fuer:

- `**/STATUS.md`
- `PLAN_GAPS_*.md`
- `docs/roadmap/status/*.md`
- `docs/architecture/process-kernel/wave-*/package-*/STATUS.md`
- `docs/architecture/process-kernel/DELIVERY-MAP.md`
- `DEVELOPMENT-MAP.md`

### Allgemeine Muss-Regeln

1. Erste Zeile ist immer eine H1.
2. Jedes Dokument enthaelt einen klaren Status- oder Einordnungsblock.
3. Datum immer im Format `YYYY-MM-DD`.
4. Statuswerte nur aus definierter Menge.
5. Dateien und Endpunkte immer in Backticks.
6. Keine stillen Behauptungen ohne Beleg bei Statusaussagen.
7. Wenn auf Gaps oder Waves verwiesen wird, muss die Referenz explizit und konsistent sein.

### Erlaubte Statuswerte

Fuer Liefer- und Fortschrittsstatus sind nur diese Werte zulaessig:

- `geplant`
- `in arbeit`
- `teilweise abgeschlossen`
- `abgeschlossen`
- `blockiert`
- `verworfen`
- `historisch`

## Verbindliches Schema fuer `STATUS.md`

### Geltungsbereich

Das Schema gilt fuer:

- `docs/architecture/process-kernel/STATUS.md`
- `docs/architecture/process-kernel/wave-*/STATUS.md`
- optionale weitere `STATUS.md`, wenn sie als lebende Lieferdoku genutzt werden

### Pflichtabschnitte

Jede `STATUS.md` muss diese Abschnitte in dieser Reihenfolge enthalten:

1. `# <Titel>`
2. `## Scope`
3. `## Zielbild`
4. `## Lieferumfang`
5. `## Abnahmekriterien`
6. `## Tests`
7. `## Status`

Optional:

- `## Gaps geschlossen`
- `## Risiken`
- `## Naechste Schritte`
- `## Referenzen`

## Verbindliches Minimal-Schema fuer `wave-*/package-*/STATUS.md`

Package-Statusdokumente gelten als untergeordnete Lieferdoku innerhalb einer Wave. Sie sind in der Regel historisch oder abgeleitete Teillieferungen, nicht die operative Haupt-Source-of-Truth.

Pflichtbestandteile:

1. H1 in Zeile 1
2. mindestens ein strukturierender Abschnitt aus `## Paket`, `## Scope` oder `## Arbeitspakete`
3. ein Verifikations- oder Test-Abschnitt (`## Verifikation`, `## Testergebnis` oder `## Tests`)
4. ein erkennbarer Lieferinhalt, zum Beispiel Artefakte, Arbeitspakete oder Abhaengigkeiten

Empfehlung:

- historische Paketdokumente sollen explizit als `historisch` gekennzeichnet werden, wenn sie nur noch Teil der Lieferchronik sind
- ein eigener `## Status`-Abschnitt mit Datum ist fuer neu angefasste Paketdokumente empfohlen, aber nicht zwingend

## Verbindliches Minimal-Schema fuer `DELIVERY-MAP.md`

Die Delivery Map ist eine abgeleitete Steuerungssicht, keine operative Hauptquelle.

Pflichtbestandteile:

1. H1 in Zeile 1
2. Datumsangabe im Format `YYYY-MM-DD`
3. ein Wave-Mapping-Abschnitt
4. ein Gap-Mapping-Abschnitt
5. mindestens ein Link oder Pfadverweis auf operative Statusquellen

Empfehlung:

- die Datei soll explizit markieren, dass sie eine abgeleitete Sicht ist

## Verbindliches Minimal-Schema fuer `DEVELOPMENT-MAP.md`

Die Development Map ist eine Orientierungs- und Onboarding-Sicht. Wenn sie nicht den aktuellen Lieferstand fuehrt, muss sie explizit als historische oder abgeleitete Sicht markiert werden.

Pflichtbestandteile:

1. H1 in Zeile 1
2. `## Einordnung` oder `**Zweck:**`
3. `## Referenzen`
4. ein expliziter Statushinweis (`historisch` oder `abgeleitete Sicht`)
5. mindestens ein Markdown-Link auf aktuelle operative Steuerungsdokumente

## Verbindliches Minimal-Schema fuer zentrale Referenzdokumente

Fuer `README.md`, `docs/architecture/index.md`, `docs/AI-VISION.md` und `docs/AGENT-INTEGRATION.md` gelten folgende Mindestregeln:

1. H1 in Zeile 1
2. ein Einordnungs- oder Zweckabschnitt (`## Einordnung`, `## Zweck`, `## Zielbild` oder `**Zweck:**`)
3. mindestens ein Referenzabschnitt oder mehrere Markdown-Links auf weiterfuehrende Repo-Dokumente
4. wenn das Dokument nicht der operative Lieferstand ist, muss es das explizit sagen (`abgeleitete Sicht`, `Referenzdokument` oder `historisch`)

## Verbindliches Minimal-Schema fuer ADR-Dokumente

Fuer `docs/adr/*.md` gelten folgende Mindestregeln:

1. H1 in Zeile 1
2. erkennbare Metadaten fuer Status und Datum
3. mindestens ein Kontext-Abschnitt (`## Context` oder `## Kontext`)
4. mindestens ein Entscheidungs-Abschnitt (`## Decision` oder `## Entscheidung`)
5. mindestens ein Konsequenz-Abschnitt (`## Consequences` oder `## Konsequenzen`)

Erlaubte Metadatenformate:

- `## Status` mit Wert und Datum
- `**Status:** ...` und `**Date:** ...` oder `**Datum:** ...`
- eine Metadaten-Tabelle mit `Status` und `Date` oder `Datum`

Hinweis:

- Sprachmischung in Bestands-ADRs ist toleriert, solange die Struktur pruefbar bleibt

Pflichtbestandteile:

1. H1 in Zeile 1
2. ein Paket- oder Scope-Abschnitt (`## Paket` oder `## Scope`)
3. ein Ziel-Abschnitt (`## Ziel` oder `## Zielbild`)
4. ein Verifikations- oder Test-Abschnitt (`## Verifikation`, `## Testergebnis` oder `## Tests`)
5. ein `## Status`-Abschnitt
6. Statuswert aus der erlaubten Menge
7. Datum im `## Status`-Abschnitt im Format `YYYY-MM-DD`

Empfehlung:

- historische Paketdokumente sollen explizit als `historisch` gekennzeichnet werden, wenn sie nur noch Teil der Lieferchronik sind

## Verbindliches Minimal-Schema fuer `DELIVERY-MAP.md`

Die Delivery Map ist eine abgeleitete Steuerungssicht, keine operative Hauptquelle.

Pflichtbestandteile:

1. H1 in Zeile 1
2. Datumsangabe im Format `YYYY-MM-DD`
3. `## Wave -> Gap Mapping`
4. `## Gap -> Wave Mapping`
5. mindestens ein Markdown-Link auf operative Statusquellen
6. klarer Hinweis, dass die Datei eine abgeleitete Sicht ist

## Verbindliches Minimal-Schema fuer `DEVELOPMENT-MAP.md`

Die Development Map ist eine Orientierungs- und Onboarding-Sicht. Wenn sie nicht den aktuellen Lieferstand fuehrt, muss sie explizit als historische oder abgeleitete Sicht markiert werden.

Pflichtbestandteile:

1. H1 in Zeile 1
2. `## Einordnung` oder `**Zweck:**`
3. `## Referenzen`
4. ein expliziter Statushinweis (`historisch` oder `abgeleitete Sicht`)
5. mindestens ein Markdown-Link auf aktuelle operative Steuerungsdokumente

### Pflichtinhalt je Abschnitt

#### 1. Titel

Beispiel:

- `# Wave-31 Status`
- `# Process Kernel Status`

#### 2. Scope

Muss enthalten:

- fachlicher oder technischer Scope
- betroffene Gaps, falls vorhanden

#### 3. Zielbild

Muss enthalten:

- fachliche Absicht
- was durch die Lieferung konkret verbessert oder geschlossen wird

#### 4. Lieferumfang

Muss als Tabelle vorliegen mit mindestens:

- `AP`
- `Zielmodul`
- `Beschreibung`
- `Status`

#### 5. Abnahmekriterien

Muss enthalten:

- pruefbare Kriterien
- keine rein vagen Aussagen wie "besser", "sauber", "modern"

#### 6. Tests

Muss enthalten:

- Testdatei oder Testkommando
- Anzahl oder Ergebnis

Erlaubte Formen:

- Tabelle
- kurzer Block mit `pytest ...`
- Ergebniszeile wie `192 passed`

#### 7. Status

Muss enthalten:

- Statuswert aus der erlaubten Menge
- Datum
- optional Kurzfazit

Empfohlene Form:

- `` `abgeschlossen` - 2026-03-15 - 105 Tests gruen, Gaps 017 und 040 geschlossen ``

oder

- `## Status: abgeschlossen`
- `Datum: 2026-03-18`

### Zusatzregel fuer Global-`STATUS.md`

Die globale Statusdatei darf aggregieren, aber nicht den Detailnachweis ersetzen.

Pflicht:

- Verweise auf untergeordnete `wave-*/STATUS.md`
- keine "abgeschlossen"-Aussage ohne referenzierte Detailquelle

## Verbindliches Schema fuer `PLAN_GAPS_*.md`

### Geltungsbereich

Das Schema gilt fuer:

- `PLAN_GAPS_*.md`
- vergleichbare Gap-Planungsdokumente mit operativem Charakter

### Pflichtabschnitte

Jede `PLAN_GAPS_*.md` muss diese Abschnitte in dieser Reihenfolge enthalten:

1. `# <Titel>`
2. `## Scope`
3. `## Einordnung`
4. `## Bewertungslogik`
5. Ein Abschnitt pro Gap
6. `## Abhaengigkeiten`
7. `## Priorisierung`
8. `## Akzeptanz / Done`
9. `## Referenzen`

Optional:

- `## Risiken`
- `## Naechste Schritte`

### Pflichtinhalt pro Gap

Jeder Gap-Block muss folgende Felder enthalten:

- `Gap-ID`
- `Titel`
- `KPI-Ziel`
- `Aufwand`
- `Prioritaet`
- `Horizon`
- `Current State`
- `Requirements`
- `Design`
- `Acceptance Criteria`
- `Implementation Steps`

### Pflichtregel fuer Planungsdokumente

Ein `PLAN_GAPS_*.md` ist per Default kein Ist-Status-Dokument.

Deshalb muss `## Einordnung` klar sagen:

- ob das Dokument Planung, Umsetzungsentwurf oder historischer Plan ist
- welche Datei den aktuellen Lieferstatus abbildet

Beispiel:

- `Dieses Dokument ist ein Umsetzungsplan und nicht die operative Source-of-Truth fuer den Lieferstatus.`
- `Der aktuelle Ist-Stand wird in docs/architecture/process-kernel/STATUS.md und den zugehoerigen wave-*/STATUS.md-Dateien gefuehrt.`

## Verbindliches Minimal-Schema fuer `docs/roadmap/status/*.md`

### Geltungsbereich

Das Schema gilt fuer operative Roadmap- und Steuerungsdokumente in:

- `docs/roadmap/status/*.md`

### Pflichtregeln

1. Dateiname beginnt mit `YYYY-MM-DD-`.
2. Dokument beginnt mit einer H1.
3. Dokument enthaelt mindestens einen Einordnungs- oder Zweckblock:
   - `## Ziel`
   - `## Statusabgleich`
   - `**Zweck:**`
4. Dokument enthaelt mindestens eine Repo-Referenz als Markdown-Link.
5. Wenn das Dokument Liefer- oder Abschlussaussagen wie `erledigt` oder `abgeschlossen` enthaelt, muss es auf den operativen Wahrheitsstand verweisen:
   - `docs/architecture/process-kernel/STATUS.md`
   - oder eine `wave-*/STATUS.md`-Datei

### Ziel dieser Regeln

Roadmap-Statusdokumente bleiben flexibel, muessen aber:

- zeitlich einordenbar sein
- ihren Zweck klar machen
- auf operative Statusquellen rueckverweisen, wenn sie Fortschritt behaupten

## Synchronisationsregeln zwischen Dokumenttypen

### STATUS -> PLAN

Wenn ein Gap in einer `STATUS.md` als geschlossen ausgewiesen wird, darf ein Planungsdokument den Gap weiter enthalten, aber nur:

- mit explizitem Hinweis `historische Planung`
- oder mit aktualisiertem Statusbezug

### PLAN -> STATUS

Ein `PLAN_GAPS_*.md` darf nie allein den Eindruck erzeugen, dass ein Gap bereits geliefert ist, wenn keine `STATUS.md` dies belegt.

### Global -> Wave

Die globale `process-kernel/STATUS.md` darf nur verdichten:

- was in Wave-Dateien belegt ist
- oder was explizit als aggregierter Management-Status gekennzeichnet ist

## Maschinenpruefbare Sollregeln

Diese Regeln eignen sich spaeter fuer `Vale`, ein eigenes `docs-sync`-Script oder CI:

1. `STATUS.md` enthaelt alle Pflichtabschnitte.
2. `PLAN_GAPS_*.md` enthaelt `## Einordnung`.
3. Datumsformat entspricht `YYYY-MM-DD`.
4. Statuswerte entsprechen der erlaubten Liste.
5. `wave-*/STATUS.md` enthaelt mindestens einen Testnachweis.
6. `process-kernel/STATUS.md` enthaelt Referenzen auf Wave-Dateien.
7. Planungsdokumente mit Gap-IDs duerfen abgeschlossene Gaps nur mit expliziter Einordnung weiterfuehren.

## Empfehlung fuer Agentenregeln

Fuer mehrere parallele Agents sollte zusaetzlich in `CLAUDE.md` oder einer kuenftigen Agent-Governance-Datei festgelegt werden:

1. `STATUS.md` nur nach vorhandenem Schema aendern.
2. `PLAN_GAPS_*.md` nie als Ist-Status-Datei behandeln.
3. Neue Statusbehauptungen nur mit Test- oder Dateibeleg eintragen.
4. `docs/archive/**` nicht als Source-of-Truth verwenden.
5. Neue Steuerungsdokumente nur anlegen, wenn kein passender Dokumenttyp schon existiert.

## Minimal-Templates

### Template: `STATUS.md`

```md
# <Titel>

## Scope
<Kurzbeschreibung des Scopes>

## Zielbild
<Welche Lieferung wird erreicht?>

## Lieferumfang
| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `...` | ... | geplant |

## Abnahmekriterien
- ...

## Tests
- `pytest ...`
- Ergebnis: `...`

## Status
`in arbeit` - 2026-03-19 - <Kurzfazit>
```

### Template: `PLAN_GAPS_*.md`

```md
# Plan for closing gaps <IDs>

## Scope
<Welche Gaps und welcher Kontext?>

## Einordnung
Dieses Dokument ist ein Umsetzungsplan und nicht die operative Source-of-Truth fuer den Lieferstatus.
Der aktuelle Ist-Stand wird in `<Statusdatei>` gefuehrt.

## Bewertungslogik
- Prioritaet: ...
- Aufwand: ...
- Horizon: ...

## Gap <ID>: <Titel>
**KPI-Ziel:** ...
**Aufwand:** ...
**Prioritaet:** ...
**Horizon:** ...

### Current State
...

### Requirements
...

### Design
...

### Acceptance Criteria
...

### Implementation Steps
1. ...

## Abhaengigkeiten
- ...

## Priorisierung
1. ...

## Akzeptanz / Done
- ...

## Referenzen
- ...
```

## Naechster Schritt

Auf Basis dieser Governance sollten als Nächstes umgesetzt werden:

1. `Vale`-Regeln fuer Dokumenttypen
2. `markdownlint` fuer Formatkonsistenz
3. ein kleines `docs-sync`-Script fuer Pflichtabschnitte und Statuswerte
4. CI-Checks nur fuer Steuerungsdokumente, nicht fuer `docs/archive/**`

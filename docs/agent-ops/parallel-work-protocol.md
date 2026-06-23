# Parallel Work Protocol

## Ziel

Zwei oder mehr Agenten sollen gleichzeitig arbeiten koennen, ohne sich gegenseitig den Kontext oder Dateiaenderungen zu zerstoeren.

## Arbeitsmodell

### Lead-Agent

- priorisiert
- definiert Slices
- integriert Ergebnisse
- entscheidet bei Ueberschneidungen

### Slice-Agent

- besitzt einen klar abgegrenzten Arbeitsbereich
- dokumentiert Fortschritt, Risiken und offene Fragen
- aendert keine fremden Dateien ohne dokumentierte Abstimmung

## Claim-Protokoll (Pflicht vor Arbeitsbeginn)

Kein Agent darf einen Slice beginnen, ohne ihn vorher zu claimen.

### Schritt-fuer-Schritt

1. `docs/agent-ops/active-workboard.md` lesen.
2. Pruefen: Ist der gewuenschte Slice `offen`? Falls `reserviert` oder `in arbeit` → anderen Slice waehlen.
3. Slice-Zeile auf `reserviert` setzen, eigenen Namen/Sessionkennung als Owner eintragen.
4. Commit: `chore(workboard): claim SLICE-ID` — ausschliesslich die Workboard-Datei.
5. Erst jetzt mit der Implementierung beginnen.

### Freigabe nach Abschluss

- Slice auf `abgeschlossen` setzen, Handoff-Block im Workboard erganezen.
- Commit mit allen Ergebnis-Dateien.
- Naechsten empfohlenen Slice als `offen` in die Tabelle aufnehmen.

### Konflikt-Eskalation

Falls zwei Agents denselben Slice gleichzeitig geclaimt haben (Race Condition):

1. Den juengeren Claim zurueckziehen (git revert des Claim-Commits).
2. Den aelteren Claim als gueltigen Owner bestaetigen.
3. Alternativen Slice fuer den zweiten Agent im Workboard erganzen.

## Slice-Definition

Jeder Slice muss mindestens enthalten:

- Ziel
- fachlicher Scope
- Dateibesitz
- Abnahmekriterien
- bekannte Risiken
- noetige Tests
- noetige Doku-Updates

Neue AI- oder Agenten-Slices muessen ausserdem den AI-Harness aus
`task-slice-template.md` enthalten. Der Harness macht fachlichen Vertrag,
Architekturvertrag, Datenvertrag, Testvertrag, Security-Vertrag,
Betriebsvertrag, Dokumentationsvertrag und externe Gates explizit. Ein Slice
ohne diesen Harness darf nicht von `offen` oder `reserviert` auf `in arbeit`
gesetzt werden, ausser er ist als Legacy-Slice dokumentiert.

## Ueberschneidungsregel

Wenn zwei Agenten dieselbe Datei brauchen:

1. zuerst pruefen, ob die Arbeit anders geschnitten werden kann
2. falls nein, die Datei explizit im Workboard markieren
3. Integrationsreihenfolge festhalten
4. vor Commit die Integration pruefen

## Restart-Sicherheit

Jeder Agent hinterlaesst vor Abschluss oder Pause:

- einen kurzen Handoff
- oder einen Resume-Block mit:
  - Stand
  - offene Arbeit
  - offene Risiken
  - betroffene Dateien
  - naechstem konkreten Schritt

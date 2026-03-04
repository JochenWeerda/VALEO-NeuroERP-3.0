# Jira CSV Import – Mappinghinweise (Finance Suite S1–S6)

Datei: `docs/roadmap/finance-suite-jira-import.csv`

## Empfohlenes Mapping in Jira

- `Issue ID` -> **External ID** (oder Textfeld zur temporären Referenz)
- `Issue Type` -> **Issue Type**
- `Summary` -> **Summary**
- `Description` -> **Description**
- `Epic Name` -> **Epic Name** (nur für `Epic`)
- `Parent ID` -> **Parent** (wenn unterstützt)  
  - Alternative: Epics zuerst importieren, danach Stories mit `Epic Link` manuell/Batch setzen.
- `Story Points` -> **Story Points**
- `Priority` -> **Priority**
- `Labels` -> **Labels**
- `Sprint` -> **Sprint** (optional; wenn Board-Sprints bereits existieren)

## Importreihenfolge (falls Parent-Mapping nicht verfügbar)

1. Nur Zeilen mit `Issue Type = Epic` importieren.
2. Epicschlüssel exportieren/merken.
3. Stories importieren und `Epic Link` per Bulk-Edit setzen:
   - `Parent ID` (`E1` … `E19`) als Zuordnungsanker nutzen.

## Hinweise

- Datei ist bewusst in ASCII gehalten.
- Priorität ist an den Phase-1-Fokus gekoppelt (`Highest` für P0-kritisch).
- Labels sind so gewählt, dass Filter nach Modul, Risiko und Phase möglich sind.

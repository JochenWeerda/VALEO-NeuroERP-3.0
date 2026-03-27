# ADR-031 - Standardmaske vs Spezialmaske

**Status:** akzeptiert
**Datum:** 2026-03-27
**Typ:** Entscheidungsregel fuer Workflow- und UI-Umsetzung

## Kontext

Bei der Analyse und Umsetzung von End-to-End-Workflows tauchen wiederholt fachliche Luecken auf, die entweder:

- durch Erweiterung bestehender Standardmasken
- oder durch neue Spezialmasken

geloest werden koennen.

Ohne feste Regel entstehen schnell:

- ueberladene Standardmasken
- doppelte Funktionalitaet
- unklare Benutzerfuehrung
- schlechte Wartbarkeit

## Entscheidung

Fuer neue Workflow-Anforderungen gilt folgende Reihenfolge:

1. Zuerst pruefen, ob die bestehende Standardmaske mit vertretbarem Aufwand erweitert werden kann.
2. Danach pruefen, ob die Erweiterung auch fuer andere Prozesse wiederverwendbar und verstaendlich bleibt.
3. Danach pruefen, ob die Benutzerfuehrung trotz Erweiterung klar und wartbar bleibt.
4. Wenn die Standardmaske dadurch ueberladen, fachlich unsauber oder UX-seitig unklar wuerde, ist eine Spezialmaske zulaessig.
5. Die Entscheidung ist kurz in der zugehoerigen Workflow-Doku oder Wave-Doku zu begruenden.

## Konsequenzen

- Standardmasken bleiben der bevorzugte Ort fuer robuste Datenerfassung.
- Spezialmasken bleiben moeglich, aber nur bei echtem fachlichen oder UX-seitigen Bedarf.
- Workflow-Prozessraeume duerfen keine Schatten-CRUD-Logik aufbauen, wenn bereits eine belastbare Standardmaske existiert.
- Neue Schnellstarts oder Intake-Dialoge muessen klar in den regulaeren Folgeprozess ueberfuehren.

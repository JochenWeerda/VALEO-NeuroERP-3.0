# Operational Rollout Scope 2026-04-09

## Ziel

Das gemeinsame Arbeitsmodell aus:

- Vorgang
- Objekt
- Ressourcenlage
- Wirtschaftslage
- Governance
- Naechste Aktion

wird nur dort ausgerollt, wo ein echter operativer Mehrwert entsteht.

Es ist ausdruecklich **kein** Ziel, jede Liste oder jede Detailmaske mit denselben Leitstandselementen zu ueberziehen.

## Ausgerollte Fachmasken

Diese Masken haben jetzt einen kompakten Fallkopf, einen knappen Kontextblock und eine kurze Timeline, jeweils nur aus bereits geladenen Daten:

- Einkauf:
  - `angebote-liste.tsx`
  - `anfragen-liste.tsx`
  - `angebot-stamm.tsx`
  - `anfrage-stamm.tsx`
  - `bestellung-stamm.tsx`
  - `rechnungseingang.tsx`
- Annahme / Physische Kette:
  - `lkw-registrierung.tsx`
  - `rohware.tsx`
  - `qualitaets-check.tsx`
  - `wiegeschein-detail.tsx`
- Qualitaet:
  - `reklamation-detail.tsx`
- Finance:
  - `abschluss.tsx`
  - `buchungserfassung.tsx`
- Service / CRM:
  - `service/anfrage-detail.tsx`
  - `crm/opportunity-detail.tsx`

## Mehrwertkriterien

Das Modell wird eingesetzt, wenn mindestens drei dieser Punkte gleichzeitig gelten:

- echte Statusuebergaenge oder Freigaben
- sichtbare Risiken oder Blocker
- ein benoetigter Owner oder Eskalationspfad
- ein Folgeobjekt oder naechster Prozessschritt
- fachlich relevante Ressourcen-, Finanz- oder Governance-Lage

## Bewusst schlank gelassene Masken

Schlanke Register, reine Such-/Listenraeume und einfache Nachschlageflaechen bleiben bewusst ohne Leitstandskopf, wenn sonst nur Informationsduplikate entstehen wuerden.

Typische Beispiele:

- Register mit Fokus auf Suche, Filter und Export
- reine Stammdatentabellen ohne akuten Vorgangscharakter
- Listenraeume ohne Owner-, Eskalations- oder Blockerlogik
- einfache Report-/Cockpit-Seiten, deren Kernaussage bereits durch KPI oder Segmentierung getragen wird

## Performance-Regel

Der Rollout darf keine zusaetzlichen API-Requests erzwingen.

Die neuen UI-Bausteine duerfen nur:

- bereits geladene Query-Daten
- bestehende Router-/Workflow-Kontexte
- lokal berechnete Verdichtung

verwenden.

## Gestaltungsregel

Der Kopfbereich bleibt bewusst leicht:

- 1 Fallkopf
- 1 kurze Timeline
- 1 kompakter Kontextblock

Wenn eine Maske mehr erklaeren muss, gehoert die Tiefe in bestehende Fachkarten oder Tabs, nicht in den Leitstandskopf.

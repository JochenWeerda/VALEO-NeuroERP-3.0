# ERP Reference Matrix 2026-04-12

Stand: `2026-04-12`

## Zweck

Diese Matrix verdichtet die externen Referenzmuster fuer die naechste fachliche Vertiefung von VALEO NeuroERP. Sie ist bewusst neutral benannt und trennt sauber zwischen:

- fachlichem Referenzbild
- UI-/Interaktionsmuster
- Lizenz-/Codeuebernahmerisiko
- naechster sinnvoller Ausbauwelle im VALEO-Repo

## Referenzklassen

### Fachliches Tiefenbild

- Agrar-Spezialsoftware Hilfe
- weitere etablierte Landhandels- und ERP-Funktionsbilder

### Community-ERP-Referenzmuster

- Community-Agreement-/Contract-Module
- Community-Stock-/Logistik-Workflow-Repositorien
- Community-Account-/Finance-Werkzeuge
- Community-Purchase-Workflow-Repositorien
- Community-Helpdesk-/Field-Service-Repositorien

### UIX-Referenzmuster

- Moderne ERP-Oberflächen Floorplans
- Web-ERP-Standard Object Page / Overview Page / Worklist / Wizard

## Uebernahmeregel

1. Fach- und Statusmuster duerfen als Referenz uebernommen werden.
2. UI-Strukturen duerfen als Interaktionsmuster uebernommen werden.
3. Direkte Codeuebernahme nur aus permissiven oder klar kompatiblen Quellen.
4. AGPL- oder proprietaere Enterprise-Quellen nur nach expliziter Lizenzentscheidung.
5. Kein Referenzsystem wird als Ganzes nachgebaut.

## Matrix

| Bereich | Fachliches Referenzbild | UIX-Muster | VALEO-Ist | Hauptluecke | Geeignete Uebernahme | Risiko | Naechster Slice |
|---|---|---|---|---|---|---|---|
| Kontrakt- und Preisfixierung | tiefe Kontraktklassen, Paritaeten, Hedge-/Fixierungsprozesse, Engagementsicht | Object Page mit Risikoheader, Worklist fuer Fixierungen | Kontrakt-Profi-Basis ist da, aber Fixierungs- und Marktprozess noch nicht voll operativ | eigene Arbeitsraeume fuer Fixierung, Marktwert, Mahnung, Engagement | Statusmodell, Operatorflow, Risiko-/Fristenmuster | mittel | `DOM-CON-003` |
| FIBU-Operator und Abschluss | Abschluss, Reorg, Zinswesen, eBilanz-/Clearing-Betrieb | Overview Page fuer Abschlussdruck, Worklist fuer offene Operatoraufgaben | FIBU ist breit, aber Operatorpfade und Parameter noch ungleich tief | Jahreswechsel, Reorganisator, Zinsgruppen, technische Revisionssicht | Operator-Cockpit, Checklist-/Freigabemuster, Periodenstatus | mittel | `DOM-FIN-003` |
| Einkauf / Freigabe / Rechnungseingang | tiefe Freigabe-, Matching-, Nachforderungs- und Belegketten | Worklist mit Bulk-Aktionen, Object Page fuer Liefer-/Rechnungsfall | Einkaufsmasken sind verdrahtet, aber nicht alle Folgefaelle sind semantisch gleich tief | Nachforderung, Eskalation, Matching-Ausnahmen, Lieferantenkommunikation | Bulk-Action-Muster, Ausnahmenstatus, Folgeobjektlogik | niedrig bis mittel | `DOM-PROC-003` |
| Physische Kette Rohware bis Abrechnung | Partie, Annahme, Wiegung, Charge, Lager, Fracht, Settlement | kompakter Fallkopf plus Timeline und Kontextpanel | Kette ist sichtbar, aber entlang aller Uebergaben noch nicht gleich tief | Uebergabestatus, Abweichungsgrund, Objektbezug und Folgeaktion durchgaengig | Zustandsvokabular, Kettenobjekte, Ausnahmebehandlung | mittel | `DOM-SUPPLY-003` |
| CRM / Service / Folgeobjekte | Kunden-, Ticket-, Opportunity- und Servicefall mit Folgeobjekten und Ownership | flexible Header, Timeline, Folgeobjekt-Leiste | CRM/Service ist stark verbessert, aber nicht ueberall als echter Fallraum verdichtet | Ownership, Dubletten, Folgeobjektkette, Serviceabschluss | Fallstatus, Ownership, Timeline, Folgebelegmuster | niedrig bis mittel | `DOM-CRM-003` |
| Dokumente / Nachweis / Meldungen | revisionsrelevante Nachweiskette, Bescheide, externe Rueckmeldungen, Wiedervorlage | Object Page fuer Nachweisobjekte, Inbox-/Worklist fuer Rueckmeldungen | Dokument- und Melderaeume sind brauchbar, aber Artefakt-/Rueckmeldungspfad ist noch nicht ueberall gleich tief | Bescheidpfad, Artefaktstatus, Rueckmeldung am Vorgang, Wiedervorlage | Nachweisstatus, externe Rueckmeldung, Artefakt-/Dokumentkette | mittel | `DOM-DOC-003` |

## Priorisierung

### Prioritaet A

1. `DOM-FIN-003`
2. `DOM-SUPPLY-003`
3. `DOM-PROC-003`

### Prioritaet B

4. `DOM-CON-003`
5. `DOM-CRM-003`
6. `DOM-DOC-003`

## Slice-Ableitung

### DOM-FIN-003

- Ziel: FIBU-Operatorpfade fuer Abschluss, Reorganisator, Zinswesen und Revisionssicht semantisch verdichten.
- Fokus: `packages/frontend-web/src/pages/finance/*`, `packages/frontend-web/src/pages/fibu/*`, passende Finance-Endpunkte und Read-Models.
- Workflow: `docs/workflows/dom-fin-003-fibu-operatorparitaet.md`
- Card: `docs/cards/finance/DOM-FIN-003-fibu-operatorparitaet.md`

### DOM-SUPPLY-003

- Ziel: Physische Kette `Partie -> Annahme -> Wiegung -> Charge -> Fracht -> Abrechnung` mit durchgaengigem Status und Folgeaktion harmonisieren.
- Fokus: `packages/frontend-web/src/pages/annahme/*`, `packages/frontend-web/src/pages/waage/*`, `packages/frontend-web/src/pages/charge/*`, `packages/frontend-web/src/pages/logistik/*`.
- Workflow: `docs/workflows/dom-supply-003-physische-kette.md`
- Card: `docs/cards/inventory/DOM-SUPPLY-003-physische-kette.md`

### DOM-PROC-003

- Ziel: Einkaufsausnahmen, Matching, Nachforderung und Lieferantenkommunikation auf echte Folgefaelle heben.
- Fokus: `packages/frontend-web/src/pages/einkauf/*`, relevante Beschaffungsendpunkte, Dokument- und Kommunikationspfade.
- Workflow: `docs/workflows/dom-proc-003-beschaffungsausnahmen.md`
- Card: `docs/cards/einkauf/DOM-PROC-003-beschaffungsausnahmen.md`

### DOM-CON-003

- Ziel: Kontraktfixierung, Marktbewertung, Mahnung und Engagement als vollwertige Operatorraeume ausbauen.
- Fokus: `packages/frontend-web/src/pages/kontrakte/*`, `packages/frontend-web/src/pages/contracts-v2.tsx`, zugehoerige Kontraktendpunkte.
- Workflow: `docs/workflows/dom-con-003-fixierung-markt-mahnung.md`
- Card: `docs/cards/kontrakte/DOM-CON-003-fixierung-markt-mahnung.md`

### DOM-CRM-003

- Ziel: CRM-/Servicefaelle mit Ownership, Folgeobjekten, Dubletten- und Abschlusslogik angleichen.
- Fokus: `packages/frontend-web/src/pages/crm/*`, `packages/frontend-web/src/pages/service/*`, zugehoerige APIs und Agent-Ops-Verknuepfung.
- Workflow: `docs/workflows/dom-crm-003-fall-und-ownership.md`
- Card: `docs/cards/crm/DOM-CRM-003-fall-und-ownership.md`

### DOM-DOC-003

- Ziel: Nachweis-, Bescheid-, Artefakt- und Rueckmeldungskette ueber Dokumente, Meldungen und Vorgangskontext vereinheitlichen.
- Fokus: `packages/frontend-web/src/pages/dokumente/*`, `packages/frontend-web/src/pages/compliance/*`, `packages/frontend-web/src/pages/fibu/atlas.tsx`, `packages/frontend-web/src/pages/compliance/meldewesen-konsole.tsx`.
- Workflow: `docs/workflows/dom-doc-003-nachweis-und-rueckmeldung.md`
- Card: `docs/cards/compliance/DOM-DOC-003-nachweis-und-rueckmeldung.md`

## Folgerung

Die naechste Vertiefungsphase sollte nicht mehr breit ueber viele Randmodule streuen. Sie sollte die verbleibende Ungleichheit zwischen:

- Finance/FIBU,
- Beschaffung,
- physischer Liefer- und Rohwarenkette,
- Kontrakt-/Marktlogik,
- CRM/Service
- und Dokument-/Nachweisraum

gezielt blockweise angleichen.

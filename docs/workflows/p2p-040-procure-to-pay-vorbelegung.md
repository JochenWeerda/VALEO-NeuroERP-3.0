# P2P-040 - Procure-to-Pay Vorbelegung aus Bedarfsmeldung, RFQ und Vertrag

## A. Workflow-Uebersicht

Gepruefter Workflow: Vorbelegung der Standard-Bestellmaske [`packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`](c:/Users/Jochen/VALEO-NeuroERP-3.0/packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx) aus drei angrenzenden Einstiegen:

- Bedarfsmeldung / Einkaufsanfrage
- RFQ-Phase derselben Einkaufsanfrage
- Vertragsabruf ueber den Contract-Endpoint

Leitentscheidung:

- Keine Spezialmaske.
- Vorbelegung bleibt in der Standard-Bestellmaske.
- Bedarfsmeldung und RFQ liefern Bedarfsdaten, aber keinen Lieferanten.
- Nur der Vertragsabruf darf den Partnerkontext in die Bestellung tragen.

## B. Vollstaendige Card-Liste

1. `P2P-041` Bedarfsmeldung in Bestellung ueberfuehren
2. `P2P-042` RFQ-Bezug in Bestellung ueberfuehren
3. `P2P-043` Vertragsabruf in Bestellung ueberfuehren
4. `P2P-044` Vorbelegte Daten pruefen und vervollstaendigen
5. `P2P-045` Bestellung speichern oder korrigieren

Detail-Card:

- [`docs/cards/einkauf/P2P-041-vorbelegung-aus-anfrage-und-vertrag.md`](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/cards/einkauf/P2P-041-vorbelegung-aus-anfrage-und-vertrag.md)

## C. Mermaid-Diagramm

```mermaid
flowchart TD
    A([Start: P2P Vorbelegung]) --> B{Einstieg?}
    B -->|Bedarfsmeldung| C[GET /api/v1/einkauf/anfragen/{id}]
    B -->|RFQ| D[GET /api/v1/einkauf/anfragen/{id}]
    B -->|Vertrag| E[GET /api/contracts/{id}]

    C --> F[Artikel, Menge, Faelligkeit, Referenz in Bestellmaske]
    D --> F
    E --> G[Partner, Artikel, Menge, Lieferfenster in Bestellmaske]

    F --> H{Bestellung fachlich vollstaendig?}
    G --> H
    H -->|Nein| I[Lieferant, Preise oder weitere Daten ergaenzen]
    I --> H
    H -->|Ja| J[Bestellung speichern]
    J --> K([Ende])
```

## D. Soll-Ist-Abweichungen

| Card | Soll | Ist | Abweichung | Risiko | Massnahme |
|------|------|-----|------------|--------|-----------|
| `P2P-041` | Bedarfsmeldungen muessen ueber einen realen Einzelabruf vorgeladen werden. | Vor diesem Slice referenzierte das Frontend nicht vorhandene `/api/purchase-workflow/requisitions/{id}`-Pfade. | Phantom-API-Pfad. | hoch | Einzelabruf `GET /api/v1/einkauf/anfragen/{id}` im Compat-Contract eingefuehrt. |
| `P2P-042` | RFQ und Einkaufsanfrage muessen denselben Einkaufsvertrag nutzen. | RFQ referenzierte ebenfalls einen nicht nachgewiesenen `/api/purchase-workflow/rfqs/{id}`-Pfad. | Inkonsistenter Datenvertrag. | hoch | RFQ auf denselben `einkauf/anfragen/{id}`-Contract gezogen. |
| `P2P-041`/`P2P-042` | Bedarfsmeldung und RFQ duerfen keinen Lieferanten erfinden. | Frueheres Frontend-Mapping erwartete `supplierId`, obwohl Einkaufsanfragen Bedarfs- und Anforderer-Daten liefern. | Fachlich falsche Vorbelegung. | hoch | Anfragepfade fuellen nur Bedarf, Termin und Referenzen; Lieferant bleibt offen. |
| `P2P-043` | Vertragsabruf soll Partner, Artikel und Lieferfenster vorfuellen, soweit der Contract sie liefert. | Contract-Endpoint war vorhanden, aber nicht auf das Bestellmuster gemappt. | Unvollstaendige Vorbelegung. | mittel | Contract-Mapping auf `counterpartyId`, `commodity`, `qty`, `deliveryWindow.to` gezogen. |

## E. UI-/CRUD-Befunde

- `Create`: weiterhin ueber dieselbe Standard-Bestellmaske.
- `Read`: Vorbelegungsquellen jetzt ueber reale Einzelabrufe.
- `Update`: Nutzer ergaenzen fehlende Lieferanten- oder Preisangaben vor dem Speichern.
- `Delete/Storno`: unveraendert ueber nachgelagerten Bestellpfad.
- `Maskenuebergabe`: Query-Parameter `requisitionId`, `rfqId`, `contractId` bleiben der Einstieg.
- `Browser-Use`: Vorbelegungsfaelle sind jetzt reproduzierbar testbar.

## F. Risiken

- `mittel`: Einkaufsanfrage liefert aktuell nur eine flache Bedarfsstruktur; mehrzeilige RFQ-/BANF-Positionen sind nicht Teil dieses Slice.
- `mittel`: Contract-Endpoint liefert keine tiefen Konditionsdaten wie Zahlungsbedingung oder Incoterms fuer alle Vertragstypen.
- `niedrig`: Legacy-Pfade ohne `/api/v1` existieren in anderen Einkaufsseiten weiterhin und muessen separat harmonisiert werden.

## G. Konkrete Empfehlungen

1. Mehrzeilige Anfrage-/RFQ-Strukturen spaeter auf explizite Positionsvertraege erweitern.
2. Vertrags-Endpoint mittelfristig um fachlich nutzbare Einkaufskonditionen erweitern, falls der Rahmenabruf tiefer vorbelegen soll.
3. Verbleibende Einkaufsseiten mit `/api/einkauf/...` auf dieselben `/api/v1/...`-Contracts ziehen.

## Annahmen

- RFQ ist im aktuellen Einkaufspfad keine eigene Ressource, sondern eine Statusphase der Einkaufsanfrage.
- Einkaufsanfragen repraesentieren internen Bedarf und keine Lieferantenbindung.
- `counterpartyId` aus dem Contract-Endpoint ist fuer den aktuellen Slice der beste verfuegbare Partnerbezug fuer den Rahmenabruf.

## Status

**Erstanalyse abgeschlossen** — Procure-to-Pay Vorbelegung dokumentiert.

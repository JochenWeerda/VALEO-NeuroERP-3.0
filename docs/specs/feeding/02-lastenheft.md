---
title: "Fuetterungsberatung — normativer Lastenheft-Index"
type: specification
audience: [produkt, fachlich, architektur, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Navigierbarer normativer Einstieg in Anforderungen, Prioritaeten, Abnahme und Quellen des integrierten Fuetterungsberatungssystems.
---

# 02 — Lastenheft

## 1. Zweck und Quellenvertrag

Dieses Kapitel ist der stabile Einstieg in das vollstaendige, vom Auftraggeber
gelieferte `lastenheft-fuetterungsberatung.md`. Es kuerzt keine Anforderung und
erfindet keine neue Fachnorm. Bei Widerspruch gilt folgende Reihenfolge:

1. freigegebene fachliche Quelle und versionierter Golden-Test;
2. `lastenheft-fuetterungsberatung.md` und stabile FEED-ID;
3. `requirements-traceability.md` fuer den aktuellen Lieferstatus;
4. Kapitel 03–17 fuer Architektur, Bedienung und Umsetzung;
5. produktiver Code, OpenAPI und Migration als Laufzeitvertrag.

Normative Aenderungen benoetigen Requirement-ID, verantwortlichen Slice,
Akzeptanztest und Traceability-Update. Produktnamen, Texte oder Oberflaechen
anderer Anbieter sind keine Quelle fuer VALEO-Vertraege.

## 2. Produktauftrag

VALEO stellt einen geschlossenen, tenant-sicheren Beratungsprozess bereit:

```text
Betrieb → Tiergruppe → Futter/Analyse → Bedarf → Ration/Variante
        → Freigabe → Fuetterungsplan → Ist-Erfassung → Controlling
        → Beratung/Massnahme → Bericht/Einkauf/Integration
```

Das System verbindet fachlich belastbare Berechnung mit nachvollziehbaren
Entscheidungen. Ein Solver-Ergebnis allein ist kein fertiges Produkt: Herkunft,
Version, Warnungen, Freigabe, Ausfuehrung und Wirkung muessen zusammen sichtbar
sein.

## 3. Leitende Muss-Invarianten

| ID | Invariante | Abnahmequelle |
|---|---|---|
| FEED-LH-001 | Jede fachliche Entitaet ist einem Tenant zugeordnet; fremde IDs duerfen weder lesen noch ueberschreiben. | Security-/Repository-Tests |
| FEED-LH-002 | Rollenrecht und Betriebs-Grant werden serverseitig kombiniert. | Authz-Contract-Tests |
| FEED-LH-003 | Freigegebene Versionen sind unveraenderlich; Korrekturen erzeugen Nachfolger. | Workflow-/Audit-Tests |
| FEED-LH-004 | Einheiten, Bezugsbasis und Rundung sind explizit; unbekannt ist niemals numerisch null. | Property-/Golden-Tests |
| FEED-LH-005 | Jede Warnung nennt Regelversion, Ursache, Schwere und betroffene Eingabe. | Evaluation-Contract-Test |
| FEED-LH-006 | Automatisierung darf keine Freigabe, Bestellung oder Maschinenaktion ohne Policy und Human Gate ausfuehren. | Agent-/Action-Security-Eval |
| FEED-LH-007 | Externe Daten bleiben mit Provider, Abrufzeit, Quell-ID und Mappingversion nachweisbar. | Connector-Contract-Test |
| FEED-LH-008 | Mobile und Desktop nutzen denselben Fachvertrag; UI-Varianten duerfen keine eigene Wahrheit bilden. | Component-/E2E-Tests |
| FEED-LH-009 | Geld wird als Decimal/Numeric, nie als binaerer Float persistiert. | Schema-/Property-Test |
| FEED-LH-010 | Extern blockierte Live-Integrationen werden nicht durch Demo- oder Mockdaten als produktiv ausgegeben. | Deployment-/Feature-Gate-Test |

## 4. Anforderungslandkarte

| Bereich | Stabile IDs | Prioritaet | Vertiefung |
|---|---|---|---|
| Mandant, Rollen, Audit | FEED-RBAC-* | MUSS | 04, 05, 06, 16 |
| Betrieb und Tiergruppen | FEED-BUS-*, FEED-HERD-* | MUSS | 04, 05, 07 |
| Futter und Analysen | FEED-MAT-*, FEED-LAB-* | MUSS | 05, 08, 09 |
| Bedarf und Bewertung | FEED-REQ-*, FEED-EVAL-* | MUSS | 09 |
| Ration und Optimierung | FEED-RAT-*, FEED-OPT-* | MUSS | 07, 08, 09 |
| Plan und Ausfuehrung | FEED-PLAN-*, FEED-ACT-* | MUSS | 08, 12 |
| Versorgung und Einkauf | FEED-SUP-* | SOLL/MUSS | 08, 12 |
| Controlling und Leistung | FEED-PERF-* | SOLL | 07, 08 |
| Beratung und Zusammenarbeit | FEED-CONS-*, FEED-COLLAB-* | MUSS/SOLL | 08, 11 |
| Berichte und Mobil | FEED-REP-*, FEED-MOB-* | MUSS/SOLL | 07, 10 |
| Integrationen | FEED-INT-* | SOLL, teils blockiert | 12 |
| UX und NFR | FEED-UI-*, FEED-NFR-* | MUSS | 10, 13 |

Der aktuelle Status jeder Zeile steht ausschliesslich in
`requirements-traceability.md`. Dieses Kapitel fuehrt bewusst keine zweite
IMPLEMENTED-/VERIFIED-Zaehlung.

## 5. Nutzer und Verantwortungen

| Rolle | Kernauftrag | Darf nicht stillschweigend |
|---|---|---|
| Betriebsleiter | Ziele, Kosten, Planfreigabe und Wirkung ueberblicken | fachliche Warnungen wegklicken ohne Begruendung |
| Fuetterungsberater | Daten pruefen, Varianten erstellen, Empfehlung dokumentieren | fremde Betriebe ohne aktiven Grant sehen |
| Rationsspezialist | Bedarf, Restriktionen und Solver fachlich steuern | unversionierte Regelbasis verwenden |
| Herdenmanager | Gruppen- und Leistungsdaten pflegen | freigegebene Ration rueckwirkend aendern |
| Fuetterungspersonal | aktuellen Plan sicher ausfuehren und Ist melden | veralteten Plan ohne Warnung verwenden |
| Einkauf | Bedarf in kontrollierte Beschaffung ueberfuehren | automatische Bestellung ohne Freigabe ausloesen |
| Administrator | Rollen, Grants, Connectoren und Policies verwalten | Tenantgrenzen umgehen |
| Auditor/Leser | Herkunft, Entscheidungen und Versionen nachvollziehen | fachliche Daten mutieren |

## 6. Abnahmestrategie

Eine Anforderung wird erst `VERIFIED`, wenn alle zutreffenden Nachweise vorliegen:

- Domain-/Property-Test fuer Invarianten und Einheiten;
- API-Contract inklusive 400/403/404/409/422;
- Tenant- und Betriebs-Isolation;
- Migrations-/Backfill-Test;
- ScreenDefinition-/Component-/A11y-Test fuer Bedienvertraege;
- Playwright-Journey fuer den Ende-zu-Ende-Nutzen;
- Golden-Test fuer normgebundene Berechnung;
- Audit-/Eventnachweis fuer statusaendernde Aktionen;
- Dokumentations- und Drift-Gates.

Die stabilen Test-IDs stehen in Kapitel 13; die konkrete Reihenfolge und
Red-Green-Refactor-Evidenz stehen im 240-Pakete-Katalog von Kapitel 17.

## 7. Nichtziele und Schutzgrenzen

- keine Kopie fremder Produkttexte, Screens, Workflows oder Designs;
- keine veterinärmedizinische Diagnose oder Therapieentscheidung;
- keine autonome Bestellung, Freigabe oder Maschinensteuerung;
- kein produktiver DDW-/Labor-/Mixerpfad ohne Vertrag, Consent, Credentials,
  Mapping-Abnahme, Egress-Policy und Smoke-Test;
- keine zweite UI-Architektur neben Meridian und der zentralen
  ScreenDefinition-Renderkette;
- keine Prosaformel als Ersatz fuer versionierten Rechenkern und Golden-Test.

## 8. Offene externe Gates

Fachquellen muessen lizenz- und versionsklar vorliegen. Live-Provider benoetigen
Vertrag und technische Sandbox. IdP-Rollen und reale Betriebs-Grants benoetigen
organisatorische Zuweisung. Diese Gates blockieren nur den betroffenen Livepfad,
nicht die Entwicklung neutraler Ports, Fixtures, Validierung und Quarantaene.

## 9. Drift- und Reviewregel

Owner ist `domain/agrar`. Review erfolgt je Feeding-Slice und vollstaendig vor
jeder Releasefreigabe. Geaenderte Anforderungen muessen gleichzeitig in
Lastenheft, Traceability, betroffenem Fachkapitel, Testkatalog und Arbeitspaket
sichtbar sein. Laufzeitdetails werden nicht aus diesem Index generiert.


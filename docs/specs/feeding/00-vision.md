---
title: "00 — Vision und Produktgrenzen der Fuetterungsberatung"
type: explanation
audience: [produkt, fachlich, architektur, entwickler, qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Normatives Produktziel, Nutzenversprechen, Systemgrenzen, Qualitaetsziele und messbare Erfolgskriterien des integrierten Feeding-Bounded-Context.
---

# 00 — Vision

## 1. Produktauftrag

VALEO NeuroERP stellt einen integrierten Arbeitsraum fuer Fuetterungsberater,
Betriebsleiter, Herdenmanager, Fuetterer, Tierarzt, Labor, Handel und Controlling
bereit. Das Produkt verbindet wissenschaftlich reproduzierbare Rationsrechnung
mit Betriebsakte, Freigabe, Ausfuehrung, Soll-Ist-Kontrolle, Massnahmen und Bericht.

Der Erfolg wird nicht daran gemessen, wie viele Solverparameter sichtbar sind,
sondern ob ein berechtigter Nutzer den Kreislauf von einer geaenderten Analyse bis
zur nachweisbaren Wirkung einer freigegebenen Folgeration sicher schliessen kann.

## 2. Problemraum

Heute liegen fachlich relevante Informationen typischerweise in getrennten
Systemen: CRM, Futteranalyse, Herdenmanagement, Warenwirtschaft, Tabellen,
Mischwagen, Papierprotokoll und Beratungsgedaechtnis. Dadurch entstehen:

- veraltete Gruppen-, Analyse-, Preis- oder Bestandsannahmen;
- nicht reproduzierbare Rationsentscheidungen;
- unklare Versionen am Futtertisch;
- manuelle Uebertragung und Medienbrueche;
- Warnungen ohne Ursache, Verantwortung oder Wiedervorlage;
- Auswertungen ohne Verbindung zur wirksamen Rationsversion;
- schwer belegbarer Beratungserfolg.

## 3. Zielzustand

```text
CRM-Betrieb und Grants
  -> Herde und gueltige Tiergruppe
  -> Futter, Charge, Analyse, Preis und Bestand
  -> versionierter Bedarf und Constraints
  -> reproduzierbarer OptimizationRun oder manueller Entwurf
  -> erklaerbare Evaluation und Variantenvergleich
  -> Vier-Augen-Freigabe und unveraenderliche Rationsversion
  -> unveraenderliche Planversion und Mischanweisung
  -> mobile/maschinelle Ist-Rueckmeldung
  -> versionsbezogene Leistung, Abweichung und Aufgabe
  -> Beratungsfall, Wirksamkeit und revisionssicherer Bericht
```

## 4. Normative Produktprinzipien

| ID | Prinzip | Konsequenz |
|---|---|---|
| FEED-VIS-001 | Ein fachlicher Wert hat Herkunft | Quelle, Zeitpunkt, Einheit, Bezug und Schaetzstatus sind sichtbar |
| FEED-VIS-002 | Eine Freigabe veraendert keinen Inhalt | Freigegebene Rations- und Planversionen sind unveraenderlich |
| FEED-VIS-003 | Keine stille Automatik | Solver, Agent und Import erzeugen Vorschlaege/Entwuerfe, nie ungefragte Freigaben |
| FEED-VIS-004 | Unbekannt ist nicht Null | fehlende Werte bleiben `null`/unbekannt und erzeugen bei Bedarf Readiness-Hinweise |
| FEED-VIS-005 | Alltag vor Featuremenge | Rollen sehen die naechste Aufgabe und Ausnahme, nicht einen universellen Monolithen |
| FEED-VIS-006 | Desktop ist Arbeitsgeraet | Tabellen, Tastatur, Dichte, Fokus und Massenvorgaenge haben Vorrang vor Kartenoptik |
| FEED-VIS-007 | Mobil ist Ausfuehrung | Plan lesen, Ist erfassen, Foto/Beobachtung und Konfliktaufloesung funktionieren stalltauglich |
| FEED-VIS-008 | Integration ist vertraglich | Livepfade brauchen Consent, Vertrag, Secret, Egress, Mapping, Audit und Quarantaene |
| FEED-VIS-009 | Fachkern bleibt reproduzierbar | Normversion, Solverparameter, Eingaben, Ergebnis und Tests sind verknuepft |
| FEED-VIS-010 | VALEO bleibt ein ERP | CRM, Einkauf, Lager, DMS, Workflow, Finance und Identity werden wiederverwendet |

## 5. Zielgruppen und wichtigste Ergebnisse

| Rolle | Wichtigstes Ergebnis | Kritischer Fehler, der verhindert werden muss |
|---|---|---|
| Fuetterungsberater | begruendete, vergleichbare und freigabefaehige Variante | Rechnung auf veralteter Analyse oder falschem Betrieb |
| Betriebsleiter | nachvollziehbarer Plan, Kosten und Handlungsbedarf | unkontrollierte Aktivierung oder versteckte Aenderung |
| Herdenmanager | versionsbezogener Soll-Ist-Verlauf | Kennzahl ohne Gruppen-/Zeitbezug |
| Fuetterer | eindeutige aktuelle Mischanweisung | veraltete oder doppelt synchronisierte Planversion |
| Tierarzt | priorisierte Risikoursache mit Datenquelle | Diagnosebehauptung ohne Evidenz |
| Labor | pruefbarer Import und Zuordnung | ungepruefte automatische Aktivierung |
| Einkauf/Lager | planbasierter Bedarf und Reichweite | Optimierung ignoriert Reservierung/Verfuegbarkeit |
| Controlling | IOFC, Kosten, Effizienz und Beratungserfolg | Vergleich ohne Versions-/Datenqualitaetsmarker |
| Administrator | Rollen, Grants, Normen und Connectoren | tenantuebergreifender oder unprotokollierter Zugriff |

## 6. Systemgrenzen

### Im Feeding-Bounded-Context

- FeedingBusiness-Sicht, Standorte, Herden, Tiergruppen und fachliche Grants;
- Fuetterungs-Futterstamm, Referenzwerte, Analyseversionen und Bedarfsprofile;
- Ration, Version, Constraint, OptimizationRun, Evaluation und Freigabe;
- Planversion, Mischanweisung, ActualFeeding und PerformanceRecord;
- Beratungsfall, Beobachtung, Empfehlung, Massnahme und Bericht;
- feeding-spezifische ImportJobs, Mappings, Quarantaene und Events.

### In Nachbarkontexten

- CRM besitzt den Business Partner und Kontakt;
- Lager besitzt physischen Bestand, Charge, Sperrung und Reservierung;
- Einkauf besitzt Bestellung, Kontrakt und Lieferant;
- DMS besitzt Originaldatei und revisionssicheres Dokument;
- Identity besitzt Benutzer, Rollen und IdP-Zuweisung;
- Workflow/Notification besitzt generische Aufgaben- und Kanalzustellung;
- Feed-Chain besitzt Produktion, Qualitaet und Handelsdeklaration.

Feeding speichert nur stabile Referenzen und fachliche Projektionen. Es schreibt
nicht direkt in Tabellen eines Nachbarkontexts.

## 7. Nicht-Ziele

- kein Ersatz fuer tiermedizinische Diagnose oder Behandlung;
- keine unlizenzierte Kopie fremder Software, Texte, Screens oder Designs;
- kein selbst erfundener DDW-/Labor-/Mischwagen-Livevertrag;
- kein zweites CRM, Lager, Einkauf, DMS oder Identity-System;
- kein Big-Bang-Ersatz des getesteten Rationssolvers;
- keine KI-Freigabe und keine Erfindung fehlender Messwerte;
- keine abrechnungsrelevante Geldbuchung aus Solver-Floats.

## 8. Qualitaetsziele

| Rang | Qualitaet | Messbarer Zielzustand |
|---:|---|---|
| 1 | Fachliche Sicherheit | jede freigegebene Version hat Norm-/Analyse-/Preis-/Bestandskontext und Audit |
| 2 | Mandanten- und Ressourcenschutz | Tenant- und Business-Grant-Negativtests fuer jede neue Route |
| 3 | Reproduzierbarkeit | gleicher Input + gleiche Versionen ergibt innerhalb definierter Toleranz gleiches Ergebnis |
| 4 | Bedienbarkeit | Kernjourneys tastaturfaehig; kritische Aktion eindeutig; keine Doppelmutation |
| 5 | Erklaerbarkeit | Warnung nennt Kennzahl, Ziel, Ursache, Quelle und Handlung |
| 6 | Verfuegbarkeit | Offline-Fallback fuer Stallausfuehrung; Integrationsfehler blockieren nicht still |
| 7 | Barrierearmut | WCAG 2.2 AA auf Kernrouten, Status nie nur Farbe |
| 8 | Performance | Listen virtualisiert/paginiert; Interaktion ohne vermeidbare Layoutspruenge |
| 9 | Aenderbarkeit | additive Migrationen, stabile IDs, Alias-/Deprecation-Pfad statt harter Brueche |

## 9. Produkt-KPIs

- Anteil aktiver Planversionen mit aktueller Analyse, Preis und Bestand;
- Zeit von Analyseeingang bis gepruefter Zuordnung;
- Zeit von Entwurf bis Freigabe und von Freigabe bis Futtertisch;
- Anteil Ist-Fuetterungen mit eindeutiger Planversionsreferenz;
- Mischabweichung je Komponentenklasse und Trend;
- offene/ueberfaellige Massnahmen und mittlere Reaktionszeit;
- IOFC-, ECM-, N-Effizienz- und Kostenveraenderung vor/nach Versionswechsel;
- Import-Quarantaenerate und mittlere Aufloesungszeit;
- Anteil fachlicher Mutationen mit Actor, Reason und AuditEvent;
- Nutzererfolg der Rollenjourneys ohne Wechsel in den Experten-Monolithen.

## 10. Releaseziel

- Release A: beratungsfaehig — Betriebsakte bis freigegebener Bericht;
- Release B: betriebsfaehig — Plan, Mobil, Ist und Aufgaben;
- Release C: controllingfaehig — Leistung, Beratung, Integrationen und Wirkung;
- allgemeiner Rollout erst nach Feature-Flag, Pilotbetrieb, Alt/Neu-Vergleich und
  dokumentierter Abnahme durch einen fachkundigen Fuetterungsberater.

## 11. Quellen und Nachweise

- Auftraggeber-Lastenheft: `lastenheft-fuetterungsberatung.md`
- IST: `ist-audit.md`
- Zielarchitektur: `target-architecture.md`
- Anforderungen: `requirements-traceability.md`
- oeffentlicher Funktionsabgleich: `fodjan-help-traceability.md`
- UX-Entscheidung: `docs/adr/adr-041-hybrid-feed-advice-experience.md`
- Designsystem: `docs/design/frontend-design-skill-audit.md`


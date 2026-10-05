---
title: Fütterungsberatung — Funktionsabgleich und Ausbaupfad
type: explanation
audience: [produkt, fachlich, entwickler, qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-14
version: 1.0.0
---

# Fütterungsberatung — Funktionsabgleich und Ausbaupfad

## Zweck und Quellenrahmen

Dieses Dokument übersetzt öffentlich beschriebene Arbeitsabläufe marktüblicher
Fütterungssoftware in eigenständige VALEO-Anforderungen. Es ist keine Kopie eines
Hilfe-Centers und übernimmt weder geschützte Texte noch Screens oder Produktdesigns.

Ausgewertete Themenbereiche:

- [Hilfe-Übersicht](https://fodjan.com/de/hilfe/hilfe/)
- [Rationsplanung und Optimierung](https://fodjan.com/de/hilfe/rationsplanung/)
- [Futterbestand](https://fodjan.com/de/hilfe/futtermittel-erstellen/)
- [Dokumentation](https://fodjan.com/de/hilfe/dokumentation/)
- [Auswertungen](https://fodjan.com/de/hilfe/ueberblick-auswertungen-in-fodjan/)
- [Schnittstellen](https://fodjan.com/de/hilfe/schnittstellen-in-fodjan-ueberblick/)

Die Detailartikel wurden als Funktionshinweise ausgewertet. Maßgeblich für die
fachliche Umsetzung bleiben GfE 2023, DLG-Information 01|2025, der VALEO-Solver
und betriebsindividuelle Freigaben.

## Zielprozess

```text
Betrieb und Tiergruppen
  -> Futterbestand und Analysen
  -> Bedarf, Grenzen und Ziele
  -> Rationsentwurf und Varianten
  -> fachliche Prüfung und Freigabe
  -> Fütterungsbeginn und Mischauftrag
  -> Ist-Fütterung und Restfutter
  -> Soll-Ist-Controlling
  -> verbesserter Folgeentwurf
```

## Funktionsmatrix

| Arbeitsbereich | Zielbild | Stand 2026-07-14 | Nächster Ausbau |
|---|---|---|---|
| Betrieb und Rollen | Betriebe, Berater, Fütterer und Freigaberechte | alle vier Rations-Router erzwingen Rollen serverseitig (READ/WRITE/APPROVE, Connector-Verwaltung = Admin-Level) | betriebsindividuelle Rollenzuweisung im IdP ausrollen |
| Futtergruppen | Tiergruppe, Tierzahl, Laktation, Leistung, Lebendmasse, Fütterungssystem | persistenter, tenantisolierter Gruppenstamm und native Worklist | fachliche Gruppenhistorie aus Herd-Deltas verdichten |
| Futterbestand | Eigene Futtermittel, Preise, Mengen, Chargen und Reichweite | aktive Rationen werden gegen vorhandenen Bestand und deterministische Reichweite geprüft | Chargen-FIFO und reservierte Mischmengen ergänzen |
| Laboranalysen | Atteste importieren, Werte prüfen, für neue Futterversion übernehmen | verifizierte Analysen, Alter und Analysewechsel fließen in den versionierten Readiness-Befund | Labor-Material-Mapping interaktiv auflösen |
| Bedarfsprofil | Erhaltung, Leistung, Mineralstoffe und Inhaltsstoffkorridore | GfE-/DLG-Profile und Constraints vorhanden | verständliche gruppenbezogene Override-Historie |
| Futtermittelgrenzen | Min/Max je Komponente und Fütterungsweg | Wizard plus Zeilen-Fixierung Min=Max | Grenzvorlagen je Gruppe und Saison speichern |
| Rationsentwurf | Komponenten in FM/TM bearbeiten, hinzufügen und entfernen | Zeilen-CRUD in der Workbench umgesetzt | Mischreihenfolge per Tastatur/Drag-and-drop pflegen |
| Optimierungsziele | Kosten, IOFC, Leistung, Gesundheit und Umweltwirkung | mehrstufiger Solver vorhanden | Pareto-Katalog mit mehreren speicherbaren Vorschlägen |
| Alternativen | Austauschbare Futtermittel vorschlagen und Wirkung vorab vergleichen | Vorschläge/Copilot vorhanden | Alternativen nach Bestand, Preis und Restriktionen ranken |
| Tiergesundheit | Mangel/Überschuss, Struktur, Pansen- und DLG-Indikatoren | Diagnose und Warnungsanpassung vorhanden | Maßnahmen mit Verantwortlichem und Fälligkeit nachverfolgen |
| Wirtschaftlichkeit | Kosten je Kuh, je kg ECM, IOFC und Kraftfuttereffizienz | Praxis-KPIs ergänzt | Preisänderungsszenarien und Sensitivität |
| Varianten und Status | Entwurf, geplant, aktiv, gefüttert, archiviert | unveränderliche Versionen, Statusautomat, geplante Aktivierung und Ein-Aktiv-Regel umgesetzt | gefütterte Chargen gegen Version abschließen |
| Zusammenarbeit | Kommentare, Beschreibung, Freigabe und nachvollziehbare Änderung | persistente Reviewgründe, Rollenprüfung und Änderungsaudit | Benachrichtigungskanäle anbinden |
| Ausgabe | Rezept, Auswertung, Vergleich, Teilen und Maschinenexport | PDF-/Review-Pfad und Importseite vorhanden | profilierte Landwirt-/Berater-/Fütterer-Ausgaben |
| Fütterung | Mischfolge, Sollmengen, Restfutter und tatsächlich geladene Mengen | mobiles Protokoll liest die freigegebene aktive Serverversion; Browsercache bleibt Offline-Fallback | Mischwagen-Rückmeldung und Sync-Konflikte |
| Controlling | Aufnahme, Kosten, Effizienz, Stickstoff, Methan und Milchbezug | Tagesreihe (009) plus Langfristtrend-Charts (Soll-Ist je KPI, Lücken statt Nullfabrikation, Methan-Schätzkennzeichnung) und betriebsinterner Gruppen-Benchmark | anonymisierter Betriebsvergleich und Preisszenarien |
| Externe Daten | Labor, Mischwagen, MLP, Milchgüte und AMS | Integrationsimport angelegt | Connector-Readiness, Mapping und Fehlerquarantäne je Betrieb |

## Gelieferter Slice UIX-P0-PORTAL-RATIONS-006

- Portal-Fachseiten verwenden den kanonischen `/api/v1/portal`-Vertrag und
  behandeln leere optionale Listen defensiv.
- Rationskomponenten lassen sich direkt in der Workbench hinzufügen, entfernen
  und über eine kg-FM-Eingabe fixieren. Fixieren wird als identische Min-/Max-
  Grenze an den bestehenden Solver übergeben; Lösen entfernt beide Grenzen.
- Futterkosten werden primär in `ct/kg ECM` gezeigt. Ergänzend zeigt die
  Workbench die Kraftfutter-TM je kg ECM; `€/Kuh/Tag` bleibt im Detail erhalten.
- Der bestehende `ScreenDefinition -> RenderPlan -> Runtime -> Renderer`-Pfad
  wird nicht dupliziert. Die Agrar-Spezialmaske bleibt gemäß Domain Pack ein
  bestehender Spezialrenderer und nutzt die vorhandenen API-/Action-Verträge.

## Zielbildkorrektur FEED-ADVICE-UX-011

Die Spezialmaske wurde anschließend ausdrücklich ohne Bestandsschutz neu
bewertet. ADR-041 ersetzt die bisherige Annahme „Spezialmaske als Portalstart“
durch eine hybride Aufgabenarchitektur:

- `/portal/rationsoptimierung` startet in der nativen ScreenDefinition
  `agrar/feed-advice` über RenderPlan, UniversalMaskRuntime und Renderer.
- Der Solver-Arbeitsplatz wird nur für konkrete Expertentätigkeit lazy geladen.
- Stallarbeit, Bestand, Analysen, Rationslebenszyklus und Controlling sind
  eigenständige, rollengerechte Aufgaben statt lokaler Ansichtsmodi.
- Die Spezialpalette referenziert kein Fremddesign mehr, sondern folgt den aktiven
  VALEO-Semantiktokens.

Die gewichtete Variantenbewertung und UX-Gates stehen in
`docs/design/feed-advice-experience-architecture-2026-07-14.md`.

## Priorisierte Folge-Slices

1. `FEED-ADVICE-LIFECYCLE-007`: **abgeschlossen 2026-07-14** — persistente
   Futtergruppen, unveränderliche Rationsversionen, auditierter Statusautomat,
   geplante Aktivierung und serverseitige aktive Ausführungssnapshots.
2. `FEED-ADVICE-INVENTORY-008`: **abgeschlossen 2026-07-14** — Bestands- und
   Reichweitenprüfung, Analysealter/-wechsel, Preisgültigkeit, native Readiness-
   Worklist sowie auditierte Ausnahme bei blockierter Freigabe/Aktivierung.
3. `FEED-ADVICE-CONTROLLING-009`: **abgeschlossen 2026-07-14** —
   gruppenbezogene, idempotente Soll-Ist-Tagesreihen für Aufnahme, Kosten,
   Milch/ECM, Stickstoffeffizienz und gekennzeichnetes Methan samt nativer
   Meridian-Worklist und kompakter manueller Erfassung.
4. `FEED-ADVICE-CONNECTORS-010`: Labor-, Mischwagen-, MLP-, Milchgüte- und
   AMS-Connectoren mit Mapping, Readiness und Quarantäne. **Teil 1 abgeschlossen
   2026-07-14:** providerneutraler Herd-Data-/DDW-Vertrag, Delta-Sync,
   Consent-/Contract-/Secret-/Egress-Gates und kanonische Beobachtungen. Reale
   DDW-Pfade/Auth bleiben bis zum lizenzierten Partnervertrag bewusst offen.
5. `FEED-ADVICE-TRENDS-012`: **abgeschlossen 2026-07-15** — Langfristtrend-
   Ansicht im Controlling (TM-Aufnahme, Futterkosten, Milch/ECM, N-Effizienz,
   Methan als Soll-Ist-Liniencharts mit rezessiver Soll-Linie; unbekannte
   Werte als Lücke, geschätztes Methan gekennzeichnet) plus betriebsinterner
   Gruppen-Benchmark (Periodenmittel je Fütterungsgruppe, wählbare Kennzahl).
   Baut auf der validierten Token-Chart-Palette (DESIGN-CHARTS-TOKEN-006) und
   konsumiert ausschließlich den bestehenden Serien-Endpoint aus 009 — kein
   neuer API-Vertrag. Anonymisiertes betriebsübergreifendes Benchmarking
   bleibt bewusst offen.

Jeder Folgeslice braucht einen eigenen Workboard-Claim. Neue API-Verträge sind
nach dem Architecture Agent Protocol mit Domain-Pack-, ADR- und Drift-Nachweis
zu liefern.

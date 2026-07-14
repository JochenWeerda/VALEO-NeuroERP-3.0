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
| Betrieb und Rollen | Betriebe, Berater, Fütterer und Freigaberechte | Portal-/Rationszugang vorhanden | Rollen in jeder Mutation serverseitig erzwingen |
| Futtergruppen | Tiergruppe, Tierzahl, Laktation, Leistung, Lebendmasse, Fütterungssystem | im Wizard nutzbar | persistenter Gruppenstamm mit Historie |
| Futterbestand | Eigene Futtermittel, Preise, Mengen, Chargen und Reichweite | Stamm-, Wareneingangs- und Analysepfade vorhanden | Solver direkt mit verfügbarem Bestand und Reichweitenwarnung koppeln |
| Laboranalysen | Atteste importieren, Werte prüfen, für neue Futterversion übernehmen | Grundfutteranalyse und Dokumentimport vorhanden | Analysewechsel als versionierten Rationshinweis anzeigen |
| Bedarfsprofil | Erhaltung, Leistung, Mineralstoffe und Inhaltsstoffkorridore | GfE-/DLG-Profile und Constraints vorhanden | verständliche gruppenbezogene Override-Historie |
| Futtermittelgrenzen | Min/Max je Komponente und Fütterungsweg | Wizard plus Zeilen-Fixierung Min=Max | Grenzvorlagen je Gruppe und Saison speichern |
| Rationsentwurf | Komponenten in FM/TM bearbeiten, hinzufügen und entfernen | Zeilen-CRUD in der Workbench umgesetzt | Mischreihenfolge per Tastatur/Drag-and-drop pflegen |
| Optimierungsziele | Kosten, IOFC, Leistung, Gesundheit und Umweltwirkung | mehrstufiger Solver vorhanden | Pareto-Katalog mit mehreren speicherbaren Vorschlägen |
| Alternativen | Austauschbare Futtermittel vorschlagen und Wirkung vorab vergleichen | Vorschläge/Copilot vorhanden | Alternativen nach Bestand, Preis und Restriktionen ranken |
| Tiergesundheit | Mangel/Überschuss, Struktur, Pansen- und DLG-Indikatoren | Diagnose und Warnungsanpassung vorhanden | Maßnahmen mit Verantwortlichem und Fälligkeit nachverfolgen |
| Wirtschaftlichkeit | Kosten je Kuh, je kg ECM, IOFC und Kraftfuttereffizienz | Praxis-KPIs ergänzt | Preisänderungsszenarien und Sensitivität |
| Varianten und Status | Entwurf, geplant, aktiv, gefüttert, archiviert | UI-Varianten bislang nicht persistent | versionierter Rationskopf mit Fütterungsbeginn und Statusautomat |
| Zusammenarbeit | Kommentare, Beschreibung, Freigabe und nachvollziehbare Änderung | Review vorhanden | persistente Kommentare, Freigabeaudit und Benachrichtigung |
| Ausgabe | Rezept, Auswertung, Vergleich, Teilen und Maschinenexport | PDF-/Review-Pfad und Importseite vorhanden | profilierte Landwirt-/Berater-/Fütterer-Ausgaben |
| Fütterung | Mischfolge, Sollmengen, Restfutter und tatsächlich geladene Mengen | mobiles Protokoll vorhanden | offlinefähiger Ausführungsdialog und Mischwagen-Rückmeldung |
| Controlling | Aufnahme, Kosten, Effizienz, Stickstoff, Methan und Milchbezug | Einzelkennzahlen vorhanden | gemeinsame Zeitreihen mit Gruppen-/Zeitraumfilter und Soll-Ist-Abweichung |
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

## Priorisierte Folge-Slices

1. `FEED-ADVICE-LIFECYCLE-007`: persistente Futtergruppen und Rationsversionen,
   Statusautomat sowie Fütterungsbeginn.
2. `FEED-ADVICE-INVENTORY-008`: Bestands-/Reichweitenprüfung im Solver-Request,
   Analysewechsel und Preisgültigkeit.
3. `FEED-ADVICE-CONTROLLING-009`: gruppenbezogene Soll-Ist-Zeitreihen für
   Aufnahme, Mischgenauigkeit, Kosten, ECM, Stickstoff und Methan.
4. `FEED-ADVICE-CONNECTORS-010`: Labor-, Mischwagen-, MLP-, Milchgüte- und
   AMS-Connectoren mit Mapping, Readiness und Quarantäne. **Teil 1 abgeschlossen
   2026-07-14:** providerneutraler Herd-Data-/DDW-Vertrag, Delta-Sync,
   Consent-/Contract-/Secret-/Egress-Gates und kanonische Beobachtungen. Reale
   DDW-Pfade/Auth bleiben bis zum lizenzierten Partnervertrag bewusst offen.

Jeder Folgeslice braucht einen eigenen Workboard-Claim. Neue API-Verträge sind
nach dem Architecture Agent Protocol mit Domain-Pack-, ADR- und Drift-Nachweis
zu liefern.

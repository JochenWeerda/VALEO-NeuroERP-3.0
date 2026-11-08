---
title: Inhaltsgebundene Basis- und Variantenfassungen der Belegmaske
type: reference
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Belegbasis und Varianten eindeutig versionieren

Die gemeinsame Belegfamilie besitzt jetzt eine getrennte Basis und neun Varianten im quellengesteuerten Inhaltsregister. Die erste Fassung ist 1.0.0. Der bestehende gemeinsame Builder bleibt die einzige Authoring-Quelle; das Register ist dessen erzeugtes, explizit versioniertes Lieferartefakt. Es entstehen keine neun manuell gepflegten Masken und keine weitere Datenbank.

Eine Release-Version wird angehaengt und muss vorwaerts laufen; vorhandene Versionen werden nicht ueberschrieben. Arrays und andere Root-Eigenschaften werden eindeutig ersetzt, nicht positionsweise vermischt. Ein historischer Verweis enthaelt Basisversion/-hash, Variantenkennung/-version/-hash und den Hash der aufgeloesten Originaldefinition. Aufloesen mit einem vorhandenen Verweis verlangt genau diese Inhalte. Auch eine veraenderte Historie mit neu berechneten internen Hashes wird durch den alten Verweis abgewiesen. Das ersetzt keine Signatur gegen einen Angreifer, der Anwendungscode und Datenbank zugleich kontrolliert.

Die native Aufloesung im bisherigen genehmigten Sichtpruefungsmandanten verwendet das Register. Studio uebernimmt die Bindung in Originalsnapshot, Entwurf und bestehende unveraenderbare Historie. Ein bearbeiteter Entwurf behaelt zusaetzlich seine eigene vollstaendige Studio-Revision. Gefaelschte Bindungen werden serverseitig abgewiesen; ein Ursprungsverweis ist weder Freigabe noch Berechtigung. Das Register und seine Aufloesung gehoeren zum Artefakthash der Studio-Abnahme.

ScreenDefinition, Compiler, RenderPlan und beide zentralen Rendererwege tragen die Bindung weiter. Der Cache beruecksichtigt einen reinen Versionswechsel. Die Wurzel der gerenderten Maske weist die verwendete Basis-/Variantenfassung und den Original-Inhaltshash aus. Das Studio zeigt deren Versionsnummern lesbar an.

## Nachweise

Der neue regulaere Pytest-Vertrag prueft den exakten Gleichlauf aller neun Varianten mit dem Builder. Damit scheitert CI bei einer Builderaenderung ohne passende Fassung; kein zusaetzlicher Workflow oder Container ist notwendig. Generatoraufruf mit --check bestanden. 54 Backendfaelle zu Versionen, nativer Aufloesung, Studio-Import und echtem SQL-Freigabeweg bestanden. Die 34 Registry-/Dateivertraege pruefen zusaetzlich atomare Releases, simulierten Schreibabbruch und die Erhaltung eines fremden Schreiberlocks. 38 gezielte Frontend-Vertraege fuer Compiler, Renderer, Dialog, Import und Editor bestanden; TypeScript geprueft. Die anschliessende Gesamtsuite bestand mit 1355 Faellen in 272 Dateien; die abschliessende Praezisierung des Ursprungslabels und DOM-Variantenkennzeichens ist mit den 38 gezielten Vertraegen nachgeprueft. API-Doku und Antwortvertraege: 3676/3676, keine fehlenden Angaben. Godfile-Ratsche unveraendert erfuellt.

Reale lokale Browserabnahme nach erneuter synthetischer Anmeldung: Rechnung als versionierte Ausgangsfassung importiert, nach Neuladen erneut geoeffnet; Anzeige der Ausgangsfassung mit Belegbasis 1.0.0 / Variante 1.0.0, uebereinstimmender Hash an der tatsaechlichen Rendererwurzel. Keine Rechnung oder Buchung angelegt; ausschliesslich Studio-Metadaten im genehmigten Testmandanten. Lokaler Sichtnachweis: artifacts/document-version-acceptance/studio-invoice-version-light.jpg.

Beim Gegenpruefen wurden weitere sachfremde Voreinstellungen im Editor entfernt: Laden oder Uebernehmen einer anderen Maske leert die alte Lieferanten-Anforderung und verwirft eine alte Simulationsanzeige. Der derzeit spezifische Getreide-Dialog oeffnet sich nur auf ausdruecklichen Wunsch oder fuer einen passenden semantischen Entwurf. Dessen Fachfeldkatalog erscheint nur beim passenden Entwurf. Es wird kein allgemeiner Dialog fuer noch nicht implementierte Fachprofile behauptet.

## Noch zu integrieren

Unabhaengige Variantenpflege im Studio, kuratierte Belegdaten-/Command-Bindungen, vollstaendige Kopf-/Positionsbearbeitung, passende Belegkettenprofile, Speicherung der verwendeten Maskenfassung beim Erzeugen neuer Geschaeftsbelege und die Ablösung aller bisherigen Einstiege bleiben offen. Der derzeitige fachliche Freigabeprozess grain.v1 wird nicht aufgeweicht. Kein neuer MCP-Schreibzugriff wird freigeschaltet.

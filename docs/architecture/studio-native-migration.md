---
title: Bestehende Masken versioniert ins Studio uebernehmen
type: explanation
audience: [architect, entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Schrittweise Studio-Uebernahme

Nutzerentscheidung vom 16.10.2026: Bestehende Masken werden versioniert und nach und nach ins Studio umgezogen. Es entsteht weder ein zweiter Entwurfsspeicher noch eine gesonderte Freigabedatenbank. Fuehrend bleibt ScreenDefinition → RenderPlan → UniversalMaskRuntime → UniversalMaskRenderer.

## Ausgangsfassung sichern

Der Studio-Bereich „Vorhandene Maske versionieren“ bietet ausschliesslich serverseitig registrierte Quellen an. Die Auswahl erfolgt nach Bezeichnung; Tabellen- und Spaltenkenntnisse sind nicht erforderlich. Der Server bindet die Uebernahme an den angezeigten SHA-256-Quellstand. Unbekannte, fremde oder inzwischen geaenderte Quellen werden abgewiesen.

Die Ausgangsfassung wird im vorhandenen Studio-Speicher mit eigener Revision, verifiziertem Urheber, Mandant, baseScreenId und vollstaendigem urspruenglichem Definitionssnapshot gesichert. Die bestehende unveraenderbare Studio-Historie erfasst die Erstellung. Idempotenz verhindert doppelte Uebernahme; eine erneute Erstellung mit anderem Schluessel ersetzt keinen vorhandenen Entwurf. Weitere Bearbeitung verwendet den bestehenden Revisionsvergleich.

## Bestehenden Betrieb erhalten

Ein Import aendert keine aktive Maske, keine Rolle, keinen Fachcommand und keinen Beleg. Der Entwurf startet mit migration.stage=baseline und eligible_for_release=false. Die bisherige native Maske bleibt bis zur ausdruecklich geprueften Umstellung fuehrend. Die neun bereits fuer den synthetischen Sichtpruefungsmandanten genehmigten nativen Belegvarianten werden aus ihrem versionierten Code aufgeloest; dieser Bestand ist ebenfalls als Ausgangsquelle importierbar. Er ist kein dauerhafter zweiter Studio-Speicher.

Das fruehere Beleg-Veroeffentlichungsskript ist jetzt eine reine Pruefung dieser nativen Definitionen. Es erzeugt keine erfundenen Bearbeiter oder Zweitfreigeber und keine published_temp-Fassungen. Der alte --apply-Schalter wird mit einer Erklaerung abgewiesen. Frei bearbeitete Studio-Entwuerfe bleiben ausschliesslich dem normalen Studio-Verfahren unterworfen.

## Schrittweise Umstellung

1. Ausgangsfassung importieren und mit Version, Quelle und Urheber nachvollziehbar sichern.
2. Datenquellen, Aktionen und Rechte auf den vorhandenen Capability-/Command-Katalog abbilden; offene Verletzungen sichtbar abarbeiten.
3. Passende Pruefungen absolvieren: Darstellung und mandantengebundene Lesezugriffe fuer reine Lesemasken; zusaetzlich konkrete Fachketten und Wirkungen fuer schreibende Aenderungen.
4. Genau diese gepruefte Revision durch eine andere berechtigte Person freigeben und den Bedienweg kontrolliert umstellen.
5. Den bisherigen Bedienweg erst nach positiver Abnahme entfernen.

Derzeit ist grain.v1 das implementierte fachliche Studio-Freigabeprofil. Der Import behauptet kein weiteres bestandenes Profil. Nicht abgedeckte Commands und Prozesse bleiben gesperrt, bis ein entsprechender Nachweis umgesetzt ist; ein Quellhash oder ein Import ersetzt diesen Nachweis nicht. STUDIO-RELEASE-001 bleibt unveraendert verbindlich.

## Gemeinsame Belegmaske statt neuer Einzelmasken

Die bisherigen rund 14 Belegeinstiege sind nicht mit 14 unabhaengigen Studio-Masken gleichzusetzen. Der vorhandene Beleg-Builder liefert neun Fachvarianten aus einer gemeinsamen Quelle. Ausgangsimporte sichern den Bestand. Die ergaenzte Versionsbindung trennt gemeinsame Basisversion, Variantenkennung/-version und aufgeloeste Gesamtfassung; ein Editor fuer unabhaengige Variantenfreigaben steht noch aus. Ein spaeterer Belegfall verweist auf genau diese freigegebene Kombination. Bestehende Beleg- und Buchungshistorien werden dadurch nicht umgeschrieben.

Noch ausstehend sind die vollstaendige Alt-Einstieg-zu-Zielvariante-Matrix, Studio-Katalogbindungen fuer alle Belegdatenquellen und Commands, vollstaendige Kopf-/Positionsbearbeitung, fachliche Belegketten-Pruefprofile und die Browserabnahme jeder abgeloesten Funktion. Der aktuelle Ausgangsimport behauptet weder deren Fertigstellung noch die vollstaendige Migration aller 14 Einstiege.

## Versionsbindung der Belegfamilie (16.10.2026)

Die Belegfamilie besitzt jetzt ein versioniertes Inhaltsregister unter config/document_screen_versions.json. Die gemeinsame Basis und die neun Varianten sind getrennt gespeichert; ein Variantenpatch ersetzt ganze Root-Eigenschaften, insbesondere Arrays. Es gibt kein mehrdeutiges positionsweises Zusammenmischen von Tabellen oder Aktionen. Der gemeinsame Python-Builder bleibt die Authoring-Quelle. Der Generator prueft dessen exakte Uebereinstimmung mit der aktuellen materialisierten Fassung; ein regulaerer Pytest-Vertrag macht Abweichungen in CI rot.

Eine neue Fassung wird ausschliesslich mit expliziter Release-Version angehaengt. Ein exklusiver Schreiberlock und atomarer Dateiaustausch schuetzen gegen verlorene parallele Releases und teilweise gelesene Dateien. Vorhandene Basis-/Variantenfassungen werden nicht ersetzt. Jeder Verweis enthaelt Basisversion/-hash, Variantenkennung/-version/-hash und den Hash der vollstaendig aufgeloesten Ausgangsdefinition. Historische Verweise werden mit genau ihrer Fassung aufgeloest, nicht ueber den aktuellen Alias; geaenderte Inhalte werden auch nach einer Neuberechnung interner Registerhashes durch den bereits gespeicherten Verweis erkannt.

Die native Belegaufloesung verwendet dieses Register im bisher genehmigten Sichtpruefungsmandanten. Studio uebernimmt den originalen Verweis in Ausgangssnapshot und unveraenderbare Historie. Ein editierter Studio-Entwurf hat weiterhin seine eigene vollstaendige Revision; der Ursprungsverweis ist kein Freigabenachweis fuer diese Aenderung. Gefaelschte Ursprungsverweise scheitern an der serverseitigen Validierung. Compiler-Cache und RenderPlan tragen die Bindung durchgaengig weiter; ein alleiniger Versionswechsel liefert keinen alten RenderPlan. Die Browserwurzel weist die dargestellte Fassung aus.

Der Generator erstellt Releases der gemeinsamen Familie; das ist noch kein Editor fuer unabhaengige Variantenfreigaben. Fachliche Command-/Datenquellenkataloge, vollstaendige Positionsbearbeitung, Belegkettenprofile, dauerhafte Zuordnung beim Erzeugen neuer Geschaeftsbelege und die komplette Alt-Einstieg-Migration bleiben als naechste Integrationsschritte offen. Die bestehende Studio-Freigabepruefung wird nicht gelockert.

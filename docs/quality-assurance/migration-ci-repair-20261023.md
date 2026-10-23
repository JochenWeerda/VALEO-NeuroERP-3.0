---
title: PR38 CI-Vertragsreparatur und Sicherheitsupdates 2026-10-23
type: reference
owner: Codex
status: teilweise abgeschlossen
last_reviewed: 2026-10-23
---

# PR38 CI-Vertragsreparatur

## Bestaetigte Ursachen und Korrekturen

Die CI meldete16 Masken-Sicherheitsfehler: eine vorhandene Fahrer-Definition war nicht mehr registriert, und sechs wiederhergestellte verbotene Agentenaktionen fehlten im abgeleiteten Gefahrenvertrag. Die Registrierung ist wieder vorhanden; der hydrierte Vertrag projiziert tatsaechliche forbiddenForAgents-Beschraenkungen aus den vorhandenen aktiven Fachaktionen. Dies vergibt weder Berechtigungen noch Freigaben und schaltet keinen MCP-Write frei.

Der Routengenerator verlor nach der Migration den oeffentlichen Suchparameter search, obwohl der geschlossene Deep-Link-Vertrag ihn weiterhin vorsieht. Er bleibt explizit Teil der geschlossenen Vereinigung. Geprueft wird nach echter Neuerzeugung statt nur gegen eine aeltere eingecheckte Datei.

Drei CRM-Native-Einstiege referenzierten unregistrierte IDs mit literalem /:id statt der gemeinsamen PartyNativePage. Weitere KIM-/Kunden-Cockpit- und Pflege-Adapter verloren ihre Weiterleitung. Zehn genau nachgewiesene Einstiege wurden wieder an vorhandene gemeinsame Vertraege gebunden. Zwei Kontrollsichten verwenden wieder denselben idempotenten Domain-Command wie die gemeinsame Belegkontrolle. Neue Parent-Builder bleiben erhalten; keine pauschale Seitenruecknahme und keine neue Handmade-Oberflaeche.

Das Handbuch nahm einen Register-Snapshot vor der Stamm-Registrierung und hing dadurch von vorherigen Imports ab. Es vervollstaendigt jetzt zuerst das Register und verwendet sortierte hydrierte Definitionen. Das Handbuch und die weiteren Projektionen wurden neu erzeugt. Sieben Slice-Vertraege wurden mit vorhandenen Zielen, Tests und ehrlichen Abnahmegrenzen vervollstaendigt; kein Runtime-/Browser-Siegel wurde erfunden.

Die Dokumentationsheuristik erkennt nun tatsaechlich transitive statische und verzoegerte Imports. Kommentare und String-Beispiele erzeugen keine Kanten; verwaiste Zyklen bleiben rot. Legacy-Suffixe allein sind keine Ausnahme. Der gemeinsame PartyNativePage-Renderer wird nach funktionaler Pruefung als echter Runtime-Pfad erkannt; versteckte Runtime-Huellen bleiben ausgeschlossen.

## Sicherheitsupdates

Offiziell bestaetigte Korrekturversionen, kohärent in requirements.txt aktualisiert:

- GitPython3.2.1: [GHSA-83vg-56qc-22m7](https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-83vg-56qc-22m7).
- Black26.10.1: [GHSA-cg8m-r9f2-5wm2](https://github.com/advisories/GHSA-cg8m-r9f2-5wm2).
- OpenTelemetryAPI/SDK/HTTP-Exporter1.45.1 und Instrumentierung0.66b1: [GHSA-xcq7-p3pf-p88h](https://github.com/advisories/GHSA-xcq7-p3pf-p88h). Die Versionen und gegenseitigen Abhaengigkeiten wurden direkt gegen PyPI-Metadaten geprueft.

Die komplette requirements.txt wurde ohne Aenderung der laufenden Umgebung frisch aufgeloest. Alle155 daraus ermittelten direkten und transitiven Pakete wurden explizit auditiert: keine bekannten Schwachstellen. --no-deps ueberspringt hier keine transitive Abhaengigkeit; die vollstaendig aufgeloeste155er-Liste wird als Eingabe verwendet. Keine Ausnahme hinzugefuegt. Gepatchte Pakete wurden ausschliesslich in einem lokalen Pruefverzeichnis installiert. Ein echter HTTP-Request mit SQL-Ausfuehrung erzeugt unter der neuen OTel-Gruppe nachweislich HTTP- und Datenbank-Spans, ohne Exportnetzwerk und ohne PostgreSQL-Schreibzugriff.

## Nachweise

- 849 betroffene Backend-, Generator- und Readiness-Vertragsfaelle bestanden.
- Zusaetzlicher gepatchter OTel-/Generatorlauf21 bestanden; Runtime-Evidenz9 bestanden.
- Zwoelf gezielte CRM-/Routingfaelle bestanden, davon fuenf neue echte Renderfaelle fuer kanonische Maskenkennung, Datensatz-ID-Vorrang und Deep-Link-Abschnitt.
- Gesamte Frontend-Typpruefung nach Routenneuerzeugung bestanden.
- Handbuch-, Aktionsrechte-, CLI-, MCP- und Studio-Katalog-Checks bestanden;848 native Katalogdefinitionen. Keine Live-Veroeffentlichung durch Katalogerzeugung.
- Sieben unveraenderte Slice-Readiness-Pruefungen bestanden.

## Nicht abgeschlossen

Der diagnostische komplette UI-Lauf ergibt1700 Tests:1482 bestanden,218 fehlgeschlagen in52 Dateien. Drei echte Bedienfehler liegen im aktiven fremden Start-Dashboard-/Workspace-Claim;215 Fehler in51 Dateien sind Quelltext-Assertions. Diese sind vor einer Ablösung auf echte Fach-/Navigationsvertraege zu pruefen, nicht pauschal zu loeschen oder als irrelevant zu deklarieren. Die fuenf nachtraeglich angelegten neuen CRM-Renderfaelle sind zusaetzlich separat gruen geprueft.

Der Dokumentationslauf ist trotz verbesserter Importanalyse noch rot: zuletzt272 Seiten ohne nachgewiesene Route/Nav-Erreichbarkeit. Keine Baseline erhoeht. Ein Legacy-Name alleine berechtigt nicht zur Loeschung; echte Verbraucher und Fachparitaet sind vorher zu pruefen. Statische Studio-Gates melden weiter fehlende echte API-/Runtime-Nachweise. PR38 bleibt Entwurf; main wird nicht mit unvollstaendig abgenommenem Bestand ersetzt. Gemeinsamer Pruefstand und fremde Arbeitskopien bleiben geschuetzt.

## Getrennter main-Sicherheitshotfix

Der kleine vier-Dateien-Hotfix d61993b9e liegt auf main und ist als Elternstand in den Reparaturzweig integriert. Er aktiviert keine Maskenmigration. GitHub hat den direkten Push mit den bestehenden Adminrechten akzeptiert und dabei die PR-/Statusvorgaben als umgangen protokolliert; lokale Schutzpruefungen wurden eingehalten, der GitHub-Gesamtnachlauf ist separat abzuwarten. Siehe security-patches-20261023.md.

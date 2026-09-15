---
title: Risikobasierter Security-Dependency-Gate
type: reference
audience: [entwickler, agent, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-09-15
---

# Risikobasierter Security-Dependency-Gate

## Release-Regel

Keine bekannte, praktisch ausnutzbare kritische Schwachstelle darf unbehandelt
in ein Release gelangen. Eine alte Versionsnummer allein erzwingt keinen
Major-Sprung. Fehlende Erkenntnisse sind keine Freigabe: unbekannte oder noch
nicht belegte Befunde blockieren konservativ ebenfalls, unabhaengig von Severity.

Dependabot liefert Signale und Security-PRs. Es erhaelt weder Merge-Rechte noch
einen automatischen Upgrade-Auftrag. `.github/dependabot.yml` aktiviert die
Manifest-Abdeckung fuer Root und Services und begrenzt Routine-Version-PRs
auf null; Security-PRs bleiben moeglich. Das entspricht der
[GitHub-Dokumentation](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates).
Major-Updates werden nicht pauschal ignoriert: ein erforderlicher Fix darf als
PR vorgeschlagen werden, benoetigt aber Kompatibilitaetsnachweis und Review.
Die Repository-Einstellung fuer Security-Updates wird damit nicht umgeschaltet.

## Entscheidungsablauf

1. pip-audit loest das vollstaendige Service-Manifest auf und erzeugt einen
   unveraenderten Rohbericht. Scanner-/Aufloesefehler blockieren.
2. `scripts/security_dependency_gate.py` ordnet jeden Befund einer exakten
   Manifest-/Paket-/Versions-/Advisory-Bewertung zu. CVE-Aliase werden erkannt.
3. Nur `not_affected` mit nachgewiesen unerreichbarem Angriffspfad ist derzeit
   als Freigabe implementiert. `accepted_risk`, erreichbare Pfade oder
   allgemeine Freitext-Ausnahmen werden nicht akzeptiert. Weitere nachweisbare
   Kompensationsmassnahmen brauchen einen eigenen maschinenpruefbaren Kontrolltyp.
4. Owner, Quellen, Begruendung, Review-Datum, Ablaufdatum (maximal 90 Tage),
   Quell-/Manifest-/Deployment-Fingerprints und Kontrollpruefung sind Pflicht.
   Neue oder geaenderte Dateien im geprueften Bereich machen die Bewertung
   ungueltig. Kein automatisches Erneuern von Fingerprints oder Review-Fristen.
5. Der Rohbericht bleibt bestehen. `dependency-decision.json` zeigt jede
   Einordnung; `status.json` unterscheidet Scanner-Exit und Gate-Exit. Duplikate
   werden nur in der Entscheidungssicht zusammengefasst.

Die Entscheidung ist deterministisch. Ein LLM darf den Befund untersuchen und
eine Bewertung als Aenderung vorschlagen, aber nicht im CI eine Ausnahme
herbeibegruenden, Pins aendern oder selbst mergen. CODEOWNERS bindet Policy und
Gate-Code an das bestehende Maintainer-Review. Neue Bewertungen gehoeren in
reviewbare Aenderungen mit Negativ- und Positivnachweis.

## ChromaDB 0.5.23 in services/ai

Bereits vorhandene Bewertung aus `config/security/triage-exceptions.json`
und `tests/test_chromadb_embedded_only_contract.py` erneut geprueft und fuer
den Service-Dependency-Gate enger gebunden: nur die genaue Version 0.5.23,
nur dieses Manifest, nur drei CVEs, gueltig bis 2026-10-15.

| Befund | Voraussetzung | Ergebnis im geprueften Service |
|---|---|---|
| [CVE-2026-45833](https://github.com/advisories/GHSA-36p7-vc44-83pf) | Chroma-Server-API und manipulierte Collection-Modellkonfiguration | Serverpfad nicht erreichbar |
| [CVE-2026-45830](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr) | Autorisierung ueber die Chroma-Server-API | Serverpfad nicht erreichbar |
| [CVE-2026-45831](https://github.com/advisories/GHSA-xph7-9rjv-w5fr) | Chroma SimpleRBACAuthorizationProvider im Serverbetrieb | Provider nicht im Einsatz |

Die Bibliothek bleibt verwundbar; ihre bekannte Angriffsvoraussetzung besteht
in diesem geprueften Einsatz nicht. Der Kontrolltyp prueft PersistentClient,
Server-/Remote-Code-Muster sowie die gesichteten Service-, Compose- und
Kubernetes-Dateien. Fingerprints sichern den gesamten betrachteten Quellstand.
Das beweist weder allgemeine ERP-Mandantentrennung noch fremde, ausserhalb des
Repositorys betriebene Deployments. Aenderungen des Betriebsmodells erfordern
vor Auslieferung eine neue Bewertung.

## Transformers 4.46.3

Der aktuelle CI-Audit auf a9b720a75 enthaelt 26 unterschiedliche
Transformers-Befunde: unter anderem Modell-/Checkpoint-Deserialisierung,
Konfigurations-Codeausfuehrung, Tokenizer-/Regex-Pfade und Datei-/URL-Verarbeitung.
Der Resolver-Konflikt mit ChromaDB ist ein Kompatibilitaetsbefund, keine
Sicherheitskontrolle. Kein direkter Import im Anwendungscode ist ein Hinweis,
aber noch kein belastbarer Nachweis aller transitiven Modellladepfade.

Deshalb keine pauschale Freigabe fuer Transformers. Die 26 Befunde bleiben
im Gate blockierend, bis genaue Aufruf-/Datenpfade und wirksame Kontrollen je
Befund belegt sind. Der Agent erzwingt keinen Major-Sprung als Ersatz fuer diese
Analyse. Eine unbenutzte Abhaengigkeit entfernen, einen engen Backport anwenden,
einen Ladepfad begrenzen oder kompatibel aktualisieren sind moegliche,
separat zu pruefende Massnahmen.

## Einbindung und Nachweise

`service-security.yml` ist auch als Workflow wiederverwendbar und prueft die
uebergebene Release-SHA. `release-gates.yml` verlangt dessen Erfolg, bevor die
bestehenden Release-Pruefungen beginnen; Staging und Produktion haengen bereits
von diesem wiederverwendbaren Gate ab. Damit genuegt ein gruener alter Scan
nicht: Ablauf und aktuelle Aufloesung werden fuer den Release neu geprueft.
Kein Deployment wurde ausgefuehrt, bestehende Branch-Protection unveraendert.

- Neun Policy-Regressionen und neun Audit-Runner-Regressionen bestanden.
- Realer CI-Bericht aus Run 34898484483: drei Chroma-Befunde als `not_affected`,
  26 Transformers-Befunde blockierend; Release-Entscheidung bleibt false.
- Integrationstest: Scanner-Exit 1 bleibt dokumentiert, waehrend ausschliesslich
  bestaetigte unerreichbare Befunde Gate-Exit 0 ergeben koennen.
- Ablauf, erreichbarer Angriffspfad, neue/geaenderte Quellen, falsche Version,
  widerspruechliche Bewertungen und unvollstaendige Inventare blockieren.

Die fruehere Regel dieses Service-Audits, dass jeder Versionsbefund ohne
Bewertung blockiert, wird mit dem ausdruecklichen Nutzerauftrag vom 2026-09-15
praezisiert. Bestehende Root-, Container- und SAST-Gates bleiben unveraendert.

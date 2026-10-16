---
title: ChromaDB Reachability-Nachweis beider Verbraucher
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Befristete ChromaDB-Bewertung

Der Service-Security-Job blockierte wegen der am 15. Oktober abgelaufenen drei bestehenden Bewertungen fuer chromadb 0.5.23. Die Bewertung wurde anhand des unveraenderten Linux-pip-audit-Berichts, der kanonischen Quellen und der aktuellen Advisory-Eintraege erneuert. Die Advisories nennen weiterhin keine korrigierte Version: [Code Injection](https://github.com/advisories/GHSA-36p7-vc44-83pf), [Server-Grenzen](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr), [Server-Autorisierung](https://github.com/advisories/GHSA-xph7-9rjv-w5fr).

Beide Verbraucher verwenden eingebettete Clients: PersistentClient im AI-Dienst und Client mit lokalen Settings im Hauptbackend. Die erfassten Compose- und Kubernetes-Pfade enthalten keinen Chroma-Server, keinen Remote-Client und keine Remote-Code-Konfiguration. Seit der vorherigen Bewertung hat sich docker-compose.yml geaendert; diese Deploymentfassung wurde erneut in die Kontrolle einbezogen. Dies ist ausschliesslich ein Nachweis zur Erreichbarkeit dieser drei Server-Schwachstellen, keine allgemeine Aussage zur Sicherheit aller RAG-Datenzugriffe.

Zusaetzlich wurde eine Nachweisluecke geschlossen: app/infrastructure/rag/vector_store.py gehoert jetzt zum Fingerprint und zur eingebetteten Betriebskontrolle. Damit sind 98 statt 97 Dateien erfasst. Auch ein neu eingefuehrter Remote-Client in diesem zweiten Verbraucher blockiert nach einer blossen Hash-Erneuerung weiterhin. Unbekannte Findings, Versionswechsel, Hash-Drift und Ablauf bleiben sperrend. Keine neue Ausnahme, kein deaktivierter Scan, keine neue Abhaengigkeit.

## Nachweis

Neun vorhandene Gate-Tests und zwoelf Tests mit dem zweiten Verbraucher bestehen; darin drei neue Vertraege fuer Aenderung, Entfernung und serverseitige Betriebsarten (fuenf negative Varianten). Drei vorhandene Embedded-Only-Vertraege bestehen ebenfalls. Der originale Scannerbericht bleibt unveraendert mit Exitcode 1 und drei Findings; die separate Auswertung ergibt drei nicht erreichbare Findings und null unbewertete Findings. Die Bewertung gilt bis ausschliesslich 2026-10-23 und muss bei jeder Aenderung der Quellen oder Deployments frueher erneuert werden. Keine Datenbank oder Container erzeugt.

Die lokale Pruefung ersetzt nicht den abschliessenden gruenen GitHub-Service-Security-Lauf. Tabellenkatalog-Drift und verbleibende Backend-Vertraege sind gesonderte CI-Befunde.

## Automatische Regression in der Backend-CI

Der bestehende Service-Security-Workflow ruft die bisherige Gate-Suite direkt auf und entdeckt neue Script-Testdateien nicht automatisch. Ein eigener Pytest-Vertrag fuehrt deshalb die zwoelf Backend-Policy-Faelle als isolierte Unittest-Suite aus, propagiert jeden Fehler und weist auch eine versehentliche Null-Test-Ausfuehrung zurueck. Der Pytest-Vertrag besteht; er verwendet weder Kompatibilitaets-App noch Datenbank. Fremde Workflowdateien und Tests wurden nicht geaendert.

---
title: Rekursive Stabilisierung Mahnversand und MCP-Prozessbetrieb
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Belegte CI-Vertragsfehler und blockierenden MCP-Prozessbetrieb ohne Gate-Ausnahmen korrigieren.
---

# Rekursive Stabilisierung

## Mahnversand

[Quality Gate 38126182106](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38126182106)
meldete genau einen Frontendfehler bei 1062 bestandenen Tests: Die zwei neuen
Mahnversand-Buttons deklarierten gleichzeitig size=sm und min-h-touch, entgegen
dem bestehenden 44-px-Vertrag. Nur die konkurrierende Groessendeklaration entfernt;
Versand, Sperren, Beschriftungen und Fehlerfeedback erhalten. Bestehende 111 UIX-
und fuenf Versandtests unveraendert gruen: 116 Tests, 32,08 Sekunden.
Keine neue Seitenarchitektur oder Abschwaechung des Meridian-Vertrags.

## Deterministischer Geheimnisvertrag

Der vollstaendige develop-[Lauf 38126200584](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38126200584)
bestand 17327 Backendtests; genau ein Test scheiterte, weil die zufaellige Base64-
Darstellung eines AES-GCM-Chiffrats die zwei Buchstaben pw enthielt. Dieser Zufall
ist kein Klartextnachweis. Der Krypto-Vertrag wurde aus der DB-Suite in eine
datenbankfreie Datei verlagert und durch zehn echte AEAD-Pruefungen ersetzt:
Format/Laenge, Roundtrip, andere Mandanten/Zwecke/Schluessel, manipulierte Nonce,
Chiffrat und Tag sowie fehlender Schluessel. Eine gezielt gewaehlte Testnonce
reproduziert die Buchstabenuebereinstimmung deterministisch. Die Produktkrypto
und deren Zufallsquelle bleiben unveraendert.

## MCP-Prozessbetrieb

Der bestehende lokale Node-Adapter blockierte den Eventloop beim Start/Lesen,
hatte kein Zeitlimit und liess den Kindprozess gerade bei Erfolg weiterlaufen.
Asyncio-Prozessaufrufe ersetzen die blockierenden Aufrufe. Standardzeitlimit
30 Sekunden, explizit endlich und positiv; Antwort wird nach JSON-RPC-Version,
Aufrufkennung und Ergebnisobjekt geprueft. Benachrichtigungen vor der Antwort
werden verarbeitet. Fehler liefern wie bisher None; Abbruch bleibt ein Abbruch.

Jeder Pfad bereinigt den Kindprozess einschliesslich stdout-Drain, terminate,
begrenztem Warten und kill als Rueckfall. Optionales stderr wird verworfen:
kein voller Fehlerkanal und keine ungeprueften privaten Servertexte im Log.
Echte lokale Node-Proben pruefen Erfolg, Benachrichtigung, vollen stderr-Kanal,
ungueltiges JSON/Version/ID/Ergebnis, Fehlerantwort, EOF, Zeitlimit und Abbruch.
Jeder erzeugte Testprozess wird nachweislich beendet; waehrend einer langsamen
Antwort laeuft der Eventloop weiter. 19 MCP-Proben bestanden, einschliesslich
eines Servers, der unter POSIX terminate ignoriert (Windows beendet direkt).
Zusammen mit zehn Krypto-Vertraegen 29 Tests in 10,25 Sekunden, ohne
Datenbank/Netz/Docker. Alle 13 Dokumentationsgeneratorchecks auf isoliertem
Lieferstand bestanden ohne Artefaktdrift. ESLint der Mahnversand-Datei erfolgreich.

Grundlagen: [Python Asyncio-Prozesse](https://docs.python.org/3.11/library/asyncio-subprocess.html)
und [MCP-stdio-Vertrag](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports).

## Grenzen und Folgeabnahme

Der Node-Adapter behalt den bestehenden einzelnen tools/call-Aufruf. Ein
vollstaendiger MCP-Initialize-/Capability-Handshake und der fachliche PSM-Import
des bestehenden Agrar-Endpunkts sind damit nicht abgenommen. Dessen bisheriger
Importpfad und Mandantenfallback bleiben gesondert zu pruefen. Kein Recht wird
durch diese Transportkorrektur verliehen.

Pruefstand --status meldete fehlende DATABASE_URL/TEST_DATABASE_URL. Alle neuen
Pruefungen sind datenbankfrei; keine neue DB, Migration, Ruecksetzung oder
Dockerinstanz. Fremde Frontend-, Personal- und Generatorarbeitsfassungen erhalten.
Vollstaendiger GitHub-/Sonar-Abschluss bleibt bis zum tatsaechlichen Ergebnis offen.

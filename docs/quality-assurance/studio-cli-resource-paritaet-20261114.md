---
title: CLI-Ressourcenaktionen sicher ausfuehren
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-11-14
---

# CLI-Ressourcenaktionen sicher ausfuehren

Slice `STUDIO-CLI-RESOURCE-PARITAET-20261114`. Vor der Aenderung zeigte
ein Mock-Transport-Test fuer die native Sortenmaske, dass `--modus dryRun`
einen echten PUT mit `_mode` sendete und Erfolg meldete. Die fachliche
Ressourcenroute interpretiert diesen Umschlag nicht als Trockenlauf.

Der gemeinsame CLI-Adapter laesst ausschliesslich die im Maskenadapter
festgelegten Kombinationen aus Screen, Methode und Pfad zu, nur fuer
menschliche Execute-Aufrufe mit sicherer Objektkennung. Deklarierte
Eingabefelder werden als unverpackter Ressourcenkoerper gesendet.
Fuer die sechs versionierten CRM-Segmentaktionen und DSGVO-Export/-Loeschung
belegen die serverseitigen Pydantic-Modelle `Mutation`, `SegmentUpdate`,
`MemberInput` und `ProcessPayload` die gesonderten Steuerfelder: gelesene
positive Version, echter Idempotenzschluessel und bei geforderter Begruendung
der Auditgrund. Diese Werte stammen aus CLI-Optionen, nicht ungeprueft aus
Eingabedaten. Andere Ressourcen mit solchen Zusatzvertraegen bleiben gesperrt.
Bei ungewissem Ausgang wird der Schluessel fuer eine bewusste Wiederholung
angezeigt; die CLI wiederholt keine Ressourcenmutation automatisch. Rechte und Mandant
prueft weiterhin der Server.

Antworten muessen die erwartete sichere ID bestaetigen; bei Kindanlage
gelten abweichende Kind-ID und gegebenenfalls Kampagnenbezug, bei den
freigegebenen Loeschwegen ausschliesslich leeres HTTP 204. Die generischen
Studio-Kommandos behalten ihre bestehenden Vorschau-Modi.

Pruefung ohne Datenbank: der neue Test war vor der Reparatur rot; danach
CLI- und Lesekontrakte erfolgreich, darunter Vorschau-Sperre, einmaliger
PUT, menschliche Identitaet, unsichere IDs, Antwort- und Kindpruefung,
204 sowie kein Retry bei ungewissem POST-Ausgang. Zusaetzlich pruefen 27
Ressourcentests alle acht versionierten Aktionen mit den echten Servermodellen,
fehlender Version oder Begruendung und Wiederholungsschluessel bei Fehlern.
Der separate generierte
CLI-Registercheck ist nach dem vom Lead durchgefuehrten Generatorlauf erneut
zu pruefen. Keine neue Datenbank oder Dockerressource.

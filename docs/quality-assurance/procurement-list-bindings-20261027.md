---
title: Kanonische Bindung der Einkaufslisten
type: qa
audience: [entwickler, qa, agent]
owner: Codex
status: active
last_reviewed: 2026-10-27
---

# Einkaufsanfragen und Auftragsbestaetigungen

Die gerouteten Listenseiten forderten nicht registrierte Screen-IDs mit dem
Suffix -liste an. Sie verwenden jetzt die bestehenden kanonischen Definitionen
einkauf/anfragen und einkauf/auftragsbestaetigungen. Test-IDs, Fachaktionen,
Rollen und Endpunkte bleiben erhalten.

Zwei gezielt ausgewaehlte bestehende UIX-Faelle bestanden mit tatsaechlicher
NativeListPage, Runtime und Renderer: Suche/Touch-Arbeitsbereich sowie echter
CSV-Export. Die beiden Definitionen stammen unveraendert aus den registrierten
Python-Buildern. HTTP/Auth und Browsergeometrie sind ersetzt. 27 weitere Faelle
derselben Datei waren nur durch den CLI-Filter nicht ausgewaehlt; sie sind
keine permanent uebersprungenen Tests und keine zusaetzliche Freigabe.

Die gemeinsame UIX-Testmigration und deren Fixtures werden im zugehoerigen
Frontend-Lieferslice integriert. Die hier korrigierten produktiven Bindungen
beseitigen die fehlgeschlagenen Definitionabrufe; eine Gesamt-CI-Freigabe
wird daraus nicht abgeleitet.

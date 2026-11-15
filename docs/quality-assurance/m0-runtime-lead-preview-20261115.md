---
title: M0 Runtime-Sweep – Lead-Vorschau mit geprueftem Kontext
owner: Codex
status: lokal abgenommen
last_reviewed: 2026-11-15
---

# Lead-Vorschau: Mandantenkontext

Der Runtime-Sweep auf main 2338578d0 (Lauf 43700900452) meldete HTTP500 fuer
GET /api/v1/crm/lead-generierung/preview. Der Router konstruierte den Service
ohne Mandant; dessen Konstruktor lehnt einen fehlenden Mandanten absichtlich ab.
Die Vorschau nutzt nun dieselbe get_tenant_id-Abhaengigkeit wie die uebrigen
Wege des Routers und gibt diesen geprueften Kontext an den Service weiter.
Kein Standardmandant, keine Header-/Query-basierte Auswahl eingefuehrt.

Gegenprobe auf altem Router: sechs von zehn HTTP-Vertraegen rot (500 statt
200/401/403). Nach Korrektur zehn bestanden in 1,34 Sekunden. Die Faelle decken
zwei Sicherheitskontexte, GAP/LKV/beide, unveraenderte Filter, ungueltige Grenzen
und Abweisung vor Quelldatenzugriff bei fehlender Identitaet oder ungeprueftem
Kontext ab. Der echte Servicekonstruktor, die echte Vorschau, Mandantenabhaengigkeit
und Antwortvalidierung laufen; Anbieteridentitaet und oeffentliche Quelldaten
sind explizite Attrappen. Kein JWT-, PostgreSQL-/RLS- oder Echt-GAP-Nachweis.

Der erste lokale Versuch ohne die fuer den HTTP-Testclient erforderlichen
Thread-/Socketrechte wurde ohne Testergebnis beendet. Der berechtigte Lauf
reproduzierte die sechs roten Faelle; nur dieser ist die Gegenprobe. Kein
Datenbankzugriff (TEST_DATABASE_URL entfernt, DB-Port unbenutzbar), kein Docker-
Build oder neuer Container. Bestehende Starlette-Testclient-Deprecation bleibt.

Noch offen: echter Runtime-Sweep des neuen SHA auf dem vorhandenen CI-Jobaufbau.
Der PR137-Integrationskopf 4c7c6374b wurde durch diesen getrennten Slice nicht geaendert.

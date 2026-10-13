---
title: Studio-Inhaltsupdates pruefen angezeigte Revision
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Studio-Inhaltsupdate ohne verlorene Aenderung

PUT /api/v1/studio/drafts/{id} verlangt expected_revision zusammen mit definition. Der Speicher prueft die Revision innerhalb der bestehenden SQL-Zeilensperre beziehungsweise des Testspeicher-Locks, bevor Inhalt oder Editor geaendert werden. Ein fehlendes Feld ergibt 422; ein inzwischen geaenderter Entwurf ergibt 409 ohne Ueberschreibung. Die Mandantenpruefung kommt vor dem Revisionsvergleich; eine fremde ID ergibt 404.

POST /api/v1/studio/drafts ersetzt keinen vorhandenen Entwurf derselben Mandanten-/Screenkennung mehr. Ein vorhandener Datensatz oder eine konkurrierende SQL-Unique-Verletzung ergibt 409. Eine unbekannte ausdrueckliche Entwurfs-ID legt auch im Testspeicher keinen neuen Datensatz mehr an. Fuer interne administrative Speicheraufrufe bleibt die Revision optional; der HTTP-Pfad und der Pilotinstaller uebergeben sie ausdruecklich.

Der Studio-Client sendet beim Aktualisieren die gespeicherte Revision. Ohne geladenen Stand scheitert der Client bereits vor dem Request. Der Pilot-Belegmaskeninstaller verwendet nach Retirement dessen zurueckgegebene neue Revision zum Speichern der erneuerten Definition.

Abnahme: 111 Python-/SQL-Faelle auf valeo_probe (control_findings_20261013); neun Frontendfaelle in vier Studio-Dateien. Neue HTTP-Faelle pruefen fehlende und veraltete Revision, abgewiesene Create-Dublette sowie 404 eines fremden Updates. Der SQL-Fall schreibt zwei Bearbeiter nacheinander mit demselben gelesenen Ausgangsstand: Der zweite wird abgewiesen und der erste bleibt exakt erhalten. Dies ist keine Last-/Konkurrenzabnahme zweier gleichzeitig laufender DB-Transaktionen.

Architekturentscheidung fuer die naechste Arbeit: Das zentrale AuditLog verlangt einen lokalen user_id-Fremdschluessel und user_email. Der verifizierte externe Studio-Subject darf dafuer nicht durch einen erfundenen Benutzer oder eine erfundene E-Mail ersetzt werden. Studio braucht eine eigene transaktionale, mandantengebundene Freigabe-/Revisionshistorie mit gepruefter Subjectidentitaet und idempotenten Ergebnissen. Diese Historie und Idempotenz bei unklaren Commit-Ergebnissen sind weiterhin offen, ebenso die Prozessvariantensimulation und reale Browserabnahme. Keine Migration oder neue Datenbank in diesem Slice.

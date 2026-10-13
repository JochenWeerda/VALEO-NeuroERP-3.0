---
title: Studio-Reviewstatus und revisionsgebundene Uebergaenge
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Studio-Review-Lifecycle

Der zentrale Speicher erlaubt ausschliesslich draft -> review -> published_temp -> retired. Jede Speicherung eines editierbaren Entwurfs setzt den Status auf draft, auch wenn er zuvor review war. Veroeffentlichte Inhalte sind nicht editierbar. Ein zurueckgezogener Entwurf kann durch erneutes Speichern als neue Kandidatenfassung wieder beginnen; direktes Wiederfreigeben ist unzulaessig. Dieselben Regeln gelten im SQL- und expliziten Testspeicher.

Alle drei HTTP-Statusaktionen (submit-review, publish, retire) verlangen die angezeigte expected_revision. Sie vergleichen den gelesenen Stand und benutzen anschliessend den Snapshotvergleich unter Schreibsperre. Veraltete Revisionen und unzulaessige Statuswechsel ergeben 409. Fehlende Eingabefelder ergeben 422. Die gepruefte menschliche Adminrolle und Vier-Augen-Regel bleiben fuer Publikation bestehen. Die UI bietet Einreichung nur aus draft und Freigabe nur aus review an; Einreichung sendet jetzt ebenfalls die gespeicherte Revision.

Der bestehende Pilot-Belegmasken-Installer zieht eine geaenderte veroeffentlichte Definition zuerst zurueck. Er speichert dann den neuen Kandidaten und durchlaeuft Einreichung/Publikation jeweils mit Snapshot. Der alte direkte Sprung published_temp -> draft entfaellt. Der Installer ist weiterhin ein lokal administrierter Testmandantenpfad, keine Agentenfreischaltung.

Abnahme: 88 Python-/PostgreSQL-Faelle in den fuenf Studio-Dateien plus test_belegmasken_veroeffentlichen.py; neun Vitest-Faelle in vier Studio-Dateien. Der neue HTTP-Lifecyclevertrag deckt fehlende Einreichung, Bearbeitung nach Review, erneute Einreichung, unzulaessige Statusspruenge und Retirement mit falscher/richtiger Revision ab. Der SQL-Vertrag belegt Reviewentwertung durch Bearbeitung und zwei abgelehnte Publikationsversuche. Bestehende Tests bestaetigen die Erneuerung der neun Pilotmasken.

Handbuch-Abnahme: Alle fuenf committed HEAD-Dateien unter docs/agent-handbuch stimmen nach Generatornormalisierung mit den aktuell generierten Inhalten ueberein. Der lokale --check bleibt wegen fremder aelterer Arbeitskopien rot. Diese wurden bewusst erhalten; es ist kein Drift des committed Handbuchs nachgewiesen.

Offen: Unveraenderliche Revisions-/Publikationshistorie, Idempotenz der Statusaktionen, Versionsschutz beim Inhaltsupdate, starke Produktionsfreigabe und reale Browserabnahme. Interne Statusaufrufer benoetigen weiterhin eigene vertrauenswuerdige Administration; der Store allein authentifiziert nicht. Der vorhandene SQL-zu-Speicher-Fallback bleibt separat zu schliessen. Prozessvarianten und ihre fachliche Simulation bleiben Teil des Gesamtziels.

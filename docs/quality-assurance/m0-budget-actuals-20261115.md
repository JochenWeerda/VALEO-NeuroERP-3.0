---
title: M0 Budget-Istwerte bei Datenbankfehlern
owner: Codex
status: lokal abgenommen
last_reviewed: 2026-11-15
---

# Budgetfehler bleiben unbekannte Istwerte

budget_summary setzte bei jedem Fehler der Journalabfrage actual auf 0.0.
Dadurch sah ein nicht ermittelbarer Verbrauch wie ein gepruefter Nullverbrauch
aus. Der Fehlerpfad fuehrt jetzt rollback aus und liefert eine neutrale503-
Antwort. Vorhandene Nullwerte, leere Aggregatergebnisse und erfolgreiche Werte
bleiben erhalten. Keine SQL-/DSN-Details gelangen in diese Antwort.

Gegenprobe: zwei von fuenf gezielten Faellen vor Fix rot. Nach Fix fuenf gruen;
mit dem ersten Rohware-Vertragsstand gemeinsam21pass in2,08s (ueberlappende
Zahlen nicht summieren). Getestet wird der echte Handler mit expliziten DB-
Ergebnisattrappen, kein echter PostgreSQL- oder Transaktionsnachweis. Die
Rollback-Methode wird genau einmal aufgerufen; keine Commit-Nebenwirkung.

Das erzeugt keine fehlenden Budgettabellen. Deren kanonische Migration und die
fachliche Konten-/Periodenabgrenzung der Istwertsumme sind separat zu klaeren;
dieser Slice bestaetigt keine vollstaendige Budgetierungsfunktion.

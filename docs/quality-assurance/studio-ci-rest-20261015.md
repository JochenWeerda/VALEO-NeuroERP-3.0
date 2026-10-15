---
title: Studio-CI-Reste nach Vier-Augen-Abnahme
type: reference
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-15
---

# Gemeinsamer Studio-Vertrag und Pruefstand-Grenze

fetchStudioDrafts deklariert die bestehende Listenhuelle ausdruecklich als drafts?: StudioDraftRecord[]. Damit bleibt die bestehende leere Liste als Rueckfall erhalten; response.data hat einen geprueften Typ statt unknown. Die fokussierte TypeScript-Projektpruefung bestand ohne Fehler. Fuenf Studio-API-/RunPage-Faelle bestanden.

Die vorhandene SQL-Fixture verwendet pruefstand_erlaubt aus dem kanonischen testgrenze-Helfer statt einer eigenen Namenspruefung. require_db prueft weiterhin die ausdrueckliche Test-URL und verhindert die Entwicklungsdatenbank. Keine neue Datenbank, kein neuer Container, keine Ruecksetzung.

Der geteilte Arbeitsbaum besitzt eine fremde aeltere Fassung von tests/testgrenze.py. Fuer die lokale SQL-Abnahme wurde ausschliesslich dessen bereits committierte HEAD-Fassung im Testprozess geladen; die fremde Datei bleibt unangetastet. Ein normaler CI-Checkout hat den Helfer bereits.

Beide SQL-Persistenzfaelle bestanden mit explizit ausgewaehltem valeo_probe, strikter Datenbankanforderung und ohne Skips. Die vorhandene Fixture prueft Speicherung ueber Prozessspeichergrenzen sowie Mandantenisolation und Vier Augen. Pruefstandrevision: portal_lohndienst_persistenz_20261014. Die Typpruefung tsconfig.typecheck.json endete mit Status 0.

Der develop-Abgleich bleibt durch den privaten Benutzerkennungsbefund im vorhandenen CI-Startskript blockiert. Keine Ausnahme, kein Hook-Bypass und kein Force-Push. Der bestehende Handshake zum aktiven CI-GRUEN-Claim bleibt fuehrend.

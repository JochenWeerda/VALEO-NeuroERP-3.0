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

## Weitere direkte CI-Befunde

Der aktuelle PostgreSQL-Lauf auf 7c7e1791e hatte einen Fehler und zwoelf Setupfehler an festen Datenbanknamen. Auch der eigenstaendige Idempotenz-Sperrtest verwendet jetzt denselben kanonischen Waechter; require_db bleibt vorgeschaltet. Der gemeinsame Nachlauf fuer Persistenz, Historie, Speicherschluessel und Statuswiederholung bestand mit zehn SQL-Faellen, ohne Skips (sieben bewusst nicht ausgewaehlte Unitfaelle). Die acht vorangegangenen gezielten SQL-Nachweise werden dadurch nicht als zusaetzliche unabhaengige Faelle doppelt gezaehlt.

Auch die drei weiteren SQL-Snapshotfaelle derselben korrigierten Fixture bestanden separat: Konflikt nach Anzeige, Bearbeitung invalidiert Review und Schutz des ersten Schreibers. Damit sind alle dreizehn im aktuellen CI-Lauf betroffenen Faelle lokal positiv nachgeprueft; keine Skips in diesen Abnahmen. Eine erfolgreiche Wiederholung des GitHub-Jobs wird damit nicht vorweggenommen.

Der Docs-Build scheiterte am Service-Inventar. Die neue Inventarprojektion stammt vollstaendig aus den committierten HEAD-Diensten und dem kanonischen Generator: 293 Module, einschliesslich der zwei neuen Studio-Dienste und des bereits committierten SEPA-Generators. Andere Inventare und die fremde aeltere Arbeitskopie wurden nicht ueberschrieben. Der Vergleich ignoriert ausschliesslich die vom bestehenden Drift-Checker ausgeschlossenen Datums-/Generatorzeilen.

Quellen: [PostgreSQL-Lauf](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38681909839), [Docs-Build](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38681909847). Der E2E-Smoke desselben Stands war erfolgreich; dies ist keine Aussage ueber alle anderen CI-Gates.

## GitHub-Bestaetigung und exakte Ratsche

Der Meilenstein f9ad9934e bestaetigt die Korrekturen auch auf GitHub: [Docs-Build erfolgreich](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683206741) einschliesslich Inventar-/Handbuchabgleich und [PostgreSQL-Prueflauf erfolgreich](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683206799).

Die unabhaengige Integritaetspruefung meldete anschliessend eine nicht nachgezogene Senkung: process_kernel_api.py ist nach der eigenen Vertragsbereinigung 6170 statt 6184 Zeilen lang. Nur dieser Baselineeintrag wird auf die echte committierte Laenge gesenkt. Alle anderen Eintraege, die 1000-Zeilen-Grenze und das Verbot von Erhoehungen bleiben bestehen. Die Ratschenfunktion prueft die Projektion gegen alle committierten Endpunkte, ohne fremde Arbeitsdateien zu ersetzen. Der GitHub-Nachlauf dieser letzten Baselinesenkung steht bei Auslieferung noch aus; die gesamte Quality-Pipeline wird nicht als gruen ausgegeben.

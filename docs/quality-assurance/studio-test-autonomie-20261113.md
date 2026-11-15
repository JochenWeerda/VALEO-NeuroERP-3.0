# Autonomie: schnelle Verhaltenstests (13.11.2026)

Der Slice ergänzt `tests/test_agent_autonomie.py` um datenbankfreie Tests der bestehenden Autonomie- und Qualitätsentscheidungen in `tests/test_agent_autonomie_unit.py`. Die Datenbankgrenze liefert kontrollierte Fakten und zeichnet Schreibversuche auf; Qualitätsmodell, Rollenprüfung, Vertrauensstufe und Entscheidung werden nicht ersetzt. Es wird die eingecheckte Autonomiepolitik verwendet.

Abgedeckt sind Grenzwerte der Startphase und der Fehler-, Befund- und Einwandquoten; ein bestandener Testnachweis exakt an der Altersgrenze, veraltete, fehlgeschlagene und fehlende Nachweise; Politik- und Delegationsgrenze, Risikoanforderung, Einwand und fachliche Ablehnung. Die Tests vergleichen ausgewählte Entscheidungen mit den Vertrauensstufen A0/A1/A2 und prüfen, dass Autor, unberechtigte Rolle und Agent keine Politikfreigabe erteilen. Verschachtelte Agenten- und Einzelfreigabekontexte werden auch nach einer Ausnahme zurückgesetzt.

Prüfung im Arbeitsbaum `artifacts/psm-zulassungen-20261104`: `python -m pytest --noconftest -o addopts= tests/test_agent_autonomie_unit.py -q` — **26 bestanden**. Nach erfolgreichem Lauf meldete die lokale Windows-Python-Umgebung beim Aufräumen von `pyreadline3` einen ignorierten `OSError`; der Prozess endete mit Code 0.

Die simulierte Grenze beweist weder SQL, Persistenz, Transaktionen, RLS noch das Zusammenspiel realer HTTP-Wege. Dafür bleiben die bestehenden PostgreSQL-Integrationstests erforderlich; in diesem Slice wurde keine Datenbank gestartet, zurückgesetzt oder verändert.

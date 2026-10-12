# Offene Posten: verifizierter Audit-Urheber

Stand: 2026-10-12. Slice `OPEN-ITEMS-VERIFIED-ACTOR-20261012`.

Der lokale Audit-Helfer vertraute `X-User-ID` oder einem ohne Signaturprüfung
dekodierten JWT-Rumpf. Beide Werte waren vom Aufrufer austauschbar.
Er verwendet jetzt ausschließlich `current_identity().subject` aus dem
verifizierten Ausführungskontext. Fehlende, abgelaufene oder widerrufene
Identität wird durch die bestehende Identitätsgrenze abgewiesen; ein fehlender
Request erzeugt keinen anonymen Ersatzurheber.

Die fünf fokussierten Verträge prüfen gefälschte Header und Token-Rümpfe sowie
fehlenden Kontext. Sie isolieren die Urheberauswahl; die Sitzungsprüfung wird
in diesen Unit-Tests ausdrücklich ersetzt. Sie beweisen daher keine
Token-Signaturprüfung. Die bestehenden RSA-/Sitzungsverträge bleiben maßgeblich.
Die 178 bestehenden Rollenverträge werden gemeinsam erneut ausgeführt.

Erster abgeschlossener Lauf: 183 Tests bestanden, eine Warnung, 154,46 Sekunden.
Der Prozess scheiterte zusätzlich am globalen Coverage-Grenzwert: Die beiden
ausgewählten Dateien ergeben 42,33 Prozent für die gesamte Anwendung, gefordert
sind 60 Prozent. Dies ist keine bestandene Gesamt-Coverage-Abnahme. Eine
separate gezielte Funktionsabnahme verwendet `-o addopts=''`; die versionierte
Konfiguration und der CI-Grenzwert werden nicht verändert.

Durch Entfernen der überholten Dekodierung liegt `open_items.py` wieder unter
der Godfile-Grenze. Keine Baseline-Ausnahme, keine fachliche Buchungsänderung,
keine Datenbank-, Container- oder Migrationsanlage.

Noch offen für die systemweite Audit-Abnahme: Der gemeinsame FIBU-Audit-Helfer
enthält ebenfalls Header-Rückfälle; die Mahnaktion nimmt einen Operator aus
dem Aktionsrumpf. Diese Änderung schließt ausschließlich den hier geprüften
lokalen Helfer und behauptet keine vollständige Audit-Sicherheit.

---
title: Batch-11-Kundenliste CI-Nachlauf
status: aktiv
last_reviewed: 2026-11-14
---

# Kundenliste: Auswahl und Navigation

Der bisherige Batch-11-Test nahm einen exakt so benannten Kunden-Button an.
Der Renderer hat unterschiedliche Desktop- und Touch-Bedienwege; auf der
Touch-Karte gehoeren weitere Feldwerte zum zugaenglichen Namen. Der Test setzt
nun beide Geraetemodi ausdruecklich: Desktop-Auswahl per Enter auf der
fokussierbaren Zeile und Touch-Auswahl per Kundenkarte. In beiden Faellen
prueft er die beschriftete Vollansicht-Aktion und die Route zur ausgewaehlten
Kundenakte sowie das Ausbleiben eines Schreibaufrufs. Der registrierte
Routenbaum fuehrt `/crm/kunden/:id` auf Customer 360.

Der komplette gezielte Batch-11-Lauf bestand mit 61 Tests (hoechstens zwei
Worker). Eine Gegenprobe ohne Desktop-Zeilenauswahl schlug fehl, weil die
Vollansicht-Aktion fehlte. Die unveraenderte Batch-11/12-Fixture wurde zusaetzlich
gegen die kanonischen Python-Builder verglichen. Der urspruengliche Test lief
lokal im Standardmodus gruen; die CI-Meldung reproduzierte sich daher nicht
unveraendert lokal. Der Nachweis verwendet synthetische HTTP-Daten und JSDOM;
er ersetzt keine Browser- oder Backendabnahme.

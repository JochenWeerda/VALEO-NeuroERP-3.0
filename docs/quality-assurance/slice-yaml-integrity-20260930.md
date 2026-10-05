---
title: Eindeutige Slice-YAMLs statt unsichtbarer Governance-Vertraege
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-30
description: Historische Schlussmarken lesen und echte YAML-Widersprueche verhindern.
---

# Slice-YAML-Integritaet

Der bisherige `yaml.safe_load` scheiterte an leeren Schlussdokumenten und
`_find_slice_yaml` verschluckte den Formfehler als angeblich fehlenden Slice.
Ein einfaches Lesen nur des ersten Dokuments haette dagegen befuellte zweite
Vertraege still verworfen. Beide Verhaltensweisen sind jetzt ausgeschlossen.

`valeo_slice.py` verwendet einen SafeLoader mit eindeutigen Schluesseln,
liest alle Dokumente und erlaubt genau ein befuelltes Mapping. Leere
Schlussdokumente sind kompatibel. Mehrere befuellte Dokumente, doppelte
Schluessel, nichtskalare Schluessel und unsichere YAML-Tags sind konkrete
Fehler mit Pfad/Zeile. Mehrfach definierte Slice-IDs sind ein Widerspruch.

Die strikte Erstinventur der 290 YAMLs zeigte 19 echte Formfehler, zusaetzlich
zum Problem der leeren Schlussmarken. Ausschliesslich abgeschlossene
historische Slices wurden syntaktisch normalisiert:

- Plain-Text-Listen mit Doppelpunkten/Anfuehrungszeichen als gefaltete
  Textskalare serialisiert; Inhalte, Owner und Status bleiben erhalten.
- Zwei Masken-Slices hatten disjunkte Header-/Inhaltsdokumente. Sie sind
  jeweils ein Mapping; kein Feld wurde verworfen.
- Im Security-Remainder stand `coordination` zweimal. Beide Saetze stehen
  jetzt in einem Feld; der alte Loader hatte den ersten still ueberschrieben.

Nach Normalisierung: **290 von 290 YAMLs eindeutig lesbar, null Formfehler,
keine mehrfach definierten kanonischen Slice-IDs**. Der Bestandstest und
gezielte Negativtests verhindern Rueckfaelle; sie laufen im unabhaengigen
Quality-Gate-Job. Historische Fachlieferungen wurden nicht erneut umgesetzt.

Nachweis: 20 CLI-Vertragstests nach Erstkorrektur; anschliessend zusammen mit
den Verbesserungsvertraegen 90 Tests bestanden. Darunter Schutz gegen
leere Schlussmarken, zweite Verträge, doppelte Schluessel und doppelte IDs.

Grenze: 21 Legacy-YAMLs verwenden nur `id`, und viele alte Slices enthalten
nicht den heutigen AI-Harness. Syntaktische Lesbarkeit ist kein Nachweis
vollstaendiger aktueller Vertraege. Fachliche Felder und Abnahmen werden nicht
aus Platzhaltern erfunden. Der bestehende Changed-Slice-Readiness-Check bleibt
fuer neue oder geaenderte aktive Slices verbindlich. Gegen den Ausgangscommit
bewiesene reine Syntaxreparaturen eines bereits abgeschlossenen Legacy-Slice
brauchen keinen nachtraeglich erfundenen Harness: ein konservativer Textvergleich
erlaubt nur Blockskalare, Dokumentmarken und die bekannte zusammengefuehrte
Koordinationszeile. Inhalt, Status und Identitaet bleiben gleich. Inhalts- oder
Statusaenderungen verlangen weiterhin den vollen Vertrag; neue Dateien sind
niemals Legacy. Drei echte CLI-Vertragstests sichern diese Grenze.

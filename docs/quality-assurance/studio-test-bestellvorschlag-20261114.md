---
title: Studio-Testmigration Bestellvorschlag
status: aktiv
last_reviewed: 2026-11-14
owner: Codex
---

# Bestellvorschlag: drei Familienvarianten

Drei erwartete Fehlschlaege der alten Seitenquelltext-Pruefung fuer Lager,
Rohware und Verkauf ersetzt `bestellvorschlag-studio.test.tsx` durch zwoelf
Verhaltenstests. Die echten Seiten, Renderer und Runtime verarbeiten jeweils
die aus dem Familienregister materialisierte Definition. Der Test prueft
synthetische Tabellendaten, Variantenwechsel, die zugehoerigen Speicherwege
und Eingaben, die fehlende Schaltflaeche ohne projiziertes Fachrecht,
HTTP-403/409-Ablehnung ohne Erfolgsmeldung sowie Doppelaufrufschutz bei
laufendem Speichern. Die alte Variable `pendingAction` und konkrete Farbnamen
sind keine Bestandteile des neuen Vertrags.

Die Fixture `bestellvorschlag-family.json` wurde durch
`family_definition('bestellvorschlag', variante)` erzeugt; der neue
`test_bestellvorschlag_studio_fixture.py` vergleicht alle drei Fassungen mit dem
aktuellen Register. Die UI fragt das Masken-Daten-Gateway ab, dessen deklarierte
fachliche Quelle pro Variante wird ebenfalls geprueft. HTTP, Identitaet,
Navigation und Toast sind simuliert. Dadurch sind weder serverseitige Rollen-
und Mandantenpruefung noch echte Bestell- oder Browserablaeufe abgenommen.

Gezielt geprueft am 14.11.2026: Vitest 12/12 bestanden (18,66 s, maximal zwei
Worker), Fixture-Pruefung 1/1 bestanden (67,99 s). Radix meldete fehlende
Dialogbeschreibungen im Testlauf; das ist ein offener Accessibility-Befund.
Kein Build, keine Datenbank und keine Gesamtsuite.

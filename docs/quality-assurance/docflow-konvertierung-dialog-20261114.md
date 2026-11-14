---
title: Umwandlungsdialog DocFlow UI-Test
status: aktiv
last_reviewed: 2026-11-14
---

# Umwandlungsdialog mit Teilmengen

Vier gezielte Frontendtests fuehren den echten allgemeinen Eingabe- und
Vorschau-Dialog mit einer deklarativ definierten Umwandlungsaktion aus. Sie
belegen den vollstaendigen Optionsabruf fuer den ausgewaehlten Folgebeleg,
Einheit und Restmenge, die Uebernahme von vier von sechs Einheiten und den
vollstaendigen Auswahl- und Versionsumschlag bei Vorschau und Ausfuehrung.
Die zweite Position bleibt mit null erhalten. Das Beispiel besitzt keine
Preisberechtigung.

Weitere Tests belegen, dass eine abgelehnte Vorschau keine Ausfuehrung anstoesst
und die Eingabe erhaelt, dass veraltete Optionsdaten keinen Dialog oeffnen und
dass nach Navigation eine spaete Antwort verworfen sowie ein doppelter Klick
nicht doppelt geladen wird. Ergebnis: vier Tests bestanden, hoechstens zwei
Worker.

Screen-Definition, Runtime-Grenze und HTTP-Antworten sind kontrollierte
Testdaten; die generischen Dialog- und Tabellenkomponenten laufen echt. Dieser
Nachweis ersetzt keine Datenbank-, Authentifizierungs- oder Browserabnahme und
prueft den Umschlag an der Runtime-Grenze, nicht den HTTP-Adapter oder die
serverseitige Mengenpruefung.

Nach Integration wurde die Aktionsdefinition durch eine aus dem echten
Sales-Order-Builder erzeugte JSON-Fixture ersetzt. Ein Python-Vertrag
vergleicht diese vollstaendig mit dem aktuellen Builder. Die vier Dialogtests
bestehen weiterhin; der Test kann so keine veraltete Handdefinition behalten.
Der gezielte Frontendnachlauf fuer Auswahl, Transport und Dialog umfasst
48 bestandene Faelle (ueberlappend zu frueheren Laeufen).

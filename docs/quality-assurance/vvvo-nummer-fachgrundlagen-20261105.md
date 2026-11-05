---
title: VVVO-Nummer - Fachgrundlagen und Einsatz im Agrarhandel
type: reference
audience: [agent, entwickler, fachbereich, qa]
owner: Codex Lead
status: recherchiert
last_reviewed: 2026-11-05
version: 1.0.0
---

# VVVO-Nummer: Registrierung, Lieferzuordnung und Wiedervorlage

Recherche auf Nutzerauftrag am 05.11.2026; die folgenden Konsequenzen sind ein Implementierungsrahmen, keine Behauptung bereits implementierter Lieferpruefungen.

## Amtliche Registrierung

[§26 ViehVerkV](https://www.gesetze-im-internet.de/viehverkv_2007/__26.html) verlangt die Anzeige der dort genannten Tierhaltungen vor Taetigkeitsbeginn und unverzuegliche Aenderungsmeldungen. Die zustaendige Stelle vergibt eine zwoelfstellige Registriernummer. Die Pflicht ist nicht auf gewerbliche Grossbetriebe beschraenkt.

Die [Niedersaechsische Tierseuchenkasse](https://w.ndstsk.de/faq/6) ordnet die Nummer dem tatsaechlichen Tierhaltungsstandort zu; mehrere Standorte erhalten grundsaetzlich eigene Nummern. Ihre Darstellung enthaelt zusaetzlich den Laendercode 276. Ein ERP darf deshalb Kundenadresse, Rechnungsempfaenger und Tierhaltungsstandort nicht gleichsetzen; Nummern als Zeichenfolge mit fuehrenden Nullen behandeln.

## Futtermittellieferung und QS

[QS-Leitfaden Futtermittelwirtschaft 01.01.2026, 4.20.1, Seiten 50–51](https://q-s.de/services/files/dl/downloadcenter/c-futtermittelwirtschaft/2026/leitfaden/deutsch/Leitfaden_Futtermittelwirtschaft_01_01.2026.pdf): Bei direkter Lieferung loser Mischfuttermittel an landwirtschaftliche Endabnehmer muss im QS-Geltungsbereich die Standortnummer aktiv erfragt, dokumentiert und einem Warenbegleitpapier zugeordnet werden. Verantwortlich ist der Haendler mit direkter Kundenbeziehung; eine bereits passende Herstellerdokumentation muss nicht doppelt erstellt werden. Fuer Einzelfutter, Barverkauf und verpackte/gesackte Ware wird dieses Verfahren empfohlen. Das ist eine QS-Anforderung, keine aus §26 folgende allgemeine Rechnungsangabe.

## Keine pauschale Nummern-Erneuerung

Die genannten Vorschriften belegen keine allgemeine jaehrliche Erneuerung oder einen automatischen Ablauf der VVVO-Nummer. Jahresmeldungen bestimmter Tierbestaende nach §26 Absatz3 sind etwas anderes. [LAVES](https://www.laves.niedersachsen.de/startseite/futtermittel/informationen_fur_landwirtschaftliche_betriebe/anzeige-betrieblicher-veranderung-auf-landwirtschaftlichen-betrieben-184272.html) beschreibt jaehrliche Bestaetigungen einer Futtermittelregistrierung im Rahmen von Liefervertraegen. Daraus folgt keine universelle VVVO-Ablauffrist.

Die Registrierung als Futtermittelunternehmen ist ein eigener Sachverhalt; siehe [LAVES zur Registrierung](https://www.laves.niedersachsen.de/startseite/futtermittel/informationen_fur_landwirtschaftliche_betriebe/registrierung-gemass-futtermittelhygieneverordnung-fmhyvo-fur-landwirtschaftliche-betriebe-197760.html). VVVO, InVeKoS, Futtermittelregistrierung und QS-Zertifizierung nicht ungeprueft zu einem Status zusammenziehen.

## Folgerungen fuer VALEO

- Standortnummer am Liefer-/Tierhaltungsstandort fuehren; mehrere Nummern pro Kunde ermoeglichen.
- Pflicht anhand Ware, Gebinde, Lieferfall und anwendbarem Qualitaetssystem entscheiden; keine pauschale Pflicht fuer jeden Kunden oder jeden Artikel.
- Lieferbeleg behaelt den zum Vorgang gehoerenden Standort-/Nummernstand; spaetere Stammdatenpflege darf alte Belege nicht umschreiben.
- Formatpruefung belegt keine amtliche Existenz oder QS-Lieferberechtigung. Angaben, Quelle und Bestaetigung getrennt nachweisen.
- Die vorhandene Servicefrist von 365 Tagen ist lediglich bestehende interne Wiedervorlage. Fehlender interner Termin beweist weder ungueltige Nummer noch fehlende amtliche Registrierung; keine automatische Liefersperre daraus ableiten.

Die aktuelle SQL-Faelligkeitskorrektur zeigt solche offenen Wiedervorlagen an. Eine gesetzliche Prueffrist oder neue Fachfreigabe wird dadurch nicht geschaffen.

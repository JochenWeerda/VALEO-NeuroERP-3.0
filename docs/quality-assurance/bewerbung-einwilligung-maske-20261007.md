# Die Masken zur Einwilligung (Slice BEWERBUNG-EINWILLIGUNG-MASKE-20261007)

Stand: 2026-10-07 · Welle 2, Slice 25 · schließt offenen Punkt 2 aus
[Die Einwilligung zur längeren Aufbewahrung](bewerbung-einwilligung-20261006.md)

## Auftrag

Erteilen, Widerrufen und Fassungen anlegen waren nur über die API erreichbar. Art. 7
Abs. 3 DSGVO meint auch die **Zugänglichkeit**: Der Widerruf gehört an eine Stelle,
die das Personalbüro ohne Umwege findet. Vorgabe: **keine handgebaute Maske**, sondern
Mask-Builder und Screen Definitions.

## Warum dieser Weg

Die vollständig generische `UniversalNativeDetailPage` kam nicht in Frage:

* Sie sammelt für eine Aktion **keine Eingaben** — sie übergibt nur die gelesenen
  Entitätsdaten. `inputFlow` ist im Frontend Dokumentation, kein Dialog. Erteilen
  braucht aber Fassung, Ende und Kanal.
* Ihr Aktionsweg erwartet `ActionResult`-Antworten (`success`, `_mode`-Trockenlauf);
  die Einwilligungswege sind fachliche REST-Wege mit eigenen Antworten.

Deshalb das im Projekt etablierte **Capture-Muster** (Bewerbungen-Arbeitsliste,
Fahrzeug-Stamm): Die Screen Definition steht im Backend-Register
(`screen_definitions_capture.py`) und als Kopie in `masks/capture-screens.ts`;
`UniversalMaskRenderer` zeichnet sie mit Formularzustand. Die Seite liefert nur
Daten, Auswahloptionen, Kennzahlen und Aktions-Handler — kein eigenes Feld-, Register-
oder Tabellen-JSX.

## Was gebaut ist

| Maske | Route | Inhalt |
|---|---|---|
| `personal/bewerbung-einwilligung` (objectPage) | `/personal/bewerbung/:id/einwilligung` | Register **Einwilligung**: Bewerber, Stelle, läuft bis, erteilt am (Anzeige); Fassung (Auswahl aus den Fassungen), gültig bis, Kanal, erfasst durch; Wortlaut der gewählten Fassung (Anzeige). Register **Verzeichnis**: Erteilungen und Widerrufe. |
| `personal/einwilligungserklaerungen` (worklist) | `/personal/einwilligungserklaerungen` | Wortlaut und Ersteller, Liste der Fassungen. |
| `personal/bewerbungen` (erweitert) | — | Zeilenaktion **Einwilligung**, Fußaktion **Einwilligungserklärungen**. |

Navigation: Personal → Einwilligungserklärungen.

### Zusagen der Fachlogik, in der Maske gehalten

* **Widerruf: ein Klick mit Bestätigung** — kein Grund, kein Feld, keine Freigabe.
  Er steht im Kopf, gleich weit vorn wie das Erteilen. Die Bestätigung nennt die
  Folge (die Bewerbung wird wieder löschfähig). Ein Vertrag prüft, dass der Dialog
  kein Eingabefeld enthält und der Aufruf nur die Kennung trägt.
* **Keine Vorauswahl der Fassung.** Welche Fassung unterschrieben wurde, sagt der
  Mensch; eine vorbelegte neueste Fassung wäre bei einem älteren Formular eine falsche
  Behauptung.
* **Der Wortlaut ist Anzeige.** Er folgt der gewählten Fassung und ist keine Eingabe.
* **Fassungen: Anlegen mit Bestätigung, kein Bearbeiten, kein Löschen.** Der Dialog
  sagt, dass der Text danach nicht mehr änderbar ist. Derselbe Wortlaut meldet die
  vorhandene Nummer (409 aus dem Backend).
* **Erteilen ohne Fassung ist gesperrt**; **Widerrufen ohne Einwilligung ist
  gesperrt** — statt eines Fehlers nach dem Klick.
* **Doppelklick-Schutz** je Aktion, Rückmeldung bei Erfolg und Fehler, Rücksetzen
  in `finally` (Mutation-Lifecycle-Invariante).

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_bewerbung_einwilligung_masken.py` | **20 bestanden** — beide SDs im Register, nicht vorläufig, `generatorReady`, Advisory **1,0**, Governance und UX-Lint ohne Fehler, kein `*_id`-Feld, jede Aktion mit Befehl; Widerruf ohne Grund/Freigabe; Kanäle = Dienst-Wörterbuch |
| Systemweite SD-Verträge (Meridian, Agent-Vertrag, Omnibox, Governance) | **131 bestanden**, nachdem die Identität der neuen ObjectPage (`applicant_name`) in die Meridian-Liste eingetragen ist |
| Vitest `__tests__/pages/personal/bewerbung-einwilligung.test.tsx` | **14 bestanden** — Optionen aus der API, Wortlaut folgt der Auswahl, Erteilen-Payload, Doppelklick, Unvollständig, Fehlergrund, Sperren, Widerruf ohne Rumpf nach Bestätigung, Abbruch, Fassung anlegen, 409-Hinweis, kein Änderungsweg, Sprung aus der Arbeitsliste |
| Frontend-Nachbarn (Navigation, Spaltenpriorität, App-Routing) | **25 bestanden** |
| `tsc --noEmit` (ganzes Projekt) | 0 Fehler |
| ESLint der geänderten Dateien | 0 Fehler |
| Routing-Integrität, Navigationsziele | bestanden (935 Routen) |

**Nicht geprüft: die Sichtprüfung in der laufenden App.** Der Backend-Container läuft
mit einem Image vor den Fassungs-Wegen (`GET …/einwilligungserklaerungen` antwortet
dort noch mit dem alten Platzhalter-404), und das Frontend antwortete auf Port 3001
nicht. Ein Neubau des Images oder eigene Server in der geteilten Umgebung wurden nicht
ungefragt gestartet.

## Nebenbefund (nicht Teil dieses Slices)

Die Handler in `app/api/v1/endpoints/mask_actions.py` melden **Erfolg ohne
fachliche Wirkung**: Keine der neun `execute`-Funktionen enthält ein INSERT, ein
UPDATE oder einen Dienstaufruf (geprüft 07.10.2026). `qualifizieren` (CRM-Lead),
`bestellen`, `create_activity`, `stornieren` u. a. bauen ein Ergebnis-Dict, schreiben
Audit und Outbox und antworten `success: true` — der Lead wird nicht qualifiziert,
die Bestellung entsteht nicht, die Lagerbewegung bleibt unstorniert. Das ist
derselbe Fehlertyp wie ein „bereit"-Flag, das nur Negativa prüft: Die Maske bestätigt
etwas, das nicht geschehen ist. Eigener Slice.

## Offene Punkte (Handshake)

1. **Sichtprüfung** in der laufenden App nach Neubau des Backend-Images.
2. **Rollenbindung** für die ganze Datei `personal_bewerbungen.py` (aus dem Vorslice).
3. **Selbstwiderruf** durch den Bewerbenden (Punkt 3 der Einwilligungs-Doku).
4. **Erfolg ohne Wirkung** in `mask_actions.py` (Nebenbefund oben).

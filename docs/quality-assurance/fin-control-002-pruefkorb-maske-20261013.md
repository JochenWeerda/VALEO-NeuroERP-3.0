# FIN-CONTROL-002: Prüfkorb als Arbeitsliste, Lagebild, Hinweis am Beleg

Stand: 2026-10-13 · Slice `FIN-CONTROL-002` · baut auf
[FIN-CONTROL-001](fin-control-001-kontroll-engine-20261013.md) auf

## Ziel

Der Prüfkorb war nach FIN-CONTROL-001 nur über zwei API-Wege erreichbar. Jetzt hat der Controller eine
Maske, das System sagt ihm, worauf er zuerst sehen sollte, und die Buchhaltung erfährt am Beleg vorab, dass
ein Vorgang im Prüfkorb vermerkt wird.

## Geliefert

| Teil | Wo |
|---|---|
| Arbeitsliste | `GET /api/v1/kontrolle/pruefkorb` — Seiten, Suche, Sortierung, Spaltenfilter der Maskenlaufzeit (`filter_plan`). Ohne Filter: offene Befunde, kritische zuerst, darin die ältesten. Bezeichnungen statt interner Schlüssel (Art, Vorgang, Aktion), Belegnummer, Sprung zum Beleg. |
| Lagebild | `GET /api/v1/kontrolle/lagebild` — offen, kritisch, Warnungen, älter als 7 Tage, offener Betrag, geprüft in 30 Tagen, Verteilung nach Art, Häufungen (ab drei Befunden derselben Person in 30 Tagen) und daraus Sätze für den Controller (`hinweise`, `lage`). |
| Maske | ScreenDefinition `finance/pruefkorb` (`app/core/screen_definitions_kontrolle.py`): native Arbeitsliste nach dem Muster der Beleg-Kontrolle, Kennzahlen aus dem Lagebild, Zeilenaktionen „Bewerten" (nur bei offenen Befunden) und „Zum Beleg". Seite `pages/finance/pruefkorb.tsx`, Route `/finance/pruefkorb`, Navigation Finanzen → Prüfkorb. |
| Bewerten | Dialog mit Pflichttext; ruft den Kommandoweg `POST /api/v1/kontrolle/befunde/{id}/pruefung`. Rolle und Funktionstrennung prüft der Server; seinen Grund zeigt die Maske. |
| Hinweis am Beleg | `Belegaktion.hinweis` (Belegvertrag, Zusatzfeld): Eine erlaubte Aktion, deren Ausführung einen Befund erzeugt, sagt das vorab — „Wird im Prüfkorb des Controllers vermerkt: …". Der Belegkopf nimmt den Satz in `aktionshinweis` auf. |

Lesen dürfen den Korb Kontrollrollen, die Finanzrollen und `manager`; bewerten nur Kontrollrollen, nie wer
gebucht hat.

## Abgrenzung zur Beleg-Kontrolle

`auswertungen/beleg-kontrolle` (`domain_ops.document_control_exceptions`) führt **unerledigte Belege**:
offene Bestellungen, fehlende Eingangsbelege, nicht fakturierte Lieferscheine — Vorgänge, die noch
jemand zu Ende bringen muss, mit Zuweisung und Bearbeitungsstand. Der Prüfkorb führt **Auffälligkeiten an
bereits gebuchten Vorgängen**, die eine unabhängige Person bewertet. Zwei Listen, weil zwei Fragen und
zwei Rollen; beide stehen in der Navigation nebeneinander.

## Nachweis

- `tests/test_kontrolle_pruefkorb.py` (9, gegen die frische Datenbank): Reihenfolge; Blättern, Suchen,
  Sortieren, Filtern (eine unbekannte Sortierspalte gelangt nicht in die Abfrage); geprüfte Befunde
  verlassen die Liste und bleiben auffindbar; Befund am Beleg nennt Belegart und Nummer und führt zum
  Beleg; Leserechte und Mandantengrenze; leeres und gefülltes Lagebild mit Häufung; Maske besteht
  Governance, UX-Prüfung und Readiness und zeigt keine internen Schlüssel; **jede Spalte und jede Kennzahl
  der Maske hat ein Feld in der Antwort des Servers**.
- `tests/test_belege_lesen.py`, `tests/test_beleg_screen_definition.py`: Hinweis am Beleg nur dort, wo
  ein Befund entsteht.
- `pruefkorb.test.tsx` (2): Bewertung über den Kommandoweg, Liste wird neu geladen, Dialog schließt; bei
  Ablehnung zeigt die Maske den Grund des Servers, der Dialog bleibt offen, der Knopf ist wieder bedienbar.
- 238 Tests der Beleg-, Masken-, Routen- und Inventarprüfungen grün; Navigationsziele geprüft (941 Routen).

## Auslegungen (meine)

- **„Älter als 7 Tage"** als Wartefrist und **Häufung ab drei Befunden in 30 Tagen** sind Startwerte.
- **Häufungen zählen je auslösender Person**, nicht je Geschäftspartner — der Befund kennt den Partner
  nicht als eigenes Feld.
- **„Zum Beleg" gibt es nur für DocFlow-Belege.** Hauptbuchbuchung, Zahlungslauf und Import haben keine
  Zielmaske, die der Korb sicher öffnen könnte; die Maske sagt das.

## Nicht umgesetzt

- **Nicht im Browser geprüft.** Die Sichtprüfung über die echte Anmeldung steht aus; die Testidentität
  braucht dafür die Rolle `controller`. Insbesondere ist offen, wie die Kennzahl „Lage" (ein Satz statt
  einer Zahl) in der Kennzahlenreihe aussieht.
- Keine Benachrichtigung des Controllers bei neuen kritischen Befunden.
- Kein Hinweis am Beleg für die Wege außerhalb von DocFlow (Hauptbuch, Finanzrechnung, Import).
- Belegmasken sind weiter nur im Testmandanten veröffentlicht; der Sprung „Zum Beleg" führt in anderen
  Mandanten auf eine Route ohne veröffentlichte Maske.
- Kasse und Rücklastschriften: unverändert offen (Untersuchung bei Codex).

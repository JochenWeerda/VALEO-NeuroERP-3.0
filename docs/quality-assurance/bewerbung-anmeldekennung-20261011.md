# Wer handelt, trägt das System ein (Slice BEWERBUNG-ANMELDEKENNUNG-20261011)

Stand: 2026-10-11 · Folgeslice zu [Urheber, Idempotenz, Fehlermeldungen](bewerbung-command-urheber-20261011.md)

## Entscheidung

Vorgabe des Auftraggebers: das wählen, was fachlich stimmt und im Alltag einfach läuft – „was
nicht einfach läuft, läuft einfach nicht“.

**Niemand tippt seinen eigenen Namen.** Wer eine Fassung anlegt, eine Einwilligung erfasst oder
widerruft, eine Bewerbung entscheidet oder den Löschlauf startet, steht danach im Beleg – eingetragen
aus der Anmeldung. Ein Eingabefeld dafür ist ein Schritt mehr, wird im Alltag leer gelassen oder mit
irgendetwas gefüllt, und belegt am Ende nichts.

| Angabe | Vorher | Jetzt |
|---|---|---|
| `erstellt_durch` (Fassung) | Freitext im Formular | Anmeldung |
| `erfasst_durch` (Einwilligung erteilen und widerrufen) | Freitext im Formular bzw. in der Abfrage | Anmeldung |
| `entschieden_durch` (Einstellung, Ablehnung) | Freitext im Rumpf | Anmeldung |
| `durchgefuehrt_durch` (Löschlauf) | Pflichtfeld im Rumpf | Anmeldung |
| `beschluss_durch` (Aufbewahrungsfrist) | Freitext | **bleibt Freitext** |

Die Ausnahme ist fachlich begründet: Der Beschluss über die Aufbewahrungsfrist beschreibt das
Gremium („Vorstand“, mit Datum), nicht die Person, die ihn am Bildschirm einträgt.

## Was im Beleg steht

- **In den Fachfeldern der Anmeldename** – `preferred_username` aus dem Token, sonst `name`, sonst
  `email`, sonst `sub`. Bei Keycloak und Entra ist `sub` eine UUID; in „Erfasst durch“ wäre sie
  unlesbar.
- **Im Audit die Kennung** (`sub`), weil sie stabil bleibt, wenn sich der Name ändert.
- Nennt die Anmeldung weder Namen noch Kennung, wird nichts geschrieben (403).

`get_current_user` liefert dafür zusätzlich `name`; `anmeldename()` in `app/auth/deps.py` ist die
eine Stelle, an der die Reihenfolge steht. Andere Module können sie übernehmen.

## Verträglichkeit

- Die vier Felder bleiben in den Eingabemodellen erlaubt, werden aber nicht gelesen. Ein älterer
  Aufrufer, der sie noch sendet, scheitert nicht; sein Wert steht nur nicht mehr im Beleg.
- `durchgefuehrt_durch` war Pflicht und ist es nicht mehr. Der Löschlauf braucht weiterhin die
  wörtliche Bestätigung.
- Die Masken „Einwilligungserklärungen“ und „Einwilligung einer Bewerbung“ haben die Eingabefelder
  nicht mehr; in den Listen bleibt die Spalte als Anzeige.

## Nachweis

Im isolierten Lieferstand gegen `valeo_probe`:

- `tests/test_bewerbung_command_urheber_vertrag.py`: sechs neue Verträge (zusammen **25 grün**) –
  Anmeldename im Beleg und Kennung im Audit, die Reihenfolge der Token-Angaben, Entscheidung,
  Einwilligung erteilen und widerrufen, Löschlauf ohne getippten Namen (und der Beschluss bleibt,
  wie eingegeben), Masken ohne die Eingabefelder.
- Drei Bestandsverträge umgestellt: Entscheidung und Löschprotokoll nennen die Anmeldung; aus
  „ohne Namen kein Lauf“ (422) wurde „ohne Kennung in der Anmeldung kein Lauf“ (403).
- Nachbarschaft (Bewerbung, Rollenmatrix, Masken, MCP): **455 grün**.
- Frontend: Vitest `bewerbung-einwilligung` 14 grün, `tsc` 0 Fehler, ESLint 0.
- Gates grün: Single Head, Response-Modelle, OpenAPI-Doku und -Spec, Code-Inventare,
  Doku-Generatoren, Improvement-Pipelines.

## Nachtrag: die übrigen Module (Slice ANMELDEKENNUNG-UEBRIGE-20261011)

Dieselbe Regel gilt jetzt auch dort, wo `erfasst_durch` noch aus dem Rumpf kam:

| Weg | Angabe |
|---|---|
| `POST /etiketten/druckauftrag` | wer den Druckauftrag anlegt |
| `POST /schaeden/meldungen` | wer den Schaden erfasst |
| `POST /genossenschaft/mitglieder` und Anteilsbewegungen (samt Gegenbuchung) | wer bucht |
| `POST /kontrakte/{id}/dispositionen` | wer abruft |
| `POST /personal/time-accounts/{ref}/adjust` | wer das Zeitkonto korrigiert |

Keines dieser Module hat im Frontend ein Eingabefeld dafür: Die Angabe blieb bisher leer, oder ein
Aufrufer schrieb hinein, was er wollte. Die Felder bleiben in den Eingabemodellen erlaubt und werden
nicht gelesen. `personal.py` und `kontrakte.py` stehen unter der Godfile-Ratsche; die Änderung dort
ist zeilenneutral.

Nachweis: je Modul ein Vertrag in der bestehenden Vertragsdatei (Anmeldung mit UUID als Kennung und
lesbarem Namen, im Rumpf ein anderer Name – im Beleg steht der Anmeldename). Mit den Modulverträgen
**254 grün** gegen `valeo_probe`; Gates grün.

## Sichtprüfung (11.10.2026, Entwicklungsdatenbank, Browser ohne Oberfläche)

- **Einwilligungserklärungen:** Die Maske hat ein Feld, den Wortlaut. Fassung 1 angelegt (Rückfrage
  „danach nicht mehr änderbar", Meldung „Fassung 1 angelegt"); gesendet wurde nur der Wortlaut, in der
  Liste steht unter „Erstellt durch" die Anmeldung.
- **Einwilligung einer Bewerbung:** Fassung, Gültig bis und Kanal gewählt, erteilt („läuft bis
  11.10.2027"), danach widerrufen (Rückfrage, Stand „keine"). Gesendet wurden Fassung, Datum und Kanal;
  im Verzeichnis stehen beide Vorgänge mit der Anmeldung unter „Erfasst durch".
- Keine Fehler in der Browserkonsole.

Die Idempotenz der übrigen Masken-Commands ist geprüft und geschlossen:
[masken-command-idempotenz-20261011.md](masken-command-idempotenz-20261011.md).

## Offen

1. **Nicht aus diesen Slices:** `test_parallel_installation_endpoints` legt einen Drucker mit festem
   Namen an und räumt nicht auf; im geteilten Prüfstand scheitert er am zweiten Lauf an
   `ux_drucker_name`. Die 409-Antwort dort gibt außerdem den Datenbanktext samt Wert zurück –
   dieselbe Schwäche, die `grund_ohne_daten` in der Bewerbungsstrecke geschlossen hat.

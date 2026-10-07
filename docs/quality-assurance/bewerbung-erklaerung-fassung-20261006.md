# Die Einwilligungserklärung in Fassungen (Slice BEWERBUNG-ERKLAERUNG-FASSUNG-20261006)

Stand: 2026-10-06 · Welle 2, Slice 24 · schließt offenen Punkt 4 aus
[Die Einwilligung zur längeren Aufbewahrung](bewerbung-einwilligung-20261006.md)

## Auftrag

Seit dem Vorslice trug jede Erteilung ihren Wortlaut als **freien Text**. Jede
Erteilung konnte einen anderen Text haben, und niemand merkte es; ein Tippfehler im
Personalbüro erzeugte still eine neue „Erklärung“. Nachweisbar (Art. 7 Abs. 1 DSGVO)
ist eine Einwilligung erst, wenn feststeht, **welcher Fassung** zugestimmt wurde —
und dass diese Fassung sich seitdem nicht geändert hat.

## Vorab geprüft: keine Dublette

Es gibt kein Modell für versionierte Erklärungstexte.
`business_partners.privacy_policy_version` ist ein Etikett ohne Text; die
CRM-Einwilligungstabellen beschreiben die Erlaubnis, **angesprochen** zu werden, nicht
die, Daten **aufzubewahren** (Begründung im Vorslice).

## Was gebaut ist

Migration `bewerbung_erklaerung_fassung_20261006`:

* **`domain_hr.bewerbung_einwilligungserklaerungen`** — je Mandant fortlaufende
  `fassung` (1, 2, 3 …) mit `wortlaut`, `erstellt_am`, `erstellt_durch`.
  * **Unveränderlich**, und zwar in der Datenbank: Ein Trigger weist jedes UPDATE ab.
    Wer eine Fassung ändert, ändert rückwirkend, wozu alle früheren Bewerber
    eingewilligt haben. Ein neuer Wortlaut ist eine neue Fassung.
  * **Löschbar nur, solange keine Erteilung darauf verweist** (Fremdschlüssel
    `RESTRICT`). Eine nie benutzte Fassung belegt nichts; eine benutzte ist Teil
    eines Nachweises.
  * **Derselbe Wortlaut ist eine Fassung** (eindeutiger Index auf
    `tenant_id, md5(wortlaut)`). Randleerzeichen machen keinen anderen Text:
    gespeichert wird getrimmt, und eine Prüfbedingung hält das auch bei direktem SQL.
  * **Kein Personenbezug.** Die Fassung bleibt, wenn eine Bewerbung gelöscht wird —
    andere können demselben Text zugestimmt haben.
* **`bewerbung_einwilligungen.erklaerung_id`** ersetzt `einwilligungstext`. Der
  Fremdschlüssel ist **zusammengesetzt** (`tenant_id, erklaerung_id`): Eine Erteilung
  kann nicht auf die Fassung eines anderen Mandanten zeigen, auch nicht per direktem
  SQL. Eine Prüfbedingung verlangt die Fassung genau bei der Erteilung — der Widerruf
  braucht weiterhin **nichts** (Art. 7 Abs. 3).
* **Bestand:** Vorhandene Erteilungen werden überführt — je Mandant ein Wortlaut,
  eine Fassung, nummeriert in der Reihenfolge der ersten Verwendung,
  `erstellt_durch = "Migration: aus freiem Text uebernommen"`. Danach entfällt die
  freie Spalte: Der Wortlaut steht an **einer** Stelle.

Wege (`/api/v1/personal/applications/…`), vor dem Platzhalter `{application_id}`
montiert:

| Weg | Wirkung |
|---|---|
| `GET einwilligungserklaerungen` | Fassungen des Mandanten, neueste zuerst |
| `POST einwilligungserklaerungen` | nächste Fassung; gleicher Wortlaut → 409 mit der vorhandenen Nummer |
| `GET einwilligungserklaerungen/{fassung}` | eine Fassung; fremd oder unbekannt → 404 |
| `POST {id}/einwilligung` | verlangt jetzt `fassung` statt `einwilligungstext` |

Kein PUT, PATCH oder DELETE für Fassungen. Antworten der Einwilligung nennen
`fassung` **und** `einwilligungstext` (den Wortlaut der Fassung) — die Lesesicht
bleibt für den Nachweis vollständig.

### Entscheidungen

* **Die Nummer vergibt das System.** Fassungen werden unter einer Transaktionssperre
  je Mandant (`pg_advisory_xact_lock`) nummeriert; die Eindeutigkeit in der Datenbank
  ist die letzte Instanz. Wer eine Nummer mitschickt, wird abgewiesen statt still
  überstimmt.
* **Auch ältere Fassungen sind erteilbar.** Wer ein früher gedrucktes Formular
  unterschrieben hat, hat **diesem** Text zugestimmt; ihn auf die neueste Fassung zu
  buchen wäre eine falsche Behauptung.
* **Eine unbekannte Fassung ist 422, nicht 404.** Die Bewerbung existiert; falsch ist
  die Angabe im Rumpf.
* **Der Eingabewechsel bricht keinen Verbraucher.** Im Frontend nutzt niemand die
  Einwilligungswege (die Treffer dort sind CRM-Einwilligungen).

## Nachweis

Gelaufen am 06.10.2026:

| Prüfung | Ergebnis |
|---|---|
| Bestandsüberführung auf `valeo_probe`: vier Altvorgänge (zwei Texte, einer nur mit Randleerraum doppelt, ein Widerruf), dann upgrade → downgrade → upgrade | zwei Fassungen (1, 2) in Reihenfolge der ersten Verwendung; Widerruf ohne Fassung; Rückweg stellt den Text in jeder Erteilung wieder her; Probedaten entfernt |
| `valeo_probe` und `valeo_neuro_erp` auf Head | beide `bewerbung_erklaerung_fassung_20261006`; Bedingungen und Trigger identisch |
| `tests/test_bewerbung_erklaerung_fassung_vertrag.py` | **32 bestanden** |
| `tests/test_bewerbung_einwilligung_vertrag.py` (angepasst) | **42 bestanden** |
| `tests/test_bewerbung_loeschlauf_vertrag.py` | **52 bestanden** (zusammen 126 in 33 s, gegen `valeo_probe`) |
| Ratschen: Pagination, Baseline-Integrität, tote Transaktionen, Godfiles, Tabellenverweise | alle grün |

Die neuen Verträge prüfen unter anderem: fortlaufende Nummern je Mandant, auch bei
sechs gleichzeitigen Anlagen; gleicher Wortlaut (auch mit anderem Randleerraum) ist
409 mit der vorhandenen Nummer; leerer Wortlaut wird abgewiesen, ohne zu schreiben;
die Liste steht vor dem Platzhalter und zeigt die neueste zuerst; eine fremde Fassung
ist unsichtbar und nicht erteilbar; freier Text wird nicht mehr angenommen; jedes
UPDATE einer Fassung scheitert in der Datenbank; eine benutzte Fassung ist nicht
löschbar, eine unbenutzte schon; mit der Bewerbung geht der Vorgang, die Fassung
bleibt; die Tabelle trägt keine Personenspalte.

## Grenzen

* **Der Rückweg trimmt.** Ein Altvorgang, dessen Text sich nur im Randleerraum
  unterschied, erhält nach downgrade den getrimmten Wortlaut seiner Fassung, nicht
  den ursprünglichen Leerraum. Inhaltlich derselbe Text; byte-genau ist er es nicht.
* **Rollenschutz geschlossen am 07.10.2026** — [Rollenschutz vom 07.10.2026](personal-bewerbungen-rollenschutz-20261007.md). Alle Wege rollenbezogen, Fassung anlegen nur PERSONAL_ADMIN/admin.
* **OpenAPI und Inventare** sind nicht in diesem Commit; sie werden wie bei den
  Vorslices aus dem committeten Stand integriert.

## Offene Punkte (Handshake)

1. **Rollenbindung geschlossen am 07.10.2026** — [Rollenschutz vom 07.10.2026](personal-bewerbungen-rollenschutz-20261007.md).
2. **Maske** (Punkt 2 der Einwilligungs-QA-Doku): Sie kann jetzt auf Fassungen bauen
   — Auswahlliste statt Textfeld, Wortlaut zur Ansicht.
3. **Selbstwiderruf** durch den Bewerbenden (Punkt 3 dort) bleibt offen.

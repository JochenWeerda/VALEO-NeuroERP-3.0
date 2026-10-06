# Die Einwilligung zur längeren Aufbewahrung (Slice BEWERBUNG-EINWILLIGUNG-20261006)

Stand: 2026-10-06 · Welle 2, Slice 23 · schließt offenen Punkt 4 aus
[Der Löschlauf für Bewerberdaten](bewerbung-loeschlauf-20261006.md)

## Auftrag

Der Löschlauf achtet seit dem Vorslice eine Einwilligung zur längeren Aufbewahrung
(Talentpool, Art. 6 Abs. 1 lit. a DSGVO) — aber **es gab keinen Weg, sie zu erteilen
oder zu widerrufen**. Die Spalten waren da und niemand konnte sie füllen.

Zwei Pflichten bestimmen die Form:

**Art. 7 Abs. 3 DSGVO** — der Widerruf muss jederzeit möglich sein und darf **nicht
schwerer** sein als die Erteilung. Darum verlangt `DELETE` **keinen Rumpf**, keinen
Grund, keine Freigabe. Ein Vertrag prüft, dass der Weg überhaupt kein Eingabemodell
hat: Eine Rücknahme, für die man sich rechtfertigen muss, ist keine freie.

**Art. 7 Abs. 1 DSGVO** — der Verantwortliche muss **nachweisen** können, dass eine
Einwilligung vorlag. Die zwei Spalten auf `applications` sagen nur *bis wann* und
*seit wann* — nicht **wozu** und nicht **wie** erteilt. Und nach einem Widerruf
stehen sie leer: Dann ist nicht mehr zu belegen, warum die Daten im abgelaufenen
Zeitraum überhaupt noch da waren. Darum ist der Widerruf eine **neue Zeile** und
keine Änderung: Wer die Erteilung überschreibt, vernichtet genau den Nachweis, den
Absatz 1 verlangt.

## Die Tabellenfrage zuerst: es gab schon drei

`domain_crm.crm_contact_consents` (+ `crm_contact_consent_history`) und
`domain_crm.crm_consents`. Keine davon wird hier benutzt, und zwar nicht aus
Bequemlichkeit:

* Beide hängen an einem **CRM-Kontakt** bzw. **Partner**. Für jeden Bewerber einen
  CRM-Kontakt anzulegen würde Bewerberdaten in den Vertrieb tragen — das Gegenteil
  von Datenminimierung, und der Löschlauf müsste dann auch dort löschen.
* Sie beschreiben eine **andere Erlaubnis**: `channel`, `consent_type`,
  Double-Opt-In, `ip_address` — die Erlaubnis, **angesprochen** zu werden. Hier geht
  es um die Erlaubnis, Daten **aufzubewahren**. Wer beides in eine Tabelle legt,
  lässt einen widerrufenen Werbe-Opt-In wie einen widerrufenen
  Aufbewahrungs-Opt-In aussehen — und löscht Daten, für die die Erlaubnis noch gilt,
  oder behält welche, für die sie weg ist.

Das ist die **Gegenprobe** zur Löschsperre im Vorslice: Dort war der Begriff
*derselbe* (ein Datensatz, der nicht gelöscht werden darf), und
`public.gobd_loeschsperren` wurde wiederverwendet. Hier ist er ein anderer. Die Regel
ist nicht „immer eine eigene Tabelle" und nicht „immer wiederverwenden", sondern:
derselbe Begriff → dieselbe Tabelle.

**Nebenbefund, nicht Teil dieses Slices:** `crm_consents` und
`crm_contact_consents` sind **zwei Tabellen für einen Begriff**. Die zweite migriert
Daten aus der ersten, die erste bleibt stehen. Eigener Slice.

## Was gebaut ist

Migration `bewerbung_einwilligung_20261006`:

| Gegenstand | Zweck |
| --- | --- |
| `domain_hr.bewerbung_einwilligungen` | Das **fortschreibende** Verzeichnis der Vorgänge. Kein UPDATE, kein DELETE. |
| `ck_beweinw_vorgang` | `ERTEILT` oder `WIDERRUFEN` — nichts dazwischen. |
| `ck_beweinw_erteilung_befristet` | Eine Erteilung hat ein Ende, ein Widerruf hat keines. |
| `ck_beweinw_erteilung_mit_wortlaut` | Ohne Wortlaut ist nicht nachweisbar, **wozu** eingewilligt wurde. |
| `ck_beweinw_kanal` / `ck_beweinw_kanal_bei_erteilung` | Der Kanal gehört zur Erteilung; beim Widerruf bleibt er **leer**. |
| `fk_beweinw_bewerbung` `ON DELETE CASCADE` | Ist der Mensch gelöscht, gibt es keine Aufbewahrung mehr zu rechtfertigen — und ein Nachweis, der nur noch den Namen hält, ist selbst die Speicherung, die beendet werden sollte. |

Drei Wege:

```
GET    /personal/applications/{id}/einwilligung   Stand und Verzeichnis
POST   /personal/applications/{id}/einwilligung   Erteilen
DELETE /personal/applications/{id}/einwilligung   Widerrufen — ohne Rumpf
```

### Der Kanal wird beim Widerruf nicht erfunden

Der erste Entwurf schrieb beim Widerruf `kanal = "WEB"`, weil die Spalte `NOT NULL`
war. Das ist eine **Behauptung über einen Vorgang, von dem niemand weiß, wie er
einging** — dasselbe Muster wie die erfundenen Bestätigungen, die diese Welle
abbaut. Die Spalte ist jetzt nullbar, und eine Prüfbedingung verlangt den Kanal
**nur** bei der Erteilung. Leer heißt „nicht erhoben".

Ihn beim Widerruf zu *erfragen* wäre die andere falsche Antwort: eine Angabe mehr
als bei der Erteilung, und damit ein höherer Aufwand (Art. 7 Abs. 3).

### Stand und Verzeichnis sind nicht dieselbe Angabe zweimal

`applications.aufbewahrung_einwilligung_bis/_am` ist der **operative Stand**, den der
Löschlauf liest; das Verzeichnis ist der **Nachweis der Vorgänge**. Das ist Stand und
Journal, nicht eine doppelt gehaltene Ableitung: Geschrieben werden beide nur von
einem Dienst, in **einer** Transaktion, auf einer mit `FOR UPDATE` gesperrten
Bewerbung. Ein Vertrag prüft nach Erteilen/Widerrufen/Erneut-Erteilen, dass der Stand
immer der letzten Verzeichniszeile entspricht.

### Eine Erlaubnis ohne nahes Ende ist ein Vorrat

`gueltig_bis` muss in der Zukunft liegen und höchstens 1095 Tage entfernt —
dieselbe Obergrenze wie bei der Aufbewahrungsfrist. Eine Einwilligung „auf
unbestimmte Zeit" wäre keine für einen bestimmten Zweck; sie kann erneuert werden,
und das Verzeichnis zeigt dann beide Erteilungen.

## Nachweis

**Gelaufen am 06.10.2026**, nachdem Docker wieder lief. Beim Schreiben des Slices
war der Docker-Dienst gestoppt; die Verträge waren geschrieben, aber nicht
ausgeführt, und der Slice blieb so lange in Arbeit.

| Prüfung | Ergebnis |
|---|---|
| `valeo_probe` mit `pruefstand_db.py --keep` von `bewerbung_loeschlauf_20261006` auf Head | Revision `bewerbung_einwilligung_20261006` |
| Rückweg auf `valeo_probe`: `downgrade` auf den Vorgänger, dann `upgrade head` | Tabelle weg, dann wieder da; Revision stimmt |
| `valeo_neuro_erp` | stand bereits auf Head (Backend-Start); 0 Zeilen im Verzeichnis |
| Prüfbedingungen frisch gegen gewachsen | identisch (Primärschlüssel, Fremdschlüssel, fünf Prüfbedingungen) |
| `tests/test_bewerbung_einwilligung_vertrag.py` gegen `valeo_probe` | **42 bestanden** (98 s) |
| Nachbar `tests/test_bewerbung_loeschlauf_vertrag.py` gegen `valeo_probe` | **52 bestanden** (53 s) |
| `scripts/check_table_references.py` | OK: keine neuen Verweise ins Leere (1/25 an der Schwelle) |

Aufruf:

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_bewerbung_einwilligung_vertrag.py
```

Die Verträge prüfen unter anderem: Erteilen setzt Stand **und** Verzeichniszeile;
ohne Wortlaut, mit vergangenem Ende, mit heutigem Ende, über die Obergrenze hinaus
oder mit unbekanntem Kanal wird abgewiesen, und zwar ohne etwas zu schreiben; der
Widerruf braucht keinen Rumpf und der Weg hat kein Eingabemodell; die Erteilung
bleibt mit Wortlaut und Kanal im Verzeichnis stehen; der Kanal des Widerrufs ist
leer; ein Widerruf ohne Einwilligung sagt das statt stillzuhalten; zweimal
widerrufen schreibt nur einen Vorgang; erneut erteilen ist möglich; die Einwilligung
schützt den Löschlauf **sofort** und der Widerruf macht **sofort** wieder
löschfähig; eine abgelaufene Einwilligung läuft nicht mehr; die Datenbank hält alle
sieben Formfehler auch bei direktem SQL ab; ein Vorgang ohne Bewerbung ist
unmöglich; mit der Bewerbung geht der Nachweis; der Stand entspricht immer der
letzten Zeile; es gibt keinen `PUT`/`PATCH`; der Dienst fasst die CRM-Tabellen nicht
an; die Wörterbücher stehen in Dienst und Schema deckungsgleich.

Alle fünf Ratschen sind **grün**: die vier ohne Datenbankbedarf (Pagination,
Baseline-Integrität, tote Transaktionen, Godfiles) seit dem Schreiben, die
Tabellenverweis-Ratsche seit dem Nachweislauf.

## Offene Punkte (Handshake)

1. ~~**Der Nachweis läuft noch nicht.**~~ **Gelaufen am 06.10.2026**: Migration in
   beiden Datenbanken, 42 Verträge, fünfte Ratsche; siehe Nachweis.
2. **Keine Maske.** Erteilen und Widerrufen sind nur über die API erreichbar. Der
   Widerruf gehört an eine Stelle, die ein Bewerber oder das Personalbüro ohne
   Umwege findet — Art. 7 Abs. 3 meint auch die Zugänglichkeit.
3. **Kein Widerruf durch den Bewerbenden selbst.** Beide Wege setzen ein internes
   Token voraus; der Mensch, dem die Daten gehören, kann heute nur anrufen. Ein
   Selbstbedienungsweg (Token im Bestätigungs-Mail) ist ein eigener Slice und
   dieselbe Lücke wie bei den Art.-17-Wegen.
4. **Der Wortlaut ist freier Text.** Je Erteilung wird er mitgeschrieben — das ist
   der Nachweis. Eine **versionierte** Einwilligungserklärung (eine Fassung, viele
   Erteilungen) wäre das nächste Stück Ordnung; heute kann jede Erteilung einen
   anderen Text tragen, und niemand merkt es.

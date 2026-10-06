# Quittung ohne Vorgang (Slice QUITTUNG-OHNE-VORGANG-20261006)

Stand: 2026-10-06 · Welle 2, Slice 18

## Der Befund

Drei Wege bestätigten einen Vorgang, der **nicht stattfand**.

| Weg | Was er antwortete | Was geschah |
| --- | --- | --- |
| `POST /schaeden/meldungen` | `201`, Meldungsnummer `SM-…`, `status: "gemeldet"` | **nichts** — kein INSERT, nur ein Logeintrag |
| `GET /schaeden/meldungen` | Hagelschaden am Winterweizen, 12.500 €, Zeuge „Hans Müller" | erfundene Literale |
| `GET /schaeden/versicherungen` | vier Verträge mit Vertragsnummern | erfundene Literale |
| `POST /etiketten/druckauftrag` | `201`, Auftragsnummer, `status: "erstellt"` | **nichts** — kein INSERT, kein Druck |
| `GET /etiketten/drucker` | drei Drucker mit IP-Adressen, Status „online" | erfundene Literale |
| `POST /gelangensbestaetigung/{id}/mahnung` | `erinnerung_gesendet: true` | **nichts** — „Stub: In production this would send email/fax" |

**Das ist nicht derselbe Fehler wie eine fehlende Tabelle.** Dort antwortet der
Weg 503, und jemand merkt es. Hier bekommt ein Haus eine Meldungsnummer in die
Hand und meldet deshalb **nicht noch einmal** — während die Frist läuft. § 30
Abs. 1 VVG verlangt die Anzeige unverzüglich nach Kenntnis; Hagelpolicen nennen
regelmäßig wenige Tage. Der Schaden ist dann nicht versichert, und es gibt keinen
Beleg, dass jemand es versucht hat.

Dasselbe bei der Erinnerung zur Gelangensbestätigung: Sie gehört zur
Nachweiskette nach § 17a UStDV. `erinnerung_gesendet: true` heißt, dass niemand
mehr nachhakt — und am Ende fehlt die Bestätigung in der Prüfung.

**Die Regel dieses Slices:** *Ein Weg darf nicht quittieren, was er nicht getan
hat.* Entweder er tut es, oder er sagt, dass er es nicht kann.

### Der Prüfstand bestätigte auch die Tests

`test_schaeden_and_etiketten_endpoints_work` übergab den Drucker `DR-001`, den es
nie gab, und erwartete `201`. Der Test prüfte das Erfundene mit — er konnte nicht
scheitern, weil nichts geprüft wurde, was existieren musste.

## Was jetzt gilt

### Migration `quittung_ohne_vorgang_20261006`

Vier Tabellen in `domain_erp`: `versicherungen`, `schaden_meldungen`, `drucker`,
`druckauftraege` — alle mit `tenant_id`, Statuswörterbuch und
Eindeutigkeitsindex je Mandant. Dazu drei Spalten an
`domain_compliance.gelangensbestaetigung` für den Erinnerungsvermerk.

| Prüfbedingung | Was sie verhindert |
| --- | --- |
| `ck_schaden_meldung_datiert` | `(status = 'ENTWURF') = (gemeldet_am IS NULL)` — ein „gemeldet" ohne Wann ist kein Nachweis, und ein Entwurf hat keinen Meldezeitpunkt. |
| `ck_schaden_ablehnung_begruendet` | Eine Ablehnung ohne Grund. |
| `ck_schaden_regulierung_beziffert` | Eine Regulierung ohne Betrag. |
| `ck_schaden_beschrieben` | Ein Schaden ohne Hergang. |
| `ck_versicherung_frist_positiv` | Eine Meldefrist von null oder weniger Tagen. |
| `ck_druckauftrag_druck_datiert` | `GEDRUCKT` ohne Zeitpunkt — solange kein Spooler angebunden ist, ist dieser Stand damit unerreichbar. |
| `ck_druckauftrag_uebermittlung_datiert` | `UEBERMITTELT` ohne Zeitpunkt. |
| `ck_druckauftrag_fehler_begruendet` | Ein Fehlerstand ohne Fehlertext. |
| `fk_druckauftrag_drucker` (RESTRICT) | Ein Drucker verschwindet nicht, während Aufträge auf ihn zeigen. |
| `fk_schaden_versicherung` (RESTRICT) | Ein Vertrag verschwindet nicht, während Schäden auf ihn zeigen. |

### Die Meldefrist steht am Vertrag

`versicherungen.meldefrist_tage`; `melden_bis` am Schaden ist **abgeleitet** aus
Schadendatum plus Frist, und `frist_ueberschritten` folgt daraus. Eine Frist im
Code würde für alle Policen gleich gelten, und das tut sie nicht. Ohne Frist am
Vertrag gibt es **keine** abgeleitete Frist — und keine erfundene.

### Das Erfassen ist kein Melden

`POST /schaeden/meldungen` erzeugt einen **`ENTWURF`**. Es gibt keinen Versandweg
zum Versicherer; das System darf nicht behaupten, er sei unterrichtet. Dafür gibt
es `POST /schaeden/meldungen/{id}/melden`, das festhält **wann**, **durch wen**
und **auf welchem Weg** (`TELEFON`, `EMAIL`, `POST`, `FAX`, `PORTAL`,
`PERSOENLICH`).

Ohne zugeordneten Vertrag wird das Melden abgewiesen: Ohne ihn ist nicht
feststellbar, wem gemeldet wurde und welche Frist galt.

Die Zustandsfolge ist festgelegt: `ENTWURF → GEMELDET → IN_BEARBEITUNG →
REGULIERT | ABGELEHNT`. Aus `REGULIERT` und `ABGELEHNT` führt kein Weg heraus —
eine abgeschlossene Schadenakte wird nicht nachträglich geöffnet.

### Der Druckauftrag behauptet keinen Druck

Er wird gespeichert und endet bei `ANGELEGT`. Die Antwort trägt ein eigenes Feld
`uebermittlung: "NICHT_ANGEBUNDEN"` — der Versandstand, getrennt vom
Auftragsstand, weil ein Auftrag angelegt sein kann, ohne dass ihn je ein Drucker
gesehen hat. Ein unbekannter oder fremder Drucker ist ein 422; vorher ging jede
Kennung durch, weil die Liste aus Literalen bestand.

Ein gedruckter Auftrag wird nicht abgebrochen: Etiketten im Umlauf macht kein
Abbruch rückgängig.

### Die Erinnerung behauptet keinen Versand

`erinnerung_vermerkt: true`, `versand: "NICHT_KONFIGURIERT"`, `versuche: n`,
`angefordert_am`, plus ein Hinweistext. Festgehalten wird, **dass** erinnert
werden soll — das ist etwas wert. Die Behauptung, es sei versendet, ist es nicht.

### Masken

* `schaeden/meldung.tsx`: Der Toast sagte „Die Meldung wurde erfolgreich
  übermittelt." Jetzt: „Der Schaden ist erfasst, aber noch nicht gemeldet.
  Unterrichten Sie die Versicherung und halten Sie die Meldung anschließend im
  Register fest." Und das Feld heißt `schadendatum`.
* `schaeden/liste.tsx`: Feldnamen und Statuswörterbuch des Registers; `ENTWURF`
  wird als „noch nicht gemeldet" ausgeschrieben.
* **Ein Fund im Frontend:** `useSchaeden` zeigte auf `/api/v1/schaeden` — eine
  Route, die es nicht gibt — und `makeHook` hielt über `initialData` eine
  erfundene Hagelschadenmeldung über 12.500 € dauerhaft sichtbar. Die Abfrage
  schlug immer fehl, und niemand sah es. Jetzt der richtige Weg
  (`/api/v1/schaeden/meldungen`) und **keine** Vorbefüllung.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_quittung_ohne_vorgang_vertrag.py        → 36 passed
  tests/test_parallel_installation_endpoints.py      → zusammen 39 passed
  + Fuhrpark/Sanktionen/Steuernachweis              → 44 passed, 12 skipped
```

Die 36 Verträge prüfen unter anderem: jede Meldung und jeder Auftrag ist nach dem
Schreiben in der Datenbank wiederzufinden; die Listen zeigen **genau** das
Geschriebene und sind vorher leer; kein Weg antwortet mehr aus einer Literalliste
(geprüft auf `vers-001`, `drk-001`, „Hans Müller", „Demo data"); das Anlegen
erzeugt einen Entwurf; `GEMELDET` ohne Zeitpunkt ist in der Datenbank unmöglich;
doppeltes Melden, ein unbekannter Meldeweg und ein Melden ohne Vertrag werden
abgewiesen; die Frist folgt dem Vertrag und eine überschrittene wird benannt;
ohne Frist am Vertrag gibt es keine erfundene; Regulierung braucht einen Betrag,
Ablehnung einen Grund; eine abgeschlossene Akte wird nicht geöffnet; der Auftrag
nennt den Versandstand; ein unbekannter und ein fremder Drucker werden
abgewiesen; `GEDRUCKT` ohne Zeitpunkt ist unmöglich; ein gedruckter Auftrag wird
nicht abgebrochen; die Erinnerung wird vermerkt und nicht versendet, die Versuche
werden gezählt und stehen in der Datenbank; alles mandantengebunden.

Migration gegen die frische `valeo_probe` und die gewachsene `valeo_neuro_erp`
hochgezogen. Gates: Tabellenverweise **4 → 2** an lebenden Wegen, alle vier
Ratschen grün. `tsc` und `eslint` sauber.

### Ein Fund des Prüfstands

Mein Testfixture legte Gelangensbestätigungen mit `lieferschein_nr = 'LS-1'` an
und lief in `ux_gelangensbestaetigung_tenant_lieferschein` — den
Eindeutigkeitsindex aus dem eigenen Slice STEUERNACHWEIS-MANDANT-20261001. Die
Datenbank hat sich richtig verteidigt; das Fixture war falsch.

## Offene Punkte (Handshake)

1. **Die Masken zeigen jetzt leere Listen** statt der gewohnten Demo-Daten. Das
   wirkt wie ein Rückschritt und ist das Gegenteil: Vorher stand dort eine
   Hagelschadenmeldung, die niemand gemeldet hatte.
2. **Das Melden ist ein eigener Schritt.** Das ändert den Ablauf in der Maske;
   fachliche Abnahme beim Versicherungs-Owner. Ein Weg, der die Meldung in der
   Maske festhält, fehlt noch — heute geht das nur über die API.
3. **Kein Versandweg gebaut:** kein E-Mail-/Fax-Versand an den Versicherer, kein
   Druckspooler. Beides bleibt eine benannte Lücke; die Stände
   `UEBERMITTELT`/`GEDRUCKT` und `versand` sind dafür vorgesehen.
4. **Systemischer Fund, eigener Slice:** `makeHook` in
   `packages/frontend-web/src/lib/api/betrieb.ts` setzt bei **rund vierzig**
   Hooks erfundene `initialData` als Fallback. Schlägt die Abfrage fehl — oder
   zeigt sie wie hier auf eine Route, die es nicht gibt —, bleibt die Attrappe
   sichtbar und der Fehler unsichtbar. Hier ist nur `useSchaeden` korrigiert.
5. **Fremder Rotstand:** 7 Vitest-Fehlschläge zu Touch-Zielen (44 px) und
   Start-Dashboard; `button.tsx` und `start-dashboard.tsx` sind im geteilten Baum
   von einem anderen Agenten geändert. Nicht aus diesem Slice, nicht angefasst.
6. `app/api/v1/endpoints/open_items.py` trägt eine „In production"-Notiz zu einer
   fehlenden `open_item_payments`-Tabelle. Dort **wird** geschrieben (in die
   Journalbeschreibung), es ist also keine falsche Quittung — aber ein
   Modellierungsrückstand.

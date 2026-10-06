
# Bewerbermanagement in Ordnung (Slice BEWERBERMANAGEMENT-ORDNUNG-20261006)

Stand: 2026-10-06 · Welle 2, Slice 21 · schließt die Mängel aus
[Personal-Zerlegung](personal-zerlegung-20261006.md)

## Auftrag

Die Zerlegung hat den Code wortgleich umgezogen und sieben Mängel **benannt statt
behoben** — damit bei einem späteren Fehler unterscheidbar bleibt, was der Umzug
und was die Korrektur gebrochen hat. Zwei davon hielt `TestBenannteMaengel` als
Vertrag fest. Dieser Slice behebt alle sieben, und die Verträge kehren sich um.

## Was behoben ist

### 1. Der Fehler nennt seine Ursache

```python
    except Exception:
        raise HTTPException(status_code=503, detail="applications table not available")
```

Das stand an allen vier Wegen. Es ist nur dann wahr, wenn die Tabelle tatsächlich
fehlt — bei einem Rechtefehler, einer verletzten Prüfbedingung oder einem
Verbindungsabbruch schickt es den Leser in die Migration, während das Problem
woanders liegt.

`bewerbung_service.fehler_deuten` unterscheidet jetzt: Eine fehlende Tabelle
**oder Spalte** (`UndefinedTable`, `UndefinedColumn`) ist ein 503 mit
Migrationshinweis; alles andere ein 409 mit dem Grund. Beides rollt die
Transaktion zurück.

### 2. Die Stufen haben Übergänge

`APPLICATION_STAGES` war ein `set`, und geprüft wurde nur, ob die Zielstufe darin
vorkommt. Eine **abgelehnte** Bewerbung ließ sich damit auf `EINGESTELLT` setzen
und eine eingestellte auf `EINGANG`.

Das ist kein Komfortproblem, sondern ein fehlender Nachweis: Niemand kann später
sagen, ob die Ablehnung je galt.

```
EINGANG ⇄ VORAUSWAHL ⇄ ERSTGESPRAECH ⇄ ENDGESPRAECH ⇄ ANGEBOT
                      └──────────────┬──────────────┘
                                     ▼
                        EINGESTELLT | ABGELEHNT   (endgültig)
```

Innerhalb der laufenden Pipeline bleibt ein Rückschritt erlaubt — eine Vorauswahl
kann sich als zu früh erweisen. Aus einem endgültigen Stand führt kein Weg heraus;
für eine neue Bewerbung desselben Menschen ist ein neuer Vorgang anzulegen, und
der Fehlertext sagt das.

`UEBERGAENGE` wird aus den beiden Mengen `LAUFEND` und `ENDGUELTIG` **erzeugt**,
nicht zweimal geschrieben.

### 3. Eine Ablehnung braucht einen Grund

Nicht wegen einer Formvorschrift: Im Streitfall trägt der Arbeitgeber nach § 22
AGG die Beweislast. Wer nicht sagen kann, warum er abgelehnt hat, trägt sie ohne
Beweis.

Der Grund steht in einer **eigenen Spalte** (`ablehnungsgrund`), nicht in `notes`.
`notes` ist ein Verlaufsfeld, in das jeder Stufenwechsel schreibt — ein Grund, der
darin untergeht, ist kein Nachweis. Ein Vertrag prüft genau diese Trennung.

Dazu `entschieden_am` und `entschieden_durch`: Ein endgültiger Stand ohne
Zeitpunkt ist kein Nachweis.

### 4. Das Wörterbuch steht in der Datenbank

| Prüfbedingung | Was sie verhindert |
| --- | --- |
| `ck_bewerbung_status` | Ein Stand außerhalb der sieben Stufen — ein Importweg umgeht das Schema, die Datenbank nicht. |
| `ck_bewerbung_ablehnung_begruendet` | `ABGELEHNT` ohne Grund. |
| `ck_bewerbung_entscheidung_datiert` | `EINGESTELLT`/`ABGELEHNT` ohne Zeitpunkt. |
| `ck_bewerbung_name_gefuellt` | Eine Bewerbung ohne Namen. |

Die Migration **zählt vor dem Umbau**, ob der Bestand Stände außerhalb des
Wörterbuchs führt, und bricht ab, statt sie stillschweigend umzuschreiben: In
welchem Stand eine Bewerbung war, ist eine Tatsache und keine Lästigkeit. Der
Bestand trug `EINGANG` und `VORAUSWAHL` — beide im Wörterbuch, 3 Zeilen, keine
Datenarbeit nötig.

Das Downgrade bricht ab, wenn eine Entscheidung festgehalten ist: Der
Ablehnungsgrund ist der Nachweis, auf den es ankommt.

### 5. Form, Grenze, Kennung

* `BewerbungOut` je Weg statt `PersonalOut` mit `extra="allow"` — vorher gab es
  drei verschiedene Antwortformen unter einem Namen.
* `limit`/`offset`; `limit > 1000` ist ein 422.
* `extra="forbid"` auf der Eingabe: Ein mitgeschickter `status` wird abgewiesen
  statt verschluckt.
* `uuid7` statt `uuid4` — zeitgeordnet, und ein Vertrag prüft die Ordnung zweier
  Kennungen.
* Ein neuer Weg `GET /applications/{id}`: Vorher war eine einzelne Bewerbung nur
  über die Liste zu finden.

### 6. Die Lohnwege nennen den Mandanten

Beide nahmen `tenant_id` mit `noqa: ARG001` entgegen und verwarfen ihn. Für eine
Rechenvorschau ist das tragbar; für eine Übergabe an DATEV/FIBU nicht — eine
Lohnabrechnung, die nicht sagt, für welches Haus sie gilt, lässt sich dem falschen
zuordnen. Beide Antworten tragen jetzt `mandant`.

**Was nicht verändert wurde:** Die Rechnung bleibt eine **Vorschau**, und der
Vorbehalt („Produktiv massgeblich sind amtlicher BMF-PAP, DATEV-/Steuerberater­freigabe
und freigegebene SV-Parameter") steht wörtlich weiter in der Antwort. Ein Vertrag
hält das fest, damit „behoben" nicht als „umgeschrieben" missverstanden wird.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_bewerbermanagement_ordnung_vertrag.py   → 37 passed
  tests/test_personal_zerlegung_vertrag.py           → zusammen 53 passed
  + alle Personal-, Lohn- und Bewerbungstests        → 179 passed
```

Die 37 Verträge prüfen unter anderem: alle vier Prüfbedingungen greifen auch bei
direktem SQL; ein unbekannter Stand, eine Ablehnung ohne Grund und ein endgültiger
Stand ohne Zeitpunkt sind in der Datenbank unmöglich; die Pipeline läuft vorwärts
und erlaubt Rückschritte **nur** innerhalb der laufenden Stufen; eine abgelehnte
Bewerbung wird nicht eingestellt und eine eingestellte nicht zurückgesetzt; der
Fehlertext nennt die erlaubten Ziele; der Ablehnungsgrund landet nicht im
Verlaufsfeld; eine fehlende Tabelle ist ein 503 mit Hinweis und jeder andere
Fehler ein 409 mit Grund; die Liste ist begrenzt; ein unbekanntes Eingabefeld
wird abgewiesen; die Kennungen sind zeitgeordnet; fremde Bewerbungen sind nicht
lesbar, nicht änderbar und nicht löschbar; beide Lohnantworten nennen den
Mandanten und der Vorbehalt steht noch da.

Migration gegen die frische `valeo_probe` und die gewachsene `valeo_neuro_erp`
hochgezogen (3 Bewerbungen, beide Stände im Wörterbuch). Alle vier Ratschen grün.

## Die Verträge haben sich umgekehrt

`TestBenannteMaengel` verlangte, dass die Mängel **noch da** sind — damit sie nicht
als behoben gelten. Jetzt heißt die Klasse `TestMaengelBehoben` und hält fest, dass
sie nicht zurückkommen. Zwei weitere Verträge der Zerlegung sind nachgezogen: Die
Prüfung auf die **Form** des Stufenwörterbuchs (ein `set`) ist durch eine Prüfung
auf die Stufen selbst ersetzt, und das SQL des Löschwegs liegt jetzt im Dienst.

## Offene Punkte (Handshake)

1. **`ABGELEHNT` ist endgültig** — eine Fehleingabe ist nicht mehr durch
   Zurücksetzen zu heilen, sondern durch einen neuen Vorgang. Beabsichtigt (eine
   Ablehnung ist eine Mitteilung an einen Menschen), Abnahme beim Personal-Owner.
2. **Die Begründungspflicht bei Ablehnung** ist eine neue Pflichtangabe; die
   Maske braucht ein Feld dafür.
3. **Speicherbegrenzung (Art. 5 Abs. 1 lit. e DSGVO):** Bewerberdaten sind nach
   Abschluss des Verfahrens zu löschen — üblich sind sechs Monate nach der
   Ablehnung (Frist des § 15 Abs. 4 AGG plus Zustellung). Es gibt einen Löschweg,
   aber **keine Frist und keinen Lauf**, der ihn anstößt. `entschieden_am` ist die
   Grundlage dafür und jetzt vorhanden; der Lauf selbst fehlt und ist ein eigener
   Slice.
4. Ein Weg, der die Bewerbung einem Mitarbeiter zuordnet (`EINGESTELLT` →
   Personalstamm), fehlt. Heute endet die Pipeline im Stand.

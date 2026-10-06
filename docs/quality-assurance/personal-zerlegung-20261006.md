# Zerlegung von personal.py (Slice PERSONAL-ZERLEGUNG-20261006)

Stand: 2026-10-06 · Welle 2, Slice 20

## Anlass

`app/api/v1/endpoints/personal.py` stand mit 3315 Zeilen in der Godfile-Ratsche
und wuchs auf 3342 — ein neuer `delete_application`-Weg (Commit `f7fcbdd7c`,
anderer Agent). Die Ratsche wurde rot an der Baseline, die im Slice
[Personal-Organisation-Zeitkonto](personal-organisation-zeitkonto-20261006.md)
gesenkt worden war.

**Das ist die Ratsche, die arbeitet.** Sie verlangt genau zwei mögliche
Antworten: Die Datei schrumpft, oder das Wachstum wird begründet. Auf
Nutzeranweisung wurde zerlegt.

## Der Schnitt lag schon da

Zwei Fächer am Ende der Datei teilen mit der Personalverwaltung **nur den
Prefix** `/personal`:

| Neues Modul | Wege | Zeilen |
| --- | --- | --- |
| `personal_bewerbungen.py` | `GET/POST /applications`, `PATCH /applications/{id}/stage`, `DELETE /applications/{id}` | 172 |
| `personal_lohnabrechnung.py` | `POST /lohn/berechnung`, `POST /lohn/closeout-preview` | 133 |

`personal.py`: **3342 → 3083** Zeilen. Baseline nachgezogen (down-only).

### Eine Zerlegung ist keine Gelegenheit, Verhalten zu ändern

Der Code ist **wortgleich** umgezogen — auch dort, wo er fragwürdig ist. Hätte
ich beim Umzug korrigiert, wäre bei jedem späteren Fehler nicht mehr zu
unterscheiden, was der Umzug und was die Korrektur gebrochen hat.

Drei Verträge halten den Umzug fest: das Stufenwörterbuch samt seiner Form (ein
`set`), der wörtliche Vorbehalt der Lohnrechnung („Produktiv massgeblich sind
amtlicher BMF-PAP …") und die unveränderten Beitragsgrundlagen.

Der `delete_application`-Weg stammt vom anderen Agenten und ist wortgleich
mitgewandert; ein Vertrag prüft das ausdrücklich.

### Eine Änderung war nötig

`PersonalOut` war **in** `endpoints/personal.py` definiert und damit von den
beiden herausgenommenen Modulen nicht erreichbar. Es liegt jetzt in
`app/api/v1/schemas/personal_schemas.py` — dort, wo die Datei im Kopf ohnehin
sagt: „Import these instead of defining locally." Dieselbe Klasse, dasselbe
`extra="allow"`, eine Definition statt zweier.

### Montagereihenfolge

Die beiden neuen Router stehen in `api.py` **vor** `personal.router`. Heute gibt
es in `personal.py` keinen Platzhalterpfad auf oberster Ebene, der `/applications`
oder `/lohn/…` verschlucken könnte — ein Vertrag prüft auch das. Die Reihenfolge
ist trotzdem festgelegt und begründet, damit sie nicht zufällig wird, wenn später
einer dazukommt.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_personal_zerlegung_vertrag.py      → 13 passed
  + alle Personal- und Lohntests (22 Dateien)   → 139 passed
```

Die 13 Verträge prüfen: alle sechs umgezogenen Wege sind unter **denselben**
Pfaden und Methoden erreichbar; kein Weg unter `/api/v1/personal` ist doppelt
montiert (65 Wege); die festen Pfade stehen vor dem Sammelrouter; `personal.py`
hat keinen Platzhalter auf oberster Ebene; die Datei liegt unter 3315 Zeilen und
die Baseline nennt die neue Größe; die neuen Module sind keine Godfiles; der Code
ist wortgleich umgezogen; `personal.py` kennt die sechs Funktionen nicht mehr;
`PersonalOut` steht nur noch an einer Stelle.

Alle vier Ratschen grün.

## Benannte Mängel — behoben im Folgeslice

Die beiden Fächer trugen sieben Mängel, die der Umzug bewusst nicht angefasst hat.
`TestBenannteMaengel` hielt zwei davon **als Vertrag** fest, damit sie nicht als
behoben gelten.

**Alle sieben sind seit dem 06.10.2026 behoben** —
[Bewerbermanagement-Ordnung](bewerbermanagement-ordnung-20261006.md). Die
Verträge haben sich umgekehrt: `TestMaengelBehoben` hält jetzt fest, dass sie
nicht zurückkommen.

| Mangel | Behoben durch |
| --- | --- |
| `except Exception: 503 "applications table not available"` — verwischte jeden Fehler zu einer Tabellenaussage | `bewerbung_service.fehler_deuten`: fehlende Tabelle/Spalte → 503 mit Migrationshinweis, alles andere → 409 mit Grund |
| `response_model=PersonalOut` mit `extra="allow"` | `BewerbungOut` je Weg |
| Die Bewerbungsliste war unbegrenzt | `limit`/`offset` |
| `APPLICATION_STAGES` als `set` ohne Übergänge — eine abgelehnte Bewerbung ließ sich einstellen | `UEBERGAENGE`, aus `LAUFEND` und `ENDGUELTIG` erzeugt |
| `uuid4` | `uuid7` |
| `domain_hr.applications.status` war freier Text | `ck_bewerbung_status` plus drei weitere Prüfbedingungen |
| Die Lohnwege verwarfen den Mandanten (`noqa: ARG001`) | Beide Antworten nennen `mandant` |

Dass die Lohnrechnung eine **Vorschau** ist, bleibt unverändert und steht
weiterhin wörtlich in der Antwort.


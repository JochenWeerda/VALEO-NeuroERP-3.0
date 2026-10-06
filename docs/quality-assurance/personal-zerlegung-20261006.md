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

## Benannte Mängel — nicht behoben, sondern festgehalten

Die beiden Fächer tragen Mängel, die der Umzug bewusst nicht angefasst hat. Damit
sie nicht als behoben gelten, hält `TestBenannteMaengel` zwei davon **als Vertrag**
fest: Der Test schlägt an, sobald jemand sie behebt, und verlangt dann, dass diese
Zusage hier mitgeht. Ein Mangel in einem Test ist besser als einer in einer Notiz.

| Mangel | Wo |
| --- | --- |
| `except Exception: raise HTTPException(503, "applications table not available")` — verwischt jeden Fehler zu einer Tabellenaussage, auch einen Rechtefehler oder eine verletzte Prüfbedingung | alle vier Bewerbungswege |
| `response_model=PersonalOut` mit `extra="allow"` — beschreibt nichts | alle vier Bewerbungswege |
| Die Bewerbungsliste ist **unbegrenzt** (kein `limit`) | `list_applications` |
| `APPLICATION_STAGES` ist ein `set` ohne erlaubte Übergänge: Eine abgelehnte Bewerbung lässt sich auf `EINGESTELLT` setzen | `update_application_stage` |
| `uuid4` statt `uuid7` | `create_application` |
| Kein Statuswörterbuch in der Datenbank (`domain_hr.applications.status` ist freier Text) | Migration fehlt |
| Die Lohnwege lesen keinen Mandanten — `tenant_id` wird mit `noqa: ARG001` entgegengenommen und verworfen. Für eine Preview tragbar, für eine Übergabe an DATEV nicht | beide Lohnwege |

Der Vollständigkeit halber: Die Lohnrechnung ist ausdrücklich eine **Preview**;
der Vorbehalt steht in der Antwort und ist wörtlich erhalten.

## Offener Punkt (Handshake)

Die Mängel oben gehören in einen eigenen Slice **Bewerbermanagement**. Er braucht
eine Migration (Statuswörterbuch mit Übergängen auf `domain_hr.applications`),
typisierte Antwortmodelle und eine Begrenzung der Liste. Wer ihn nimmt, streicht
die entsprechenden Zeilen hier und entfernt den zugehörigen Vertrag aus
`TestBenannteMaengel`.

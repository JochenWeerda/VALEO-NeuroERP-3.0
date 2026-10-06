# Der Löschlauf für Bewerberdaten (Slice BEWERBUNG-LOESCHLAUF-20261006)

Stand: 2026-10-06 · Welle 2, Slice 22 · schließt offenen Punkt 3 aus
[Bewerbermanagement-Ordnung](bewerbermanagement-ordnung-20261006.md)

## Auftrag

Art. 5 Abs. 1 lit. e DSGVO verlangt, personenbezogene Daten nicht länger zu halten
als für den Zweck nötig. Für Bewerberdaten ist der Zweck mit dem Verfahren
erledigt; die üblichen sechs Monate nach der Ablehnung leiten sich aus § 15 Abs. 4
AGG ab (zwei Monate Geltendmachung) plus Zustellung und Klagefrist-Puffer.

Es gab einen Löschweg je Bewerbung — aber **keine Frist und keinen Lauf**, der ihn
anstößt. Ein Löschweg, den niemand geht, erfüllt die Pflicht nicht.

## Drei Entscheidungen

### 1. Eine eigene Aufbewahrungsregel, nicht `gobd_aufbewahrungsrichtlinien`

Die GoBD-Richtlinie rechnet in **Jahren** und sagt „mindestens so lange"; hier gilt
das **Gegenteil** — „höchstens so lange" — und die Einheit ist der **Tag**. Zwei
entgegengesetzte Pflichten gehören nicht in eine Tabelle: Wer sie zusammenlegt,
kann später nicht mehr sagen, ob eine Zahl eine Untergrenze oder eine Obergrenze
ist. Sechs Monate sind außerdem kein Jahr, und eine Frist, die man aufrunden muss,
hält Daten länger als nötig.

`domain_hr.bewerbung_aufbewahrung` führt je Mandant **eine** aktive Regel
(`ux_bewaufb_mandant`, partiell auf `aktiv`): Zwei wären zwei Obergrenzen, und der
Lauf müsste raten, welche gilt.

### 2. Die Löschsperre wird wiederverwendet

`public.gobd_loeschsperren` ist trotz ihres Namens keine GoBD-Sache, sondern der
allgemeine Begriff: ein Datensatz, der nicht gelöscht werden darf. Läuft eine
AGG-Klage, sind die Bewerberdaten **Beweismittel**. Eine zweite Sperrtabelle wäre
genau die Dublette, die diese Welle abbaut; ein Vertrag prüft über den
Syntaxbaum der Migration, dass keine entstanden ist.

**Dabei ein Fehler, der teuer gewesen wäre:** Das Wörterbuch dieser Tabelle ist
**englisch** (`ACTIVE`/`RELEASED`/`EXPIRED`, siehe `app/finance/models.py`,
`DocumentHold`). Mein erster Entwurf verglich gegen `"AKTIV"` — das hätte **jede**
Sperre übergangen und Beweismittel vernichtet, und zwar lautlos: Eine Sperre, die
nicht greift, sieht wie keine Sperre aus. Zwei Verträge halten den englischen Stand
jetzt fest. Es ist dasselbe Muster wie bei `shifts_status_ck` im
[Zeitkonto-Slice](personal-organisation-zeitkonto-20261006.md) — ein deutsches
Wörterbuch dort anzunehmen, wo ein englisches steht.

### 3. Ohne Regel wird nicht gelöscht

Gibt es für den Mandanten keine Regel, löscht der Lauf nichts und antwortet 409 mit
Grund **und Weg**: Eine Frist, die niemand beschlossen hat, ist keine Grundlage, um
Daten zu vernichten. Dass der Lauf dann nichts tut, könnte als Fehlfunktion
missverstanden werden; deshalb nennt die Antwort ausdrücklich, dass eine Regel
fehlt, und wo sie beschlossen wird.

## Was gebaut ist

Migration `bewerbung_loeschlauf_20261006`:

| Gegenstand | Zweck |
| --- | --- |
| `domain_hr.bewerbung_aufbewahrung` | Die Frist in Tagen, mit gesetzlicher Grundlage, Beschlussdatum und -person. **Keine Vorbefüllung.** |
| `ck_bewaufb_tage_positiv` / `ck_bewaufb_tage_obergrenze` (≤ 1095) | Eine Frist von zehn Jahren wäre keine Aufbewahrung, sondern ein Vorrat. Die Grenze fängt den Tippfehler; die fachliche Angemessenheit entscheidet das Haus. |
| `ck_bewaufb_grundlage_benannt` | Eine Frist ohne Grundlage ist eine Zahl ohne Recht. |
| `applications.aufbewahrung_einwilligung_bis` / `…_am` | Talentpool, Art. 6 Abs. 1 lit. a DSGVO. Die Einwilligung hat selbst ein Ende. |
| `ck_bewerbung_einwilligung_datiert` | Eine Einwilligung, von der niemand weiß, wann sie erteilt wurde, ist keine Rechtsgrundlage. |
| `domain_hr.bewerbung_loeschlaeufe` | Der Nachweis: Zeitpunkt, angewandte Frist, Stichtag, geprüft, gelöscht, übersprungen je Grund, durch wen. |
| `ck_bewloesch_summe_stimmt` | Gelöscht und übersprungen können zusammen nicht mehr sein als geprüft. |

**Das Protokoll trägt Zahlen, keine Namen.** Man muss beweisen können, *dass*
gelöscht wurde, ohne zu behalten, *was* gelöscht wurde — ein Protokoll mit
Bewerbernamen wäre genau die Speicherung, die der Lauf beenden soll. Ein Vertrag
prüft die Spaltenliste.

Fünf Wege in `personal_bewerbungen.py`:

```
GET  /personal/applications/aufbewahrung        Die beschlossene Frist (409, wenn keine)
PUT  /personal/applications/aufbewahrung        Sie festlegen
GET  /personal/applications/loeschlauf/faellig  Trockenlauf — ändert nichts
POST /personal/applications/loeschlauf          Ausführen
GET  /personal/applications/loeschlaeufe        Der Nachweis
```

### Der Trockenlauf ist kein Komfort

Personenbezogene Daten unbesehen zu vernichten ist leichtfertig. Der Trockenlauf
zeigt Name und Mailadresse der fälligen Zeilen — **damit** geprüft werden kann, was
gelöscht wird — und nennt zu jeder bleibenden Zeile den Grund (`LOESCHSPERRE` oder
`EINWILLIGUNG`). Ins Protokoll kommt der Name nicht. Ein Vertrag hält beide Seiten
fest.

### Der Auftrag ist bestätigt und zurechenbar

`POST` verlangt `durchgefuehrt_durch` **und** `bestaetigung: "ENDGUELTIG LOESCHEN"`.
Ein Eingriff, der Daten endgültig vernichtet, muss einem Menschen zurechenbar sein,
und ein versehentlich abgeschickter POST darf nichts vernichten. Löschung und
Protokoll liegen in **einer** Transaktion: Ein Protokoll ohne Löschung wäre eine
falsche Zusage, eine Löschung ohne Protokoll ein unbelegter Eingriff.

Ein abgeschnittener Lauf (Grenze erreicht) sagt das in `weitere_faellig` — sonst
sähe ein halber Lauf wie ein fertiger aus.

### Montagereihenfolge

Die festen Pfade stehen **vor** `/applications/{application_id}`. Stünden sie
danach, läse der Platzhalter `aufbewahrung` als Bewerbungskennung und antwortete
404. Zwei Verträge halten die Reihenfolge und die einmalige Montage fest.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_bewerbung_loeschlauf_vertrag.py        → 52 passed
  + Bewerbermanagement + Personal-Zerlegung        → zusammen 105 passed
```

Die 52 Verträge prüfen unter anderem: ohne Regel löscht weder Trockenlauf noch Lauf
etwas, und es entsteht **kein** Protokolleintrag über einen Lauf, der nicht
stattgefunden hat; die Frist ist je Mandant eindeutig, braucht eine Grundlage und
hält ihre Grenzen auch bei direktem SQL; der Trockenlauf ändert nichts und schreibt
nichts; offene Bewerbungen (`EINGANG`, `VORAUSWAHL`) bleiben unberührt, weil ihnen
der Fristanker fehlt; eine abgelaufene Ablehnung **und** eine abgelaufene Einstellung
werden gelöscht; eine aktive Löschsperre schützt, eine freigegebene nicht mehr, eine
fremde gar nicht; eine laufende Einwilligung schützt, eine abgelaufene nicht mehr;
Zähler und Bestand stimmen im gemischten Fall zusammen (5 geprüft, 3 gelöscht, 1+1
übersprungen, 3 bleiben); ohne Bestätigung, mit falscher Bestätigung und ohne Namen
läuft nichts; das Protokoll führt keine personenbezogene Spalte und die Antwort
keinen Namen; alles ist mandantengebunden.

Migration gegen die frische `valeo_probe` **und** die gewachsene
`valeo_neuro_erp` hochgezogen. Alle fünf Ratschen grün.

### Ein Nebenfund: zwei Tabellen, die die Entwicklungsdatenbank nie bekam

Die Tabellenverweis-Ratsche war rot mit `domain_shared.jobs` und
`domain_shared.job_artifacts` an einem lebenden Weg (`job_runner.py`). Gegen die
**frische** `valeo_probe` war sie grün: Beide Tabellen legt
`job_runner_tables_repair_20260625` an, die Revision steht in `alembic_version` der
Entwicklungsdatenbank — die Tabellen fehlten dort trotzdem. Das ist die
[bekannte Drift](../../docs/quality-assurance/pruefstand-datenbank.md) der
gewachsenen DB, kein Codefehler. Repariert durch das **wörtliche** SQL dieser
Revision (idempotent, `IF NOT EXISTS`); danach grün. Die Ratsche hat damit nicht
meinen Slice, sondern eine stillschweigende Lücke der Entwicklungsdatenbank
gemeldet.

## Offene Punkte (Handshake)

1. **Der Lauf wird nicht automatisch geplant.** Ein Löschlauf vernichtet Daten
   endgültig; ihn ohne Aufsicht in einen Zeitplan zu hängen, wäre leichtfertig. Er
   ist ein Weg, den jemand aufruft. Die Einrichtung eines regelmäßigen Laufs und
   die Festlegung der Frist gehören dem Datenschutz-Owner.
2. **Keine Maske.** Frist, Trockenlauf und Lauf sind heute nur über die API
   erreichbar. Eine Maske braucht beides: die Frist als Stammdatum und den
   Trockenlauf als Vorschau vor der Freigabe.
3. **Kein Rechteschutz über den Mandanten hinaus.** Jeder, der ein gültiges Token
   und den Mandantenkopf hat, kann den Lauf anstoßen. Die Zurechenbarkeit steht im
   Protokoll (`durchgefuehrt_durch`), aber sie ist eine **Angabe**, keine geprüfte
   Identität. Ein eigener Slice sollte den Weg an eine Rolle binden.
4. ~~**Die Einwilligung hat keinen Weg.**~~ **Gebaut am 06.10.2026** —
   [Die Einwilligung zur längeren Aufbewahrung](bewerbung-einwilligung-20261006.md):
   Erteilen, Widerrufen (ohne Rumpf, ohne Grund — Art. 7 Abs. 3) und ein
   fortschreibendes Verzeichnis als Nachweis nach Art. 7 Abs. 1. **Der Nachweis
   dieses Folgeslices ist noch nicht gelaufen** (PostgreSQL auf dieser Maschine
   nicht erreichbar); der Punkt bleibt bis dahin offen.

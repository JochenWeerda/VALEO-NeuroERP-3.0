# Mengen, Einheiten und Gebinde im Agrarhandel

Stand: 2026-09-15 · Claude Code · Slice `FSX-MENGENMODELL`.
Gehoert zu `docs/design/flow-spine-entlastung-masterplan.md` (K5) und zum
n:m-Belegfluss.

## Warum es dieses Dokument gibt

K5 des Ebene-1-Kriterienkatalogs — „Teilmengen und Zuordnungen sind in der Maske
aufloesbar" — ist gesperrt, weil das positionsbezogene Mengenmodell fehlt. Bevor
es gebaut wird, muss klar sein, **womit** dort gerechnet wird. Im Agrarhandel ist
das nicht selbstverstaendlich: Die gebraeuchlichste Handelsgroesse ist nicht
Kilogramm, und mehrere gaengige „Einheiten" sind ueberhaupt keine Masse.

Alles Folgende ist belegt; die Quellen stehen am Ende. Wo etwas **nicht** belegt
ist, steht es ausdruecklich dabei.

## 1. Drei Arten von Einheit, nicht eine

Der wichtigste Befund der Recherche ist eine Unterscheidung, die ein naives
Einheitensystem nicht trifft:

| Art | Beispiele | Umrechnung |
|-----|-----------|------------|
| **Masse** | kg, **dt**, t | global und exakt |
| **Volumen** | ml, l, hl | global und exakt |
| **Zaehleinheit** | Stueck, Sack, Kanister, Big Bag, Palette, **Einheit (Saatgut)**, **Pack** | **nur je Artikel**, nie global |

**Zaehleinheiten duerfen nicht global umgerechnet werden.** Ein Sack Saatgetreide
wiegt anders als ein Sack Duenger; eine „Einheit" Mais ist etwas anderes als eine
Einheit Weizen. Wer dafuer einen globalen Faktor hinterlegt, erzeugt eine Zahl,
die in den meisten Faellen falsch ist — und zwar unauffaellig falsch.

Der bestehende `unit_factor` in `docflow_source_proposals.py` macht das bereits
richtig: Er kennt nur die Masseumrechnung und liefert fuer alles andere `None`,
worauf die Quelle uebersprungen statt geraten wird. **Diese Disziplin gilt
weiter.**

## 2. dt ist die Standardgroesse des Getreidehandels

**1 dt = 100 kg = 1/10 t.** Die Dezitonne wurde eingefuehrt, um den
**Doppelzentner** abzuloesen, der ebenfalls 100 kg entsprach; sie ist in Europa
in Landwirtschaft und Rohstoffhandel die uebliche Groesse zwischen Kilogramm und
Tonne.

Fachlich haengt daran mehr als ein Faktor: **1 dt Futtergerste entspricht
1,00 Getreideeinheit (GE)** — die GE ist die Vergleichsgroesse fuer
Futterwert-Rechnungen. Preise, Kontrakte und Abrechnungen im Getreidehandel
laufen ueblicherweise **je dt**.

**Konsequenz fuer das Modell:** dt ist keine Sonderform von kg, sondern die
**Anzeige- und Abrechnungsgroesse erster Wahl** bei Getreide. Intern wird in kg
gerechnet; angezeigt und abgerechnet wird in dt, wo der Artikel es vorgibt.
Rundung gehoert an die Anzeige, nie an den gespeicherten Wert.

## 3. Gebinde: die Verpackungsleiter je Artikel

„Gebinde" ist die zusammengefasste Verpackungs- oder Verkaufseinheit — Sack,
Karton, Kiste, Kanister, Box. Zu unterscheiden sind **Verkaufseinheit** (was der
Kunde kauft) und **Verpackungseinheit** (wie es verpackt ist); sie fallen
haeufig, aber nicht immer zusammen.

Belegte Groessen aus dem Handel:

| Warengruppe | Uebliche Gebinde |
|-------------|------------------|
| Duenger | lose Ware; Sack 25 kg; **Big Bag 500 / 600 / 750 / 1000 kg** (Umstellung von 600 auf 750 kg im Gange) |
| Saatgetreide | Sack zu **750.000 keimfaehigen Koernern** (= 0,75 Einheiten), Dinkel 500.000 (= 0,5 E) |
| Mais-/Ruebensaatgut | **Einheit zu 50.000 Koernern** (auch 100.000), Sack ca. 15 kg |
| PSM | Kanister und Flaschen in Litern; Gebinde bis 5 l/5 kg mit erleichterten Transportvorschriften |

**Die Leiter ist artikelbezogen:** Basiseinheit (kg, l, Stueck) → Gebinde
(Sack/Kanister/Big Bag mit Faktor) → Lagereinheit (Palette). Jeder Faktor gehoert
an den **Artikel**, nicht an die Einheit.

## 4. Die Saatgut-Einheit ist eine Kornzahl, kein Gewicht

Das ist der Fall, an dem ein gewichtsbasiertes Modell zerbricht.

- **Saatgetreide:** 1 Einheit = **1 Million keimfaehige Koerner**. Verkauft wird
  in Saecken zu 750.000 Koernern (0,75 E).
- **Mais/Rueben:** 1 Einheit = **50.000 Koerner** (teils 100.000). Ein
  50.000er-Sack wiegt **ca. 15 kg**.

Der Sinn: Der Landwirt bekommt eine **exakte Zahl keimfaehiger Koerner je
Hektar**, unabhaengig von Tausendkorngewicht und Keimfaehigkeit. Das Gewicht
steht zwar auf dem Etikett — zum Einstellen der Drillmaschine —, ist aber
**nicht** die Handelsgroesse.

**Konsequenz:** Einheit → kg ist **je Artikel und je Partie** verschieden (TKG
und Keimfaehigkeit schwanken). Eine Umrechnung darf nur erfolgen, wenn am
Artikel oder an der Charge ein Faktor hinterlegt ist; sonst gilt dieselbe Regel
wie oben — **nicht umrechnen, sondern sagen, dass es nicht geht.**

### 4a. Die Verpackungsleiter wird stufenweise gepflegt, nicht umgerechnet

**Praezisierung des Users, 2026-09-15:** Bei **Hybrid- und Maissaatgut ist die
Bezugsgroesse 1 Einheit (EH)**. Die Gebinde haengen daran, nicht an der
Kornzahl:

- 1 EH = 50.000 **oder** 90.000 Koerner — je Artikel verschieden
- 1 EH = 1 Sack
- 1 Big Bag = z. B. **11 EH**

**Daraus folgt eine Anforderung an das Modell, die ein erster Entwurf verfehlt
hatte:** Ein Gebindefaktor darf sich auf eine **andere Gebindestufe** beziehen,
nicht nur auf die Basiseinheit. Niemand pflegt „ein Big Bag = 550.000 Koerner"
ein — er pflegt „11 Einheiten" ein, und das Modell rechnet die Leiter herunter
(BB → EH → Korn).

Diese Zuordnungen gehoeren **in die Artikelanlage**: Bezugsgroesse,
Kornzahl je Einheit, Saeck- und Big-Bag-Groesse. Sie sind Stammdaten des
Artikels, nicht Konfiguration des Einheitensystems.

Ein Ringbezug in der Pflege (Sack → Big Bag → Sack) wird abgefangen: Die
Umrechnung liefert dann „nicht moeglich" statt endlos zu laufen oder eine Zahl
zu erfinden.

## 5. Der Pack: verbundene Artikel mit Rollenschranke

Ein **Pack** fasst *verschiedene* Artikel zu einer Verkaufseinheit zusammen — im
Pflanzenschutz ueblich, etwa Mittel plus zugehoeriges Additiv. Fachlich ist er
dem verknuepften Artikel aehnlich, hat aber eine eigene Regel.

**Zwei Zustaende, rollenabhaengig:**

- **Aufloesbar.** Der Pack darf in seine Artikel zerlegt und auf sie einzeln
  gebucht werden — wer das darf, entscheidet das Rollenrecht.
- **Gesperrt.** Die Artikel duerfen **nur miteinander** verkauft **und nur
  miteinander** zurueckgenommen werden. Eine Teilrueckgabe ist dann keine
  Mengenfrage, sondern unzulaessig.

**Eine harte Schranke aus dem Fachrecht, die fuer beide Zustaende gilt:**
Pflanzenschutzmittel duerfen **nur in der Originalverpackung** abgegeben werden;
ein Umfuellen in kleinere Verpackungseinheiten ist unzulaessig.

Daraus folgt fuer das Mengenmodell: **Ein Pack kann in ganze Artikel aufgeloest
werden, ein Artikel darin aber nie unter sein Gebinde geteilt.** „Halber
Kanister" ist keine zulaessige Teilmenge — nicht weil das Modell es nicht
koennte, sondern weil der Handel es nicht darf. Die Teilbarkeit ist damit eine
**Eigenschaft des Artikels**, nicht eine Freiheit der Belegposition.

## 6. Was daraus fuer K5 folgt

Das positionsbezogene n:m-Modell braucht je Zuordnung:

- **Quellposition** und **Zielposition**
- **Menge** und **Einheit** — und die Einheit muss in die Einheit der
  Quellposition umrechenbar sein, sonst wird die Zuordnung abgelehnt statt
  geraten
- **Status**: bereits berechnet, noch offen, vollstaendig berechnet

Dazu drei Regeln, die sich aus dem Obigen ergeben:

1. **Keine Umrechnung ohne belegten Faktor.** Masse und Volumen global,
   Zaehleinheiten nur mit artikelbezogenem Faktor. Fehlt er, ist die Zuordnung
   nicht moeglich — und das wird gesagt.
2. **Teilbarkeit ist Artikeleigenschaft.** Ein nicht teilbarer Artikel (PSM in
   Originalgebinde, gesperrter Pack) laesst nur ganzzahlige Gebinde zu.
3. **Parallele Zuordnungen duerfen dieselbe Restmenge nicht doppelt vergeben.**
   Das ist dieselbe Lektion wie FSX-011: ein Nachschlagen genuegt nicht, die
   Grenze gehoert in die Datenbank.

**Und eine fachliche Regel, die ausdruecklich nicht aus der Mengenrechnung
folgt:** Eine Gutschrift gibt **nicht automatisch** Liefermenge zur erneuten
Berechnung frei. Ob sie das tut, ist eine Entscheidung des Falls — Warenrueckgabe
ja, Preisnachlass nein. Das Modell muss beides koennen und darf keines
voraussetzen.

## 7. Was hier bewusst offen bleibt

- **Keimfaehigkeit und TKG je Partie** — sie machen die Umrechnung
  Einheit ↔ kg chargenabhaengig. Ob das im Mengenmodell abgebildet wird oder in
  der Charge bleibt, ist noch nicht entschieden.
- **Getreideeinheit (GE)** als Vergleichsgroesse ist erwaehnt, aber nicht
  modelliert; sie gehoert in die Futterrechnung, nicht in den Belegfluss.
- **Pfand und Ruecknahme von Gebinden** (Kanisterrueckgabe) sind ein eigener
  Vorgang und hier nicht behandelt.

## Quellen

- [Dezitonne — Brockhaus](https://brockhaus.de/ecs/enzy/article/dezitonne)
- [Dezitonne (dt), Maßeinheit für Massen — Agenda-21-Lexikon](https://www.agenda21-treffpunkt.de/lexikon/Dezitonne.htm)
- [Getreideeinheit — Wikipedia](https://de.wikipedia.org/wiki/Getreideeinheit)
- [Aufs Körnchen genau: Saatgetreide in Einheiten — ZG Raiffeisen](https://www.zg-raiffeisen.de/news/aufs-koernchen-genau-saatgetreide-in-einheiten)
- [Für und Wider von Saatguteinheiten — LWK Niedersachsen](https://www.lwk-niedersachsen.de/lwk/news/28306_F%C3%BCr_und_Wider_von_Saatguteinheiten)
- [Vorschriften zur Abgabe von Pflanzenschutzmitteln — BVL](https://www.bvl.bund.de/DE/Arbeitsbereiche/04_Pflanzenschutzmittel/05_Haendler/03_VorschriftenAbgabePSM/psm_VorschriftenAbgabePSM_node.html)
- [Transport von Pflanzenschutzmitteln — LK Oberösterreich](https://ooe.lko.at/transport-von-pflanzenschutzmitteln+2400+3781248)
- [Gebinde, Verkaufseinheiten, Verpackungseinheiten — Tanner AG](https://www.tannerag.ch/de/news-anwendungen/gebinde-verkaufseinheiten-verpackungseinheiten-logistische-einheiten-und-co-201813)
- [Verkaufseinheit und Verpackungseinheit einfach erklärt — Lilie GmbH](https://www.lilie-gmbh.de/neuigkeiten/beitrag/verkaufseinheit.html)
- [Dünger in Big Bags — Yara Deutschland](https://www.yara.de/pflanzenernaehrung/duengeranwendung/duenger-in-big-bags/)
- [Dünger im Big Bag vom Werk bis zum Hof — BWagrar](https://www.bwagrar.de/themen/betrieb-management/article-5436372-204222/duenger-im-big-bag-vom-werk-bis-zum-hof-.html)

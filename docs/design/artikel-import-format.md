# Artikelimport — kanonisches Zwischenformat

Stand: 2026-09-15 · Slice `FSX-ARTIKEL-IMPORT`.
Gehoert zu `docs/design/agrar-mengen-gebinde-modell.md`.

## Warum ein Zwischenformat

Lieferantenangebote kommen als PDF, Tabelle, E-Mail oder Foto. Sie werden
**zuerst** in dieses XML ueberfuehrt und erst danach geprueft und uebernommen.

Der Umweg ist der Zweck. Zwischen „was im Angebot steht" und „was im Stammsatz
landet" gehoert eine Stufe, die man **lesen, pruefen und zurueckweisen** kann.
Wer direkt aus einem PDF in den Artikelstamm schreibt, hat keinen Ort, an dem
ein Mensch widersprechen koennte.

## Fuenf Ebenen, strikt getrennt

```
Artikel → Variante → Lieferantenartikel → Gebinde → Kondition
```

Am Beispiel des Angebots GENO-Saaten:

```
Artikel: WWH Hycard (Winterweizen, Saatgut)
├─ Beizung: lt. Etikett            ← Eigenschaft der Ware
└─ Lieferant: GENO-Saaten
   ├─ Gebinde: 1 kg                 ← Eigenschaft der Bezugsquelle
   ├─ Preis 64,00 EUR/kg · BKH      ← Kondition
   ├─ Preis 66,50 EUR/kg · franko   ← Kondition
   ├─ Zahlung: 10 Tage netto
   └─ Lieferbedingungen

Logistikregeln des Lieferanten (artikeluebergreifend)
├─ BigBag 1000 kg  −1,00 EUR/dt
├─ BigBag  500 kg   Standard
├─ Sack     25 kg  +1,00 EUR/dt   (ausgenommen Hybriden)
├─ Palette 49 × 25 kg = 1225 kg
├─ Oeko-Palette 40 × 25 kg = 1000 kg
├─ Euro-Tauschpalette 20,00 EUR
└─ Anbruchpalette     20,00 EUR
```

**Der Grund ist nicht Ordnungsliebe.** „25 kg" ist keine Eigenschaft der Sorte —
dieselbe Sorte kann morgen als 500-kg-BigBag kommen. Und `franko` ist keine
Eigenschaft des Artikels, sondern eine Beschaffungskondition. Wer beides in
einen Satz wirft, kann Gebinde und Fracht nicht mehr aendern, ohne den Artikel
anzufassen — und hat beim naechsten Angebot einen zweiten Artikel.

**Die Beizung dagegen gehoert an den Artikel**, nicht an den Lieferanten: Sie
beschreibt die Ware, nicht die Bezugsquelle.

## Drei Regeln des Formats

### 1. Kein Preis ohne Preisbasis

`64,00 EUR` allein ist keine Angabe, sondern eine Zahl. Saatgut wird in **€/kg,
€/dt, €/EH und €/Gebinde** angeboten — ohne Menge und Einheit entstehen genau
die Umrechnungsfehler, die das Mengenmodell vermeidet.

Empfohlen ist die ausfuehrliche Form; die flache wird gleichwertig gelesen:

```xml
<priceBasis>
  <amount>64.00</amount>
  <currency>EUR</currency>
  <quantity>1</quantity>
  <unit>KG</unit>
</priceBasis>
```

Fehlt Menge oder Einheit, wird das Dokument **abgewiesen**.

Dasselbe gilt fuer Zu- und Abschlaege: `−1,00 EUR je dt` ist etwas anderes als
`−1,00 EUR je Gebinde`. Ein Wert ungleich null ohne `perUnit` wird abgewiesen;
`0,00` braucht keine Bezugsgroesse, weil er nichts aendert.

### 2. Unklares wird nicht gedeutet

Die Frachtangabe **„BKH"** aus der Vorlage ist nicht aufgeloest. Sie bekommt
`type = nicht_eindeutig_erkannt` und bleibt als `sourceValue` erhalten.

Sie als „ab Werk" oder „frei Haus" zu deuten waere eine Behauptung — und sie
stuende danach im Stammsatz, ohne dass jemand sie je geprueft haette. Dieselbe
Haltung wie „nicht ermittelt" im Leitstand: **lieber eine offene Angabe als eine
erfundene.**

Auch **verstandene** Werte behalten ihren Quellwert. Wer spaeter die Zuordnung
anzweifelt, soll nachlesen koennen, was dastand.

### 3. Gerechnet wird nachgerechnet

Eine Palette mit 49 Saecken zu 25 kg muss 1225 kg wiegen. Der Import prueft das
gegen die angegebenen Gebinde. Geht es nicht auf, ist das ein **Befund** — ein
Tippfehler im Angebot oder ein anderes Gebinde als angenommen. Beides will
jemand wissen, **bevor** daraus Lagerbestand wird.

## Abbruch oder Hinweis

Der Unterschied ist bewusst gesetzt:

| Fall | Folge |
|------|-------|
| Preis ohne Menge/Einheit | **Abbruch** — damit kann man nicht rechnen |
| Zuschlag ohne Bezugsgroesse | **Abbruch** — der Wert ist nicht anwendbar |
| Artikel ohne Namen, kaputtes XML | **Abbruch** |
| Frachtangabe nicht verstanden | **Hinweis** — der Rest bleibt brauchbar |
| Palette geht nicht auf | **Hinweis** — mit Nennung der vorhandenen Gebinde |

## Was dieser Slice ausdruecklich **nicht** tut

**Er schreibt nicht in den Artikelstamm.** Das Format, der Parser und die
Pruefung stehen; die Uebernahme nach `domain_inventory.articles` ist ein eigener
Schritt mit eigener Abnahme. Der Grund ist derselbe wie beim Zwischenformat
selbst: Zwischen „gelesen" und „uebernommen" gehoert eine Entscheidung.

Ebenfalls offen:

- **Die Bedeutung von „BKH“** — sie gehoert vom Lieferanten geklaert, nicht vom
  Import geraten.
- **Die Uebernahme in `domain_inventory.articles`** — die Bruecke erzeugt
  Varianten im Speicher; geschrieben wird noch kein Stammsatz.

## Die Bruecke ins Mengenmodell

`app/services/article_units_bridge.py` setzt das Importformat in das
Mengenmodell um — so, wie im Landhandel tatsaechlich gefuehrt wird:

**Je Gebindegroesse ein eigener Artikel.** Aus drei Gebinderegeln werden drei
Stammsaetze — `WWH Hycard BIG_BAG 1000 kg`, `... 500 kg`, `... BAG 25 kg`. Nicht
ein Artikel mit drei Gebinden: Lager, Disposition, Inventur und Etikett
unterscheiden Sack und BigBag, auch wenn dieselbe Sorte darin ist. Damit
erledigt sich nebenbei die Mehrdeutigkeit zweier BigBag-Groessen von selbst.

**Die Sorteneigenschaften werden vererbt** — Artikelart, Kategorie, Beizung,
Basiseinheit, Handelsgroesse und Teilbarkeit stehen in jeder Variante unter
`inherited`, damit im Stammsatz nachlesbar bleibt, woher sie kommen. Innerhalb
einer Variante laufen dann die **Chargen** mit eigener Gebinde- und
Einheitenzuordnung (`agrar_units.ChargenEinheiten`); dort gehoert das
Tausendkorngewicht einer konkreten Partie hin, nicht an den Artikel.

**Die Palette haengt nur an dem Gebinde, das sie stapelt.** Sie wird als
Vielfaches des Gebindes eingetragen — `49 x sack:25`, nicht `1225 kg` — und
steht deshalb nur im Sack-Artikel. So bleibt sie richtig, wenn sich das
Sackgewicht aendert, und taucht nicht dort auf, wo sie nichts stapelt.

**Konditionen bleiben draussen.** Zuschlaege, Ausnahmen (`HYBRID=true`) und
Palettengebuehren stehen als `conditions` neben den Einheiten — an der Variante,
zu der sie gehoeren, oder lieferantenweit. Die Verpackungsleiter beantwortet
„wie viele Kilogramm sind ein BigBag“, nicht „was kostet er“. Wer beides
vermischt, kann den Preis nicht aendern, ohne die Mengenrechnung anzufassen.

**Geraten wird nichts.** Ein unbekannter Gebindetyp, ein Gebinde in fremder
Einheit, eine Palette, die zu keinem oder zu mehreren Gebinden passt: Das gibt
einen **Hinweis**, keine gebogene Zuordnung — und die uebrigen Varianten bleiben
brauchbar. Die einzige Ableitung, die sich die Bruecke erlaubt, folgt aus dem
Recht: Pflanzenschutzmittel sind nicht teilbar, weil sie nur in der
Originalverpackung abgegeben werden duerfen.

Die Vorlage liegt als `tests/data/geno-saaten-angebot.xml` daneben — Import- und
Brueckentests lesen dieselbe Datei.

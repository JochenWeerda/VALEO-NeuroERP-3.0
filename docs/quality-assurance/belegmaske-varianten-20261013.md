# BELEG-020: Eine Belegmaske, neun Varianten

Stand: 2026-10-13 · Slice `BELEG-020` (Teil 1: Definition und Lesewege) · aus dem
[Masterplan Belegmaske mit Varianten](../design/belegmaske-varianten-masterplan.md) ·
Folge aus [Belegvertrag](belegvertrag-20261013.md), [Lesender Belegweg](belege-lesen-20261013.md),
[Rechte an Belegen](beleg-rechte-20261013.md)

## Auftrag

Entscheidung des Auftraggebers vom 13.10.2026: Für jeden Schritt einer Belegfolge keine eigene Maske,
sondern die Variante einer Belegmaske — mal mit Preisen, mal nur mit Mengen.

## Geliefert

- **Eine Quelle:** `app/core/screen_definitions_beleg.py`, `build_beleg_screen_definition(belegart)`.
  Aus einem Grundgerüst und der Variante des Belegvertrags entsteht die ScreenDefinition
  `beleg/<belegart>` — für alle neun Belegarten. Es gibt keine ausgeschriebene Definition je Belegart.
- **Was die Variante bestimmt:** Titel und Beschriftungen (Rechnung Nr. / Kunde / Umsatzsteuer gegen
  Eingangsrechnung Nr. / Lieferant / Vorsteuer), Preisspalten und Summenfelder nur mit Preisen,
  Aufwandskonto nur im Einkauf, offene Menge nur mit Folgebeleg, Buchungsstand nur, wo Finance bucht.
- **Was gleich bleibt:** fünf Reiter (Kopf, Positionen, Belegkette, Dokumente, Verlauf) und die Spalten
  von Kette, Dokumenten und Verlauf.
- **Aktionen aus dem Verzeichnis der Belegkommandos:** Adresse, Methode, Recht und Gefahrenstufe; ab
  R3 mit Bestätigung. Genau eine Hauptaktion je Variante: der nächste Schritt der Belegfolge.
- **Die Variante als Begriff der Definition** (`variant`: Belegart, Partnerrolle, mit Preisen, bucht,
  Folgebelege).
- **Lesewege für die Maske**, aus dem Belegvertrag, mit denselben Rechten:
  `GET /api/v1/belege/{belegart}/{id}/kopf` (flache Kopffelder, dazu die Aktionen des Belegs) und
  `GET …/tabs/{positionen|kette|dokumente|historie}` (Seiten in der Form der Mask-Engine).

## Nachweis

`tests/test_beleg_screen_definition.py`, 24 bestanden gegen `valeo_probe`:

- Jede der neun Varianten besteht die Regeln der Masken (`governance_errors`, `ux_lint` ohne Befund).
- Preise nur in Varianten mit Preisen; der Lieferschein hat genau die sieben Mengenspalten.
- Aktionen stimmen mit Verzeichnis und Variante überein.
- **Die Definition verspricht nichts, was der Weg nicht liefert:** Für alle 17 Referenzbelege antwortet
  jede Datenquelle, und jedes Kopffeld und jede Spalte der Definition ist in der Antwort.
- Kopf und Reiter gelten dieselben Rechte wie der Beleg: 403 ohne Rolle, das Lager ohne jeden Betrag.
- Kette lesbar beschriftet, Blättern stimmt.

## Was noch nicht gilt

- **Die Maske ist nicht sichtbar.** Die neun Definitionen sind nicht in der Registry der Masken
  eingetragen; es gibt keine Route, keinen Navigationspunkt und keinen Aufruf im Frontend. Der Eintrag
  zieht Aktionskatalog, MCP-Aktionskarte, Agenten-Handbuch, Synonyme und Routen nach und gehört mit der
  Sichtprüfung im Browser zusammen (Entscheidung E4: keine Maskenmigration ohne sie).
- **Die Maske führt noch keine Aktion aus.** Die Definition nennt die Kommandos; dass die Mask-Engine
  sie mit Idempotenzschlüssel, Version und Mengenangabe aufruft und den Zustand aus `aktionen`
  übernimmt, ist nicht gebaut.
- **Erfassen und Bearbeiten** eines Belegs in der Maske fehlt; die Variante ist lesend.
- **Bausteine** (Lieferung, Zahlung, Lager …) hängt noch keine Variante ein.
- Das Recht `belege.<recht>` der Aktionen ist ein Name der Definition; das Frontend kennt ihn nicht.

## Nachtrag Teil 2a: sichtbar nur im Testmandanten der Sichtprüfung

Entscheidung des Auftraggebers vom 13.10.2026: Die neun Belegdefinitionen dürfen registriert werden,
zunächst **nur für den autorisierten Testmandanten** `00000000-0000-0000-0000-000000000051`. Das ist
keine Produktivfreigabe.

- **Nicht in der Registry aller Mandanten.** `scripts/belegmasken_veroeffentlichen.py [--apply]`
  veröffentlicht die Varianten über den vorhandenen Weg für mandantenbezogene Masken
  (`studio_draft_store`, Stand `published_temp`). Das Skript nimmt nur Mandanten aus
  `ERLAUBTE_MANDANTEN` an; jeder andere Mandant bekommt für `beleg/…` weiterhin „nicht gefunden".
  Wiederholbar: Ein zweiter Lauf ändert nichts, eine geänderte Definition wird erneuert.
- **Route** `belege/:belegart/:id` → `pages/belege/beleg.tsx`, ein Einstieg von wenigen Zeilen auf
  `UniversalNativeDetailPage`. Kein Navigationspunkt.
- In der Entwicklungsdatenbank sind die neun Varianten für den Testmandanten veröffentlicht.
  `python scripts/belegmasken_veroeffentlichen.py --adressen` nennt die Adressen der 17 Referenzbelege.

Nachweis: `tests/test_belegmasken_veroeffentlichen.py`, 4 bestanden gegen `valeo_probe` (nicht in der
Registry; fremder Mandant abgelehnt; der freigegebene sieht alle neun, kein anderer; zweiter Lauf und
Erneuerung). `tsc --noEmit` ohne Befund; Routing-Integrität und Navigationsziele in Ordnung;
Architektur-Index 940/940.

**Nicht geprüft und weiter offen (Teil 2b):**

- **Die Sichtprüfung im Browser steht aus.** Ich habe die Maske nicht im Browser gesehen; dafür braucht
  es die Anmeldung der Testkennung mit Bindung an den Testmandanten und Bereichsrollen.
- **Aktionen:** Ob die Mask-Engine die DocFlow-Kommandos mit Idempotenzschlüssel, Version und Mengen
  aufruft und die Freigabe (APPROVAL-001) anfragen und erteilen lässt, ist nicht gebaut und nicht
  geprüft. Bis dahin ist die Maske lesend zu betrachten.
- Keine Belegliste in der Maske; ein Beleg wird über seine Adresse geöffnet.

## Nachtrag Teil 2b: Knöpfe hängen am Zustand des Belegs (Serverseite)

Befund der Sichtprüfung im Browser (Codex, `beleg-pilot-routing-preview-20261013.md`): Buchen, Freigeben
und Folgebeleg waren an einem stornierten Beleg aktiv.

- **Jede Aktion der Definition trägt `enabledWhen`** auf ein Kopffeld `aktion_<schlüssel>`
  (`zustandsfeld` in `screen_definitions_beleg.py`).
- **Der Kopfweg setzt diese Felder** aus `aktionen` des Belegvertrags — also aus Zustand, Recht und
  Freigabe. Was der Beleg nicht anbietet, fehlt; ein fehlendes Feld sperrt den Knopf.
- **`aktionshinweis`** im Kopf nennt je gesperrter Aktion den Grund vom Server („Buchen: Freigabe
  erforderlich (R3) …").
- Für den Testmandanten neu veröffentlicht.

Nachweis: `tests/test_beleg_screen_definition.py`, jetzt 25 bestanden — stornierter Beleg ohne aktive
Aktion; offene Rechnung buchbar, nicht stornierbar; Eingangsrechnung über der Grenze gesperrt mit Grund
und „Freigabe anfragen" aktiv; gebuchte Rechnung ohne „Buchen"; ohne Recht nichts aktiv.

**Noch nicht wirksam im Browser:** Die Detailseite (`UniversalNativeDetailPage`) gibt dem Renderer
keinen `screenContext` mit; ohne ihn wertet `actionIsEnabled` kein `enabledWhen` aus und lässt jeden
Knopf aktiv. Das betrifft jede native Detailmaske, nicht nur die Belegmaske. Die Datei ist bei Codex in
Arbeit (Laufzeit der Maskenaktionen); ich habe sie nicht angefasst. Nötig ist dort: `screenContext` mit
den Kopfdaten des Belegs als `data` an `UniversalMaskRenderer` geben.

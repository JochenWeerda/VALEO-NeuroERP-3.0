# Benutzerhandbuch: abgelöste Masken nachgezogen

Stand: 2026-10-12 · Slice `HANDBUCH-ABGELOESTE-MASKEN-20261012` · offener Punkt aus
[Mahnwesen-Einzelmaske](mahnwesen-einzelmaske-abloesen-20261011.md),
[Ein Mahnlauf](ein-mahnlauf-20261011.md) und
[Kontenplan-Hülle](kontenplan-huelle-abloesen-20261012.md)

## Befund

Das Kapitel Finanzbuchhaltung nannte für vier Wege noch gelöschte Masken und zeigte deren
Bildschirmfotos vom Juli:

| Weg | stand im Handbuch | zeigt tatsächlich |
|---|---|---|
| `/finance/dunning`, `/finance/mahnwesen` | `@/pages/finance/mahnwesen` | `@/pages/finance/mahnlauf` |
| `/mahnwesen/mahnlauf` | `@/pages/mahnwesen/mahnlauf` | `@/pages/finance/mahnlauf` |
| `/finance/kontenplan` | `@/pages/finance/kontenplan` | `@/pages/finance/chart-of-accounts` |

## Lieferung

- `docs/benutzerhandbuch/finanzbuchhaltung.md` aus dem Routen-Inventar neu erzeugt. Neben den vier
  Wegen kommt dadurch `/finance/rechnungstapel` ins Kapitel (123 statt 122 Routen).
- Sechs Bildschirmfotos frisch aufgenommen (Vite :3001, Playwright headless, Ausschnitt `main` bei
  1280 × 720, WebP): Mahnlauf für `finance__mahnlauf`, `finance__mahnwesen`, `finance__dunning`,
  `mahnwesen__mahnlauf`; Kontenplan für `finance__kontenplan`, `finance__chart-of-accounts`.
  Beim Aufnehmen wurde nichts geschrieben.
- `screenshot-manifest.json`: nur das Feld `module` dieser vier Einträge.

## Bewusst nicht getan

**Kein Neuerzeugen des ganzen Handbuchs.** `scripts/generate_benutzerhandbuch_full.py` hätte 14
Kapitel geändert und dabei handgeschriebenen Inhalt gelöscht: das Feldbuch-Kapitel in
`wissensbasis-kundenportal.md` (Schritte für Schläge und Maßnahmen, Fehlertabelle, Praxis-Nachweis)
und den Eintrag „Moderne Bedienung" im Inhaltsverzeichnis. Diese 13 Dateien sind unverändert.

## Offen

- **Der Generator überschreibt Handgeschriebenes.** Solange das so ist, darf er nicht blind über
  alle Kapitel laufen. Er braucht entweder geschützte Abschnitte oder eine Liste handgepflegter
  Masken.
- **13 Kapitel sind hinter dem Routen-Inventar** (neue Masken fehlen, u. a. Verkauf, CRM, Lager,
  Futtermittel). `--check` endet davor wie danach mit Fehlerstatus; die Prüfung läuft nicht in der CI.
- **Die Texte bleiben Schablone.** Auch für Mahnlauf und Kontenplan steht dort „Filter setzen,
  Speichern". Was die Masken wirklich tun (Posten abwählen, Mahnlauf ausführen; Konto anlegen,
  ändern, deaktivieren), steht nicht im Handbuch.
- **Die übrigen rund 840 Bildschirmfotos** stammen vom 08.07.2026.

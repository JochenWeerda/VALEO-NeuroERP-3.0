# Domaenenabnahme (Fahrplan M4)

Erzeugt mit `python scripts/domaenen_abnahme.py`; Quelle je Domaene ist die YAML-Datei daneben. Kriterien: Prozessliste aus der L3-Referenz, Maskenabnahme, keine Demo- oder Festwerte, Rollen geprueft ([Fahrplan](../../roadmap/fahrplan-verkaufsprodukt.md)).

| Domaene | Reifematrix | Prozesse | abgenommen | teilweise | fehlt | hoechste Luecke | Platzhaltermasken | Festwert-Treffer |
|---|---|---:|---:|---:|---:|---|---:|---:|
| [CRM (Kundenakte bis Wiedervorlage)](crm.md) | D04 | 13 | 0 | 11 | 2 | P1 | 0 | 15 |
| [Einkauf (Anfrage bis Eingangsrechnung)](einkauf.md) | D02 | 9 | 0 | 9 | 0 | P1 | 2 | 4 |
| [Annahme, Waage und Ernte (Wiegung bis Gutschrift)](ernte-waage.md) | D06 | 13 | 0 | 13 | 0 | P1 | 8 | 0 |
| [Kontrakte und Streckengeschaeft](kontrakte-strecke.md) | D11 | 23 | 2 | 19 | 2 | P1 | 3 | 0 |
| [Lager (Bestand, Korrektur, Umlagerung, Fremdware, Inventur, Chargen)](lager.md) | D05 | 12 | 0 | 12 | 0 | P1 | 12 | 10 |
| [Logistik und Fuhrpark (Tour bis Frachtabrechnung)](logistik.md) | D07 | 13 | 0 | 12 | 1 | P0 | 6 | 0 |
| [Produktion und Muehle (Rezeptur bis Chargenfreigabe)](produktion-muehle.md) | D13 | 15 | 0 | 13 | 2 | P0 | 10 | 0 |
| [Verkauf (Angebot bis Rechnung)](verkauf.md) | D01 | 10 | 0 | 9 | 1 | P1 | 8 | 0 |

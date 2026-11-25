---
title: Artikelmodell - Zuordnung a.eins / L3 / VALEO
type: reference
audience: [entwickler, fachbereich]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-24
version: 1.1.0
description: Verbindliche Zuordnung der Artikelobjekte von a.eins (AMIC) und L3 (zvoove Handel) zu vorhandenen VALEO-Strukturen, mit Beleglage und offenen Punkten.
---

# Artikelmodell - Zuordnung a.eins / L3 / VALEO

Nutzerauftrag 24.11.2026: Vor weiterer Implementierung das vorhandene VALEO-Modell untersuchen, die a.eins-Ebenen
(Mengeneinheit, Artikelstamm, Artikel, Artikel-Auspraegung) verbindlich zuordnen, keine parallelen
Stammdatenstrukturen erfinden. Diese Datei trennt **belegt** (im Code/Schema oder in einer Referenz nachgewiesen)
von **offen** (fachlich zu klaeren).

## 1. Quellen

| Quelle | Inhalt |
|---|---|
| Schema `valeo_probe` / `valeo_neuro_erp` (24.11.2026) | Tabellen und Spalten, Schluessel, Bestand |
| Migrationen `fachliche_vertiefung_wave6/9/10_20260521` | Mengeneinheiten/-gruppen, Artikelverpackung; individuelle Artikelnummern; Haupt-/Ober-/Warengruppen |
| Skill `l3-stammdaten-referenz` (Live-Erkundung L3) | Artikel-Stamm-Maske (14 Reiter), Artikel-Gruppen, Mengen-/Gebinde-Einheiten, Haupt-Artikel-Nr., VARIANTEN |
| Nutzer-Recherche L3-Analysen 2025 (24.11.2026) | Artikelnummer-Konvention, ARTIKEL-GRP, Feldliste, Master-Nr. |
| a.eins-Hilfe (vom Nutzer eingefuegt) | Mengeneinheit, Gebinde, Gebindetypen, Faktorherkunft, LVS |

Die frueher erwaehnte lokale a.eins-Sammlung `docs/Referenz-ERP-reference/` ist im Repository nicht (mehr) vorhanden.

## 2. Zuordnung

| Fachobjekt | a.eins | L3 | VALEO (vorhanden) | Stand |
|---|---|---|---|---|
| Mengeneinheit | Mengeneinheit (Grund-/Gebinde-ME) | Mengen-Einheiten, Gebinde-Einheiten | `domain_shared.artikel_mengeneinheiten` (Wave 6, erweitert #186/#191) | **belegt** |
| Mengeneinheitsgruppe | Zuordnung zum Artikel - ME-Gruppe | Alternativ-Einheiten am Artikel (Reiter EINHEITEN) | `domain_shared.artikel_mengeneinheitengruppen` (Wave 6); `domain_inventory.article_units` (nur `create_all`, 0 Zeilen) | belegt, **nicht mit `articles` verknuepft** |
| Artikelverpackung | Artikelverpackung | Gebinde / Gebinde-Nr. | `domain_shared.artikel_verpackungen` (Wave 6, 3 Stufen) | belegt, nicht verknuepft |
| Haupt-/Ober-/Warengruppe | Haupt-/Ober-/Warengruppen | Artikel-Gruppe (ARTIKEL-GRP) | `domain_shared.hauptwarengruppen` -> `oberwarengruppen` (`haupt_id`) -> `warengruppen` (`ober_id`) (Wave 10) | belegt; **`articles.warengruppe` ist Freitext ohne Fremdschluessel** |
| Artikel | Artikel | Artikel-Nr. (Artikel-Stamm F3) | `domain_inventory.articles` (Schluessel `(id, tenant_id)`) | **belegt** |
| Individuelle Artikelnummer | Individuelle Artikelnummern | Kunden-/Lieferanten-Art.-Nr. | `domain_shared.individuelle_artikelnummern` (Wave 9) | belegt |
| Artikelstamm | eigene Ebene ueber dem Artikel | Modul heisst "Artikel-Stamm", ist aber die Artikelmaske selbst | **kein Gegenstueck** | **offen** |
| Artikel-Auspraegung | eigene Ebene unter dem Artikel | Reiter VARIANTEN; Block "Haupt-Artikel-Nr." (Verknuepfung zu uebergeordnetem Artikel) | **kein Gegenstueck**; keine Haupt-Artikel-Spalte in `articles` | **offen** |
| Master-Nr. | - | Feld in Einkauf-Lieferschein-Positionen | `master_nr` nur im Schema `einkauf_lieferschein` (Position), ohne Fachbedeutung | **offen** |

Folgerung fuer die Gebinde-Faktorherkunft (unveraendert vier a.eins-Stufen):

- Stufe 1 Mengeneinheit -> Stammsatz der Mengeneinheit. **Pflegbar.**
- Stufe 3 Artikel -> `domain_inventory.articles`, Fremdschluessel `(artikel_id, tenant_id)`. **Pflegbar.**
- Stufe 2 Artikelstamm und 4 Auspraegung -> **nicht pflegbar (422)**, bis zugeordnet. Der Suchpfad laeuft ueber die
  vorhandenen Stufen nach unten.

## 3. Nicht gleichsetzen

- **Artikelgruppe ist nicht Artikelstamm.** In L3 ist die Artikel-Gruppe ein eigenes Objekt (ARTIKEL-GRP), auf das
  andere Bereiche verweisen; in VALEO entspricht ihr die Warengruppen-Hierarchie (Wave 10), nicht eine Gebindestufe.
- **L3 "Artikel-Stamm" ist nicht a.eins "Artikelstamm".** In L3 ist es der Name der Artikelmaske (Ebene Artikel).
- **L3 "Haupt-Artikel-Nr." / VARIANTEN ist ein Kandidat fuer a.eins "Auspraegung"** oder fuer "Artikelstamm"
  (der Haupt-Artikel als uebergeordnete Produktidentitaet). Welche Richtung gilt, ist nicht belegt.

## 4. L3-Nummernsystem (Migration, kein Systemzwang)

Bei Folkerts bilden die ersten drei Stellen der L3-Artikelnummer die Artikelgruppe (220050 -> Gruppe 220; Nutzer-
Recherche, Rennerlisten-Auswertung 03.09.2025). Das gehoert in die **L3-Uebernahme** (Ableitung der Warengruppe beim
Import), nicht als Pflichtregel in VALEO - andere Mandanten nummerieren anders. Im gewachsenen Bestand von
`valeo_neuro_erp` (Testdaten, 132 Artikel) kommt die Konvention nicht vor.

## 5. Offene Punkte (fachlich zu klaeren)

1. **Artikelstamm und Auspraegung in a.eins** - Bedeutung laut Hilfe ("Artikelstamm und Artikel - Uebersicht",
   Auspraegungsseite; beim Nutzer angefragt).
2. **L3 Haupt-Artikel-Nr. und VARIANTEN** - an einem Artikel der Art "Variante"/"Baugruppe" erkunden (Skill
   `l3-stammdaten-referenz`: Reiter nur bei typisierten Artikeln sichtbar).
3. **L3 Master-Nr.** - Bedeutung in der Einkauf-Lieferschein-Position.
4. **`articles.warengruppe`** - Freitext an die Warengruppen-Hierarchie binden (Fremdschluessel); Altwerte sind
   Testdaten. Eigener Schnitt.
5. **Mengeneinheitsgruppe und Artikelverpackung an den Artikel binden** - beide existieren (Wave 6), ohne Bezug zu
   `articles`; `article_units` existiert nur ueber `create_all`. Konsolidieren statt neu anlegen. Eigener Schnitt.

Gewuenscht vom Nutzer, um 1-3 zu schliessen: L3-Masken Artikel-Stamm (alle Reiter), Artikelgruppen-Stamm,
Gebindestamm, Mengeneinheiten-Stamm.

## 6. Coverage-Matrix L3-Artikelstammmaske -> VALEO (Stand 24.11.2026)

Grundlage: zehn Originalaufnahmen L3/zvoove Handel 26.07.01 (Nutzer, 24.11.2026) und Skill `l3-stammdaten-referenz`,
abgeglichen gegen das Schema von `valeo_probe` (Spalten von `domain_inventory.articles`, Tabellen) und den Code.
Einstufung: **vorhanden** (Feld/Tabelle mit fachlich passender Bedeutung), **teilweise** (Daten da, Beziehung oder
Wirkung fehlt), **fehlend**, **redundant** (mehrere Orte fuer dieselbe Sache), **ungeklaert** (Bedeutung offen).
"Feld vorhanden" heisst nicht, dass das Kennzeichen serverseitig wirkt - das ist je Kennzeichen eigens zu pruefen.

### 6.1 Identitaet und Beziehungen

| L3 | VALEO-Artefakt | Stand |
|---|---|---|
| Artikel-Nr., Bezeichnung 1/2, Kurztext | `articles.article_number`, `name`, `description2`, `short_description` | vorhanden |
| 2. Matchcode, Suchbegriff | `articles.matchcode2`, `suchbegriff` | vorhanden |
| Artikel-Gruppe | `articles.warengruppe` (Freitext) + `domain_shared.warengruppen`/`oberwarengruppen`/`hauptwarengruppen` | teilweise - kein Fremdschluessel |
| Artikel-Art (1000 = Normal-Artikel Lager) | `articles.lagerartikel` (bool), `category` | ungeklaert - kein Artikelart-Schluessel |
| Sort.-Nr. | - | fehlend |
| Artikel gesperrt | `articles.is_active`, `domain_shared.artikel_sperren`, `domain_compliance.compliance_artikel_sperre_audit` | redundant - Sperre an zwei Orten |
| Selektionen | `domain_inventory.article_selections` | vorhanden |
| Haupt-Artikel-Nr. | - | **fehlend** (Kandidat a.eins Artikelstamm, ungeklaert) |
| Varianten (Reiter) | - | **fehlend** (Kandidat a.eins Auspraegung, ungeklaert) |
| Alternativ-Artikel 1-5 | - | fehlend |
| Folgeartikel | `domain_shared.artikel_folgeartikel` (Artikelnummern als Text) | teilweise - kein Fremdschluessel |
| Baugruppe (2 Reiter) | `domain_shared.stuecklisten`/`stuecklisten_positionen`, `artikel_bestandteile_def`/`_zuordnung` | ungeklaert - welche Struktur der L3-Baugruppe entspricht |
| Lieferanten, Lieferanten-Art.-Nr. | `domain_inventory.article_suppliers`; `articles.lieferanten_artikelnummer`, `lieferantennummer`, `supplier_number` | redundant - Lieferant am Artikel dreifach |
| Individuelle Artikelnummern | `domain_shared.individuelle_artikelnummern` | vorhanden |

### 6.2 Einheiten, Gebinde, Preisbezug (Schnitt 2b)

| L3 | VALEO-Artefakt | Stand |
|---|---|---|
| Mengen-Einheit | `articles.unit` (Text) + `domain_shared.artikel_mengeneinheiten` | teilweise - Einheit am Artikel nicht an den Stamm gebunden |
| Gewicht | `articles.weight` | vorhanden |
| hl-Gewicht | - | fehlend |
| Preis je (Bezugsmenge) | `articles.einheit_preiseinheit` (Text "100 kg"), `artikel_mengeneinheiten.preisbezug_*` (#186), `document_items.price_unit_quantity` (#193) | redundant - drei Orte; Vorbelegung Stamm -> Position fehlt |
| Verpackungsart, Gebinde, Gebindemenge | `articles.gebinde_groesse`, `gebinde_einheit`; `domain_shared.artikel_verpackungen` | redundant/teilweise - Verpackung nicht am Artikel |
| Alternativ-Einheiten (Schluessel, Umrechnung, Einheit, Runden) | `domain_inventory.article_units` (nur `create_all`, 0 Zeilen), `artikel_mengeneinheitengruppen`, Gebindefaktoren Stufe 3 (#191) | redundant - Umrechnungsrichtung und Runden in L3 ungeklaert |
| Paletten | `domain_einkauf.paletten_konto_buchungen` | teilweise (Paletten-Konto, nicht Artikelstamm) |
| Kennz. Disposition, Verpackungsmaterial-Verbrauch | - | fehlend |

### 6.3 Steuer, Bewertung, Preise, Rabatte

| L3 | VALEO-Artefakt | Stand |
|---|---|---|
| Steuerschluessel / Satz | `articles.steuerschluessel_verkauf`/`_einkauf`, `mehrwertsteuer_prozent` | redundant - Satz gehoert in `tax_keys` (Steuerlogik eine Quelle) |
| Bewertungs-Art (D = Durchschnitts-EK), Bewertung-Prozent | `app/services/bestandsbewertung.py` (gleitender Durchschnitt systemweit, #184/#189) | teilweise - keine Wahl je Artikel |
| Verkaufs-Preistabellen, Gueltigkeit, Staffeln | `domain_pricing.price_lists`/`price_list_items`, `staffelrabatte`/`staffelrabatt_artikel` | vorhanden |
| Empfohlener VK, kalkulatorischer EK | `articles.sales_price`, `purchase_price` | teilweise - Bedeutung nicht getrennt benannt |
| Bewertungspreis, Marktpreis | Bewertung aus Bewegungen (#184) | ungeklaert - eigener Marktpreis fehlt |
| Auftrags-/Lose-/Selbstabholer-Rabatt, Zu-/Abschlag 1/2, auf Positionsnetto, Summenzeile, skontierfaehig, WRV, Bonus, rabattfaehig | `articles.rabatt_*`, `zu_abschlag_1_*`/`_2_*`, `berechne_zu_abschlag_auf_netto`, `einfuegen_summe_nach_zu_abschlag`, `skontofaehig`, `warenrueckverguetung`, `bonus_faehig`, `rabattfaehig` | vorhanden (Felder) - **Zu-/Abschlag als Folgeposition fehlt im Rechenkern** |

### 6.4 Kennzeichnung, Landhandel, Gefahrgut, Einstellungen, Dokumente

| L3 | VALEO-Artefakt | Stand |
|---|---|---|
| Kontrakt erlaubt, Chargen-/Serien-Nr., Bioware, Waage-Artikel, PflSchG, Explosivstoff-Ausgangsstoff, nur Einzelverkauf, Umbuchung bei LS-Freigabe | `articles.kontrakt_erlaubt`, `chargen_nr_erforderlich`/`chargenpflicht`, `serien_nr_erforderlich`, `bioware`/`bio_kennzeichnung`, `waage_artikel`, `pflanzenschutzmittel`, `explosionsstoff`, `nur_einzelverkauf`, `artikel_umbuchung_bei_ls_freigabe` | vorhanden (Felder); Chargen- und Bio-Kennzeichen doppelt; Wirkung je Kennzeichen ungeprueft |
| Haltbarkeit, Regal-Flaeche, Min.-Menge Auftrag, Kostenstelle, Duengemittel-Inhalte | `haltbarkeit_tage`, `regal_flaeche`, `min_menge_auftrag`, `kostenstelle`, `duengemittel_inhalte_*` | vorhanden |
| EAN, alternative EAN | `ean_code`, `alt_ean_code`, `domain_inventory.article_alternative_eans` (nur `create_all`) | redundant |
| Webportal, Intrastat, Etiketten | `web_sichtbar`, `web_preis_auf_anfrage`, `intrastat_warennr`/`zolltarifnummer`, `etikett_*` | vorhanden |
| Belegartbezogener Druck der Beschreibung | `druck_anfrage` ... `druck_wiegeschein`, `druck_statt_artikel_bezeichnung`, `druck_zusaetzlich` | vorhanden (Felder) - Wirkung in DocFlow-Vorlagen ungeprueft |
| LH: Kauf-Abrechnung, MVA, Mahlerzeugnis, Schnittstellen-Nr., Nachhaltige Biomasse, Waage-Etikett, NaWaRo, Getreidemeldung, MVO | `kaufabrechnung`, `mva_kontrakt`, `mahlerzeugnis`, `schnittstelle_*`, `nachhaltige_biomasse`, `waage_etikett_art`, `nawaro_endprodukt`, `getreidemeldung_*`, `mvo_*` | vorhanden |
| Kaufabrechnung-Sorten | `domain_shared.agrar_sorten` | ungeklaert - Zuordnung Artikel <-> Sorte |
| Gefahrgut: Klasse, UN-Nr., Verpackungsgruppe, Bezeichnung | `gefahrgutklasse`, `gefahrgut_un_nummer`, `gefahrgut_verpackungsgruppe`, `gefahrgut_anhaenge` | teilweise - Befoerderungskategorie, Multiplikationsfaktor, Befreiungsmenge, Tunnelbeschraenkung fehlen |
| Einstellungen: Formel-Nr. Aufmass, Kasse (Preiseingabe, Altersprüfung, Pfand, Kombikiste, Bon-Text), Kommission, Toleranz-Menge | - | fehlend (Kasse ggf. im POS-Bereich - ungeklaert) |
| Unterlagen, Dateien | `domain_inventory.article_documents` | teilweise |
| Analysen | `analyse_text`, `analyse_bild_datei`, `analyse_*` | vorhanden |
| Saatgut (Reiter) | `domain_agrar.agrar_saatgut`, `saatgut_partien`, `agrar_saatgut_lizenzen` | vorhanden (eigene Tabellen) |

### 6.5 Folgerungen fuer die naechsten Schnitte

1. **Konsolidieren statt anlegen:** Preisbezug (drei Orte), Alternativ-Einheiten (`article_units` / ME-Gruppen /
   Stufenfaktoren), Verpackung (`gebinde_*` / `artikel_verpackungen`), Lieferant am Artikel, Sperre, EAN.
2. **Beziehungen referenziell machen:** Warengruppe, Folgeartikel, Mengeneinheit am Artikel - mandantengebundene
   Fremdschluessel statt Text.
3. **Fehlend, aber belegt:** Alternativartikel 1-5, Sort.-Nr., hl-Gewicht, Zu-/Abschlag als Folgeposition im
   Rechenkern.
4. **Nicht ohne Fachnachweis:** Haupt-Artikel-Nr. und Varianten (a.eins Artikelstamm/Auspraegung), Baugruppe, Artikel-
   Art. Erst nach den angefragten L3-Aufnahmen (Haupt-Artikel befuellt, Varianten, Artikelgruppen-Stamm,
   Gebindestamm, Mengeneinheiten-Stamm).
5. Die vier a.eins-Faktorherkunftsstufen bleiben; die L3-Artikelgruppe ist **keine** zusaetzliche Faktorherkunft.

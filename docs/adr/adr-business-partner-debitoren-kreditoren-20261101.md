---
title: Geschäftspartnerstamm führt Debitoren und Kreditoren
type: adr
audience: [entwickler, architektur, qa]
owner: Claude
status: akzeptiert
last_reviewed: 2026-11-01
version: 1.0.0
description: Debitorenanlage im fuehrenden Kundenstamm, Kundennummer je Mandant und Stufenplan zum zentralen Geschaeftspartnerstamm.
---

# ADR: Geschäftspartnerstamm führt Debitoren und Kreditoren

**Status:** Akzeptiert. **Datum:** 2026-11-01.

## Kontext

Die Debitorenanlage (`finance/debitoren/new`) schrieb in `domain_erp.debitors`. Liste und Detail
(`/api/v1/finance/debitoren`) lesen dagegen `domain_crm.customers`. Ein neu angelegter Debitor
erschien deshalb nie in der Liste, und die Detailmaske nach der Anlage meldete 404.

Bestandsaufnahme vom 01.11.2026 (Code: Dateien in `app/` und `modules/`, die die Tabelle nennen;
Zeilen: gewachsene Entwicklungsdatenbank / frisch migrierter Prüfstand):

| Aggregat | Rolle heute | Code | Zeilen dev / Prüfstand |
| --- | --- | --- | --- |
| `domain_crm.business_partners` | Zielmodell: Partner-ID je Mandant, Rollenflags `is_customer`/`is_supplier`, `debtor_account`/`creditor_account`, Bank, Steuer | 19 | 7 / 0 |
| `domain_crm.customers` | führender Kundenstamm; Liste/Detail Debitoren, Belege, Annahme, Portal | 41 | 6 / 0 |
| `public.kunden` | L3-Altstamm ohne Mandant, Satelliten über `kunden_nr` | 23 | 463 / 0 |
| `domain_erp.debitors` | nur noch Altlese-/Änderungswege (`/finance/debtors/{id}`), Export | 4 | 0 / 0 |
| `domain_einkauf.lieferanten` | führender Kreditorenstamm (`/finance/kreditoren`); Spalte `partner_id` ungenutzt | 12 | 18 / 0 |
| `domain_erp.creditors` | Altweg `creditors.py` | 2 | 0 / 0 |

Fremdschlüssel auf `domain_crm.customers` im Prüfstand: Aktivitäten, Anfragen, Leads, Angebote,
Aufträge, Lieferscheine, Trocknungsregeln, Erntennahmen, Portal-Empfehlungen, Lohndienst und
`domain_erp.debitors.customer_id`. Offene Posten (`domain_erp.offene_posten.debtor_id`) und das
CRM-360 vergleichen `debtor_id` bereits mit der Kunden-ID. Die Debitorenidentität ist also schon
heute die Kunden-ID. `domain_erp.debitors` ist der einzige Abweichler.

## Entscheidung

1. **Ziel:** Ein Geschäftspartner je Mandant (`domain_crm.business_partners.partner_id`) mit Rollen.
   CRM führt Kundenbeziehung (Kontakte, Aktivitäten, Angebote), Einkauf die Lieferantenrolle
   (Konditionen, Bestellungen), die Debitoren-/Kreditorenbuchhaltung Konto, OP, Zahlungsbedingungen,
   Mahnwesen und Kreditlimit. Ein Landwirt, der Getreide liefert und Dünger kauft, ist **ein**
   Partner mit Debitoren- und Kreditorenrolle, nicht zwei Stammsätze.
2. **Übergang (ab sofort):** `domain_crm.customers` ist der führende Debitorenstamm. Die Anlage läuft
   über die eine Fachaktion `CustomerService.create_customer`; `POST /api/v1/finance/debitoren` und
   der Altzugang `POST /api/v1/finance/debtors/` sind Zugänge dazu, kein eigener CRUD-Pfad.
   `domain_erp.debitors` bekommt keine neuen Zeilen mehr.
3. **Nummern je Mandant:** `customer_number` ist je Mandant eindeutig
   (`uq_customers_mandant_nummer`, Migration `kundennummer_mandant_20261101`), nicht systemweit.
4. **Nicht gehaltene Felder werden abgelehnt, nicht verworfen.** Seit Stufe 3 liegen Bankverbindung,
   Skonto und Steuernummer am Geschäftspartner; was weiterhin kein Ziel hat (Notizen), beantwortet die
   Anlage mit 422, statt es still fallen zu lassen.
5. **DSGVO:** Zuordnung und Löschprüfung nur über eindeutige, mandantenbezogene IDs. Aktivitäten, die
   nur über einen gleichen Freitextnamen passen, werden nicht gelöscht (bestätigt 01.11.2026).
6. **Nicht destruktiv:** Keine Tabelle wird gelöscht, keine Nummer neu vergeben, keine Buchung oder
   Belegreferenz umgeschrieben. GoBD-relevante Referenzen bleiben nachvollziehbar.

## Plan zur Vereinheitlichung

Jede Stufe ist einzeln auslieferbar und braucht beide Prüfstände (Schema frisch, Daten gewachsen).

| Stufe | Inhalt | Prüfkriterium |
| --- | --- | --- |
| 0 (erledigt 01.11.) | Anlage in den Kundenstamm, Nummer je Mandant, Adressspalte für JSONB und VARCHAR | Anlage → Liste → Detail auf frischem Prüfstand; fremder Mandant sieht nichts |
| 1 (erledigt 01.11.) | Partnerbrücke: `BusinessPartnerService.partner_fuer_rolle` in Kundenanlage (`CustomerService.create_customer`), Interessenten-Konvertierung, CSV-Kundenimport und Lieferantenanlage (`ProcurementService.create_lieferant`); wiederverwendet nur bei eindeutiger USt-IdNr. **und** Name im Mandanten, ein Name allein ordnet nie zu; Rolle `is_customer`/`is_supplier` am Partner; kein eigener Commit | kein neuer Kunde/Lieferant ohne Partner-ID; Landwirt als Kunde und Lieferant = ein Partner; fremder Mandant teilt keinen Partner |
| 2 (erledigt 01.11.) | Rückfüllung (`partner_rueckfuellung_20261101`): ordnet Kunden und Lieferanten ohne Partner nach der Regel der Brücke zu, IDs/Nummern/Belege unverändert; Klärliste `domain_crm.partner_klaerfaelle` (RLS) für: ohne USt-IdNr. bei gleichnamigem Partner, mögliche Dublette (mehrere Kunden bzw. Lieferanten mit gleicher USt-IdNr. und Name), USt-IdNr. eines Partners anderen Namens, mehrere passende Partner, Mandant ohne Stammsatz, Verknüpfung auf fehlenden/fremden Partner; Protokoll `partner_rueckfuellung_protokoll`, Downgrade nimmt nur Protokolliertes zurück | Probelauf gewachsene DB 01.11.: 20 zugeordnet, 4 Klärfälle; Downgrade stellt den Ausgangsstand her |
| 3 (erledigt 01.11.) | Rollenfelder am Partner: Debitoren- und Kreditorenanlage nehmen IBAN (Mod-97), BIC, Bank, Kontoinhaber, Skonto und Steuernummer an und legen sie am Geschäftspartner ab; ein bestehender Partner bekommt nur leere Felder gefüllt, abweichende Werte → 409 statt Überschreiben; Kreditor-Änderung lehnt Bankfelder ab (am Partner pflegen); Debitor- und Kreditor-Detail zeigen die Partnerfelder schreibgeschützt. Klärfälle werden in `crm/partner-klaerfaelle-liste` per Zeilenaktion entschieden (`zuordnen` zu einem Partner des Mandanten, `neuer-partner`), mit Begründung, Audit und Ereignis, Recht `STAMMDATEN` | Landwirt als Kunde und Lieferant: gleiche IBAN passt, andere IBAN → 409; fremder Partner nicht zuordenbar; Fall danach erledigt |
| 3b | Konten und SEPA: `debtor_account`/`creditor_account` am Partner vergeben, SEPA-Mandat (`domain_shared.sepa_mandates.debitor_id`) auf den Partner beziehen | Fachentscheidung zur Kontennummernvergabe offen |
| 4 | Lesewege umstellen: Debitoren-/Kreditorenliste lesen Partner + Rolle; OP-Zuordnung über ID statt `kunde_name` (`_op_by_name`) | Liste stimmt bei Namensgleichheit zweier Kunden |
| 5 | Altwege stilllegen: `/finance/debtors/{id}` (GET/PUT/DELETE), `creditors.py`, `crm/convert-lead` (`customer_extensions.py`; liest `domain_crm.leads` über ein ORM-Modell, das zum frischen Schema nicht passt — seit 01.11. mandantengebunden und mit Brücke), Export aus `domain_erp.debitors`; Tabellen bleiben als Archiv lesbar | keine Codereferenz außer Archivlesen |
| 6 | `public.kunden` (L3-Altstamm) über `business_partner_id` anbinden; separates Vorhaben | eigene ADR |

## Konsequenzen

- Neue Debitoren erscheinen sofort in Liste und Detail; die Anlage aus Finanzen und CRM ist dieselbe Fachaktion.
- Seit Stufe 3 erfasst `finance/debitoren/new` Bank, Skonto und Steuernummer wieder; sie landen am Geschäftspartner. Notizen bleiben ohne Ziel und werden abgelehnt.
- Bis 01.11.2026 scheiterte die lokale Kundenanlage auf jeder frisch migrierten Datenbank, sobald eine Straße angegeben war: Die Migrationen legen `address` als JSONB an, die gewachsene Entwicklungsdatenbank als VARCHAR. Der Dienst schreibt jetzt die Form, die die Spalte hat.
- Bei Anlage über crm-core trägt der lokale Eintrag jetzt Kreditlimit, Zahlungsziel, USt-IdNr. und Adresse; vorher nur Nummer und Name.
- Klärfälle werden in der Studio-Liste entschieden; bis dahin bleiben diese Sätze ohne Partner.
- Die gewachsene Entwicklungsdatenbank hat bei `business_partners` 34 Pflicht-Booleans ohne Default; Brücke und Rückfüllung setzen sie ausdrücklich auf `false`.
- Der Altweg `/finance/debtors/{id}` liest weiter `domain_erp.debitors` (überall leer). Die Legacy-Rückfallmaske kann einen neuen Debitor dort nicht öffnen; sie ist nur Rückfall, wenn die native Maske fehlt (Stufe 5).

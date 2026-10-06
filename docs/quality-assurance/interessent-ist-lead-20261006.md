# Interessent ist Lead (Slice INTERESSENT-IST-LEAD-20261006)

Stand: 2026-10-06 · Welle 2, Slice 19

## Befund 1 — drei Modelle für einen Begriff, und der benutzte war der leere

| Tabelle | Inhalt | Zeilen (Dev) | Wer |
| --- | --- | --- | --- |
| `public.crm_leads` | company, contact_person, email, phone, source, potential, priority, status | **97** | `crm_lead_gen_service`, `crm_partner_suche`, `crm_reports` |
| `domain_crm.leads` | customer_id, lead_source, estimated_value, probability | 0 | `compliance_dsgvo` |
| `domain_crm.interessenten` | — | **existiert nicht** | `customers.py` |

`domain_crm.leads` hängt an einem `customer_id`: Das ist eine **Verkaufschance an
einem bestehenden Kunden**, kein Interessent. `public.crm_leads` ist das Register,
das Daten führt — die übernommenen Leads der Durchdringungs-Akquise (`source`:
`lkv`, `gap`).

`domain_crm.interessenten` wurde **nicht angelegt**. Ein vierter Begriff für
dieselbe Sache wäre das Gegenteil einer Ordnung, und die Daten liegen schon
woanders.

Ein fünfter Ort heißt auch „Interessent": `portal_interessent.py` hält die
Selbstregistrierung aus dem Portal **im Speicher** (eine Liste, kein Tabellenbezug).
Das ist ein anderer Vorgang (Onboarding vor der Anlage) und bleibt unberührt.

## Befund 2 — eine Quittung ohne Vorgang

```python
    except Exception:
        db.rollback()

    return {"id": new_id, "interessenten_nr": interessenten_nr,
            "status": "INTERESSENT", **payload.model_dump()}
```

Der Weg antwortete `201` mit einer Interessentennummer, auch wenn der INSERT
scheiterte — und er scheiterte immer, weil die Tabelle nicht existiert. Die Liste
antwortete `[]`. Ein Haus, das keine Interessenten sieht, akquiriert nicht und
merkt nicht, dass die Liste nur nicht lesbar war.

Die Nummer kam aus `COUNT(*) + 1` mit `except: pass` → `seq = 1`. Zwei Fehler in
einer Zeile: Jeder übernommene Akquise-Lead ohne Nummer verschob die Zählung, und
ein Lesefehler ergab immer `INT-JJJJ-00001`.

## Befund 3 — die Löschung nach Art. 17 DSGVO traf die leere Tabelle

```sql
UPDATE domain_crm.leads SET company_name = :anon_name,
       contact_person = :anon_name, email = :anon_email, phone = NULL
```

**Diese vier Spalten gibt es dort nicht.** Der Schritt scheiterte mit
`UndefinedColumn`, landete als Fehler im Protokoll, und
`_loeschung_ist_vollstaendig` lieferte `False`: **Jeder Löschantrag zu einem Lead
blieb dauerhaft `IN_BEARBEITUNG`** — Art. 12 Abs. 3 DSGVO verlangt den Bescheid
innerhalb eines Monats. Gleichzeitig blieben die Personendaten unberührt, denn sie
liegen in `public.crm_leads`: 97 Zeilen mit Firmenname, Ansprechpartner, E-Mail
und Telefon.

Zwei Pflichten verletzt auf einmal — die Löschung (Art. 17 Abs. 1) und der
Bescheid (Art. 12 Abs. 3).

**Dass das überhaupt auffiel, ist das Verdienst des vorangegangenen
Art.-17-Slices:** Dort wurden Sicherungspunkte je Schritt und ein ehrliches
Protokoll eingebaut, und der Status wird nur noch auf `ABGESCHLOSSEN` gesetzt,
wenn wirklich gelöscht wurde. Ohne diese Arbeit hätte der Antrag „erledigt"
gemeldet, und niemand hätte gemerkt, dass nichts gelöscht wird.

Jetzt anonymisiert der Schritt `public.crm_leads` (`company`, `contact_person`,
`email`, `phone`, `notes`, `assigned_to`) und zusätzlich `domain_crm.leads.notes`
— die Verkaufschance führt keine Namen, aber eine Notiz kann Personenbezug
enthalten.

## Befund 4 — `konvertieren` quittierte einen Kunden, den es verwarf

Der Weg legte über `BusinessPartnerService.create_customer_record` einen echten
Kundensatz an und setzte danach den Interessentenstand in einem **eigenen**
`try/except: db.rollback()`. Scheitert dieses UPDATE, nimmt das `rollback` den
Kundensatz mit — dieselbe Transaktion — und die Antwort meldete trotzdem
`status: "KUNDE"` samt Kundennummer. Ein Haus hätte eine Kundennummer gehabt, zu
der es keinen Kunden gibt.

Jetzt ist es **eine** Transaktion: Kundensatz und Standwechsel gelten zusammen
oder scheitern zusammen. Ein zweiter Durchlauf wird abgewiesen (er legte einen
zweiten Kundensatz an), und die Zeile wird mit `FOR UPDATE` gesperrt.

## Was jetzt gilt

* `GET/POST /crm/customers/interessenten` und
  `POST …/{id}/konvertieren` arbeiten auf `public.crm_leads`.
* Die Spaltennamen des Registers sind englisch, der Weg nennt sie deutsch. Die
  Abbildung steht **einmal** (`interessent_service.als_dict`,
  `HERKUNFT_ZU_QUELLE`), damit nicht beide Benennungen durch den Code wandern.
* Die Interessentennummer wird in den Notizen vermerkt (`[INT-JJJJ-NNNNN]`), weil
  das Register keine Nummernspalte führt. Gezählt wird die **höchste vermerkte**
  Nummer. Übernommene Akquise-Leads haben keine Nummer, und es wird keine
  erfunden — `interessenten_nr` ist dort `null`.
* Statuswörterbuch `NEW`/`CONTACTED`/`QUALIFIED`/`CONVERTED`/`LOST`, geprüft beim
  Filtern. Es bleibt englisch, weil 97 Zeilen darauf stehen.
* Eigene Antwortmodelle (`InteressentOut`) statt `CustomersOut` mit
  `extra="allow"`; Pagination mit `limit`/`offset`.
* `uuid7` statt `uuid4`.

**Keine Migration.** `public.crm_leads` existiert und führt die Daten. Es wurde
keine Tabelle angelegt und keine gelöscht.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_interessent_ist_lead_vertrag.py   → 19 passed
  + DSGVO/CRM/Portal (5 Dateien)               → 53 passed
```

Die 19 Verträge prüfen unter anderem: ein angelegter Interessent steht in
`public.crm_leads` und erscheint in der Liste; `domain_crm.interessenten` wird
nicht angelegt und im Code nicht mehr gelesen; übernommene Akquise-Leads
erscheinen mit und tragen keine erfundene Nummer; die Nummern laufen hoch und
nummernlose Zeilen verschieben die Zählung nicht; ein Lesefehler vergibt nicht die
Nummer eins; ein Schreibfehler ist ein 409 und keine Quittung (strukturell
geprüft: jeder `except`-Zweig mit `rollback` wirft erneut, per AST); die
Konvertierung erzeugt Kunde **und** Standwechsel, ein zweites Mal wird abgewiesen,
und scheitert der Standwechsel, bleibt **kein** Kundensatz zurück; eine
Art.-17-Löschung anonymisiert das Register und schließt den Antrag ab
(`rows_affected == 1`, kein Fehler im Protokoll).

Gates: Tabellenverweise **2 → 1** an lebenden Wegen; Paginierungs-Baseline
gesenkt; Baseline-Integrität und tote Transaktionen grün.

## Offene Punkte (Handshake)

1. **`public.crm_leads` liegt im `public`-Schema**, was der Mehrschema-Ordnung
   widerspricht. Der Umzug nach `domain_crm` ist ein eigener Slice **mit Daten**
   (97 Zeilen) und berührt `crm_lead_gen_service`, `crm_partner_suche`,
   `crm_reports`.
2. **`domain_crm.leads` ist leer und meint etwas anderes** (Verkaufschance an
   einem Kunden). Ob dieser Begriff gebraucht wird, gehört in den CRM-ADR; die
   Tabelle bleibt vorerst.
3. **Der Portalweg** (`portal_interessent.py`) hält Interessenten im Speicher.
   Eine Selbstregistrierung, die einen Serverneustart nicht übersteht, ist eine
   eigene Lücke.
4. **Fremder Rotstand, Godfile:** `app/api/v1/endpoints/personal.py` ist im
   geteilten Baum von 3315 auf 3342 Zeilen gewachsen (ein neuer
   `delete_application`-Weg, nicht committet). Das bricht die Ratsche an der
   Baseline, die dieser Agent im Slice
   PERSONAL-ORGANISATION-ZEITKONTO-20261006 gesenkt hat — die Ratsche arbeitet
   also wie vorgesehen. Nicht angefasst.

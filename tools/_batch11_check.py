"""Check batch 11 page -> screen_id coverage in screen_definitions_listen.py."""
import re
from pathlib import Path

# page rel path -> screen_id (convention from migration)
BATCH11 = {
    "admin/audit-log.tsx": "admin/audit-log-liste",
    "agrar/bodenproben/liste.tsx": "agrar/bodenproben-liste",
    "agrar/ernte-annahme-energiemais.tsx": "agrar/ernte-annahme-energiemais-liste",
    "agrar/feldbuch/ackerschlagkartei.tsx": "agrar/feldbuch-ackerschlagkartei-liste",
    "agrar/feldbuch/flurstueck-kataster.tsx": "agrar/feldbuch-flurstueck-kataster-liste",
    "agrar/kultur-stamm.tsx": "agrar/kultur-stamm-liste",
    "agrar/maschinen-auslastung.tsx": "agrar/maschinen-auslastung-liste",
    "agrar/nachhaltigkeit-eudr.tsx": "agrar/nachhaltigkeit-eudr-liste",
    "agrar/pflanzenschutz-applikationen.tsx": "agrar/pflanzenschutz-applikationen-liste",
    "agrar/psm/abgabedokumentation.tsx": "agrar/psm-abgabedokumentation-liste",
    "agrar/psm/beratung.tsx": "agrar/psm-beratung-liste",
    "agrar/psm/sachkunde-register.tsx": "agrar/psm-sachkunde-register-liste",
    "agrar/psm/wasserschutz.tsx": "agrar/psm-wasserschutz-liste",
    "agrar/saatgut/bestellungen.tsx": "agrar/saatgut-bestellungen-liste",
    "agrar/saatgut/sortenregister.tsx": "agrar/saatgut-sortenregister-liste",
    "agrar/schlaege/index.tsx": "agrar/schlaege-liste",
    "agrar/schlaege/karte.tsx": "agrar/schlaege-karte-liste",
    "agrar/schlaege/kulturhistorie.tsx": "agrar/schlaege-kulturhistorie-liste",
    "agrar/vertrag-kontingente.tsx": "agrar/vertrag-kontingente-liste",
    "charge/wareneingang.tsx": "charge/wareneingang-liste",
    "compliance/bvl-umsatzmeldung.tsx": "compliance/bvl-umsatzmeldung-liste",
    "compliance/CrossCompliancePage.tsx": "compliance/cross-compliance-liste",
    "compliance/eudr-compliance.tsx": "compliance/eudr-compliance-liste",
    "compliance/export-pruefung.tsx": "compliance/export-pruefung-liste",
    "compliance/gefahrstoff-doku.tsx": "compliance/gefahrstoff-doku-liste",
    "compliance/qs-checkliste.tsx": "compliance/qs-checkliste-liste",
    "compliance/sachkunde-register.tsx": "compliance/sachkunde-liste",
    "compliance/vvvo-register.tsx": "compliance/vvvo-liste",
    "compliance/zulassungen-register.tsx": "compliance/zulassungen-liste",
    "controlling/plan-ist.tsx": "controlling/plan-ist-liste",
    "crm/contact-detail.tsx": "crm/contact-detail-liste",
    "crm/kontakt-management.tsx": "crm/kontakt-management-liste",
    "crm/kunden-liste.tsx": "crm/kunden-liste",
    "crm/lead-detail.tsx": "crm/leads-liste",
    "crm/lieferanten-liste.tsx": "crm/lieferanten-liste",
    "dokumente/ablage.tsx": "dokumente/ablage-liste",
    "einkauf/anfragen-create.tsx": "einkauf/anfragen-create-liste",
    "einkauf/angebote-vergleich.tsx": "einkauf/angebote-vergleich-liste",
    "einkauf/bestellvorschlaege.tsx": "einkauf/bestellvorschlaege-liste",
    "einkauf/dienstleistungen-haltung.tsx": "einkauf/dienstleistungen-haltung-liste",
    "einkauf/EinkaufVorgangPage.tsx": "einkauf/einkauf-vorgang-liste",
    "einkauf/kontrakte-service.tsx": "einkauf/kontrakte-service-liste",
    "einkauf/rechnung-abgleich.tsx": "einkauf/rechnung-abgleich-liste",
    "einkauf/rechnungseingaenge-liste.tsx": "einkauf/rechnungseingaenge-liste",
    "einkauf/retouren.tsx": "einkauf/retouren-liste",
    "etiketten/druck.tsx": "etiketten/druck-liste",
    "export/intrastat-meldung.tsx": "export/intrastat-meldung-liste",
    "export/umsatzsteuer-voranmeldung.tsx": "export/umsatzsteuer-voranmeldung-liste",
    "fibu/anlagen.tsx": "fibu/anlagen-liste",
    "fibu/buchungsjournal.tsx": "fibu/buchungsjournal-liste",
    "fibu/debitoren.tsx": "fibu/debitoren-liste",
    "fibu/hauptbuch.tsx": "fibu/hauptbuch-liste",
    "fibu/kassenbuch.tsx": "fibu/kassenbuch-liste",
    "fibu/kostenstellenrechnung.tsx": "fibu/kostenstellen-liste",
    "fibu/kreditoren.tsx": "fibu/kreditoren-liste",
    "fibu/offene-posten.tsx": "fibu/offene-posten-liste",
    "fibu/schnittstelle-fibu.tsx": "fibu/schnittstelle-fibu-liste",
    "fibu/verbindlichkeiten.tsx": "fibu/verbindlichkeiten-liste",
    "fibu/zahlungslaeufe.tsx": "fibu/zahlungslaeufe-liste",
}

listen = Path("app/core/screen_definitions_listen.py").read_text(encoding="utf-8")
ids = set(re.findall(r'screen_id="([^"]+)"', listen))
pages_root = Path("packages/frontend-web/src/pages")

missing_sd = []
for page, sid in BATCH11.items():
    if sid not in ids:
        missing_sd.append((page, sid))

print("Missing screen definitions:", len(missing_sd))
for p, s in missing_sd:
    print(f"  {s} ({p})")

native = hand = missing_file = 0
for page, sid in BATCH11.items():
    fp = pages_root / page
    if not fp.exists():
        missing_file += 1
        continue
    t = fp.read_text(encoding="utf-8")
    if "NativeListPage" in t and f'screenId="{sid}"' in t:
        native += 1
    else:
        hand += 1
        print(f"HAND: {page} expect {sid}")

print(f"files: native={native} hand={hand} missing={missing_file}")

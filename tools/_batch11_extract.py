import re
from pathlib import Path

pages = [
    "admin/audit-log.tsx",
    "agrar/bodenproben/liste.tsx",
    "agrar/ernte-annahme-energiemais.tsx",
    "agrar/feldbuch/ackerschlagkartei.tsx",
    "agrar/feldbuch/flurstueck-kataster.tsx",
    "agrar/kultur-stamm.tsx",
    "agrar/maschinen-auslastung.tsx",
    "agrar/nachhaltigkeit-eudr.tsx",
    "agrar/pflanzenschutz-applikationen.tsx",
    "agrar/psm/abgabedokumentation.tsx",
    "agrar/psm/beratung.tsx",
    "agrar/psm/sachkunde-register.tsx",
    "agrar/psm/wasserschutz.tsx",
    "agrar/saatgut/bestellungen.tsx",
    "agrar/saatgut/sortenregister.tsx",
    "agrar/schlaege/index.tsx",
    "agrar/schlaege/karte.tsx",
    "agrar/schlaege/kulturhistorie.tsx",
    "agrar/vertrag-kontingente.tsx",
    "charge/wareneingang.tsx",
    "compliance/bvl-umsatzmeldung.tsx",
    "compliance/CrossCompliancePage.tsx",
    "compliance/eudr-compliance.tsx",
    "compliance/export-pruefung.tsx",
    "compliance/gefahrstoff-doku.tsx",
    "compliance/qs-checkliste.tsx",
    "compliance/sachkunde-register.tsx",
    "compliance/vvvo-register.tsx",
    "compliance/zulassungen-register.tsx",
    "controlling/plan-ist.tsx",
    "crm/contact-detail.tsx",
    "crm/kontakt-management.tsx",
    "crm/kunden-liste.tsx",
    "crm/lead-detail.tsx",
    "crm/lieferanten-liste.tsx",
    "dokumente/ablage.tsx",
    "einkauf/anfragen-create.tsx",
    "einkauf/angebote-vergleich.tsx",
    "einkauf/bestellvorschlaege.tsx",
    "einkauf/dienstleistungen-haltung.tsx",
    "einkauf/EinkaufVorgangPage.tsx",
    "einkauf/kontrakte-service.tsx",
    "einkauf/rechnung-abgleich.tsx",
    "einkauf/rechnungseingaenge-liste.tsx",
    "einkauf/retouren.tsx",
    "etiketten/druck.tsx",
    "export/intrastat-meldung.tsx",
    "export/umsatzsteuer-voranmeldung.tsx",
    "fibu/anlagen.tsx",
    "fibu/buchungsjournal.tsx",
    "fibu/debitoren.tsx",
    "fibu/hauptbuch.tsx",
    "fibu/kassenbuch.tsx",
    "fibu/kostenstellenrechnung.tsx",
    "fibu/kreditoren.tsx",
    "fibu/offene-posten.tsx",
    "fibu/schnittstelle-fibu.tsx",
    "fibu/verbindlichkeiten.tsx",
    "fibu/zahlungslaeufe.tsx",
]
root = Path("packages/frontend-web/src/pages")
api_re = re.compile(r"""['"](/api/v1[^'"]+)['"]""")
for p in pages:
    fp = root / p
    if not fp.exists():
        print("MISSING", p)
        continue
    t = fp.read_text(encoding="utf-8")
    native = "NativeListPage" in t
    apis = sorted(set(api_re.findall(t)))
    hooks = sorted(set(re.findall(r"use[A-Z][a-zA-Z0-9]+", t)))
    keys = re.findall(r"""key:\s*['"](\w+)['"]""", t)[:10]
    print(f"--- {p} native={native}")
    if apis:
        print("  api:", apis)
    elif hooks:
        print("  hooks:", hooks[:12])
    if keys:
        print("  cols:", keys)

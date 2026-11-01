import os
import re
from pathlib import Path

base = Path("packages/frontend-web/src/pages")
files = """admin/audit-log.tsx
agrar/bodenproben/liste.tsx
agrar/ernte-annahme-energiemais.tsx
agrar/feldbuch/ackerschlagkartei.tsx
agrar/feldbuch/flurstueck-kataster.tsx
agrar/kultur-stamm.tsx
agrar/maschinen-auslastung.tsx
agrar/nachhaltigkeit-eudr.tsx
agrar/pflanzenschutz-applikationen.tsx
agrar/psm/abgabedokumentation.tsx
agrar/psm/beratung.tsx
agrar/psm/sachkunde-register.tsx
agrar/psm/wasserschutz.tsx
agrar/saatgut/bestellungen.tsx
agrar/saatgut/sortenregister.tsx
agrar/schlaege/index.tsx
agrar/schlaege/karte.tsx
agrar/schlaege/kulturhistorie.tsx
agrar/vertrag-kontingente.tsx
charge/wareneingang.tsx
compliance/bvl-umsatzmeldung.tsx
compliance/CrossCompliancePage.tsx
compliance/eudr-compliance.tsx
compliance/export-pruefung.tsx
compliance/gefahrstoff-doku.tsx
compliance/qs-checkliste.tsx
compliance/sachkunde-register.tsx
compliance/vvvo-register.tsx
compliance/zulassungen-register.tsx
controlling/plan-ist.tsx
crm/contact-detail.tsx
crm/kontakt-management.tsx
crm/kunden-liste.tsx
crm/lead-detail.tsx
crm/lieferanten-liste.tsx
dokumente/ablage.tsx
einkauf/anfragen-create.tsx
einkauf/angebote-vergleich.tsx
einkauf/bestellvorschlaege.tsx
einkauf/dienstleistungen-haltung.tsx
einkauf/EinkaufVorgangPage.tsx
einkauf/kontrakte-service.tsx
einkauf/rechnung-abgleich.tsx
einkauf/rechnungseingaenge-liste.tsx
einkauf/retouren.tsx
etiketten/druck.tsx
export/intrastat-meldung.tsx
export/umsatzsteuer-voranmeldung.tsx
fibu/anlagen.tsx
fibu/buchungsjournal.tsx
fibu/debitoren.tsx
fibu/hauptbuch.tsx
fibu/kassenbuch.tsx
fibu/kostenstellenrechnung.tsx
fibu/kreditoren.tsx
fibu/offene-posten.tsx
fibu/schnittstelle-fibu.tsx
fibu/verbindlichkeiten.tsx
fibu/zahlungslaeufe.tsx""".strip().split("\n")

ALLOW = {"crm/kunden-liste", "crm/lieferanten-liste", "einkauf/rechnungseingaenge-liste"}
missing = []
bad = []
ok = []
for f in files:
    p = base / f.replace("/", os.sep)
    if not p.is_file():
        missing.append(f)
        continue
    t = p.read_text(encoding="utf-8")
    if "NativeListPage" not in t:
        bad.append((f, "no NativeListPage"))
        continue
    m = re.search(r'screenId="([^"]+)"', t)
    if not m:
        bad.append((f, "no screenId"))
        continue
    sid = m.group(1)
    if not sid.endswith("-liste") and sid not in ALLOW:
        bad.append((f, f"screenId={sid}"))
    else:
        ok.append((f, sid))

print("missing", len(missing))
for x in missing:
    print("  ", x)
print("bad", len(bad))
for x in bad:
    print("  ", x)
print("ok", len(ok), "/", len(files))

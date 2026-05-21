"""
Extrahiert A.eins/amic.de Hilfedokumentation nach Fachdomänen
und erzeugt strukturierte Markdown-Referenzdokumente in docs/valeo-reference/
"""
import json, os, re
from collections import defaultdict

SRC = r'C:\Users\Jochen\VALEO-NeuroERP-3.0\data_results Landhandel ERP.json'
OUT_DIR = r'C:\Users\Jochen\VALEO-NeuroERP-3.0\docs\valeo-reference'
os.makedirs(OUT_DIR, exist_ok=True)

with open(SRC, encoding='utf-8', errors='replace') as f:
    data = json.load(f)

def fix_text(s: str) -> str:
    """Bereinigt Encoding-Artefakte aus Windows-1252-Konvertierung."""
    return (s.replace('\r\n', '\n').replace('\r', '\n')
             .replace('�', '?').strip())

# Domänen-Zuordnung: (Dateiname, Label, Schlüsselwörter)
DOMAINS = [
    ('01_kontrakt_rohware',       'Kontrakt & Rohware',
     ['kontrakt', 'rohware', 'erntemeldung', 'ernte', 'abrechnun', 'deckungsbeitrag',
      'preisfix', 'sammelabrechnung', 'selbstabrechnung', 'kontraktumsatz']),
    ('02_warenwirtschaft_auftrag', 'Warenwirtschaft & Auftragsabwicklung',
     ['auftrag', 'angebot', 'lieferschein', 'strecke', 'bestellung', 'wareneingang',
      'verkauf', 'einkauf', 'rfq', 'ab-preis', 'auftragsposition', 'ab-rechnung',
      'kommissionsauftrag']),
    ('03_fibu_buchhaltung',        'Finanzbuchhaltung & Rechnungswesen',
     ['fibu', 'buchung', 'buchungssatz', 'journal', 'bilanz', 'guv', 'bwa', 'kontenplan',
      'sachkonto', 'mahnung', 'zahlungslauf', 'zahlungseingang', 'op-', 'offene posten',
      'kreditor', 'debitor', 'nebenbuch', 'verbindlichkeit', 'forderung', 'skonto',
      'abschluss', 'periodenabschluss', 'zahlungsvorschlag']),
    ('04_erechnung_edi',           'eRechnung, EDI & Schnittstellen',
     ['erechnung', 'e-rechnung', 'edi', 'datanorm', 'edifact', 'xml', 'schnittstelle',
      'eclearing', 'clearing', 'zugang', 'xrechnung', 'ubl', 'peppol', 'elnvoice']),
    ('05_intrastat_meldewesen',    'Intrastat & Meldewesen',
     ['intrastat', 'innergemeinschaftlich', 'eu-staat', 'warenbewegung', 'meldung',
      'meldewesen', 'statistik', 'außenhandel', 'ausfuhr', 'einfuhr', 'atlas', 'zoll']),
    ('06_crm_kunden',              'CRM, Kunden- & Lieferantenstamm',
     ['kunde', 'lieferant', 'gesch?ftspartner', 'adresse', 'kontakt', 'crm',
      'kundenstamm', 'lieferantenstamm', 'betrieb', 'ansprechpartner', 'segment']),
    ('07_preise_konditionen',      'Preise, Konditionen & Kalkulation',
     ['preis', 'kondition', 'rabatt', 'staffel', 'kalkulation', 'marge',
      'preisgruppe', 'preisfindung', 'zuschlag', 'abzug', 'sonderpreis',
      'matif', 'terminbörse', 'hedging']),
    ('08_lager_bestand',           'Lager, Bestände & Inventur',
     ['lager', 'lagerplatz', 'bestand', 'inventur', 'einlagerung', 'auslagerung',
      'umlagerung', 'lagerbewegung', 'silo', 'tank', 'schüttgut', 'charge',
      'chargenrückverfolgung', 'mindesthaltbarkeit', 'mhd']),
    ('09_waage_annahme',           'Waage, Annahme & Hofliste',
     ['waage', 'wieg', 'annahme', 'hofliste', 'lkw', 'fahrzeug', 'kennzeichen',
      'brutto', 'tara', 'netto', 'fuhrwerk', 'qualit?tscheck', 'probenahme',
      'wiegeschein', 'rohwareannahme']),
    ('10_logistik_transport',      'Logistik, Transport & Versand',
     ['logistik', 'transport', 'spedition', 'versand', 'fracht', 'disposition',
      'avis', 'lieferschein', 'verladung', 'lkw-beladung', 'route', 'tour']),
    ('11_produktion_mischfutter',  'Produktion & Mischfutterherstellung',
     ['produktion', 'mischfutter', 'rezeptur', 'mischung', 'komponente',
      'rohstoff', 'wirkstoff', 'futtermittel', 'ration', 'mischanlage',
      'mischprotokoll', 'produktionsauftrag']),
    ('12_psm_pflanzenschutz',      'Pflanzenschutz & PSM-Dokumentation',
     ['pflanzenschutz', 'psm', 'sachkunde', 'wirkstoff', 'mittel', 'zulassung',
      'anwendungshinweis', 'karenzzeit', 'abstandsauflage', 'applikation',
      'behandlungsprotokoll', 'abdriftminderung']),
    ('13_agrar_feldbuch',          'Agrar, Feldbuch & Pflanzenbau',
     ['schlag', 'feldbuch', 'düng', 'saatgut', 'anbau', 'flur',
      'aussaat', 'kulturpflanze', 'sorte', 'd?ngung', 'n-bilanz',
      'flik', 'gis', 'geodaten', 'schlagkarte']),
    ('14_nawaro_energie',          'NaWaRo, Bioenergie & Nachhaltigkeit',
     ['nawaro', 'nachwachsend', 'biomasse', 'biogas', 'biokraft',
      'nachhaltigkeitsnachweis', 'enni', 'iscc', 'red', 'co2', 'treibhausgas']),
    ('15_compliance_qualitaet',    'Compliance, Qualität & Zertifizierung',
     ['compliance', 'qualit', 'pcn', 'ufi', 'lksg', 'qs ', 'cross-compliance',
      'vvvo', 'bvl', 'sachkundeausweis', 'zertifikat', 'audit', 'gdpr', 'dsgvo']),
    ('16_system_admin',            'System, Administration & Konfiguration',
     ['einricht', 'parameter', 'setup', 'konfigur', 'admin', 'benutzer',
      'berechtigung', 'recht ', 'lizenz', 'mandant', 'nummernkreis',
      'druckvorlage', 'formular', 'workflow', 'automatik']),
]

def score_item(item, keywords):
    text = (item['title'] + ' ' + item['content'][:300]).lower()
    return sum(1 for kw in keywords if kw.lower() in text)

# Assign each item to best-matching domain
buckets = defaultdict(list)
for item in data:
    best_domain = None
    best_score = 0
    for fname, label, kws in DOMAINS:
        s = score_item(item, kws)
        if s > best_score:
            best_score = s
            best_domain = fname
    if best_domain and best_score > 0:
        buckets[best_domain].append(item)

# Write domain files
total_written = 0
for fname, label, _ in DOMAINS:
    items = buckets.get(fname, [])
    if not items:
        continue
    out_path = os.path.join(OUT_DIR, f'{fname}.md')
    lines = [f'# {label} — A.eins Referenzwissen\n',
             f'> Quelle: amic.de A.eins Hilfe ({len(items)} Seiten)\n',
             f'> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.\n\n']
    for item in items:
        title = fix_text(item.get('title', ''))
        content = fix_text(item.get('content', ''))
        if not title and not content:
            continue
        lines.append(f'## {title}\n\n')
        # Truncate very long entries to max 2000 chars for readability
        if len(content) > 2000:
            content = content[:2000] + '\n[...]\n'
        lines.append(content + '\n\n---\n\n')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(''.join(lines))
    size_kb = os.path.getsize(out_path) // 1024
    print(f'  {fname}.md  ({len(items)} Einträge, {size_kb} KB)')
    total_written += len(items)

# Write index
unmatched = len(data) - total_written
index_lines = ['# A.eins Referenzwissen — Index\n\n',
               f'Quelle: amic.de/hilfe — {len(data)} Hilfeseiten zu A.eins Landhandel ERP\n\n',
               'Dieses Wissen dient als fachliche Referenz für VALEO NeuroERP.\n\n',
               '## Domänen\n\n']
for fname, label, _ in DOMAINS:
    items = buckets.get(fname, [])
    if items:
        index_lines.append(f'- [{label}]({fname}.md) — {len(items)} Seiten\n')
index_lines.append(f'\n_{unmatched} Seiten ohne Domänenzuordnung_\n')
with open(os.path.join(OUT_DIR, 'README.md'), 'w', encoding='utf-8') as f:
    f.write(''.join(index_lines))

print(f'\nFertig. {total_written}/{len(data)} Seiten in {len(buckets)} Domänen verarbeitet.')
print(f'Output: {OUT_DIR}')

# Masken-Studio-Inventar (2026-10-22)

Erzeugt mit `python scripts/mask_studio_inventory.py --markdown <datei>`. Ziel: nur Studio-generierte
Masken; jede Maskenfunktion auch per CLI und MCP, in CI geprueft (Nutzerentscheid 2026-10-19).

## Seiten

| Stufe | Routen | Anteil an Masken |
|---|---:|---:|
| studio_versioniert | 6 | 0.9 % |
| screen_definition | 596 | 88.8 % |
| builder_altmuster | 34 | 5.1 % |
| handgebaut | 35 | 5.2 % |
| weiterleitung | 0 |  |

Gesamt 671 Routen, davon 671 Masken.

## Aktionen

| Befund | Anzahl |
|---|---:|
| Aktionen gesamt (ohne Doppel je Maske) | 1168 |
| davon serverwirksam | 245 |
| … mit REST-Kommandoweg | 245 |
| … mit eigenem MCP-Werkzeug | 45 |
| … per generischem MCP-Werkzeug (`mask.action.execute`) | 71 |
| … MCP bewusst gesperrt | 129 |
| … MCP offen (`open_high` u. a.) | 0 |
| … MCP unklassifiziert | 0 |
| … mit CLI-Zugang | 245 |
| nicht deklariert (kein Kommando, Endpunkt, Navigation) | 330 |
| nicht verfuegbar (`stubReason`, die Maske nennt den Grund) | 25 |

## Versionierte Familien

- `beleg`: 9 Varianten — goods_receipt 1.2.0, purchase_credit_memo 1.2.0, purchase_invoice 1.2.0, purchase_order 1.2.0, sales_credit_memo 1.2.0, sales_delivery 1.2.0, sales_invoice 1.2.0, sales_offer 1.2.0, sales_order 1.2.0
- `native_studio`: Release 1.0.0, 847 Screens (5 statisch geprueft; Browser-/Freigabenachweis nicht gemessen)

## Studio-Katalog

Studio-Masken tragen nur Katalogaktionen. Was hier bedienbar ist, ist es in jeder Studio-Maske.

| Katalogaktion | Route | CLI | MCP |
|---|---|---|---|
| `create_activity` | ja | ja | mapped |
| `mahnen` | ja | ja | blocked_human_only, mapped_read |
| `freigeben` | ja | ja | blocked_human_only |
| `stornieren` | ja | ja | blocked_human_only |

Datenquellen: 15, ohne Route: keine.

## Beleg-Einstiege ausserhalb der Belegfamilie

Stichwortsuche im Routenpfad (Angebot, Auftrag, Bestellung, Lieferschein, Wareneingang, Rechnung,
Gutschrift). Jeder Treffer ist Kandidat fuer eine Variante der Familie `beleg` oder ihre Liste — die
fachliche Zuordnung fuehrt `docs/design/beleg-studio-variantenmatrix.md`.

| Route | Stufe |
|---|---|
| `agrar/saatgut/bestellung` | screen_definition |
| `agrar/sammelabrechnung` | builder_altmuster |
| `annahme/abrechnung` | handgebaut |
| `charge/wareneingang` | screen_definition |
| `einkauf/angebot` | screen_definition |
| `einkauf/angebot/:id` | screen_definition |
| `einkauf/angebote` | screen_definition |
| `einkauf/auftragsbestaetigung` | screen_definition |
| `einkauf/auftragsbestaetigung/:id` | screen_definition |
| `einkauf/auftragsbestaetigung/neu` | screen_definition |
| `einkauf/auftragsbestaetigungen` | screen_definition |
| `einkauf/bestellung/:id` | screen_definition |
| `einkauf/bestellungen` | screen_definition |
| `einkauf/bestellungen/:id` | screen_definition |
| `einkauf/bestellungen/neu` | builder_altmuster |
| `einkauf/gutschriften-belastungen` | screen_definition |
| `einkauf/lieferschein-erfassung` | handgebaut |
| `einkauf/lieferschein-frachtauftrag` | screen_definition |
| `einkauf/rechnung-abgleich` | screen_definition |
| `einkauf/rechnung-eingang-erfassung` | screen_definition |
| `einkauf/rechnungseingaenge` | screen_definition |
| `einkauf/rechnungseingaenge-liste` | screen_definition |
| `einkauf/rechnungseingang` | screen_definition |
| `einkauf/wareneingang` | screen_definition |
| `einkauf/wareneingangsabgleich` | screen_definition |
| `fuhrpark/fuhrpark-rechnungen` | screen_definition |
| `futtermittel/bestellungen` | screen_definition |
| `futtermittel/futtermittel-bestellung` | screen_definition |
| `futtermittel/futtermittel-wareneingang` | screen_definition |
| `futtermittel/wareneingang` | screen_definition |
| `portal/bestellungen` | screen_definition |
| `portal/rechnungen` | screen_definition |
| `qualitaet/labor-auftrag` | screen_definition |
| `sales/angebot-erstellen` | screen_definition |
| `sales/angebot/:id` | screen_definition |
| `sales/angebot/neu` | screen_definition |
| `sales/angebote` | screen_definition |
| `sales/angebote-liste` | handgebaut |
| `sales/auftrag-lieferschein-abgleich` | screen_definition |
| `sales/auftragskette` | screen_definition |
| `sales/rechnungen` | screen_definition |
| `verkauf/lieferschein-erfassung` | screen_definition |
| `verkauf/rechnung/:id` | screen_definition |
| `verkauf/rechnungen` | screen_definition |
| `verkauf/rechnungen/neu` | screen_definition |

Registrierte ScreenDefinitions ohne eigene Route: 461.

## Bereiche (Rollout-Reihenfolge nach Anzahl handgebauter Masken)

| Bereich | studio_versioniert | screen_definition | builder_altmuster | handgebaut | weiterleitung |
|---|---:|---:|---:|---:|---:|
| workflow | 0 | 4 | 0 | 10 | 0 |
| finance | 0 | 48 | 1 | 4 | 0 |
| futtermittel | 0 | 28 | 0 | 3 | 0 |
| sales | 0 | 27 | 0 | 3 | 0 |
| waage | 0 | 2 | 0 | 3 | 0 |
| annahme | 0 | 3 | 3 | 2 | 0 |
| auth | 0 | 0 | 0 | 2 | 0 |
| crm | 0 | 53 | 0 | 2 | 0 |
| admin | 0 | 14 | 16 | 1 | 0 |
| einkauf | 0 | 48 | 1 | 1 | 0 |
| fibu | 0 | 42 | 0 | 1 | 0 |
| lager | 0 | 21 | 0 | 1 | 0 |
| mahnwesen | 0 | 0 | 0 | 1 | 0 |
| qualitaet | 0 | 6 | 0 | 1 | 0 |
| agrar | 0 | 47 | 12 | 0 | 0 |
| agribusiness | 0 | 4 | 0 | 0 | 0 |
| alerts | 0 | 1 | 0 | 0 | 0 |
| artikel | 0 | 3 | 0 | 0 | 0 |
| banken | 0 | 1 | 0 | 0 | 0 |
| belege | 1 | 0 | 0 | 0 | 0 |
| benachrichtigungen | 0 | 1 | 0 | 0 | 0 |
| charge | 0 | 5 | 0 | 0 | 0 |
| compliance | 0 | 16 | 0 | 0 | 0 |
| contracts | 0 | 1 | 0 | 0 | 0 |
| controlling | 0 | 7 | 0 | 0 | 0 |
| copilot | 0 | 1 | 0 | 0 | 0 |
| dashboard | 0 | 3 | 0 | 0 | 0 |
| dashboards | 0 | 1 | 0 | 0 | 0 |
| dev | 0 | 1 | 0 | 0 | 0 |
| disposition | 0 | 4 | 0 | 0 | 0 |
| docflow | 0 | 6 | 0 | 0 | 0 |
| document | 0 | 1 | 0 | 0 | 0 |
| dokumente | 0 | 1 | 0 | 0 | 0 |
| einstellungen | 0 | 1 | 0 | 0 | 0 |
| energie | 0 | 2 | 0 | 0 | 0 |
| errors | 0 | 1 | 0 | 0 | 0 |
| etiketten | 0 | 1 | 0 | 0 | 0 |
| export | 0 | 1 | 0 | 0 | 0 |
| finanzplanung | 0 | 1 | 0 | 0 | 0 |
| foerderung | 0 | 2 | 0 | 0 | 0 |
| fuhrpark | 1 | 7 | 0 | 0 | 0 |
| futter | 0 | 4 | 0 | 0 | 0 |
| genossenschaft | 0 | 2 | 0 | 0 | 0 |
| hilfe | 0 | 1 | 0 | 0 | 0 |
| inbox | 0 | 1 | 0 | 0 | 0 |
| inventory | 0 | 2 | 0 | 0 | 0 |
| inventory-dashboard | 0 | 1 | 0 | 0 | 0 |
| inventory-reports | 0 | 1 | 0 | 0 | 0 |
| kasse | 0 | 2 | 0 | 0 | 0 |
| kontrakte | 0 | 10 | 0 | 0 | 0 |
| labor | 0 | 1 | 0 | 0 | 0 |
| logistik | 0 | 3 | 0 | 0 | 0 |
| management | 0 | 1 | 0 | 0 | 0 |
| marketing | 0 | 1 | 0 | 0 | 0 |
| mask-rollout | 0 | 1 | 0 | 0 | 0 |
| mobile | 0 | 1 | 0 | 0 | 0 |
| monitoring | 0 | 1 | 1 | 0 | 0 |
| nachhaltigkeit | 0 | 4 | 0 | 0 | 0 |
| nawaro | 0 | 4 | 0 | 0 | 0 |
| personal | 0 | 17 | 0 | 0 | 0 |
| planung | 0 | 1 | 0 | 0 | 0 |
| policies | 0 | 1 | 0 | 0 | 0 |
| portal | 1 | 16 | 0 | 0 | 0 |
| pos | 0 | 11 | 0 | 0 | 0 |
| preise | 0 | 4 | 0 | 0 | 0 |
| pricing | 0 | 1 | 0 | 0 | 0 |
| produktion | 0 | 5 | 0 | 0 | 0 |
| projekte | 0 | 1 | 0 | 0 | 0 |
| prospecting | 0 | 1 | 0 | 0 | 0 |
| public | 0 | 1 | 0 | 0 | 0 |
| reports | 0 | 4 | 0 | 0 | 0 |
| rezepte | 0 | 1 | 0 | 0 | 0 |
| schaeden | 0 | 3 | 0 | 0 | 0 |
| schichtplan | 0 | 1 | 0 | 0 | 0 |
| service | 0 | 5 | 0 | 0 | 0 |
| setup | 0 | 1 | 0 | 0 | 0 |
| silo | 0 | 2 | 0 | 0 | 0 |
| stammdaten | 0 | 1 | 0 | 0 | 0 |
| start | 0 | 1 | 0 | 0 | 0 |
| statistik | 0 | 1 | 0 | 0 | 0 |
| stock-management | 0 | 1 | 0 | 0 | 0 |
| strecke | 3 | 9 | 0 | 0 | 0 |
| studio | 0 | 1 | 0 | 0 | 0 |
| subventionen | 0 | 1 | 0 | 0 | 0 |
| system | 0 | 1 | 0 | 0 | 0 |
| tankstelle | 0 | 2 | 0 | 0 | 0 |
| termine | 0 | 1 | 0 | 0 | 0 |
| transporte | 0 | 2 | 0 | 0 | 0 |
| verkauf | 0 | 16 | 0 | 0 | 0 |
| verladung | 0 | 2 | 0 | 0 | 0 |
| versand | 0 | 4 | 0 | 0 | 0 |
| versicherungen | 0 | 1 | 0 | 0 | 0 |
| vertrag | 0 | 3 | 0 | 0 | 0 |
| vertrieb | 0 | 1 | 0 | 0 | 0 |
| wartung | 0 | 2 | 0 | 0 | 0 |
| weighing | 0 | 1 | 0 | 0 | 0 |
| wissen | 0 | 1 | 0 | 0 | 0 |
| workflows | 0 | 4 | 0 | 0 | 0 |
| workspace | 0 | 5 | 0 | 0 | 0 |
| zertifikate | 0 | 2 | 0 | 0 | 0 |

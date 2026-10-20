# Masken-Studio-Inventar (2026-10-20)

Erzeugt mit `python scripts/mask_studio_inventory.py --markdown <datei>`. Ziel: nur Studio-generierte
Masken; jede Maskenfunktion auch per CLI und MCP, in CI geprueft (Nutzerentscheid 2026-10-19).

## Seiten

| Stufe | Routen | Anteil an Masken |
|---|---:|---:|
| studio_versioniert | 1 | 0.2 % |
| screen_definition | 130 | 19.8 % |
| builder_altmuster | 80 | 12.2 % |
| handgebaut | 447 | 67.9 % |
| weiterleitung | 3 |  |

Gesamt 661 Routen, davon 658 Masken.

## Aktionen

| Befund | Anzahl |
|---|---:|
| Aktionen gesamt (ohne Doppel je Maske) | 421 |
| davon serverwirksam | 272 |
| … mit REST-Kommandoweg | 272 |
| … mit eigenem MCP-Werkzeug | 45 |
| … per generischem MCP-Werkzeug (`mask.action.execute`) | 67 |
| … MCP bewusst gesperrt | 160 |
| … MCP offen (`open_high` u. a.) | 0 |
| … MCP unklassifiziert | 0 |
| … mit CLI-Zugang | 272 |
| nicht deklariert (kein Kommando, Endpunkt, Navigation) | 0 |
| nicht verfuegbar (`stubReason`, die Maske nennt den Grund) | 0 |

## Versionierte Familien

- `beleg`: 9 Varianten — goods_receipt 1.2.0, purchase_credit_memo 1.2.0, purchase_invoice 1.2.0, purchase_order 1.2.0, sales_credit_memo 1.2.0, sales_delivery 1.2.0, sales_invoice 1.2.0, sales_offer 1.2.0, sales_order 1.2.0

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
| `agrar/saatgut/bestellung` | handgebaut |
| `agrar/sammelabrechnung` | handgebaut |
| `annahme/abrechnung` | handgebaut |
| `charge/wareneingang` | builder_altmuster |
| `einkauf/angebot` | builder_altmuster |
| `einkauf/angebot/:id` | screen_definition |
| `einkauf/angebote` | screen_definition |
| `einkauf/auftragsbestaetigung` | builder_altmuster |
| `einkauf/auftragsbestaetigung/:id` | screen_definition |
| `einkauf/auftragsbestaetigungen` | screen_definition |
| `einkauf/bestellung/:id` | screen_definition |
| `einkauf/bestellungen` | screen_definition |
| `einkauf/bestellungen/:id` | builder_altmuster |
| `einkauf/bestellungen/neu` | builder_altmuster |
| `einkauf/gutschriften-belastungen` | handgebaut |
| `einkauf/lieferschein-erfassung` | handgebaut |
| `einkauf/lieferschein-frachtauftrag` | handgebaut |
| `einkauf/rechnung-abgleich` | handgebaut |
| `einkauf/rechnung-eingang-erfassung` | handgebaut |
| `einkauf/rechnungseingaenge` | builder_altmuster |
| `einkauf/rechnungseingaenge-liste` | builder_altmuster |
| `einkauf/rechnungseingang` | builder_altmuster |
| `einkauf/wareneingang` | handgebaut |
| `einkauf/wareneingangsabgleich` | handgebaut |
| `fuhrpark/fuhrpark-rechnungen` | screen_definition |
| `futtermittel/bestellungen` | builder_altmuster |
| `futtermittel/futtermittel-bestellung` | builder_altmuster |
| `futtermittel/futtermittel-wareneingang` | builder_altmuster |
| `futtermittel/wareneingang` | builder_altmuster |
| `portal/bestellungen` | handgebaut |
| `portal/rechnungen` | handgebaut |
| `qualitaet/labor-auftrag` | builder_altmuster |
| `sales/angebot-erstellen` | handgebaut |
| `sales/angebot/:id` | handgebaut |
| `sales/angebot/neu` | handgebaut |
| `sales/angebote` | handgebaut |
| `sales/angebote-liste` | handgebaut |
| `sales/auftrag-lieferschein-abgleich` | handgebaut |
| `sales/auftragskette` | handgebaut |
| `sales/rechnungen` | screen_definition |
| `verkauf/lieferschein-erfassung` | handgebaut |
| `verkauf/rechnung/:id` | screen_definition |
| `verkauf/rechnungen` | screen_definition |
| `verkauf/rechnungen/neu` | handgebaut |

Registrierte ScreenDefinitions ohne eigene Route: 57.

## Bereiche (Rollout-Reihenfolge nach Anzahl handgebauter Masken)

| Bereich | studio_versioniert | screen_definition | builder_altmuster | handgebaut | weiterleitung |
|---|---:|---:|---:|---:|---:|
| agrar | 0 | 13 | 3 | 43 | 0 |
| fibu | 0 | 0 | 1 | 42 | 0 |
| finance | 0 | 9 | 16 | 28 | 0 |
| admin | 0 | 6 | 0 | 25 | 0 |
| einkauf | 0 | 16 | 9 | 23 | 0 |
| sales | 0 | 8 | 0 | 22 | 0 |
| crm | 0 | 14 | 20 | 21 | 0 |
| lager | 0 | 3 | 3 | 16 | 0 |
| portal | 0 | 1 | 0 | 16 | 0 |
| workflow | 0 | 0 | 0 | 14 | 0 |
| compliance | 0 | 1 | 2 | 13 | 0 |
| strecke | 0 | 0 | 0 | 12 | 0 |
| verkauf | 0 | 3 | 0 | 10 | 3 |
| futtermittel | 0 | 11 | 11 | 9 | 0 |
| kontrakte | 0 | 1 | 0 | 9 | 0 |
| pos | 0 | 0 | 2 | 9 | 0 |
| personal | 0 | 9 | 0 | 8 | 0 |
| controlling | 0 | 0 | 0 | 7 | 0 |
| docflow | 0 | 0 | 0 | 6 | 0 |
| annahme | 0 | 0 | 3 | 5 | 0 |
| qualitaet | 0 | 1 | 1 | 5 | 0 |
| service | 0 | 0 | 0 | 5 | 0 |
| waage | 0 | 0 | 0 | 5 | 0 |
| agribusiness | 0 | 0 | 0 | 4 | 0 |
| disposition | 0 | 0 | 0 | 4 | 0 |
| nachhaltigkeit | 0 | 0 | 0 | 4 | 0 |
| nawaro | 0 | 0 | 0 | 4 | 0 |
| preise | 0 | 0 | 0 | 4 | 0 |
| versand | 0 | 0 | 0 | 4 | 0 |
| workflows | 0 | 0 | 0 | 4 | 0 |
| charge | 0 | 1 | 1 | 3 | 0 |
| dashboard | 0 | 0 | 0 | 3 | 0 |
| produktion | 0 | 0 | 2 | 3 | 0 |
| vertrag | 0 | 0 | 0 | 3 | 0 |
| auth | 0 | 0 | 0 | 2 | 0 |
| fuhrpark | 0 | 6 | 0 | 2 | 0 |
| futter | 0 | 2 | 0 | 2 | 0 |
| genossenschaft | 0 | 0 | 0 | 2 | 0 |
| inventory | 0 | 0 | 0 | 2 | 0 |
| monitoring | 0 | 0 | 0 | 2 | 0 |
| reports | 0 | 0 | 0 | 2 | 0 |
| silo | 0 | 0 | 0 | 2 | 0 |
| tankstelle | 0 | 0 | 0 | 2 | 0 |
| zertifikate | 0 | 0 | 0 | 2 | 0 |
| alerts | 0 | 0 | 0 | 1 | 0 |
| banken | 0 | 0 | 0 | 1 | 0 |
| benachrichtigungen | 0 | 0 | 0 | 1 | 0 |
| contracts | 0 | 0 | 0 | 1 | 0 |
| copilot | 0 | 0 | 0 | 1 | 0 |
| dashboards | 0 | 0 | 0 | 1 | 0 |
| document | 0 | 0 | 0 | 1 | 0 |
| dokumente | 0 | 0 | 0 | 1 | 0 |
| einstellungen | 0 | 0 | 0 | 1 | 0 |
| errors | 0 | 0 | 0 | 1 | 0 |
| finanzplanung | 0 | 0 | 0 | 1 | 0 |
| hilfe | 0 | 0 | 0 | 1 | 0 |
| inbox | 0 | 0 | 0 | 1 | 0 |
| inventory-dashboard | 0 | 0 | 0 | 1 | 0 |
| inventory-reports | 0 | 0 | 0 | 1 | 0 |
| mahnwesen | 0 | 0 | 0 | 1 | 0 |
| management | 0 | 0 | 0 | 1 | 0 |
| marketing | 0 | 0 | 0 | 1 | 0 |
| mobile | 0 | 0 | 0 | 1 | 0 |
| policies | 0 | 0 | 0 | 1 | 0 |
| pricing | 0 | 0 | 0 | 1 | 0 |
| prospecting | 0 | 0 | 0 | 1 | 0 |
| public | 0 | 0 | 0 | 1 | 0 |
| rezepte | 0 | 0 | 0 | 1 | 0 |
| schichtplan | 0 | 0 | 0 | 1 | 0 |
| setup | 0 | 0 | 0 | 1 | 0 |
| stammdaten | 0 | 0 | 0 | 1 | 0 |
| start | 0 | 0 | 0 | 1 | 0 |
| stock-management | 0 | 0 | 0 | 1 | 0 |
| subventionen | 0 | 0 | 0 | 1 | 0 |
| system | 0 | 0 | 0 | 1 | 0 |
| vertrieb | 0 | 0 | 0 | 1 | 0 |
| weighing | 0 | 0 | 0 | 1 | 0 |
| wissen | 0 | 0 | 0 | 1 | 0 |
| artikel | 0 | 3 | 0 | 0 | 0 |
| belege | 1 | 0 | 0 | 0 | 0 |
| dev | 0 | 1 | 0 | 0 | 0 |
| etiketten | 0 | 0 | 1 | 0 | 0 |
| export | 0 | 0 | 1 | 0 | 0 |
| foerderung | 0 | 1 | 1 | 0 | 0 |
| labor | 0 | 1 | 0 | 0 | 0 |
| logistik | 0 | 3 | 0 | 0 | 0 |
| mask-rollout | 0 | 1 | 0 | 0 | 0 |
| planung | 0 | 1 | 0 | 0 | 0 |
| projekte | 0 | 1 | 0 | 0 | 0 |
| schaeden | 0 | 1 | 2 | 0 | 0 |
| studio | 0 | 1 | 0 | 0 | 0 |
| transporte | 0 | 2 | 0 | 0 | 0 |
| verladung | 0 | 1 | 1 | 0 | 0 |
| versicherungen | 0 | 1 | 0 | 0 | 0 |
| wartung | 0 | 2 | 0 | 0 | 0 |
| workspace | 0 | 5 | 0 | 0 | 0 |

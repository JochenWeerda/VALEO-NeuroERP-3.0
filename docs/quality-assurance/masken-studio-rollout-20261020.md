# Masken-Studio-Rollout (MASK-STUDIO-ROLLOUT-20261020)

Nutzerentscheid 19.10.2026: nur Studio-generierte Masken. „Studio-kompatibel“ heisst hier: Die Maske ist eine
ScreenDefinition und wird vom universellen Renderer gezeichnet; damit ist sie ueber den Studio-Import uebernehmbar.

## Befund zur Laufzeit-Aktivierung

- Veroeffentlichte Studio-Fassungen gelten nur fuer neue Masken-IDs. Native Masken werden bewusst nie aus Entwuerfen
  geliefert (`studio_draft_store.get_published_definition`).
- Eine Freigabe verlangt einen Simulationsnachweis. Den gibt es bisher nur fuer das Profil Getreideannahme
  (`grain.v1`).
- Das ist eine Sicherheitsentscheidung der Studio-Slices. Sie wird hier nicht geaendert; eine Aktivierung nativer
  Masken aus dem Studio waere eine eigene Nutzerentscheidung.

## Wellen

0. **Altlasten:** verwaiste Scheinseiten entfernen (nicht erreichbar, keine Daten).
1. **Familien:** Belege (eine Maske mit Varianten), Stammdaten (ObjectPage), Listen (ListReport), Cockpits und
   Worklists. Reihenfolge Landhandel-Kern -> Finanzen/FiBu -> CRM, Personal, Admin.
2. **Altmuster:** `MaskConfig`/`ObjectPage`/`ListReport`-Konfigurationen in ScreenDefinitions ueberfuehren.

Jede Welle senkt die Ratsche `config/mask_studio_ratchet.json`.

## Welle 0 (20.10.2026): sechs Scheinseiten, acht Routen entfernt

- `energie/verbrauch` (auch `energie`): fest eingetragene Strom- und Gaswerte samt „Einsparung“.
- `reports/lagerbestand`, `reports/umsatz`, `statistik/bewegungen`: statische Zahlen ohne Datenquelle.
- `termine/kalender`: statische Nachbildung einer Altsystem-Oberflaeche.
- `kasse/tagesabschluss` (auch `kasse/historie`): Abschluss-Assistent, der beim Fertigstellen nur weiterleitete. Der
  echte Kassenabschluss ist `pos/tagesabschluss-enhanced`.

Keine dieser Seiten war ueber Navigation, Links, Importe, Backend-Verweise oder externe Einstiege erreichbar.
Ratsche: handgebaut 483 -> 477, Altmuster 104 -> 102.

## Welle 1, Schritt 1 (20.10.2026): Einkauf Anfragen als Studio-Liste

- Neue generische Listenseite `NativeListPage` (`components/mask-builder/NativeListPage.tsx`): Spalten, Kopf- und
  Zeilenaktionen, Export und Zeilenroute kommen aus der ScreenDefinition; Kommando-Wege mit deklarierten Eingaben,
  Bestaetigung, Pflichtgrund und Doppelausfuehrungsschutz je Zeile und Aktion. Kein seitenspezifischer Code.
- ScreenDefinition `einkauf/anfragen` (`app/core/screen_definitions_listen.py`): Anlage (Navigation), CSV-Export
  (`localEffect: download`), Zeilenaktionen `senden` (Lieferantenauswahl, nur Mensch), `in_bestellung`, `loeschen`
  (nur Entwurf/Offen, Begruendung, nur Mensch).
- Kommando-Wege `app/api/v1/endpoints/einkauf_anfrage_kommandos.py` delegieren an die bestehenden Fachwege
  (`versende_einkauf_anfrage`, `convert_anfrage_to_order`) mit Audit, Ereignis, Trockenlauf und Wiederholungsschutz.
- Befunde der alten Seite behoben: Massenversand rief `/send` ohne Lieferanten (immer 422), Loeschen in jedem Status,
  Zeilenlink auf eine nicht vorhandene Route `/einkauf/anfragen/{id}`.
- Zeilenaktionen werden wie Kopfaktionen nur mit Recht gezeigt: Plan-Compiler filtert `rowActions` nach Recht, die
  Rollen-Projektion (`generate_action_permission_projection.py`) liest auch Zeilenaktionen (Tabellen und Tabs).
- Tests: `tests/test_studio_listen_kommandos.py` (Pruefstand), `native-list-page.test.tsx` (3).
  Ratsche: Altmuster 102 -> 101.
- Offen aus der Sichtung: Die Erfassung `anfrage-erfassung.tsx` sendet PATCH, der Server kennt nur PUT;
  `EinkaufCompatService.list_anfragen` verschluckt Fehler (leere Liste).

## Welle 1, Schritt 2 (20.10.2026): Einkauf Angebote

- ScreenDefinition `einkauf/angebote` auf `NativeListPage`; Zeilenaktionen `pruefen`, `genehmigen` (nur Mensch),
  `bestellen` (bestehender Weg der Objektmaske), `ablehnen` (Begruendung).
- Kommando-Wege `einkauf_angebot_kommandos.py` mit Statusgrenzen auf dem Server. Befund: Die Statuswege
  `/review`, `/approve`, `/reject` setzen jeden Status, auch ein bestelltes Angebot zurueck auf GEPRUEFT; die
  Grenze stand nur im Browser. Die alten Wege bleiben fuer bestehende Aufrufer, die Maske nutzt die neuen.
- Befunde der alten Seite: Loeschen rief `DELETE /einkauf/angebote/{id}`, den es nicht gibt (immer 405);
  „Import“ sprang in die Bestellliste; Zeilenlink auf die nicht vorhandene Route `/einkauf/angebote/{id}`.
  Loeschen entfaellt in der Liste (Ablehnen mit Begruendung ist der Fachweg).
- Ratsche: Altmuster 101 -> 100.

## Welle 1, Schritt 3 (20.10.2026): Einkauf Anlieferavis

- ScreenDefinition `einkauf/anlieferavis-liste` (die Objektmaske heisst `einkauf/anlieferavis`) auf
  `NativeListPage`: senden, bestaetigen, Wareneingang buchen (bestehender Weg mit Lieferschein und Lager),
  stornieren mit Begruendung, CSV-Export.
- **Befund, behoben:** `EinkaufCompatService.list_anlieferavis`/`get_anlieferavis` lasen `bestellung_id`,
  `geplantes_anliefer_datum` und `kennzeichen` — Spalten, die keine Migration anlegt und auch die gewachsene
  Datenbank nicht hat — und verschluckten den Fehler: Die Liste war immer leer, die Objektmaske immer 404.
  Jetzt die Spalten der Migration (`bestell_nr`, `erwartetes_datum`), ohne verschluckten Fehler.
- Kommando-Wege `einkauf_avis_kommandos.py` mit Statusgrenzen; der alte Weg `/{id}/{action}` setzte jeden Status,
  auch ein erhaltenes Avis auf STORNIERT.
- Offen: Es gibt keinen Anlageweg fuer Avise (`POST /einkauf/anlieferavis` fehlt); die Seite
  `einkauf/anlieferavis/neu` kann nicht speichern. Die Liste bietet deshalb keine Anlage an.
- Ratsche: Altmuster 100 -> 99.

## Welle 1, Schritt 4 (20.10.2026): Einkauf Auftragsbestaetigungen

- ScreenDefinition `einkauf/auftragsbestaetigungen` auf `NativeListPage`; Erfassen oeffnet die native Anlage
  (`/einkauf/auftragsbestaetigung/neu`), Pruefen und Bestaetigen nutzen die Wege der Objektmaske (Statusgrenzen
  seit STAMMDATEN-BEARBEITEN). Kein neuer Serverweg.
- Befunde der alten Seite: Loeschen rief `DELETE /einkauf/auftragsbestaetigungen/{id}` (gibt es nicht); Zeilenlink
  auf die nicht vorhandene Route `/einkauf/auftragsbestaetigungen/{id}`; „Import“ sprang in die Bestellliste. Fuer
  Avise gab es ebenfalls keinen DELETE-Weg.
- Ratsche: Altmuster 99 -> 98.

## Welle 1, Schritt 5 (20.10.2026): Einkauf Lieferanten

- ScreenDefinition `einkauf/lieferanten` auf `NativeListPage`, Quelle `/api/v1/einkauf/lieferanten` und
  Zeilenroute `/einkauf/lieferanten/{id}` — dieselbe Quelle wie die native Objektmaske `einkauf/supplier`.
- **Befund:** Die alte Liste las `/api/v1/crm/suppliers` (Tabelle `public.einkauf_lieferanten`) und oeffnete die
  Altmuster-Maske. Diese Tabelle gibt es weder in der frischen noch in der gewachsenen Datenbank; die Liste konnte
  nie Lieferanten zeigen. Die native Objektmaske liest `domain_einkauf.lieferanten` ueber den Einkaufsdienst; die
  Liste folgt jetzt dieser Quelle. Offen: `/crm/suppliers` selbst bleibt ein toter Weg.
- Ratsche: handgebaut 477 -> 476.

## Welle 1, Schritt 6 (20.10.2026): Einkauf Bestellungen

- ScreenDefinition `einkauf/bestellungen` auf `NativeListPage`, Quelle `/api/v1/einkauf/bestellungen` wie die
  Objektmaske `einkauf/purchase-order` (vorher `/purchase-orders`, eine Mischung aus Beleg- und Altdaten mit
  Zeilenlink auf die Altmuster-Maske). Zeilenaktionen `freigeben` (Obligo), `versenden`, `stornieren` (Begruendung),
  alle nur Mensch; Kommando-Wege `einkauf_bestellung_kommandos.py` delegieren an den `ProcurementService`.
- **Befund, behoben:** `POST /einkauf/bestellungen/import` las die Datei, meldete „Bestellungen werden angelegt“
  und legte nichts an. Jetzt ehrlich 501; die Liste bietet keinen Import an.
- Entfallen: Massendruck per `document.write` (die Seite steht nicht mehr auf der Ausnahmeliste der
  HTML-Senken); Druck gehoert zum Beleg.
- **Offene Fachfrage:** Der Versand setzt einen Entwurf direkt auf „versandt“ (Vertrag `test_versandwege_vertrag`)
  und umgeht damit Freigabe und Obligo-Buchung. Ob Versand eine Freigabe voraussetzt, ist eine Nutzerentscheidung.
- MCP-Zaehltests leiten die Zahl der `local_ui`-Eintraege aus den Listen-Definitionen ab.
- Ratsche: Altmuster 98 -> 96 (`einkauf/bestellungen` und `einkauf`).

## Welle 1, Schritt 7 (20.10.2026): Agrar Saatgut und Duenger

- ScreenDefinitions `agrar/saatgut-liste` und `agrar/duenger-liste` auf `NativeListPage`; Zeilen oeffnen die
  nativen Objektmasken `agrar/saatgut` bzw. `agrar/duenger` (vorher die Altmuster-Stammmasken). Beide Dienste
  erlauben `limit <= 200`; die Listen laden einmal bis zu dieser Grenze (`fetch_limit`).
- Duenger hatte zwei handgebaute Listen (`/agrar/duenger` und `/agrar/duenger-liste`); beide Routen zeigen jetzt
  dieselbe Liste. Deaktivieren als Kommando-Weg `agrar_stammdaten_kommandos.py` mit Begruendung und Audit; ein schon
  inaktiver Duenger wird abgewiesen.
- Geprueft und kein Befund: Die Agrar-Dienste nehmen `tenant_id` als Abfrageparameter; `tenant_binding` setzt ihn
  auf den geprueften Mandanten und weist Abweichungen ab.
- Ratsche: handgebaut 476 -> 473, Altmuster 96 -> 94.
- Abschluss-Reihenfolge: Code-Inventare vor dem Architekturindex erzeugen (der Index liest sie; sonst DRIFT im
  Quality Gate wie auf `bce21e65f`).

## Welle 1, Schritt 8 (20.10.2026): Futtermittel — eine Quelle fuer Liste, Einzelansicht und Loeschen

- **Befund, behoben:** Fuer `GET /futter/einzelfuttermittel`, `GET /futter/mischfuttermittel` und das Loeschen
  verdeckten Compat-Wege die Stammdatenwege von `futter_stamm`: Sie projizierten *alle* aktiven Artikel des
  Mandanten (auch Duenger und Saatgut), ihre Kennungen oeffneten keine Einzelansicht (die liest Futterkatalog bzw.
  `futtermittel_mischfutter`), und „Loeschen“ deaktivierte beliebige Artikel. Die verdeckenden Wege
  (`futter_read.py`, vier Compat-Loeschwege) sind entfernt; Liste, Einzelansicht und Loeschen arbeiten jetzt auf
  derselben Quelle. Die Zuordnungsvertraege (`test_futter_canonical_*_dispatch.py`, Codex 06.10.) pruefen jetzt
  diese Quelle; ihre Rollen- und Mandantenpruefungen bleiben.
- **Befund, behoben:** `POST /futter/{kategorie}/bulk-delete` loeschte hart aus `domain_shared.einzelfuttermittel`
  bzw. `domain_shared.mischfuttermittel` — Tabellen, die es nicht gibt. Entfernt.
- `futter_stamm` verschluckte Fehler der Listen (`except Exception: return []`); jetzt nicht mehr.
- ScreenDefinitions `futtermittel/einzelfuttermittel-liste` (Futterkatalog wie die Objektmaske, Stilllegen als neue
  Katalogrevision mit Begruendung) und `futtermittel/mischfuttermittel-liste` (Deaktivieren mit Begruendung).
  Vier Routen (`/futter/einzel`, `/futter/misch`, `/futtermittel/…-liste`) zeigen dieselben zwei Listen.
- Ratsche: handgebaut 473 -> 471, Altmuster 94 -> 89.
- Abschluss: Der Tabellenkatalog verzeichnet auch lesende/schreibende Codedateien; neue SQL-Wege brauchen einen
  neu erzeugten Katalog gegen einen frischen `init_db`-Pruefstand (DRIFT im Quality Gate auf `fb3e69ff1`).

## Start-Befund (20.10.2026): Lifespan-Kette

- Seit `fb3e69ff1` starteten die E2E-Laeufe kein Backend mehr (`RecursionError` in `merged_lifespan`). FastAPI
  verschachtelt je `include_router` den Lifespan; `api_router` hatte 454 Ebenen, die neuen Listen-Router kippten den
  Start unter uvicorn. TestClient-Tests betreten keinen Lifespan und blieben gruen.
- Behoben in `app/api/v1/api.py` (`_Sammelrouter`): Standard-Lifespans der Unterrouter werden nicht verkettet (ihre
  Start-/Stop-Handler hat `include_router` schon uebernommen und fuehrte sie verkettet doppelt aus). Tiefe 454 -> 7.
- Regressionstest `tests/test_lifespan_kette.py` startet beide Anwendungen mit Rekursionsgrenze 400 (ohne Korrektur
  rot) und prueft, dass Start-Handler einmal laufen.

## Welle 1, Schritt 9 (20.10.2026): Finance Debitoren

- ScreenDefinition `finance/debitoren-liste` auf `NativeListPage`, Quelle `/api/v1/finance/debitoren` wie die
  Objektmaske `finance/debitor`; Zeile oeffnet die native Maske (vorher `/finance/debitoren/{id}`, Altmuster).
- Sperren/Entsperren als Kommando-Wege `finance_stammdaten_kommandos.py` mit Begruendung, Audit und Finance-
  Schreibrolle (vorher `PATCH /finance/debtors/{id}` ohne Grund und Audit); „Mahnwesen“ fuehrt ins Mahnwesen.
- **Befunde der alten Seite:** „Zahlungserinnerung“ meldete Erfolg ohne jede Anfrage; „Mahnung senden“ fuer eine
  Auswahl startete einen Mahnlauf fuer *alle* Debitoren; „Loeschen“ rief `DELETE /finance/debitoren/{id}`, den es
  nicht gibt. Alle drei entfallen; Mahnungen laufen im Mahnwesen mit Vorschau.
- Ratsche: Altmuster 89 -> 88.

## Welle 1, Schritt 10 (20.10.2026): Finance Kreditoren

- **Befund, behoben:** `/finance/kreditoren` („Kreditoren-Liste“ in der Finance-Uebersicht) zeigte ein leeres
  Anlageformular statt der Kreditoren; nach dem Speichern landete man wieder dort. Die Route zeigt jetzt die
  Studio-Liste `finance/kreditoren-liste` (Quelle `/api/v1/finance/kreditoren` wie die Objektmaske
  `finance/kreditor`); die Anlage liegt unter `/finance/kreditoren-stamm`.
- Kreditoren sind die Lieferanten des Einkaufs (`ProcurementService.list_lieferanten`); ein Beleg, ein Besitzer.
- Ratsche: Altmuster 88 -> 87.

## Befund (20.10.2026): erfundene Saatgut- und Duengerprodukte, erfundene Bestellnummer

- `features/agrar/api.ts` lieferte bei *jedem* Fehler erfundene Produkte (`SEED_FALLBACK`, `FERTILIZER_FALLBACK`
  mit Lieferant, Bestand und Staffelpreisen); weil `GET /api/v1/articles` ohne Schraegstrich keinen Weg traf, zeigte
  `agrar/saatgut/liste` („Saatgutbestand und Forecast“) immer diese Scheindaten. `submitSeedOrder` meldete bei einem
  Fehler eine erfundene Bestellnummer `SO-…` als Erfolg (ohne Aufrufer, entfernt).
- Jetzt: Abrufe gegen `/api/v1/articles/` mit `category`, Fehler gehen an die Seite; `agrar/saatgut/liste` zeigt
  dieselbe Studio-Saatgutliste wie `/agrar/saatgut`.
- Ratsche: Altmuster 87 -> 86.

## Befund (20.10.2026): Scheindaten in Fachablaeufen — systemweit entfernt, Waechter

- `charge/rueckverfolgung`: ohne gefundene Charge eine erfundene Kette (Landwirt bis Muehle), als „Fallback-Sicht“.
- `lager/einlagerung`, `lager/bestandskorrektur`: erfundene Lagerorte und Artikel, wenn die Abfrage leer war —
  Buchungen auf Orte, die es nicht gibt.
- `annahme/lkw-registrierung`, `verladung/lkw-beladung`: erfundene Artikel; in der Registrierung mit dem Namen als
  Artikelkennung.
- Alle entfernt; Auswahlen zeigen nur echte Eintraege, die Rueckverfolgung einen Leerzustand.
- `lib/api/betrieb.ts`: 30 Abfragen starteten mit erfundenen Daten als `initialData` (Bankkonten mit Salden,
  Cross-Compliance-Stand, Sachkunde- und VVVO-Register, Zertifikate, Wiegungen …); das Management-Dashboard zeigte
  erfundene Kennzahlen („Umsatz MTD 1.85M“, „Liquiditaet 785K“) und Top-Kunden mit Umsaetzen. Bis zur Antwort und
  bei Fehlern dauerhaft. Jetzt leer.
- Dashboard-KPI-Widget: bei ausbleibenden Kennzahlen erfundene Werte („€ 129.200“); jetzt „–“.
- Waechter `src/__tests__/security/keine-scheindaten.test.ts`: keine Ersatzlisten `FALLBACK_/MOCK_/DUMMY_/SAMPLE_/FAKE_`
  in Seiten, Features, Bibliotheken und Komponenten, auch kleingeschriebene Ersatzobjekte (`fb`, `fallback…`,
  `mock…`); ausdrueckliche Vorfuehrungen `DEMO_` bleiben.

## Welle 1, Schritt 11 (20.10.2026): CRM-Marketing und DSGVO-Anfragen

- Fuenf Studio-Listen: `crm/kampagnen-liste`, `crm/kampagnenvorlagen-liste` (aktivieren, deaktivieren,
  duplizieren, loeschen), `crm/einwilligungen-liste` (widerrufen mit Grund), `crm/dsgvo-anfragen-liste` (Identitaet
  bestaetigen, Auskunft, Daten loeschen Art. 17, ablehnen mit Grund), `crm/segmente-liste` (neu berechnen, loeschen).
- `NativeListPage` wertet eine 2xx-Antwort eines Fachwegs ohne Umschlag als Erfolg (`success: false` bleibt
  Ablehnung); so rufen die Listen die bestehenden Fachwege mit ihren Rollen, wie Objektmasken es schon tun.
- **Befund, behoben:** `GET /gdpr/requests` gab es nicht — die Liste der Betroffenenanfragen war immer leer, ihre
  Spalten passten zu keiner API, „Loeschen“ und „Als erledigt markieren“ zielten auf nicht vorhandene Wege. Neuer
  Listenweg mandantengenau mit Bereichsrolle (die Liste zeigt E-Mail-Adressen Betroffener).
- **Befund, behoben:** Ablehnen (DSGVO) und Widerruf (Einwilligung) lasen den Grund nur als Query-Parameter; der
  Grund aus Maske, CLI und MCP (Body) ging verloren.
- **Offen (Entscheidung):** `DELETE /crm/consents/{id}` loescht den Einwilligungsnachweis hart (Art. 7 Abs. 1
  DSGVO verlangt den Nachweis); die Liste bietet Loeschen nicht an. Der Widerruf protokolliert immer
  `changed_by="contact"`, auch wenn Mitarbeitende widerrufen.
- Ratsche: Altmuster 86 -> 81.

## Welle 1, Schritt 12 (20.10.2026): CRM Verkaufschancen

- ScreenDefinition `crm/opportunities-liste` (Ladegrenze 200 wie der Dienst); Zeile oeffnet die native Maske
  `crm/opportunity`; „Angebot erstellen“ fuehrt in die Angebotserfassung, „Pipeline-Ansicht“ ins Kanban.
- **Befund, behoben:** „Gewonnen“/„Verloren“ setzten per `PUT` je Zeile den Status ohne Pruefung, Grund und Audit,
  auch fuer bereits abgeschlossene Chancen. Jetzt Kommando-Wege `crm_listen_kommandos.py` ueber
  `update_opportunity` (wie das Bearbeiten der Objektmaske), Verloren mit Begruendung, Abgeschlossene abgewiesen.
- Ratsche: Altmuster 81 -> 80.

## Sicherheitsbefund (20.10.2026): Kontakte aus crm-core ohne Mandant

- `app/api/v1/endpoints/contacts.py` reicht Liste (`/crm/contacts/`), Abruf, Anlage, Aendern und Loeschen an
  crm-core durch; crm-core fuehrt an Kontakten keinen Mandanten. Damit sah jeder Nutzer die Kontakte *aller*
  Mandanten und konnte fremde Kontakte aendern oder loeschen (wenn crm-core laeuft).
- Behoben, ohne die Quelle umzubauen: Ein Kontakt gilt nur ueber seinen Kunden als eigener (`domain_crm.customers`
  per `id` oder `business_partner_id` im Mandanten); fremde werden aus der Liste gefiltert und im Abruf, Aendern
  und Loeschen mit 404 abgewiesen; Anlage nur fuer einen eigenen Kunden. Test in `test_studio_listen_kommandos.py`.
- Offen (CRM-Konsolidierung): In `main:app` liest `GET /crm/contacts` (ohne Schraegstrich) die lokale Tabelle
  `crm_contacts` (`app/crm/router.py`), alle uebrigen Wege gehen an crm-core — neu angelegte Kontakte erscheinen
  dort nicht in der Liste. `PUT`/`DELETE` in `app/crm/router.py` haben keine Rolle, sind aber von `contacts.py`
  verdeckt (die Rollen-Ratsche dedupliziert gleiche Pfade). Auch die CRM-Lieferantenliste (alle Business Partner,
  tote Links) gehoert dorthin.

## Rollen-Ratsche: verdeckte Wege (20.10.2026)

- `scripts/check_write_routes_roles.py` dedupliziert nach Pfad und Methode und pruefte deshalb nur die erste Route
  je Pfad. Acht verdeckte Schreibwege hatten keine Rolle: `PUT/DELETE /crm/contacts/{id}`,
  `PUT/DELETE /crm/activities/{id}`, `POST /crm/consents/{id}/revoke` (`app/crm/router.py`) und
  `POST /einkauf/rechnungseingaenge/{id}/pruefen|freigeben|verbuchen` (`app/einkauf/router.py`). Heute verdeckt,
  aber erreichbar, sobald sich die Router-Reihenfolge aendert.
- Alle acht mit derselben Bereichsrolle wie der verdeckende Weg; die Ratsche prueft jetzt jedes Routenobjekt.

## Sichtung 20.10.2026: zurueckgestellt bzw. Entscheidung noetig

| Seite | Befund | Weiter |
|---|---|---|
| `verkauf/kunden-liste` | Fuehrt im Browser Business Partner und `kunden_lookup` zusammen, verschluckt beide Fehler; Kundenbestand verteilt auf crm-core, `domain_crm.customers`, Business Partner und `kunden_lookup`; Zeile oeffnet die Altmuster-Maske statt `crm/customer-360` | Quellenfrage gehoert zur CRM-Konsolidierung; danach Liste mit Serverblaetterung |
| `agrar/aussaat` (Navigation) | `GET /api/v1/agrar/aussaaten` gibt es nicht: Seite zeigt immer einen Fehler; Links auf `/agrar/aussaat/{id}` und `/agrar/aussaat/neu` ohne Route | Nutzerentscheid: entfernen oder ins Feldbuch (Ackerschlagkartei) ueberfuehren |
| `agrar/kulturpflanzen` (Navigation) | Liest die Kulturliste des Wettermoduls; Links auf `/agrar/kulturpflanzen/{id}` und `/neu` ohne Route | Nutzerentscheid: Stammdatum mit Objektmaske oder reine Wetter-Auswahl |
| `finance/bankkonten` | Zwei Bestaende: `/banken/konten` (native Maske) und `/finance/bank-accounts` (`domain_erp.bank_accounts` mit Sachkonto, Altmuster-Formular); Route zeigt ein Formular statt einer Liste | Fachentscheid: massgeblicher Bankkontenbestand (Buchungsanbindung) |
| `agrar/biostimulanzien` | Anlage-, Detail- und Bearbeiten-Routen zeigen wieder die Liste (keine Stamm-/Detailseite); API hat CRUD | Objektmaske `agrar/biostimulanz` anlegen, dann Liste |
| `lager/bestandsuebersicht`, `lager/silo-uebersicht` | Cockpits mit mehreren Kennzahlquellen, keine Listen | Cockpit-Familie |
| Datenquellen mit eigenen Parameternamen (`skip`/`search`) | Laufzeit sendet `page`/`limit`/`q`; Serverblaetterung braucht eine Parameterabbildung in der Datenquelle | Framework: `ScreenDataSource` um Parameterabbildung erweitern (auch fuer Kontrakte) |

## Zurueckgestellt: Kontraktuebersicht

`/kontrakte` (LstKontraktUebersicht) ist ein Arbeitsvorrat mit zehn Serverfiltern und Engagement-/Steuerungskennzahlen.
Ohne deklarative Filterleiste in der ScreenDefinition wuerde ein Umbau Funktion wegnehmen; zuerst das Framework.

## Laufzeit: Tabellen ohne Serverblaetterung (20.10.2026)

- **Befund, behoben (zentral):** Fuer Tabellen mit `serverPagination: false` schickte die Laufzeit trotzdem
  `page`/`limit`/`q` an den Dienst, und der Renderer zeigte nur die ersten `pageSize` Zeilen ohne Blaettern. Dienste
  ohne `q`-Auswertung (alle Einkaufslisten) machten die Suche wirkungslos; Dienste mit `limit` lieferten still nur
  die erste Seite.
- Jetzt: einmal bis zur `pageSize` der Datenquelle laden, Suche/Filter/Sortierung/Seite im Browser
  (`runtime/client-table-query.ts`), Blaettern mit Gesamtzahl. Gilt fuer alle Masken mit solchen Tabellen.

## Eingangsrechnungen zurueckgestellt

`einkauf/rechnungseingaenge-liste` hat vier parallele Wege (Compat `/einkauf/rechnungseingaenge/*`, Einkaufsrouter,
`finance/ap/invoices` der nativen Maske `finance/ap-invoice`, DocFlow-Beleg `beleg/purchase-invoice`). Nach den
Vorgaben (DocFlow fuehrend, ein Beleg ein Besitzer, eine Belegmaske mit Varianten, Kontroll-Engine beim Buchen)
gehoert die Liste in die Belegwelle, nicht in einen Listenumbau.

## CI-Nachlauf (20.10.2026)

- Reine Oberflaechenaktionen der Listen (Export, Anlage oeffnen) tragen `stubReason` und einen `command`/eine
  Route wie die Vorbilder im Bestand; Agentenvertrag und Wege-Inventar verlangen das.
- Die MCP-Karte zaehlt vier neue `local_ui`-Eintraege (Anlage-Navigation der Listen); die Zaehltests pruefen sie
  einzeln.

## Sichtung der uebrigen Routen

| Bereich | handgebaut | Altmuster |
|---|---|---|
| agrar | 48 | 6 |
| crm | 21 | 26 |
| finance | 28 | 18 |
| fibu | 42 | 1 |
| einkauf | 27 | 15 |
| admin | 27 | 0 |
| futtermittel | 9 | 16 |
| sales | 22 | 0 |
| lager | 16 | 3 |
| compliance | 14 | 2 |
| portal | 16 | 0 |
| workflow | 14 | 0 |
| personal | 12 | 0 |
| strecke | 12 | 0 |
| pos | 9 | 2 |
| verkauf | 11 | 0 |
| kontrakte | 9 | 0 |
| annahme | 5 | 3 |
| controlling | 7 | 0 |
| docflow | 6 | 0 |
| qualitaet | 5 | 1 |
| charge | 4 | 1 |
| produktion | 3 | 2 |
| service | 5 | 0 |
| waage | 5 | 0 |
| agribusiness | 4 | 0 |
| disposition | 4 | 0 |
| futter | 4 | 0 |
| nachhaltigkeit | 4 | 0 |
| nawaro | 4 | 0 |
| preise | 4 | 0 |
| versand | 4 | 0 |
| workflows | 4 | 0 |
| artikel | 3 | 0 |
| dashboard | 3 | 0 |
| schaeden | 1 | 2 |
| vertrag | 3 | 0 |
| auth | 2 | 0 |
| foerderung | 1 | 1 |
| fuhrpark | 2 | 0 |
| genossenschaft | 2 | 0 |
| inventory | 2 | 0 |
| monitoring | 2 | 0 |
| reports | 2 | 0 |
| silo | 2 | 0 |
| tankstelle | 2 | 0 |
| wartung | 2 | 0 |
| zertifikate | 2 | 0 |
| start | 1 | 0 |
| alerts | 1 | 0 |
| banken | 1 | 0 |
| benachrichtigungen | 1 | 0 |
| contracts | 1 | 0 |
| copilot | 1 | 0 |
| dashboards | 1 | 0 |
| document | 1 | 0 |
| dokumente | 1 | 0 |
| einstellungen | 1 | 0 |
| errors | 1 | 0 |
| etiketten | 0 | 1 |
| export | 0 | 1 |
| finanzplanung | 1 | 0 |
| hilfe | 1 | 0 |
| inbox | 1 | 0 |
| inventory-dashboard | 1 | 0 |
| inventory-reports | 1 | 0 |
| labor | 1 | 0 |
| mahnwesen | 1 | 0 |
| management | 1 | 0 |
| marketing | 1 | 0 |
| mobile | 1 | 0 |
| policies | 1 | 0 |
| pricing | 1 | 0 |
| projekte | 1 | 0 |
| prospecting | 1 | 0 |
| public | 1 | 0 |
| rezepte | 1 | 0 |
| schichtplan | 1 | 0 |
| setup | 1 | 0 |
| stammdaten | 1 | 0 |
| stock-management | 1 | 0 |
| subventionen | 1 | 0 |
| system | 1 | 0 |
| verladung | 0 | 1 |
| versicherungen | 1 | 0 |
| vertrieb | 1 | 0 |
| weighing | 1 | 0 |
| wissen | 1 | 0 |

### Noch verwaiste Routen (39) — vor dem Umbau einzeln entscheiden (loeschen, umleiten oder umbauen)

- `admin/setup/dms-integration` (handgebaut, @/pages/admin/setup/dms-integration)
- `agrar/saatgut/stamm/:id` (handgebaut, @/pages/agrar/saatgut/stamm)
- `agrar/schlaege/karte` (handgebaut, @/pages/agrar/schlaege/karte)
- `agrar/wetterwarnung` (handgebaut, @/pages/agrar/wetterwarnung)
- `agribusiness/farmers` (handgebaut, @/pages/agribusiness/farmers)
- `crm/campaign-builder` (handgebaut, @/pages/crm/campaign-builder)
- `crm/kontakt-management` (builder_altmuster, @/pages/crm/kontakt-management)
- `crm/opportunities-forecast` (handgebaut, @/pages/crm/opportunities-forecast)
- `dashboard/customizable` (handgebaut, @/pages/dashboard/customizable)
- `dashboards/geschaeftsfuehrung` (handgebaut, @/pages/dashboards/geschaeftsfuehrung)
- `etiketten/drucken` (builder_altmuster, @/pages/etiketten/drucken)
- `fibu/debitoren-api` (handgebaut, @/pages/fibu/debitoren-api)
- `finance/buchungen` (builder_altmuster, @/pages/finance/buchungserfassung)
- `finance/dunning-editor` (builder_altmuster, @/pages/finance/dunning-editor)
- `finance/kasse` (builder_altmuster, @/pages/finance/kasse)
- `finance/kontenplan` (handgebaut, @/pages/finance/chart-of-accounts)
- `futter/einzel` (handgebaut, @/pages/futter/einzel/liste)
- `futtermittel/bestellungen` (builder_altmuster, @/pages/futtermittel/futtermittel-bestellung)
- `futtermittel/charge-verfolgung` (builder_altmuster, @/pages/futtermittel/charge-verfolgung)
- `futtermittel/futtermittel-bestellung` (builder_altmuster, @/pages/futtermittel/futtermittel-bestellung)
- `inventory-dashboard` (handgebaut, @/pages/inventory-dashboard)
- `inventory-reports` (handgebaut, @/pages/inventory-reports)
- `inventory/epcis` (handgebaut, @/pages/inventory/epcis/index)
- `labor/proben` (handgebaut, @/pages/labor/proben-liste)
- `marketing/kampagnen` (handgebaut, @/pages/marketing/kampagnen)
- `mobile/scanner` (handgebaut, @/pages/mobile/scanner)
- `personal/schulung-neu` (handgebaut, @/pages/personal/schulung-neu)
- `portal/feldbuch-auswertungen` (handgebaut, @/pages/portal/feldbuch-auswertungen)
- `portal/whatsapp-simulator` (handgebaut, @/pages/portal/whatsapp-simulator)
- `rezepte/editor` (handgebaut, @/pages/rezepte/editor)
- `schaeden/liste` (builder_altmuster, @/pages/schaeden/meldung)
- `stock-management` (handgebaut, @/pages/stock-management)
- `subventionen/dashboard` (handgebaut, @/pages/subventionen/dashboard)
- `system/live-monitor` (handgebaut, @/pages/system/live-monitor)
- `tankstelle/zapfungen` (handgebaut, @/pages/tankstelle/zapfungen)
- `vertrag/rahmenvertraege` (handgebaut, @/pages/vertrag/rahmenvertraege)
- `vertrieb/kundenumsatz` (handgebaut, @/pages/vertrieb/kundenumsatz)
- `wartung/anlage/neu` (handgebaut, @/pages/wartung/anlagen-liste)
- `wartung/anlagen` (handgebaut, @/pages/wartung/anlagen-liste)

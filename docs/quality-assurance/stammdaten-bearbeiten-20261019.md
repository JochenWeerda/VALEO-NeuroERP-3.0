# Bearbeiten der Objektmasken (STAMMDATEN-BEARBEITEN-20261019)

Folge-Slice aus MASK-COMMANDS-ROLLOUT (Schritt 4): elf native Objektmasken hatten einen Bearbeiten-Knopf ohne
Wirkung; er war entfernt. Jetzt hat jede einen echten Bearbeitungsweg, der fuer Maske, CLI und MCP derselbe ist.

## Muster

- Kommandoweg `.../{entity_id}/actions/bearbeiten` in `app/api/v1/endpoints/stammdaten_bearbeiten.py`.
  Er **delegiert an den bestehenden Aenderungsweg** des Objekts (eine Fachaktion, mehrere Zugaenge).
- Gemeinsamer Rahmen `app.services.mask_commands.bearbeiten` ueber `run_delegated_mask_action`:
  - nur die deklarierten Eingabefelder zaehlen; die Maske schickt den ganzen Objektkontext mit, `None` gilt als
    nicht gesendet;
  - die Pruefung laeuft in jedem Modus: Begruendung, mindestens ein Feld, Objekt im Mandanten, Status, Modell;
  - `dryRun` schreibt nichts, `execute` schreibt Fachweg, Audit und Ereignis in einem Commit;
  - eine Wiederholung mit demselben Schluessel wirkt einmal.
- Die Rollen jedes Kommandowegs sind dieselben wie die seines Aenderungswegs. Beim Kontrakt sind das
  `KONTRAKT_BEARBEITEN`/`_ADMIN`, beim Lead die CRM-Rollen.
- ScreenDefinitions: Aktion mit `inputFields` (Eingabedialog der nativen Detailmaske).
  - Finanzstamm (Bankkonto, Debitor, Kreditor) und Kontrakt verlangen eine Begruendung und Bestaetigung.
  - Sie sind fuer Agenten gesperrt und stehen in `agentContract.dangerousActions`.

| Maske | Felder | Fachweg |
|---|---|---|
| Auftrag | Betreff, Liefertermin, Ansprechpartner, Versandart, Zahlungsbedingung, Lieferanschrift, Notizen; nur offen/bestaetigt | `PUT /sales/orders/{id}` |
| Kontrakt | Datum, Gueltigkeit, Menge, Einheit, Zahlungsbedingung, Notizen; nur OFFEN | `PATCH /kontrakte/{id}` |
| Chance | Bezeichnung, Zustaendig, Phase, Wert, Wahrscheinlichkeit, Abschluss, Quelle | `PUT /crm/opportunities/{id}` |
| Lead | Unternehmen, Ansprechpartner, Kontakt, Quelle, Wert, Prioritaet, Zustaendig | `crm_lead_service.update` |
| Anfrage | Anforderer, Abteilung, Prioritaet, Artikel, Menge, Einheit, Begruendung, Notizen | `PUT /einkauf/anfragen/{id}` |
| Auftragsbestaetigung | — (Lieferantenbeleg): Schritte **Pruefen** und **Bestaetigen** | Zustandswechsel des Compat-Dienstes |
| Bankkonto | Bank, Kontoart, aktiv — **kein Saldo** (Kontoauszuege), keine IBAN | `PATCH /banken/konten/{id}` |
| Debitor | Kreditlimit, aktiv | `PATCH /finance/debitoren/{id}` |
| Kreditor | Anschrift, Kontakt, Steuerdaten, Zahlungsziel, aktiv, Notiz | `PUT /finance/creditors/{id}` |
| Mischfuttermittel | Bezeichnung, Tierart, Leistungsstufe, Protein, Energie, Beschreibung | `PUT /futter/mischfuttermittel/{id}` mit Ist-Stand ergaenzt (Vollersatz leert sonst Felder) |
| Reklamation | Zustaendig, Frist; nicht geschlossen; Audit-Eintrag `bearbeitet` mit Token-Akteur | neu, in der Reklamations-Auditkette |

## Befunde unterwegs (behoben)

- **Chance:** Der Aenderungsweg schrieb nur nach crm-sales. Eine lokal gefuehrte Chance war damit nie aenderbar
  (500), obwohl das Lesen auf die lokale Tabelle zurueckfaellt. Das Aendern faellt jetzt genauso zurueck.
- **Auftragsbestaetigung:** Der Dienst fragte `bestaetigungs_nummer`/`bestellung_id` ab; die Migration legt
  `ab_nummer`/`bestell_nr` an. Den Fehler schluckte ein `except Exception`, deshalb war die Liste in jeder Datenbank
  leer und die Einzelansicht immer 404. Spalten korrigiert, Fehler-Schlucker entfernt.
- **Rechte in der Oberflaeche:** Native Aktionen waren nur sichtbar mit einem `erp_scopes`-Attribut je Nutzer (oder
  fuer `admin`). Ein Fachanwender mit der Bereichsrolle sah sie nicht.
  - Neu: `scripts/generate_action_permission_projection.py` liest die `require_roles`-Abhaengigkeiten jedes
    Kommandowegs und schreibt `action-permissions.generated.json` (46 Masken, 59 Aktionsrechte).
  - `getScreenPermissions` entscheidet danach wie der Server. Ein Scope-Attribut kann die Serverrollen nicht
    ueberstimmen. Drift-Test `tests/test_action_permission_projection.py`.
- **Body-Vertrag wirkungslos** und 23 Fundstellen: siehe `write-roles-bereiche-20261019.md` (eigener Commit).
- Prozesskern-Tests wave4/wave11/wave37: Mini-Apps ohne Testidentitaet nach dem Rollenblock (401) — nachgezogen.

## Nachweis

- `tests/test_stammdaten_bearbeiten.py` gegen die frische Pruefstand-DB `valeo_probe_writeroles`: 32 Tests gruen.
  - Wirkung: Bankkonto, Mischfutter, Lead, Reklamation, Auftragsbestaetigung.
  - Trockenlauf ohne Schreibzugriff, fremder Mandant, ohne Aenderung, gesperrter Status.
  - Deklaration aller elf Masken; Lese-SQL aller Wege gegen das echte Schema; lokaler Rueckfall der Chance.
- Bestandstests der beruehrten Module: 220 Dateien, 8782 gruen. Die 13 Fehlschlaege (fehlende Testidentitaet) sind
  nachgezogen und gruen (112).
  - Die 10 Fehler waren der Pruefstand-Schutz ohne erklaerte DB; mit `TEST_DATABASE_URL` sind sie gruen (59).
- Frontend: `screen-permissions.test.ts` 16 gruen, `tsc` (volle tsconfig) und ESLint sauber.
- Gates gruen: Projektionen, Masken-Studio-Ratsche (alle Luecken 0), Kommando-Inventar, MCP-Bindungen,
  Architektur-Drift, Rollen-Ratsche 0, Godfile. CLI-Register 220 -> 232 Aktionen.

## Offen

- Gesamtlauf der Backend-Suite: lokal wegen Speichermangels nicht moeglich, CI ist Schiedsrichter.

## CI-Nachlauf (20.10.2026)

- Pytest (PostgreSQL, `needs_live_db`) war rot: 25 Faelle. Es waren Mini-App-Tests des Prozesskerns ohne
  Testidentitaet nach dem Rollenblock; die lokale Auswahl nach Modulimport hatte sie nicht erfasst.
- Systematisch nachgesucht: alle Testdateien mit `FastAPI()` ohne Testgrenze, 62 Dateien. Davon waren 22 rot (113
  Faelle), alle 401. Nach dem Nachziehen von `ersetze_nutzer` sind 322 gruen.
- „Role description contracts“ war seit `6070f8e68` rot. `check_fachrollen.py` hielt den Gruppenschluessel
  `FACHLICH_LESEN` fuer eine Rolle (Muster `*_LESEN`). Die Gruppe heisst jetzt `BERECHNEN`, der Katalog ist gruen.
- Docs Build, Service Security und Security Scan waren schon vor diesen Commits rot und sind nicht Teil dieses Slices.

## Erfassung eingehender Auftragsbestaetigungen (20.10.2026)

- Neuer Weg `POST /api/v1/einkauf/auftragsbestaetigungen` (`einkauf_ab_erfassung.py`, Rolle EINKAUF).
  - Die AB entsteht zu einer Bestellung des Mandanten.
  - Lieferant, Bestellnummer und Waehrung leitet der Server aus der Bestellung ab. Ein vom Client gesendeter
    Lieferant wird ignoriert.
  - Dieselbe AB-Nummer wird mit 409 abgewiesen, eine fremde Bestellung mit 404.
- Native Anlage ueber `creation` der Maske `einkauf/auftragsbestaetigung`. Die Route `/einkauf/auftragsbestaetigung/neu`
  fuehrt jetzt in die native Anlage; vorher zeigte sie eine handgebaute Seite, die an einen nicht vorhandenen Weg
  sendete.
- Die Rechte-Projektion deckt auch Anlagen ab (61 Rechte).
- Nebenbefund: `preis_kalkulation_bridge` und `stammdaten_bearbeiten` hatten keine Domaenenzuordnung im
  Architekturindex (`test_generate_architecture_index` rot). Ergaenzt, Mapping 466/466.
- Nachweis:
  - `test_stammdaten_bearbeiten.py` mit 34 Tests und die Projektion gruen.
  - Maskenbezogene Suiten: 3454 gruen; der eine Fehlschlag (Architekturindex) ist behoben.
  - Routing-Integritaet, Navigationsziele, `tsc` sauber.

## CI-Nachlauf 2 (20.10.2026)

- Security Scan: `aiohttp` 3.14.4 behebt drei CVEs.
- Service Security: die chromadb-Ausnahmen sind neu geprueft (siehe `security-dependency-policy-2026-09-15.md`).
- Docs Build: die Inventare waren nicht aktuell (Drift). Alle Docs-Schritte laufen lokal gruen.

## EDI-Eingang ORDRSP mit Positionsabgleich (20.10.2026)

- `app/services/ordrsp_service.py`: Reiner Dienst ohne Datenbank.
  - Liest EDIFACT ORDRSP D.96A: UNA-Trennzeichen, Freigabezeichen, BGM-Funktion, DTM, RFF+ON, CUX, LIN-Aktion, PIA,
    QTY, PRI, MOA.
  - Gleicht die Positionen gegen die Bestellung ab: Menge, Preis, Termin, abgelehnt, zusaetzlich, nicht bestaetigt.
    Die Zuordnung laeuft ueber die Artikel- oder Lieferanten-Artikelnummer, sonst ueber die Positionsnummer.
- `POST /api/v1/einkauf/auftragsbestaetigungen/edi-ordrsp` (Rolle EINKAUF):
  - Die Bestellung wird ueber RFF+ON im Mandanten gesucht (404, wenn nicht gefunden).
  - Die AB wird ueber dieselbe Anlagefunktion wie bei der Erfassung angelegt. Die Abweichungen stehen als Text an der
    AB und als Liste in der Antwort.
  - Eine erneute Zustellung derselben Nachricht ergibt 409, eine unlesbare Nachricht 422.
  - Bestellungen aus dem Dokumentspeicher ohne Positionstabelle werden ehrlich als „Positionsabgleich nicht moeglich“
    vermerkt.
- Nachweis: `tests/test_ordrsp_service.py` (9 gruen) und die Wirkung im Pruefstand
  (`test_ordrsp_legt_ab_an_und_gleicht_positionen_ab`).

## CI-Nachlauf 3 (20.10.2026): Quality Gate und CI/CD Pipeline

Beide Workflows waren dauerhaft rot: die CI/CD Pipeline in allen 24 der letzten Laeufe, das Quality Gate in 13 von 25
(die uebrigen 11 abgebrochen). Damit ging auch das Signal der Rollen-Ratsche unter, deren Tests im vollen Lauf
mitlaufen.

- **Mandantenklassifikation:** `preis_kalkulation_bridge.py` war nicht klassifiziert.
  - Dabei fiel auf: Der Weg war ein Platzhalter mit Basispreis 100, erfundenem Gruppenrabatt und festen 19 % MwSt.
  - Jetzt delegiert er an die Preisfindung (`pricing.calculate_price`, mandantengebunden) und nimmt den Steuersatz
    aus dem Verkaufs-Steuerschluessel des Artikels.
  - Ohne gueltigen Schluessel nennt er keine Steuer.
  - Die Seite `preise/kalkulation` zeigt Fehler und fehlende Steuer an. Die Schein-Eingaben Kundengruppe und
    Sortenklasse sind durch die Kunden-ID ersetzt.
- **Paginierungs-Ratsche:** Die Positionsabfrage der ORDRSP-Verarbeitung ist jetzt auf 5000 Zeilen begrenzt.
- **Tabellenkatalog:** Neu erzeugt aus einer DB, die wie in der CI aufgebaut ist (`scripts/init_db.py`).
  - Er stimmt mit dem Beleg-Artefakt der CI ueberein (681 Tabellen).
  - Dazu kommen nur die neuen Lesestellen dieses Slices.
- **Volle Suite** (38 Fehlschlaege in der CI):
  - `test_reporting_command_atomic`: Testidentitaet fehlte.
  - `test_slice_yaml_contracts`: 21 Slice-YAMLs ohne `slice_id`, ergaenzt aus `id`; 6 Dateien mit leerem
    Folgedokument nach dem schliessenden `---`.
  - `test_beleg_aktionen`: Eine reine Leserolle wird seit dem Rollenblock schon am Schreibweg abgewiesen (403). Es
    wird weiterhin nichts gebucht; der Vertrag haelt das fest.

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

- Eingehende Auftragsbestaetigungen haben keinen Erfassungsweg; die Tabelle fuellt niemand. Das ist ein eigener
  Fachslice: EDI-ORDRSP oder Erfassung, Abgleich mit der Bestellung.
- Gesamtlauf der Backend-Suite: lokal wegen Speichermangels nicht moeglich, CI ist Schiedsrichter.

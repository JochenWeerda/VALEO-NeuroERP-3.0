# CRM Customer 360 — Bauplan (Nutzer-Spec aus L3-Screenshots, 2026-06-09)

Moderner Nachbau der L3-Kundenmaske als CRM-Customer-360 (Tabs/Drawer/Dialoge statt Pop-up-Chaos),
gleiche fachliche Tiefe. Kundenkontext bleibt bei jeder Aktion erhalten; **kein** 404; jeder Button
hat eine definierte Aktion. Fehlt ein Backend-Endpoint: Mock-/Adapter-Schicht mit TODO, UI stabil.

## Bereiche & Status

1. **Kundenkopf** (`CustomerHeaderCard`) — Stammdaten inkl. Kundengruppe/Hauptkunde/Konzern/VB/Disp/KV-Limit/Migrationshinweis. *(KIM hat Kopf; Feld-Vervollstaendigung offen.)*
2. **Action-Bar konfigurierbar** — Buttons Öffnen/Neu(=Neukunde)/Information/Präsente/Tel/E-Mail/Ang.-Auf./Faktur/Drucken; **benutzerbezogene Sichtbarkeit** (Kontextmenü „Sichtbar" + „auf Standard zurücksetzen"), persistierbar. *(QUICK-001: Neukunde+Druck da; Konfigurierbarkeit offen.)*
3. **Information-Dropdown** — Subtabs: Selektion, Profil, Mitbewerber, Kreditsicherheit, Fibu-OP, Kunden-Artikel(F11), Lieferanten-Artikel, Kunden-Preisvereinbarung(Strg+B), Kontrakt-Übersicht, Konzernzugehörigkeit(Strg+Z), Zusätzliche Felder. Jeder Punkt = stabiler Subtab; fehlende Module = Placeholder (Titel+Beschreibung+leeres Tabellenlayout), **kein 404**.
4. **Präsente-Tab** (`/crm/customers/:id/gifts`) — Filter Jahr/Ansprechpartner; Tabelle (Datum/AP/Anlass/lfd.Nr/Präsent/Anzahl/VB/Bediener); Eingabeformular; CRUD + „Zeile OK" + „Aufbereiten". Backend: `CustomerGift`-Modell nötig.
5. **Telefon-Auswahl-Dialog** — bei mehreren Nummern Dialog (Radio Telefon 1/2), leere deaktiviert; OK → TAPI-Dial/`tel:`/Copy; stabil schließbar. *(Backend `POST /crm/tapi/dial` vorhanden — KIM-L3-BACKEND-001.)*
6. **Ang./Auf.-Dropdown** — Angebote/Aufträge/Lieferschein/Anfrage/Bestellung/Übersicht; je kundenbezogene Belegliste (gemeinsame `CustomerDocuments`-Komponente). *(QUICK-001: open/new-Routing da; Dropdown-Menü offen.)*
7. **Ansprechpartner-Tab** (`/crm/customers/:id/contacts`) — obere Tabelle (Prio/Name/Vorname/Position/Abteilung) + Detailformular (~40 Felder) + rechte **Werbe-Matrix** (je Kategorie: nein/Firma/Privat) + Toolbar (Neu/Ändern/Speichern/Löschen/Abbrechen/**Pseudonymisieren**) + Unterfunktionen (Datenschutz/Präsente/Kompetenzcenter/Mailings/Zusatzfelder/L3-Connect). Backend: `CustomerContactPerson` (erweitert) + `ContactMarketingPreference`.
8. **Aktivitätenjournal** — Tabs Übersicht/Historie/Rechnungen/Mahnungen; Spalten Richtung/Datum/erl./Art/Kurzinfo/Bediener/Wiedervorlage/Disponent/Dok.Scan/E-Mail; CRUD + Folgekontakt + Filter + WV + erledigt + Verweis öffnen. *(KIM hat ContactHistoryTable + meine Backend-Felder Art/Betreff/Kommentar/CC + contact-docs-Quellen.)*
9. **Untere Beleg-Tabs** (`CustomerDocumentTabs`) — Angebote/Aufträge/Lieferscheine/Kaufangebote/Kaufabrechnungen/Fremdbestände; je Tabelle (Belegnr/Datum/Vertreter/gepl.Lieferdatum/Netto/MwSt/Brutto/erl.). *(KIM hat SalesDocumentsPanel — deckt das ab.)*

## Umsetzungs-Reihenfolge (Claude, nach Codex-Uebernahme)

- **S1 (jetzt):** Backend-Verdrahtung aus KIM-L3-BACKEND-001 ins Cockpit — Kontakt-Log Art/Betreff/Kommentar/CC (Journal §8), **Telefon-Auswahl-Dialog → Dial (§5)**, kim-api `dial`/`notifications`. Playwright-Vertrag auf neue Action-IDs (customer.create/print) ziehen. Grün halten.
- **S2:** Information-Dropdown (§3) mit Subtab-Routing + Placeholder; Ang./Auf.-Dropdown (§6).
- **S3:** Präsente-Tab (§4) inkl. Backend `CustomerGift`.
- **S4:** Ansprechpartner-Vollformular (§7) inkl. Werbe-Matrix + Pseudonymisieren (Backend-Erweiterung).
- **S5:** Action-Bar-Konfigurierbarkeit (§2, benutzerbezogen persistiert).

## Technische Leitplanken
React+TS, vorhandene VALEO-UI/DS-Komponenten, kein neues UI-Framework, Routing stabil, Kunden-ID aus Route/Context, typisierte CRUD-Service-Schicht (kim-api erweitern), Leer-/Lade-/Fehlerzustände, Playwright-E2E für Toolbar/Dropdowns/Tabs/Dialoge/Rücknavigation, kein Button ohne Aktion, fehlendes Backend = Mock/Adapter + TODO.

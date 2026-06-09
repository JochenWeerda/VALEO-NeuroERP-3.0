# KIM-Cockpit ↔ L3-CRM-Referenz — Funktionsabgleich & Bau-Spezifikation (2026-06-09)

Referenz: zvoove L3 „CRM Dashboard" (Screenshot). Ziel: alle dortigen Bedien-Funktionen in das
VALEO-KIM-Cockpit (`/crm`, `packages/frontend-web/src/pages/crm/kim/`) übernehmen.
Legende: ✅ vorhanden · 🟡 teilweise/abweichend · ❌ fehlt.

## Bereich 1 — KUNDE (Aktionsleiste, `CustomerActionBar`)

| L3-Button | Soll | KIM-Ist | Status | To-do |
|---|---|---|---|---|
| Öffnen | Stammdatenmaske Kunde | `openMaster` → Stammdaten-Dialog | ✅ | — |
| Neu | **leere** Stammdatenmaske (Neukunde anlegen) | „Neu" = `activity.create` (Kontaktformular) | ❌ Mismatch | Neuer Button/Aktion „Neukunde" → Kunden-Neuanlage-Maske (leerer Stammdialog bzw. Route) |
| Information | Info-Popup | `infoPopup` Dialog | ✅ | — |
| Präsente | Kalender-Rally/Geschenke-PR | `presents` Dialog | ✅ | — |
| Tel | **TAPI** ausgehenden Call initiieren | `logCall` = manuelles Gesprächs-**Protokoll** | 🟡 | TAPI-Wähl-Call (Bridge `tools/tapi-bridge`) auslösen + danach Log vorbefüllen |
| (E-Mail) | Mailprogramm | `sendEmail` mailto | ✅ | — |
| Ang./Auf. | Angebots-/Auftragsmaske | Navigation `angebot-erstellen` | ✅ | — |
| Faktur | Faktura zum Kunden | Navigation `op-debitoren` | ✅ | — |
| Drucker | Übersicht zum Kunden drucken | — | ❌ | Druck-/Print-Ansicht des Kunden-Cockpits |

## Bereich 2 — ANSPRECHPARTNER (`ContactPersonsTable`)

L3: Tabelle **plus** Aktionsreihe je gewähltem AP: Öffnen · Neu · Telefon · E-Mail · Präsente · Filter
(Filter wenn Business Partner mehrere AP/Abteilungen hat).

| L3 | KIM-Ist | Status | To-do |
|---|---|---|---|
| Tabelle AP inkl. W1–W10 | vorhanden | ✅ | — |
| Neu (AP anlegen) | „Neuer Kontakt"-Formular | ✅ | — |
| Öffnen (AP-Stamm bearbeiten) | — | ❌ | Zeile wählbar → AP-Edit-Dialog |
| Telefon (TAPI an AP) | — | ❌ | TAPI-Call auf AP-Telefon |
| E-Mail (an AP) | — | ❌ | mailto AP |
| Präsente (AP) | — | ❌ | Präsente-Dialog AP-bezogen |
| Filter (AP/Abteilung) | — | ❌ | Filterleiste (z.B. nach Abteilung/Priorität) |
| Zeilenauswahl (selektierter AP) | nur Anzeige | ❌ | `selectedContactId`-State + Row-Selektion |

## Bereich 3 — KONTAKTE (`ContactHistoryTable`)

L3-Tabs: **ÜBERSICHT · HISTORIE · RECHNUNGEN · MAHNUNGEN · KONTRAKTE · STRECKEN-GESCHÄFTE**

| Aspekt | Soll (L3) | KIM-Ist | Status | To-do |
|---|---|---|---|---|
| Tabs | 6 Tabs | identische 6 Tabs | ✅ | — |
| Übersicht/Historie | dokumentierte Kontakte als Liste | vorhanden (Logs) | ✅ | — |
| Neuer Kontakt: **Art** | Dropdown persönlich/Telefon/E-Mail/WhatsApp | freier Präfix-Code | 🟡 | Art-Dropdown mit Enum |
| Richtung | eingehend/ausgehend | vorhanden | ✅ | — |
| Datum | vorbelegt „heute" | vorhanden | ✅ | — |
| Betreff + Kommentar (blob) | Betreffzeile + großes Kommentarfeld | nur Kurzinfo | 🟡 | Betreff + Textarea (Kommentar/blob) |
| Footer: Wiedervorlage | WV-Datum | vorhanden | ✅ | — |
| Footer: **CC** | intern (Mitarbeiter/Abteilung → VALEO-internes Nachrichten/Notiz-System) **oder** extern (Fachberater per E-Mail) | — | ❌ | CC-Auswahl + Benachrichtigungs-Anbindung |
| Footer-Buttons | Öffnen · Neu · **Folgekontakt** · Löschen · **Verweis öffnen** · Filter · Drucker | nur „Aktivität erfassen" | 🟡 | Öffnen/Folgekontakt/Löschen/Verweis öffnen/Drucker ergänzen |
| Tabs Rechnungen/Mahnungen/Kontrakte/Strecken | **echte Beleg-Listen** → Zeile picken → Einzelbeleg öffnen | Logs clientseitig nach Stichwort gefiltert | 🟡/❌ | Reale Belegquellen je Tab + Einzelöffnen |

## Bereich 4 — ANG./AUFT./LIEF./KAUF. (`SalesDocumentsPanel`)

L3-Tabs: ANGEBOTE · AUFTRÄGE · LIEFERSCHEINE · KAUFANGEBOTE · KAUFABRECHNUNGEN · FREMDBESTÄNDE
(Fremdbestände = z.B. gekaufter, noch nicht gelieferter Dünger). Aktionen: Öffnen · Neu · Filter.

| Aspekt | KIM-Ist | Status | To-do |
|---|---|---|---|
| 6 Kategorie-Tabs | identisch vorhanden | ✅ | — |
| Listenanzeige + Spalten | vorhanden | ✅ | — |
| Öffnen (Zeile → Beleg) | „Fachprozess"-Toast (lesend) | 🟡 | Zeile wählen → Beleg öffnen (Route) |
| Neu (Eingabemaske je Beleg) | „Fachprozess"-Toast | 🟡 | „Neu" → Erfassungsmaske je Belegart |
| Filter | „Alle"-Dropdown | ✅ | — |

## Umsetzungs-Schnitt (Vorschlag, Risiko-/Abhängigkeits-sortiert)

**Slice A — Frontend-Quick-Wins (kein/kaum Backend):**
- Kunde „Neukunde" (leere Stammmaske/Route) + Drucker (Print-Ansicht).
- Ansprechpartner-Aktionsreihe (Öffnen/Telefon/E-Mail/Präsente/Filter) + Zeilenauswahl.
- Kontakte: Art-Dropdown, Betreff+Kommentar, Footer-Buttons (Öffnen/Folgekontakt/Löschen/Verweis öffnen/Drucker).
- ANG/AUFT: Öffnen→Beleg-Route, Neu→Erfassungsmaske-Route.

**Slice B — TAPI-Wählfunktion:** Kunde „Tel" + AP „Telefon" lösen ausgehenden Call über `tools/tapi-bridge` aus und befüllen anschließend das Kontakt-Log vor.

**Slice C — Kontakte-Belegtabs mit echten Quellen:** Rechnungen/Mahnungen/Kontrakte/Strecken aus den kanonischen Endpoints (Faktura/OP, Dunning, Kontrakte, Streckengeschäfte) als Listen + Einzelöffnen.

**Slice D — CC/Benachrichtigung:** internes Nachrichten-/Notizsystem (Mitarbeiter/Abteilung) + externer Fachberater (E-Mail). Erfordert Backend-Design (internes Messaging-Modell) → eigener Slice.

**Persistenz-Erweiterung** (für Slice A/D): Kontakt-Log-Felder `art`, `betreff`, `kommentar` (Text), `cc_intern`, `cc_extern` ergänzen (Satelliten-/Tabellen-Erweiterung gemäß DB-Identitäts-Standard).

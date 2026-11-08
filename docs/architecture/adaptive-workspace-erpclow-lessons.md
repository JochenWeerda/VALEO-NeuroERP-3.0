---
title: Adaptive Workspace — Lessons aus ERPClaw / ERPNext (Frappe Desk)
type: research
audience: [architect, agent, produkt, design]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-22
version: 1.0.0
description: Research-only. Was "erpclow" meint; welche Desk-/Workspace-Muster VALEO Adaptive Workspace aus ERPNext/Frappe und ERPClaw übernehmen darf — und was zu verwerfen ist.
---

# Adaptive Workspace — Lessons aus ERPClaw / ERPNext

**Stand:** 2026-10-22. Nur Dokumentation. Kein Produktcode, keine Launchpad-Änderungen, keine ScreenDefinitions, kein MCP-YAML, kein Workboard.

**Auftrag:** User-Schreibweise `erpclow/ERPNext` für VALEO Adaptive Workspace klären und in Meridian / Studio / MCP-WRITE / Mandanten übersetzen.

**Für den Lead (Phase 1):** Abschnitt 5. Diese Datei ändert keine Startseite.

---

## 1. Was „erpclow“ im Kontext wahrscheinlich ist

Im Repo `VALEO-NeuroERP-3.0` gibt es **keine** Treffer für `erpclow`, `ERPNext` oder `Frappe` (Stand 2026-10-22, Suche in Code und Doku). Es ist also **kein** VALEO-interner Codename, Slice oder Fork.

Öffentlich und fachlich passen drei Lesarten. Die erste ist die tragfähige.

### 1.1 Wahrscheinlich: Tippfehler für **ERPClaw** plus Vergleichsobjekt **ERPNext**

`erpclow` liegt eine Taste neben `erpclaw`. Öffentlich ist **ERPClaw** (Marke, Repo, Vergleichsseite) ein 2026 erschienenes, chat-first Open-Source-ERP, das sich ausdrücklich gegen ERPNext/Frappe positioniert.

| Signal | Befund |
|---|---|
| Schreibweise | `erpclow` ≈ `erpclaw` (ein Buchstabe) |
| Slash-Form `erpclow/ERPNext` | entspricht dem öffentlichen Vergleich „ERPNext vs ERPClaw“ |
| Produkt | [erpclaw.ai](https://www.erpclaw.ai/), Repo [github.com/avansaber/erpclaw](https://github.com/avansaber/erpclaw) |
| Companion-UI | [github.com/avansaber/erpclaw-web](https://github.com/avansaber/erpclaw-web) — Browser-Dashboard **neben** Chat, nicht statt Chat |
| MCP | SKILL.md deklariert stdio-Tools `erpclaw_list_actions`, `erpclaw_describe_action`, `erpclaw_action` — Transport über eine Action-Schicht, nicht ORM |
| Kernclaim | „AI-native“: Aktionsschicht ist die API; Desk/Formulare sind optional |

Das erklärt, warum der Auftrag **Workspace-Muster** von ERPNext/Frappe Desk verlangt und gleichzeitig ERPClaw im Namen steht: ERPClaw liefert die *Aktion/Agent*-Folie, ERPNext/Frappe Desk die *Arbeitsplatz*-Folie.

### 1.2 Mitgemeint (fachlich die stärkere Workspace-Quelle): **ERPNext / Frappe Desk**

ERPNext ist das produktive Open-Source-ERP auf dem Frappe Framework. Nach Login landet ein System User auf **Desk** (`/desk`): eine SPA, die **List/Form/Report/Kanban** aus **DocType-Metadaten** erzeugt. Navigation läuft über **Workspaces**, globale Suche über die **AwesomeBar**, Arbeit über **ToDo/Assignment** und **Notification Log**.

Offizielle Quellen:

- [Desk](https://docs.frappe.io/framework/user/en/desk)
- [Workspaces](https://docs.frappe.io/framework/user/en/desk/navigation/workspace)
- [Workspace-Blöcke](https://docs.frappe.io/framework/user/en/desk/workspace/blocks)
- [AwesomeBar](https://docs.frappe.io/erpnext/awesomebar-global-search)
- [Notifications](https://docs.frappe.io/erpnext/notifications)
- Bootinfo: `frappe/boot.py` → `get_bootinfo()`, Client `frappe.boot` (Session, Rollen, Module, Workspaces, Navbar, ungelesene Notifications)

Das ist der relevante Desk-Kontrakt für Adaptive Workspace — nicht Frappe als Runtime.

### 1.3 Unwahrscheinlich / verworfen als Primärlesart

| Lesart | Warum nicht |
|---|---|
| GitHub-User/Repo `erpclow` | öffentlich kein relevantes Repo; Treffer führen auf ERPClaw |
| „ERP Cloud“ (SAP/Oracle SaaS) | zu generisch; erklärt Desk/AwesomeBar/ToDo nicht |
| VALEO-interner Codename | Repo-Suche leer; Adaptive Workspace selbst ist im Repo noch kein benanntes Artefakt |
| Frappe Cloud Hosting | Hosting-Produkt, kein Workspace-Modell |

### 1.4 Arbeitsannahme für den Rest dieses Dokuments

> **erpclow/ERPNext** = Research-Paar **ERPClaw (Aktion/Agent)** × **ERPNext/Frappe Desk (Arbeitsplatz)**. VALEO übernimmt Muster, nicht Stack. Vergleichsachsen SAP Fiori Launchpad und (nur wo nötig) Odoo Systray.

---

## 2. Übernahme-Empfehlungen (passend zu Meridian, Studio, MCP-WRITE, Mandant)

Leitplanke: Meridian bleibt der Vertrag der **Maske** (`ScreenDefinition → RenderPlan → UniversalMaskRuntime → UniversalMaskRenderer`). Adaptive Workspace ist der **Einstieg und die globale Kommandoebene**, nicht ein zweites Maskensystem. MCP bleibt Transport; Schreiben nur über versionierte Domain-Commands ([MCP-WRITE](mcp-write-standard.md)). Mandant kommt aus vertrauenswürdiger Authentifizierung, nie aus der Suchzeile.

### 2.1 Frappe Workspace vs. App-Kacheln

**Was Frappe tut.** Ein Workspace ist **keine** App-Galerie. Es ist eine **team-/modulbezogene Landeseite** aus Blöcken: Shortcuts (Liste, Report, Dashboard, **Neu**-Form, optional **Live-Count**), Link-Karten, Number Cards, Charts, Quick Lists, Onboarding. Sichtbarkeit: zuerst Modulrecht, dann Workspace-Rollen, dann Block-Rechte. Public vs. private („Only to you“ / My Space). Standard-Workspaces einer App bleiben vom Vendor; Site-Änderungen liegen als Customization daneben, mit **Reset to Standard**.

**Was VALEO schon hat.** Launchpad-Spaces sind **Arbeitswelten**, nicht Module ([launchpad-spaces.md](../design/launchpad-spaces.md)). Pages sind Aufgabenräume. Kacheln dürfen `app | task | kpi | alert` sein. Personalisierung ist ein Overlay über den Katalog, nicht die ScreenDefinition.

**Übernahme (Muster, nicht UI).**

1. **Page = Workspace, nicht App-Verzeichnis.** Eine Page beantwortet „Was kann ich hier tun?“ und „Was ist jetzt wichtig?“. App-Kacheln sind der Rest, der nicht in Suche/Finder liegt.
2. **Shortcut mit Count-Filter** (Frappe) → VALEO **Task-/Alert-Kachel mit echter Queue-Zahl** (offene Wiedervorlagen, überfällige Lieferungen, PSM-Fristen). Keine dekorativen KPI-Kacheln ohne Quelle.
3. **Public Catalog vs. Private Overlay** beibehalten: Katalog in `launchpad-spaces.ts` (Lead-Besitz); Overlay lokal (`valeo.launchpad.overlay`). Später mandantenscope Server-Overlay, nicht hartcodierte Kundenskins.
4. **Reset to Standard** analog: Katalogseite zurücksetzen / ausblenden existiert bereits; erste Page einer Arbeitswelt bleibt gesperrt. Das ist das Frappe-Muster, schon VALEO-konform.
5. **Nicht** Frappe-Blöcke (Custom HTML, Chart-Widgets, Onboarding-Checklisten) auf die Startseite ziehen. Charts und KPIs gehören in Auswertungs-Floorplans (`analyticalList` / Cockpit), nicht in den Einstieg.

### 2.2 AwesomeBar vs. Command Center auf Fachaktionen

Frappe AwesomeBar (`Ctrl/Cmd+K`): DocType-Liste, **New**, Report, Page/Workspace, globale Datensatzsuche. Rechte filtern Treffer. Kein freies SQL.

VALEO hat **kein** Artefakt namens Command Center. Die Fläche heißt **Command Palette** (`packages/frontend-web/src/components/navigation/CommandPalette.tsx`) plus Omnibox (UIX-060/070): Navigation, Masken-Registry, globale Suche, VoiceBar. `detectCommandIntent` erkennt Verben, erzeugt `navigate` / `formPrefill` / `commandDraft`. **Kein Auto-Submit.** `high`/`critical` → nur Navigation; `forbiddenForAgents` → gar nicht.

ERPClaw geht weiter: Chat ruft **jede** Action. Das ist für VALEO der **falsche Primärkanal**. Facharbeit bleibt in der Maske (Meridian). Die Bar ist Beschleuniger.

**Übernahme.**

1. AwesomeBar-Ergebnisarten auf VALEO mappen, ohne neue SPA:

   | Frappe | VALEO-Phase 1 |
   |---|---|
   | List | Navigation auf Worklist-ScreenDefinition |
   | New | Prefill/Draft der Create-Aktion der Zielmaske, Confirmation in der Maske |
   | Report | Navigation auf freigegebene Auswertung |
   | Workspace/Page | Navigation auf Launchpad-Space/Page |
   | Search for | `globalSearch`, mandantengebunden |

2. **Fachaktionen in der Palette nur aus dem bestehenden Register:** ScreenDefinition-Actions, Mask-Registry, MCP-Capability. Identische Commands wie REST/UI (MCP-WRITE-015).
3. Risikoklassen: Palette darf R0 (öffnen/suchen) und vorbereitete R1-Drafts. R2 nur mit Masken-Confirmation. R3/R4 nie aus der Bar abschließen.
4. ERPClaw-MCP-Idee `list_actions` / `describe_action` / `action` ist ** palettentauglich**, wenn `action` VALEO-Domain-Commands mit Idempotenz, Tenant-Claim und Freischaltung ist — nicht `db_query.py`.

### 2.3 ToDo / Notification als proaktive Ebene

Frappe: Zuweisung eines Belegs erzeugt ToDo + System-Notification. Notification-DocType überwacht New/Save/Submit/Days Before. Dropdown oben rechts. Klick öffnet das Dokument.

Odoo Systray (Activities-Uhr, Messaging) ist dasselbe Bedürfnis mit anderer Chrom-Sprache. VALEO braucht **kein** Discuss/Chatter-Port. Die TopBar hat bereits `NotificationCenter`. Launchpad-IA verlangt bereits „Meine Aufgaben / Wiedervorlagen“ als dritten Kunden-Einstieg und ein operatives „Heute“ **mit echten Quellen** ([launchpad-informationshierarchie.md](../design/launchpad-informationshierarchie.md)).

**Übernahme.**

1. Startseite und globale Ebene **Aufgaben** speisen sich aus denselben Worklists wie die Fachmasken (Wiedervorlage, Freigabe, überfällige Lieferung) — nicht aus einem zweiten ToDo-DocType.
2. Notification-Center: Zuweisung, Erwähnung, Freigabe, Frist. Klick öffnet die Object Page / Transaction, nicht eine interne Log-Maske.
3. ProcessBand bleibt am **Beleg** (eine nächste Aktion, Blocker). Die Startseite zeigt **Ausnahmen über Belege hinweg**. Das ist Frappe-ToDo-Inbox, nicht Frappe-Form-Timeline.

### 2.4 Desk-Bootstrap über Metadaten

Frappe injiziert `bootinfo` vor dem ersten Paint: User, Rollen, Defaults, Module, Workspaces, Navbar, Notification-Count, erlaubte Views. Desk rendert danach **generisch** aus DocType-Meta. Keine kundenspezifische SPA.

VALEO hat die Stücke, aber nicht als **einen** Workspace-Boot:

| Frappe bootinfo | VALEO-Ist |
|---|---|
| `user` / roles | OIDC + Fachrollen |
| `modules` / workspaces | `launchpad-spaces` + Nav-Manifest + Feature-Flags |
| DocType Meta | ScreenDefinition + RenderPlan |
| Navbar / notifications | TopBar, NotificationCenter |
| Permissions | RBAC/ABAC, MCP-Scopes, `X-Tenant-ID` aus Claim |

**Übernahme.** Ein **Workspace-Boot-Vertrag** (JSON, tenant- und rollengebunden): erlaubte Spaces/Pages, erlaubte Palette-Commands (Capability-IDs), ungelesene Aufgaben/Notifications, Feature-Flags. Studio erzeugt ScreenDefinitions; der Boot **listet** sie, erfindet sie nicht. Kein Frappe-`boot.py`-Port, kein Python im Frontend.

Studio-Regel bleibt: Agent beschreibt Fachsprache → Semantic Catalog → ScreenDefinition. Kein SQL, keine Tabellen namen, keine zweite Builder-Kette ([studio-semantic-standard.md](studio-semantic-standard.md)).

### 2.5 SAP Fiori Launchpad Groups/Spaces vs. VALEO Launchpad-Spaces

VALEO hat Spaces/Pages **bereits als Informationsarchitektur** übernommen, ausdrücklich nicht als visuelle Kopie. SAP selbst hat Groups zugunsten Spaces/Pages abgelöst (S/4HANA Cloud Public Edition ab 2408; Classic Homepage outdated). Best Practice dort: My Home entschlacken, gelieferte Spaces nutzen, Personalisierung ist nutzerspezifisch.

**Übernahme.**

1. Nicht zu Groups zurück. VALEO-Pages sind Fiori-Pages; „Gruppen“ im Anpassen-Modus sind Pages.
2. Catalog / Target Mapping ≈ Navigationskatalog + Masken-Registry. Kachel startet eine ScreenDefinition-Route, keinen Transaktionscode.
3. Personalisierung bleibt Overlay. Kein SAP-Aktionsblatt, keine Belize-Farben, keine Statusfarbe als Dekoration.
4. Fiori „To-Dos auf My Home“ stützt Abschnitt 2.3: Aufgaben vorn, nicht acht weitere App-Kacheln.

### 2.6 Odoo Systray — nur dieser Satz

Relevant ist allein das **dauerhafte Aufgaben-/Nachrichten-Icon** mit Count. VALEO hat NotificationCenter in der TopBar und eine globale Ebene „Aufgaben“. **Nicht** übernehmen: Discuss, Chatter als Produktvertrag, OWL-Systray-Registry, Messaging-Menü als zweite Inbox.

---

## 3. Explizit verwerfen

Diese Liste ist verbindlich für Adaptive Workspace. Abweichung wäre ein neuer Architektur-Claim, nicht eine stille Übernahme.

| # | Verwerfen | Begründung |
|---|---|---|
| 1 | **Frappe-Port** (Bench, Desk-SPA, DocType-Runtime, MariaDB+Redis+Node+Nginx) | VALEO hat FastAPI, PostgreSQL, React, ScreenDefinition. Zweiter Framework-Kern sprengt Mandant, Audit, Studio. |
| 2 | **Python-Frontend** | Meridian/Studio sind TypeScript-React. Python bleibt Backend. |
| 3 | **Zweite App** (ERPClaw-Web neben Chat, Frappe Desk neben VALEO-Shell, paralleler MaskBuilder) | Eine Shell, eine Runtime-Kette. Companion-Dashboards erzeugen Drift. |
| 4 | **Beliebige ORM-/Tabellen-Calls aus der Bar** | MCP-WRITE-001/002: nur registrierte Domain-Commands. ERPClaw `db_query.py --action` ist nicht das Vorbild für die Palette. AwesomeBar sucht Metadaten und Datensätze, sie schreibt nicht frei. |
| 5 | **Hartcodierte Kundenskins** | Katalog + Overlay + Rollen. Keine Fork-CSS je Mandant, kein Custom-HTML-Workspace-Block als Produktweg. |
| 6 | **Chat-first als Primär-UX** (ERPClaw-Kernclaim) | Landhandel-ERP ist masken- und belegzentriert. Agent ist Kanal auf denselben Commands, nicht Ersatz der Object Page. |
| 7 | **SQLite local-first / Single-file-ERP** | VALEO-Prüfstand und Produktion sind PostgreSQL, mandantenisoliert. |
| 8 | **Multi-company in einer DB als Mandantenmodell** (ERPClaw-Zeile) | VALEO: Tenant aus Token/`X-Tenant-ID`, MCP-WRITE-003, ADR-013/034. Header gewähren keine Rechte. |
| 9 | **SKILL.md generiert Python als Studio-Modell** | Studio erzeugt ScreenDefinitions aus dem Semantic Catalog, keinen Modulcode. |
| 10 | **ProcessBand und ProcessRibbon zusammenlegen**, weil Desk eine Form-Timeline hat | Band = Vorgangsstand; Ribbon = Belegkette. Unverändert ([beleg-maskenfamilie-vererbung.md](uix/beleg-maskenfamilie-vererbung.md)). |

---

## 4. Mapping auf VALEO-Ist (nur gelesen)

Adaptive Workspace ist im Repo **noch kein** benanntes Lieferartefakt. Der Ist-Stand sitzt in Launchpad, Palette, Meridian und MCP.

### 4.1 Launchpad-Spaces und Personalisierung

- Katalog: `packages/frontend-web/src/app/navigation/launchpad-spaces.ts` — Spaces als Arbeitswelten (Handel & CRM, Ernte, Lager, Betriebsmittel, Finanzen, Steuerung). Max. 10 Kacheln/Page. Tile-Kinds `app`/`task`/`kpi`/`alert`.
- Overlay: `launchpad-personalization.ts`, Key `valeo.launchpad.overlay` in `localStorage`. Verstecken, Reihenfolge, Labels, Custom Pages. **Nicht** in der ScreenDefinition.
- Doku: [launchpad-spaces.md](../design/launchpad-spaces.md), [launchpad-informationshierarchie.md](../design/launchpad-informationshierarchie.md). Sprints 1–3 der Hierarchie sind dokumentiert als umgesetzt; operatives „Heute“ ohne echte Quellen **nicht** gebaut.
- Flow-Spine-Routen sind vom Launchpad ausgeschlossen. Vorgangsstand bleibt am Beleg.

**Gap zu Frappe Workspace:** Counts auf Shortcuts/Task-Kacheln sind noch nicht die Regel. Overlay ist gerätelokal, nicht mandantenserver-seitig. Custom HTML/Charts auf der Startseite bewusst abwesend (behalten).

### 4.2 Command Palette / Omnibox

- `CommandPalette.tsx` + `command-palette-model.ts`: Navigation, Shortcuts, Mask-Registry, Omnibox-Katalog.
- UIX-070: Verb → Draft/Prefill/Navigate; Sicherheitsmatrix in `command-safety.ts` / ActionRuntime. Kein Auto-Submit.
- MCP-Metadaten an der Palette beschreiben heute **Navigation**, nicht Schreib-Capabilities.
- Parallel existieren ältere Paletten (`components/command/`, `components/innendienst/`) — für Adaptive Workspace nicht als zweite Wahrheit nutzen.

**Gap zu AwesomeBar:** „New X“ und Datensatzsuche sind angelegt, aber die Palette ist noch navigationslastig. Fachaktionen R1 müssen aus dem **Capability-Register** kommen, nicht aus hartcodierten `BASE_COMMANDS`.

### 4.3 ProcessBand vs. ProcessRibbon vs. Startseite

| Fläche | Aufgabe | Darf Adaptive Workspace? |
|---|---|---|
| ProcessBand | Stand **eines** Vorgangs, eine nächste Aktion, Blocker | Nein — bleibt in der Maske |
| ProcessRibbon | Navigation der **Belegkette** | Nein — bleibt Belegfamilie |
| Launchpad / Aufgaben | Ausnahmen **über** Vorgänge | Ja — Inbox, Counts, Drilldown auf die Maske |

Frappe Form Timeline und Odoo Chatter gehören **nicht** auf die Startseite.

### 4.4 Studio ScreenDefinition

Meridian: `ScreenDefinition.layout` trägt Floorplan, Density, Context Rail, Table Profile. GeneratorReady nur bei vollständigen Metadaten. Studio-Dialog erzeugt prüfbare SDs aus Fachsprache, nicht aus SQL.

**Gap zu Frappe Desk-Meta:** Frappe erzeugt List/Form aus DocType. VALEO erzeugt Masken aus SD. Der Workspace darf nur auf **freigegebene, runtime-wired** ScreenDefinitions verlinken. Studio bleibt Authoring, Launchpad bleibt Einstieg.

### 4.5 MCP-WRITE und Mandant

- Schreiben: Capability Registry, versionierte Commands, Idempotenz, expected_version, Audit, Outbox. Writes default off, Freischaltung pro Rolle.
- Mandant: Token-Claim; Header-Mismatch 403; keine Tenant-Overrides in Payloads ([mcp-tenant-isolation-read-write-20261009.md](../quality-assurance/mcp-tenant-isolation-read-write-20261009.md)).
- Agent-Kanal: wenige Tools, fast nur Lesen; Schreiben mit Human Approval ([uix-anwender-bedienwege.md](../design/uix-anwender-bedienwege.md)).

ERPClaw „jede Action aus dem Chat“ ist mit MCP-WRITE-014 unvereinbar, solange Capabilities nicht abgenommen sind. Die Palette erbt dieselbe Sperre.

### 4.6 NotificationCenter

`TopBar` lädt `NotificationCenter`. Das ist die Systray-Analogie. Inhaltlich muss es an Fachereignisse (Zuweisung, Freigabe, Frist) angeschlossen werden, nicht an UI-Toasts.

---

## 5. Konkrete, priorisierte Übernahme-Liste für den Lead (Phase 1)

**Phase-1-Ziel:** Adaptive Workspace als **Vertrag** über dem bestehenden Launchpad und der bestehenden Palette — ohne Frappe-Port, ohne zweite App, ohne dass dieser Research-Slice Launchpad-Dateien anfasst.

Der Lead (Dateibesitz Launchpad/Palette) entscheidet die Code-Schnitte. Reihenfolge bindend.

| Prio | Übernahme | VALEO-Anker | Nicht tun | Abnahme |
|---|---|---|---|---|
| **P1** | **Palette = AwesomeBar auf Fachaktionen.** Ergebnisarten List / New / Search / Workspace. New und Draft nur aus ScreenDefinition-Actions + Capability-IDs. R3/R4 nur Navigation zur Maske. | `CommandPalette.tsx`, `command-palette-model.ts`, `command-safety.ts`, MCP-WRITE-015 | ORM aus der Bar; Auto-Submit; zweite Palette | Ctrl+K: „neuer Auftrag“ öffnet Create-Flow der SD mit Prefill; Storno erscheint nur als Navigation; Tenant-Mismatch 403 |
| **P2** | **Page als Workspace mit Task/Alert-Counts.** 6–10 Kacheln; Counts aus echten Worklists (Aufgaben, Freigaben, überfällige Lieferungen). App-Kacheln in den Finder. | `launchpad-spaces.ts` Tile-Kinds, Informationshierarchie Sprint „Heute“ | Neue App-Kacheln; Fake-KPIs; Custom-HTML-Blöcke | Eine Page zeigt Arbeit, nicht ein zweites Menü; Count = dieselbe Query wie die Ziel-Worklist |
| **P3** | **Workspace-Boot-Vertrag.** Ein GET: Spaces/Pages der Rolle, erlaubte Command-IDs, unread Aufgaben/Notifications, Flags. Mandant nur aus Claim. | Session/OIDC, Mask-Registry, Launchpad-Katalog | `frappe.boot`-Klon; Python im Client; Kundenskin im Boot | Zwei Rollen, zwei Boots; fremder Tenant leer/403; Palette zeigt nur Boot-Commands |
| **P4** | **Proaktive Ebene.** Globale „Aufgaben“ + NotificationCenter speisen sich aus Zuweisung/Frist/Freigabe. Klick → Object Page. Startseite darf diese Inbox zeigen, nicht den Vorgangsstand. | TopBar NotificationCenter, Kachel `meine-aufgaben`, ProcessBand unangetastet | Frappe-ToDo-DocType; Odoo Chatter; ProcessBand auf der Startseite | Eine Wiedervorlage erscheint in Inbox und in der Belegmaske; Band nur in der Maske |
| **P5** | **Catalog vs. Overlay härten.** Katalog bleibt Source of Truth (Spaces/Pages). Overlay bleibt nutzerspezifisch. Reset to Standard behalten. Server-Overlay nur als Folgeclaim (tenant-scoped), nicht in Phase 1 Pflicht. | `launchpad-personalization.ts`, Handshake Katalog 2026-09-17 | Hartcodierte Mandanten-Skins; Overlay in ScreenDefinition | Anpassen ändert nur Overlay; Katalog-Reset stellt Vendor-Page wieder her |

### Phase 1 ausdrücklich nicht

- Launchpad-Look Fiori/Frappe/Odoo.
- ERPClaw-Chat als Home.
- Studio-Änderungen außer: SD-Actions müssen palette-fähig **beschreibbar** sein (Capability-ID, dangerLevel, forbiddenForAgents) — das ist Contract-Hygiene, kein neuer Builder.
- Workboard-/MCP-YAML-Edits durch den Research-Slice.

### Abhängigkeiten, die der Lead klären muss (kein Besitz dieses Slices)

1. Wer den Workspace-Boot-Endpoint baut (Backend-Session vs. bestehendes Mask-Registry-API).
2. Welche Worklists als erste Count-Quellen gelten (Aufgaben, AP-Freigabe, Disposition).
3. Ob das Launchpad-Overlay in Phase 1 lokal bleibt (empfohlen) oder mandantenserver-seitig wandert.

---

## 6. Kurz: Top 5 Übernahmen / Top 5 Ablehnungen

**Übernehmen**

1. Workspace-Page mit Shortcuts+Counts statt App-Galerie.
2. AwesomeBar-Ergebnisarten auf der bestehenden Command Palette, Fachaktionen nur aus SD/Capability, kein Auto-Submit.
3. Aufgaben/Notifications als proaktive Ebene mit Drilldown auf die Maske.
4. Ein metadatengetriebener Workspace-Boot (Rolle, Mandant, erlaubte Commands).
5. Fiori Spaces/Pages als IA — VALEO-Katalog plus Overlay, Reset to Standard.

**Ablehnen**

1. Frappe-Port / Desk als zweite SPA.
2. Python-Frontend.
3. Zweite App (ERPClaw-Web, paralleler Builder).
4. Beliebige ORM-Calls aus der Bar oder Chat-first als Primär-UX.
5. Hartcodierte Kundenskins, Custom-HTML-Workspaces, SQLite-local-first, Tenant aus der Suchzeile.

---

## Quellen

### Öffentlich

- [ERPNext vs ERPClaw](https://www.erpclaw.ai/blog/erpnext-vs-erpclaw-honest-comparison/)
- [ERPClaw Repo](https://github.com/avansaber/erpclaw), [SKILL.md](https://github.com/avansaber/erpclaw/blob/main/SKILL.md), [erpclaw-web](https://github.com/avansaber/erpclaw-web)
- [Frappe Desk](https://docs.frappe.io/framework/user/en/desk), [Workspaces](https://docs.frappe.io/framework/user/en/desk/navigation/workspace), [Blocks](https://docs.frappe.io/framework/user/en/desk/workspace/blocks), [AwesomeBar](https://docs.frappe.io/erpnext/awesomebar-global-search), [Notifications](https://docs.frappe.io/erpnext/notifications)
- Frappe Bootinfo: `frappe/boot.py` `get_bootinfo()`; Übersicht [Bootinfo and Client Initialization](https://deepwiki.com/frappe/frappe/5.5-bootinfo-and-client-initialization)
- SAP: [Personalizing the SAP Fiori Launchpad](https://learning.sap.com/learning-journeys/get-started-with-in-app-extensibility-in-sap-s-4hana/personalizing-the-sap-fiori-launchpad_ea1d4d05-171d-44f3-aac1-ddb846bbc522); Spaces statt Groups (S/4HANA Cloud 2408)
- Odoo: [Activities](https://www.odoo.com/documentation/19.0/applications/essentials/activities.html) — nur Systray-Analogie

### VALEO (gelesen, nicht geändert)

- [launchpad-spaces.md](../design/launchpad-spaces.md)
- [launchpad-informationshierarchie.md](../design/launchpad-informationshierarchie.md)
- [valeo-meridian-experience.md](../design/valeo-meridian-experience.md)
- [studio-semantic-standard.md](studio-semantic-standard.md)
- [mcp-write-standard.md](mcp-write-standard.md)
- [beleg-maskenfamilie-vererbung.md](uix/beleg-maskenfamilie-vererbung.md)
- [uix-anwender-bedienwege.md](../design/uix-anwender-bedienwege.md)
- Code (read-only): `launchpad-spaces.ts`, `launchpad-personalization.ts`, `CommandPalette.tsx`, `command-palette-model.ts`, `command-safety.ts`, `notification-center.tsx`

### Repo-Suche

- `erpclow`, `ERPNext`, `Frappe`: 0 Treffer
- Adaptive Workspace: 0 Treffer vor dieser Datei

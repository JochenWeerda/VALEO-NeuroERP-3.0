---
title: Made by Studio — Qualitätsversprechen
type: reference
audience: [agent, entwickler, qa, produkt]
owner: Cursor Composer
status: aktiv
last_reviewed: 2026-10-22
version: 1.0.0
description: Verbindlicher Nachweis-Katalog — wann eine Maske das Qualitätskennzeichen „made by studio“ tragen darf.
---

# Made by Studio — Qualitätsversprechen

„Made by studio“ ist **kein Draft-Zähler** und kein reiner Import. Es ist ein
Qualitätsversprechen: Definition, Freigabe, Runtime und sichtbare Bedienung sind
nachgewiesen. Studio-Import (Stufe B) allein ersetzt keine Runtime-Verdrahtung
(Stufe C). Siehe auch [Beleg-Familienstufen](beleg-maskenfamilie-vererbung.md) §5
und [Taxonomie](maskenfamilien-taxonomie.md) §1.4.

Bezug Freigabestandard: [STUDIO-RELEASE-001](../studio-release-standard.md).
Bezug Entity-Profil: [studio-entity-release-20261021](../../quality-assurance/studio-entity-release-20261021.md).

## Gate-Checkliste (alle müssen grün)

### A — Definition & Vertrag

- [ ] ScreenDefinition aus Studio-/Meridian-Governance (kein Parallel-FormBuilder als „Studio“).
- [ ] Revisionsgebundene Historie (Actor, Zeit, Status, Definitionshash).
- [ ] AgentMaskContract / Readiness ohne Ausnahme; Aktionen mit Rechte-Deklaration aus Backend-Rollen.
- [ ] Prozessprofil gebunden (`grain.v1` lesend Agrar **oder** `studio.entity.v1` registrierte Stammdaten — kein Profil-Mixing).

### B — Freigabekette (CLI + Server)

- [ ] CLI-Lebenszyklus: Übernahme → Prüfung → Plan speichern → Simulation → Vier-Augen-Freigabe → (optional) Rücknahme.
- [ ] Simulation auf gemeinsamem `valeo_probe`, echte Domain-Commands, Rollback/Nachkontrolle ohne Restwirkung.
- [ ] Freigabe an unveränderte Kandidatenrevision + Artefakthash; Eigenfreigabe gesperrt.
- [ ] Router akzeptiert keine nachträglich geänderte Impl. als geprüft (Neustart-Grenze).

### C — Runtime

- [ ] Nutzerroute → `UniversalNative*Page` / ListPage → freigegebene Screen-ID (Inventar: `runtime_wired`).
- [ ] Commands/Datenwege Human = CLI = MCP (gleiche Rechte/Mandant); keine Stub-Wirkung.
- [ ] Gegenueber dem abgeloesten Vorgaenger: keine Funktionsverluste und keine fehlenden Datenfelder (Create/Edit/Aktionen); Paritaet ist Abnahmekriterium, nicht optional.
- [ ] Tabellenkatalog / Runtime-Catalog im Image/Dev-Deploy vorhanden (Compiler-Pflicht).

### D — Browser / Image (sichtbarer Nachweis)

- [ ] Reale SSO-Bedienung der **publizierten** Maske (nicht nur Studio-Editor-Vorschau).
- [ ] Hell- und Dunkelmodus ohne Theme-Bruch; Screenshots im Handbuch/QA.
- [ ] Image-/CI-Nachlauf mit kanonischem `table-catalog.json` grün (kein nur-lokaler Vite-Beweis).

### E — Ablösung (erst danach „Familie fertig“)

- [ ] Primärnav zeigt Runtime-Route; Legacy nur Rollback (UIX-057) bis Abnahme.
- [ ] Create/Edit-Parität dokumentiert oder geschlossen — Create-Legacy zählt nicht als Ablösung.
- [ ] Kein Anspruch „alle Masken“, solange nur ein Profil/eine Familie belegt ist.

## Was ausdrücklich nicht reicht

| Scheinbeleg | Warum unzureichend |
|---|---|
| Studio-Draft / Native-Import | Keine Aktivierung, keine Fachwirkung |
| Nur Generator-/Unit-Grün | Fehlt Live-Freigabe + Browser |
| Nur grain.v1-Lesekette | Deckt kein Stammdaten-/Belegschreiben |
| Inventar „X Drafts“ | Draft ≠ `runtime_wired` |
| Theme-Vorschau ohne Publikation | Kein Freigabenachweis |

## Aktueller Belegstand (2026-11-25, Europe/Berlin)

Bezug: PR #213 / `cursor/studio-made-open-routes-8809`; Generator-Report
[`made-by-studio-gate-report.md`](made-by-studio-gate-report.md); Inventar
`mask_route_migration_inventory.py`.

| Gate | Stand | Hinweis |
|---|---|---|
| A Entity-Stammdaten | **829/829** | `verify_made_by_studio_gates.py` — Meridian/Struktur grün |
| B Entity CLI-Freigabe / Rechte | **829/829** | Action-Permission-Projektion; Draft-clean |
| C Runtime Entity / Compiler | **829/829** | OpenAPI-Kanal + Advisory Ø **1.0** |
| D Browser publiziert | **Teilbeleg** | Playwright Cockpit-Smoke **502/502** (251 Masken × Hell/Dunkel; inkl. Compliance/FiBu/Controlling/Fuhrpark/Agrar/Finance-Listen-Ausbau; Specialized Landmark/Tablist, Mock-Auth); FlowSpine/Feed/Calendar/Chart/TileGrid/TwinPanel/Finance-Reports theme-tokenisiert; **Live-SSO** und Image-CI `table-catalog` weiter offen (Codex `STUDIO-ENTITY-RELEASE`) |
| E Ablösung | **829/829** + Routen-`hand_built` **0** | Runtime-Aliase verdrahtet; `pages_hand` ≈38 bewusst (`*-legacy`/Dlg/Charts, keine Routen) |

**Fazit:** A/B/C/E und Routen-Migration sind generatorseitig grün. Das Siegel A–D
pro Maske braucht weiterhin Live-SSO + Image-CI (Gate D Rest). Systemweites
„alle Masken made by studio“ bleibt Ziel, kein Ist-Zustand.

## Nächster Nachweis-Schritt (eine Lücke)

1. Image-/CI-Nachlauf mit Runtime-Catalog (schließen D für Entity-Profil) — Codex `STUDIO-ENTITY-RELEASE`.
2. Live-SSO-Bedienung + Theme-Screenshots der *publizierten* Maske (Theme-Smoke mit Mock-Auth ersetzt das nicht).
3. Beleg-Parent nur nach Codex-Handshake.

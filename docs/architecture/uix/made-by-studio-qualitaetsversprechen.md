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

## Aktueller Belegstand (2026-10-22)

| Gate | Stand | Hinweis |
|---|---|---|
| A Entity-Stammdaten | weitgehend | Compiler/Profil/Rechte-Projektion auf main (`431cd5f66`+) |
| B Entity CLI-Freigabe | weitgehend | SQL/CLI-Kette + Live-Probe dokumentiert; Image-CI-Nachlauf offen |
| C Runtime Entity | teilweise | Generierte CRUD/Listen verdrahtet; Massen-Altmasken offen |
| D Browser publiziert | **offen / Teil** | SSO+Dark Editor belegt; vollständige Live-Entity-Freigabe-UI + Image noch Pflicht |
| E Ablösung | offen | 757 handgebaut; Nav-Pilot Saatgut/Dünger/Lieferant/Bestellung Detail |

**Fazit:** Das Qualitätskennzeichen darf **pro freigegebener Maske/Familie** vergeben
werden, sobald A–D für diese Maske grün sind. Systemweites „alle Masken made by
studio“ bleibt Ziel, kein Ist-Zustand.

## Nächster Nachweis-Schritt (eine Lücke)

1. Image-/CI-Nachlauf mit Runtime-Catalog (schließen D für Entity-Profil).
2. Danach CLI-Migration **einer** Familien-Parent-Maske (StammObjectPageParent oder Beleg-Parent nach Codex-Handshake) — nicht 757 Routen.

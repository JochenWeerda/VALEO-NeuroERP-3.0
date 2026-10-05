# Runbook: Rollout Fütterungsberatung (`feeding_advisory`)

Stand: 2026-07-17 · Slice FEED-REL-047 · Owner: domain/agrar

## 1. Was wird ausgerollt

Das Modul `feeding_advisory` (Module-Registry) bündelt das Fütterungsberatungs-
Vertikal: Rationseditor, Fütterungspläne, mobile Ist-Dokumentation, Soll-Ist-
Controlling, Berichte, Beratung, Assistenz und Governance. Alle zugehörigen
API-Subrouter (Prefix `/feeding`) hängen am Router-Gate
`app/agrar/rations/module_gate.py` — bei deaktiviertem Modul antworten sie
mit 404 und benennen das Modul. Futterkatalog und Grundfutteranalysen bleiben
Teil des Basis-Agrar-Stacks und sind vom Gate ausgenommen.

## 2. Flag-Steuerung

- **Default:** `INSTALLED_MODULES = ["core", "agrar", "feeding_advisory"]` —
  installiert, heutiges Verhalten.
- **Pro Tenant deaktivieren:** Tenant in `TENANT_MODULE_FLAGS` mit einer Liste
  OHNE `feeding_advisory` eintragen (z. B. `{"<tenant>": ["core", "agrar"]}`).
- **Pro Tenant pilotieren:** global deaktivieren (`INSTALLED_MODULES` ohne das
  Modul) und nur Pilot-Tenants per `TENANT_MODULE_FLAGS` freischalten.
- Sichtbarkeit für Portal-Kacheln: `GET /api/v1/modules?tenant_id=…` liefert
  `feeding_advisory.enabled` je Tenant.

## 3. Vorbedingungen je Umgebung

1. `alembic upgrade head` — letzter Feed-Head: `feed_rbac_audit_20260717`
   (Kette: reports → report-types → herd-snapshots → benchmark → assist → rbac).
2. Backend-Regression: `pytest tests/test_feeding_*.py tests/test_rations_*.py`
   (Kernbatterie; im CI der volle Lauf).
3. Frontend-Build mit Routes-Stand ≥ FEED-NAV-050 (Nav-Einträge Rationseditor/
   Rationsvergleich/Beratung/Integrationsmonitor). **Achtung Docker:** der
   Frontend-Container braucht einen Rebuild, sonst fehlen die neuen Seiten.

## 4. Release-Smoke (automatisiert)

```bash
# Backend-Gate
pytest tests/test_feeding_module_flag.py --noconftest -q

# Release-Journeys A/B/C gegen laufende Umgebung
cd packages/frontend-web
PLAYWRIGHT_SKIP_WEBSERVER=1 FRONTEND_BASE_URL=http://<frontend> \
  npx playwright test tests/e2e/feeding-release-journeys.spec.ts
```

- **A:** Ration → Editor-Worklist → Editor (Positionen + Bewertung) →
  Freigabe → Planbericht inkl. CSV.
- **B:** Plan publizieren → mobile Ist-Dokumentation zeigt die Stallanweisung.
- **C:** Beratungsfall + Beobachtung → Beratungs-Maske zeigt Fall und Detail.

## 5. Referenzbetrieb-Vergleich (manueller Release-Schritt)

Vor der Breitenaktivierung auf einer Staging-Umgebung:

```bash
python scripts/seed_simulation_rations_acker.py --base http://<backend> \
  --rations-out data/seed/rations_hof_ostfriesland.json
```

Danach die Referenzrationen über `/optimize/from-profile` neu rechnen und die
Kennzahlen (Kosten/Tag, ME, sidP, DMI) gegen den Seed-Stand vergleichen.
Abweichungen > 1 % ohne erklärende Regeländerung (Changelog der
`requirements.py`-/Solver-Historie) blockieren den Rollout.

## 6. Pilotabnahme (Auftraggeber-Gate — nicht automatisierbar)

Die Abnahme durch einen fachkundigen Fütterungsberater ist Bedingung für die
Breitenaktivierung (Lastenheft Phase 6). Scope der Abnahme: Journeys A–C am
Pilotbetrieb, Bedarfswerte-Stichprobe gegen GfE-2023-Erwartung, Berichtsbild.
Ergebnis wird im Workboard und in `requirements-traceability.md`
(FEED-NFR-007) dokumentiert.

## 7. Rollback

1. **Sofort:** Modul je Tenant (oder global) über `TENANT_MODULE_FLAGS` /
   `INSTALLED_MODULES` deaktivieren — kein Deploy nötig, Gate antwortet 404,
   Portal-Kacheln verschwinden über `/modules`.
2. Daten bleiben unangetastet (alle Feed-Tabellen sind additiv/append-only);
   ein Alembic-Downgrade ist für das Abschalten NICHT erforderlich und wegen
   append-only-Semantik nur für leere Tabellen vertretbar.
3. Incident dokumentieren (Workboard + betroffene Slice-YAML), Root Cause vor
   Wiederaktivierung.

## 8. Bekannte Reste (bewusst offen)

- Rationsvergleich braucht einen Versions-Picker als Masken-Einstieg.
- Berichte-/Governance-/Assistenz-Masken (FE) folgen; Verträge sind API-seitig
  vollständig und getestet.
- Externe Gates: DDW/MLP/AMS-Livepfade (Partnervertrag), anonymisierter
  Betriebsvergleich (Opt-in-Entscheidung), IdP-Rollout `FUTTERMITTEL_*`,
  Pilotabnahme (Abschnitt 6).

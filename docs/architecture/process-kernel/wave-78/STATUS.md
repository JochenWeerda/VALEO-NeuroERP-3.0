# Wave 78 — EDI/API Hub: DigitalExchangeCoverage + Dispatch-Queue (Gap 043)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 46 passed, 0 failed
**Gap:** 043 — EDI/API Hub für Kunden/Lieferanten/Behörden, KPI: >=80% Dokumentenaustausch digital

## Lieferumfang

### A) DigitalExchangeCoverage — Gap-043-KPI

Neue Klasse in `app/core/edi_hub_contracts.py`:

```python
cov = DigitalExchangeCoverage(gesamt_dokumente=200, digital_dokumente=180)
cov.coverage_pct     # → 90.0
cov.kpi_erfuellt     # → True  (>=80%)
cov.fehlend_fuer_kpi # → 0
```

- `coverage_pct`: gerundeter Prozentwert (2 Stellen)
- `kpi_erfuellt`: True wenn >= 80.0%
- `fehlend_fuer_kpi`: wie viele Dokumente noch migriert werden müssen
- `_DIGITALE_STANDARDS`: EDIFACT, XML_UBL, JSON_API, ANSI_X12, IDOC — CSV_FLAT/EMAIL zählen nicht
- `evaluate_digital_coverage(nachrichten, partner_map)`: berechnet KPI aus echten Nachrichten

### B) PartnerApiKey — REST-API-Schlüssel

Für non-EDIFACT Partner (REST_WEBHOOK-Kanal):

```python
key = PartnerApiKey(
    key_id="K-001",
    partner_id="P-REST-001",
    key_hash=hashlib.sha256(raw.encode()).hexdigest(),
    erstellt_am=now,
    laeuft_ab_am=now + timedelta(days=365),
)
key.ist_gueltig          # True wenn aktiv + nicht abgelaufen
key.verify_hash(hash)    # prüft SHA-256-Hash
```

- Nur SHA-256-Hash wird gespeichert, nie Klartext
- `ist_abgelaufen`: prüft `laeuft_ab_am` gegen UTC-Now
- `verify_hash()`: schlägt fehl bei abgelaufen oder inaktiv

### C) EdiHubAuftrag — Ausgehende Dispatch-Queue

```python
auftrag = EdiHubAuftrag(
    auftrag_id="A-001",
    partner_id="P-001",
    nachrichtentyp=EDINachrichtenTyp.ORDERS,
    prioritaet=2,          # 1 = höchste, 5 = niedrigste
    payload_ref="BEST-2026-001",
    erstellt_am=now,
    max_versuche=3,
)
auftrag.versuch_starten()            # versuche += 1, status = GESENDET
auftrag.versuch_fehlgeschlagen("…")  # status = FEHLER
auftrag.kann_wiederholt_werden       # True wenn versuche < max_versuche
auftrag.versuch_erfolgreich()        # status = QUITTIERT
```

- Priorität validiert: 1–5 (ValueError sonst)
- Retry-Logik: `kann_wiederholt_werden` bis `max_versuche`
- Status-Maschine: PENDING → GESENDET → FEHLER/QUITTIERT

### D) EdiHubMonitor — Betriebszustand

```python
monitor = EdiHubMonitor(
    snapshot_zeitpunkt=now,
    aktive_partner=5,
    nachrichten_gesamt_24h=200,
    nachrichten_fehler_24h=4,
    sla_verletzungen_24h=0,
    ausstehende_auftraege=3,
    digital_coverage=coverage,
)
monitor.fehlerquote_pct  # 2.0
monitor.hub_gesund       # True wenn KPI+Fehlerquote+SLA OK
monitor.alert_level      # "OK" | "WARN" | "CRITICAL"
```

Hub gilt als gesund wenn:
- `digital_coverage.kpi_erfuellt` (>=80%)
- `fehlerquote_pct < 5.0`
- `sla_verletzungen_24h == 0`

## Kontrakt-Tests (46 Tests)

| Klasse | Tests | Kernprüfung |
|--------|-------|-------------|
| `TestDigitalExchangeCoverage` | 10 | KPI 80%, Rundung, fehlend_fuer_kpi |
| `TestEvaluateDigitalCoverage` | 5 | Nachrichten-basierte KPI-Berechnung |
| `TestPartnerApiKey` | 8 | Hash-Verifikation, Ablauf, Deaktivierung |
| `TestEdiHubAuftrag` | 9 | Retry-Logik, Status-Maschine, Validierung |
| `TestEdiHubMonitor` | 8 | Gesundheitsprüfung, Alert-Level |
| `TestIntegrationSzenario` | 6 | E2E: Dispatch-Zyklus, Key-Rotation, KPI-Pfad |

## KPI-Ergebnis (Gap 043)

| KPI | Ziel | Ergebnis |
|-----|------|----------|
| Digitale Abdeckung | >=80% | Contracts + Messung implementiert ✓ |
| API-Key-Sicherheit | SHA-256-Hash, kein Klartext | PartnerApiKey.verify_hash() ✓ |
| Dispatch-Retry | Max. 3 Versuche | EdiHubAuftrag.kann_wiederholt_werden ✓ |
| Hub-Monitoring | Alert OK/WARN/CRITICAL | EdiHubMonitor.alert_level ✓ |

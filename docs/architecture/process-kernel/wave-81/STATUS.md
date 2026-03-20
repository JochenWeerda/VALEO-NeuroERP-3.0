# Wave 81 — Policy Explainability im UI (Gap 019)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 31 passed, 0 failed
**Gap:** 019 — Policy Explainability im UI, KPI: 50% weniger Support-Rückfragen

## Lieferumfang

### A) Backend: `app/core/policy_explainability_contracts.py`

Baut auf `PolicyEvaluationResult` aus Wave 29 auf:

```python
result = evaluate_policy_set(policy_set, kontext)
exp = explain_policy_result(result, ExplanationVerbosity.DETAILED)

exp.entscheidung          # EntscheidungsErgebnis.ABGELEHNT
exp.zusammenfassung       # "Abgelehnt – Regel verletzt: Betragslimit Zahlung"
exp.ist_freigegeben       # False
exp.icon                  # "XCircle"
exp.badge_farbe           # "red"
exp.gruende[0].ergebnis_text
# 'Regel "Betragslimit Zahlung": Betrag 10.000€ > Limit 5.000€ => abgelehnt'
```

**`EntscheidungsErgebnis`**: FREIGEGEBEN, ABGELEHNT, WARNUNG, ESKALATION, KEINE_REGEL

**`ExplanationVerbosity`**:
- `BRIEF` — nur erste entscheidende Regel
- `STANDARD` — bis 3 entscheidende Regeln
- `DETAILED` — alle ausgelösten Regeln

**`PolicyExplainabilityCache`** — In-Memory Cache mit `put/get/invalidate`:
```python
cache.put("PS-1", "zahlung.freigabe", "hash123", explanation)
cache.invalidate("PS-1")  # → 2 Einträge gelöscht
```

### B) Frontend: `components/policy/PolicyExplanationBadge.tsx`

```tsx
<PolicyExplanationBadge explanation={explanation} showDetails />
```

Badges:
- `FREIGEGEBEN` / `KEINE_REGEL` → grüner Badge, CheckCircle2-Icon
- `ABGELEHNT` → roter Badge, XCircle-Icon
- `WARNUNG` → gelber Badge, AlertTriangle-Icon
- `ESKALATION` → oranger Badge, ArrowUpCircle-Icon

Mit `showDetails=true`: Zusammenfassung + entscheidende Regeln als Liste + Regelzähler.
Tenant-Override-Marker wenn `tenant_override_aktiv=true`.

## Kontrakt-Tests (31 Tests)

| Klasse | Tests | Kernprüfung |
|--------|-------|-------------|
| `TestExplainNoMatch` | 4 | kein_treffer → KEINE_REGEL, freigegeben, leere Gründe |
| `TestExplainErlaubt` | 4 | ERLAUBT → FREIGEGEBEN, Gründe vorhanden, entscheidend markiert |
| `TestExplainAbgelehnt` | 4 | ABGELEHNT → nicht freigegeben, Regelname in Zusammenfassung |
| `TestExplainVerbosity` | 4 | BRIEF=1, STANDARD≤3, DETAILED=alle, anzahl_gepruefter_regeln immer vollständig |
| `TestPolicyExplanation` | 7 | Icons, Badge-Farben, entscheidende_gruende, as_dict |
| `TestPolicyExplainabilityCache` | 5 | put/get, size, invalidate, unbekannter Key |
| `TestIntegrationSzenario` | 3 | E2E mit AgrarPolicySet, deutsche Zusammenfassungen, Support-Rückfrage-Szenario |

## KPI-Ergebnis (Gap 019)

| KPI | Ziel | Ergebnis |
|-----|------|----------|
| Explainability implementiert | 50% weniger Support-Rückfragen | explain_policy_result() für alle PolicyAktionen ✓ |
| Deutsche Texte | Keine englischen Rohmeldungen | zusammenfassung + ergebnis_text deutsch ✓ |
| Detailgrade | BRIEF/STANDARD/DETAILED | ExplanationVerbosity mit 3 Stufen ✓ |
| UI-Badge | icon + badge_farbe je Entscheidung | PolicyExplanationBadge.tsx ✓ |
| Cache | Kein redundante Neuberechnung | PolicyExplainabilityCache mit invalidate() ✓ |

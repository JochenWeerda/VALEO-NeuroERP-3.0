# POS-Fiskalisierung Operations UAT

Stand: 2026-06-09

## Abgedeckter Vertrag

- Typed Route `/admin-suite/pos-fiscalization` oeffnet ohne 404.
- Bestehende tenantbezogene Konfiguration wird geladen.
- TSE-Provider kann zwischen fiskaly, Swissbit Cloud, Swissbit Gateway und
  expliziter Simulation gewaehlt werden.
- Swissbit als TSE und fiskaly als DSFinV-K-Provider bleiben getrennt.
- Der Browser sendet keine Provider-Secrets.
- SUBMIT DE, RECEIPT und SAFE zeigen fehlende Produktvertraege als Blocker.
- Ein Tagesabschluss mit unvollstaendiger Fiskaltransaktion kann nicht in die
  Fibu gebucht werden.

## Automatisierter Nachweis

```text
npx playwright test playwright-tests/specs/pos/fiscalization-admin.spec.ts --project=full --workers=1
2 passed
```

Der Lauf erzeugt zuvor einen Produktions-Build und prueft die echte
TanStack-Route. Backend-Vertraege:

```text
python -m pytest -o "addopts=" tests/test_pos_fiscalization_providers.py tests/test_pos_fiscalization_security_contract.py -q
11 passed
```

## Externe Gates

- fiskaly Sandbox-/Live-Credentials und lizenzierte OpenAPI-Vertraege
- Swissbit Cloud- oder SDK-Partnervertrag
- DSFinV-K-Pruefwerkzeug und KassenSichV-/GoBD-Fachabnahme
- reale Kasse, Drucker, Offlinebetrieb und Wiederanlauf

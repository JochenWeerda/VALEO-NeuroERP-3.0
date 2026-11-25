# Made-by-Studio Gate-Report

Stand: 2026-11-25 (erzeugt mit `python scripts/verify_made_by_studio_gates.py`).

Bezug: [Made by Studio — Qualitätsversprechen](made-by-studio-qualitaetsversprechen.md).

## Zusammenfassung

| Metrik | Wert |
|--------|------|
| Registrierte ScreenDefinitions | 829 |
| Gate A (Meridian & Struktur) grün | 829 |
| Gate B (Rechte & Aktionen) grün | 829 |
| Gate C (Compiler & Kanal) grün | 829 |
| Gate E (Runtime-Verdrahtung) grün | 829 |
| Studio-Draft-Projektion ohne Violations | 822 |
| Ø Advisory-Score (Gate-C-Metrik) | 0.98 |
| Screen-IDs in runtime_wired-Routen (gesamt) | 2616 |

Gate D (Browser/Image) wird hier nicht automatisiert geprüft.

## Gate A — offene Screen-IDs (0)

Keine — alle grün.

## Gate B — offene Screen-IDs (0)

Keine — alle grün.

## Gate C — offene Screen-IDs (0)

Keine — alle grün.

## Gate E — offene Screen-IDs (0)

Keine — alle grün.

## Studio-Draft-Projektion (Auszug)

- `agrar/sammelabrechnung`: action_ungueltiger_dangerLevel:loeschen:destructive
- `agrar/zinsabrechnung`: action_ungueltiger_dangerLevel:stornieren:destructive
- `einkauf/angebot`: action_ungueltiger_dangerLevel:ablehnen:destructive
- `einkauf/anlieferavis`: action_ungueltiger_dangerLevel:stornieren:destructive
- `kontrakte/mengenzeitraeume`: action_ungueltiger_dangerLevel:zeitraum_loeschen:destructive
- `logistik/frachttabellen`: action_ungueltiger_dangerLevel:loeschen:destructive
- `workflow/flow-spine-studio`: flow_spine_katalog_maske_ungueltig

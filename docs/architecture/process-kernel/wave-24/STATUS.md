# Wave-24 Status

## Scope
Tenant-Prozessvarianten (Gap 009) + Saisonale Kampagnenvorlagen (Gap 005)

## Zielbild

Wave 24 schliesst zwei verbliebene P0/P1-Luecken:
Gap 009 (Rollenbasierte Prozessvarianten je Genossenschaft,
0 globale Hardcoded Prozessschritte) und Gap 005 (Saisonale Kampagnenprozesse
als Vorlagen, Setup-Zeit neue Kampagne <30 Minuten).

Tenant-Prozessvarianten ermöglichen mandantenspezifische Schritt-Overrides
ohne Code-Änderungen. Das Kampagnenvorlagen-System macht aus einer Vorlage
in wenigen Klicks eine vollständige Erntekampagne.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/tenant_prozess_variante.py` | `TenantProzessVariante`: mandantenspezifische Schritt-Aktivierung/-Deaktivierung, Override-Prioritäten, `resolve_process_steps()` | abgeschlossen |
| AP2 | `app/core/kampagnen_vorlage.py` | `KampagnenVorlage`: vordefinierte Ernte-Vorlagen für 5 Typen (Winterweizen, Sommergerste, Raps, Körnermais, Zuckerrüben); `instantiate_from_vorlage()` | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/kampagnen/vorlagen` — alle Vorlagen; `GET /process/kampagnen/vorlagen/{typ}/instantiate` | abgeschlossen |
| AP4 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/tenant/prozess-varianten` — Varianten-Registry; `GET /process/tenant/prozess-varianten/{prozess_key}/steps` | abgeschlossen |
| AP5 | `app/core/tenant_prozess_variante.py` | `validate_prozess_variante()` — Pruefung Schritt-Konsistenz, Pflicht-Schritte, Reihenfolge-Konflikte | abgeschlossen |
| AP6 | `app/core/kampagnen_vorlage.py` | `get_default_kampagnen_vorlagen()` — 5 Standard-Vorlagen mit Meilensteinen, Qualitaetsschwellen, Intrastat-CN8-Codes | abgeschlossen |

## Abnahmekriterien

- `resolve_process_steps()` liefert korrekte mandantenspezifische Schrittfolge
- Tenant-Override überschreibt Default, ohne Pflichtschritte zu entfernen
- `instantiate_from_vorlage()` erzeugt vollständige ErnteKampagne aus Vorlage in <1 Sekunde
- Alle 5 Standard-Vorlagen sind serialisierbar (`schema_version=1`)
- `validate_prozess_variante()` erkennt fehlende Pflichtschritte und Konflikte
- Keine Schichtverletzungen; `app/core/` importiert keine API-Module

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave24_varianten_vorlagen.py` | 41 | AP1/AP5: resolve_process_steps() (8 Tests), validate_prozess_variante() (6 Tests), Default-Schritte (5 Tests); AP2/AP6: KampagnenVorlagen (10 Tests), instantiate_from_vorlage() (5 Tests); AP3/AP4: API-Endpoints (7 Tests) |

**Gesamt Wave 24: 41 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 005 | Saisonale Kampagnenprozesse als Vorlagen, Setup <30 Min | `kampagnen_vorlage.py` mit 5 Default-Vorlagen (Winterweizen/Gerste/Raps/Mais/Zucker), CN8-Codes, Qualitaetsschwellen, Meilensteine; `instantiate_from_vorlage()` |
| Gap 009 | Rollenbasierte Prozessvarianten, 0 hardcoded Schritte | `tenant_prozess_variante.py` mit `resolve_process_steps()` + `validate_prozess_variante()`; 7 konfigurierbare agrar_settlement-Schritte |

## Status
`abgeschlossen` — 2026-03-15

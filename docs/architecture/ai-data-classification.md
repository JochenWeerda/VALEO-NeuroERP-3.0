---
title: KI-Datenklassen-Policy
description: Definiert welche Datenkategorien externen KI-Modellen zugänglich sind — maschinenlesbar und validiert.
---

# KI-Datenklassen-Policy

> **Verbindlich** für alle KI-Agenten, MCP-Tools und API-Integrationen in VALEO NeuroERP 3.0.
> Maschinenlesbare Quelle: [`config/ai_data_classification.yaml`](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/blob/main/config/ai_data_classification.yaml)
> Validierung: `python scripts/validate_data_classification.py`

---

## Klassifizierungsstufen

| Stufe | Kürzel | Externes Modell | EU-API only | Nur lokal | Niemals |
|---|---|:---:|:---:|:---:|:---:|
| Öffentlich | `PUBLIC` | ✅ | — | — | — |
| Nur EU/EWR-APIs | `EU_ONLY` | ✅ | ✅ | — | — |
| Nur lokal | `LOCAL_ONLY` | — | — | ✅ | — |
| Synthetisch/anon. erlaubt | `SYNTHETIC_ALLOWED` | — | — | — | — |
| Niemals in Kontext | `NEVER` | ❌ | ❌ | ❌ | ✅ |

!!! danger "NEVER — absolutes Verbot"
    Daten mit Stufe `NEVER` dürfen **unter keinen Umständen** an ein KI-Modell übergeben werden —
    weder direkt noch als Teil eines Prompts, Kontexts oder Tool-Ergebnisses.

---

## Datenkategorien

### Stammdaten

| Kategorie | Stufe | Beispiele | Begründung |
|---|---|---|---|
| Artikel-Stammdaten | `PUBLIC` | Artikelnummer, Bezeichnung, Warengruppe | Handelsübliche Katalogdaten ohne Personenbezug |
| Lieferanten-Stammdaten (öffentlich) | `EU_ONLY` | Firmenname, USt-ID, PLZ | Können natürliche Personen betreffen (DSGVO Art. 4) |
| Kunden-Identitätsdaten | `EU_ONLY` | Name, Adresse, E-Mail, Kundennummer | Personenbezogene Daten gem. DSGVO |
| **Mitarbeiterstamm** | **`NEVER`** | Name, Gehalt, Bankverbindung, Krankheitstage | Hochsensibel gem. DSGVO Art. 9 + BetrVG |

### Transaktionsdaten

| Kategorie | Stufe | Beispiele | Begründung |
|---|---|---|---|
| Auftrags-/Bestelldaten | `EU_ONLY` | Auftragsnummer, Preise, Lieferdatum | Preiskonditionsgeheimnisse + Kundenbezug |
| Rechnungsdaten | `EU_ONLY` | Rechnungsnummer, Betrag, Steuerbetrag | Finanztransaktionen mit GoBD-Relevanz |
| **Zahlungsdaten / Bankdaten** | **`NEVER`** | IBAN, Kontonummer, Valutadatum | Kritische Finanzdaten |
| **Lohn- und Gehaltsabrechnungen** | **`NEVER`** | Bruttogehalt, Steuerklasse, SV-Beiträge | Steuerrelevant, höchste Schutzstufe |

### Agrardaten

| Kategorie | Stufe | Beispiele | Begründung |
|---|---|---|---|
| Chargendaten (anonymisiert) | `PUBLIC` | Lot-Nummer, Sorte, Qualitätsklasse | Anonymisierte Handelsdaten |
| Chargendaten mit Erzeuger | `EU_ONLY` | Erzeuger-Name, Betriebsnummer | Können natürliche Personen identifizieren |
| Agrar-Kontrakte / Preisfixierungen | `LOCAL_ONLY` | Kontraktpreis, MATIF-Fixierung, Menge | Handelsgeheimnisse — ausschließlich lokal |

### Compliance & Audit

| Kategorie | Stufe | Beispiele | Begründung |
|---|---|---|---|
| GoBD Journal-Einträge | `LOCAL_ONLY` | Buchungstext, Konto, Betrag | Steuerrelevante Buchführungsdaten |
| **Audit-Logs / Zugriffsprotokolle** | **`NEVER`** | User-ID, Aktion, IP-Adresse | Nutzungsprofile — absolutes Verbot |
| Steuerliche Meldedaten (UStVA, DATEV) | `LOCAL_ONLY` | Steuervoranmeldung, DATEV-Export | Steuergeheimnis |

### Systemdaten

| Kategorie | Stufe | Beispiele | Begründung |
|---|---|---|---|
| Systemkonfiguration (nicht-sensibel) | `PUBLIC` | Feature-Flags, Mandanten-Name | Für Agent-Kontext nutzbar |
| **Credentials / Secrets** | **`NEVER`** | Passwörter, API-Keys, Tokens | Absolutes Verbot |
| Mandanten-Konfiguration (sensibel) | `LOCAL_ONLY` | DB-Verbindung, OIDC-Config | Nur lokale Agenten |

### KI-Training

| Kategorie | Stufe | Beispiele | Begründung |
|---|---|---|---|
| Synthetische Trainingsdaten | `SYNTHETIC_ALLOWED` | Generierte Beispiel-Aufträge | Kein Personenbezug |
| **Prompt-History** | **`NEVER`** | Nutzer-Prompts, Session-Kontext | Können Geschäftsinformationen enthalten |

---

## Anwendung in MCP-Tools

Jedes MCP-Tool-Schema in [`config/mcp_erp_tools.yaml`](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/blob/main/config/mcp_erp_tools.yaml)
muss auf diese Klassifizierung verweisen:

```yaml
# Beispiel Tool-Definition
- tool_id: get_customer_info
  data_classes:
    - master_customer_identity   # EU_ONLY → nur EU-Modelle
  external_model_allowed: false   # wegen EU_ONLY
```

## Validierung

```bash
# Manuelle Validierung
python scripts/validate_data_classification.py

# In CI (quality-gate.yml)
python scripts/validate_data_classification.py --config config/ai_data_classification.yaml
```

Die Validierung prüft:

- Alle Pflichtfelder je Stufe und Kategorie
- Referenz-Integrität (Level muss definiert sein)
- Mindestens 3 `NEVER`-Kategorien (Credentials, Audit, Zahlung)
- Keine doppelten Kategorie-IDs
- Keine leeren `rationale`-Felder

---

## Rechtliche Grundlagen

| Rechtsgrundlage | Relevanz |
|---|---|
| DSGVO Art. 4, 9 | Personenbezogene Daten, besondere Kategorien |
| DSGVO Art. 46 | Drittlandtransfer → `EU_ONLY`-Einschränkung |
| §146a AO / GoBD | Unveränderlichkeit Buchführungsdaten → `LOCAL_ONLY` |
| BetrVG §87 | Mitarbeiterdaten → `NEVER` |
| Steuergeheimnis §30 AO | Steuerdaten → `LOCAL_ONLY` |

---

*Stand: 2026-06-26 · Slice: `DATA-CLASSIFICATION-001` · Quelle: `config/ai_data_classification.yaml`*

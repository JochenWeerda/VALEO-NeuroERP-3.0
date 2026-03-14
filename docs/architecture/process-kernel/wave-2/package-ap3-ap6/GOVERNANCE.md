# Wave 2 AP3-AP6: Tenant Governance Modelle

## Uebersicht

| AP | Thema | Modell | Endpunkt |
|----|-------|--------|---------|
| AP3 | Tenant-/Verbundmodell | `TenantStructure`, `VerbundMember` | `GET /api/v1/tenant/structure` |
| AP4 | Rollen- und Berechtigungsvererbung | `RoleInheritanceChain`, `RoleDefinition` | `GET /api/v1/tenant/role-inheritance` |
| AP5 | Agenten- und Delegationssicherheit | `AgentManifest`, `DelegationPolicy` | `GET /api/v1/tenant/agent-manifests` |
| AP6 | Export- und Datenresidenzregeln | `ExportGovernancePolicy`, `DataResidencyRule` | `GET /api/v1/tenant/data-residency` |

Alle Modelle in: `app/core/tenant_governance.py`
Alle Endpunkte in: `app/api/v1/endpoints/tenant_governance.py`

---

## AP3: Tenant-/Verbundmodell

### Konzept

Landhandels-Genossenschaften arbeiten im Verbund:
- **ROOT**: Genossenschafts-Zentrale (Haupt-Mandant)
- **BRANCH**: Filialen, Betriebsstaetten, Regionaleinheiten
- **PARTNER**: Externe Partner mit eingeschraenktem Datenzugriff

### Vererbungsregeln

```
Zentrale (ROOT)
  └── Filiale Nord (BRANCH) — inherits_policies_from_parent=true
        └── Partner Schmidt (PARTNER) — inherits_roles_from_parent=true, data_scope="own"
```

Jedes Mitglied erbt optional:
- `inherits_policies_from_parent`: Uebernimmt Policy-Overrides des Elternmandanten
- `inherits_roles_from_parent`: Uebernimmt Rollen und Berechtigungen
- `data_scope`: Welche Daten sieht dieses Mitglied (`own` / `verbund` / `all`)

### Invarianten
- ROOT hat kein `parent_tenant_id`
- `data_scope=verbund` darf nur BRANCH zugewiesen werden
- Zirkulaere Eltern-Kind-Relationen sind verboten

---

## AP4: Rollen- und Berechtigungsvererbung

### Geltungsbereiche

| Scope | Bedeutung |
|-------|-----------|
| `global` | Plattformweit — wird vom SaaS-Betreiber definiert |
| `verbund` | Fuer alle Verbundmitglieder gueltig |
| `tenant` | Nur fuer diesen Mandanten |
| `process` | Nur im Kontext eines spezifischen Prozesses (z.B. AP-Freigabe) |

### Vererbungslogik

```
Effektive Berechtigungen = global_roles ∪ verbund_roles ∪ tenant_roles ∪ process_roles
```

Dabei gilt:
- Niedrigere Scope-Ebenen koennen **einschraenken**, aber **nicht erweitern** jenseits der globalen Grenzen
- `inheritable=false` Rollen werden nicht an Kinder weitergegeben (z.B. `fibu.admin`)

### Kernrollen (Standard-Landhandel)

| role_id | scope | permissions |
|---------|-------|-------------|
| `fibu.read` | tenant | `finance:read`, `ap_invoice:read` |
| `fibu.write` | tenant | `finance:write`, `ap_invoice:create` |
| `fibu.admin` | tenant | `finance:admin`, `ap_invoice:approve`, `payment_run:execute` |
| `agrar.manager` | tenant | `harvest:write`, `quality:write`, `settlement:read` |

---

## AP5: Agenten- und Delegationssicherheitsmodell

### Capability-Stufen

```
READ < WRITE < APPROVE < DELEGATE < EXECUTE_PAYMENT
```

Jede hoehere Stufe erfordert explizite Freigabe und erhoehte Audit-Anforderungen.

### Standard-Agentenregeln

| Agent-Typ | Erlaubt | Gesperrt | Human-Confirmation |
|-----------|---------|----------|--------------------|
| `ai_assistant` | READ, WRITE | EXECUTE_PAYMENT | approve, execute_payment |
| `automation` | READ, WRITE | APPROVE, EXECUTE_PAYMENT | approve, execute_payment |
| `integration` | READ, WRITE | APPROVE, EXECUTE_PAYMENT | approve |
| `human_delegate` | READ, WRITE, APPROVE | EXECUTE_PAYMENT | execute_payment |

### Delegationsregeln

- `max_delegation_depth`: Maximale Kette A→B→C (default: 1 = nur direkte Delegation)
- Jede Delegation ist zeitlich begrenzt (`valid_until`) oder explizit widerrufbar
- Alle Agent-Aktionen werden auditiert (`audit_all_actions=true`)
- Delegationseintraege werden NICHT automatisch erneuert

### Kritisch: Zahlungen

`EXECUTE_PAYMENT` ist die hoechste Capability-Stufe. Regelwerk:
1. Kein KI-Agent darf direkt Zahlungen ausfuehren
2. Automatisierungs-Agenten duerfen nur vorbereiten, nicht ausfuehren
3. Ausfuehrung erfordert immer menschliche Bestaetigung

---

## AP6: Export- und Datenresidenzregeln

### Residenzzonen

| Zone | Rechtsrahmen |
|------|-------------|
| `de` | Deutschland — GoBD, HGB, AO (Prioritaet) |
| `eu` | EU-Datenraum — DSGVO, NIS2 |
| `at` | Oesterreich — UGB, BAO |
| `ch` | Schweiz — OR, DSG |
| `unrestricted` | Keine geografische Einschraenkung |

### Exportklassifizierung

| Klasse | Bedeutung | Beispiel |
|--------|-----------|---------|
| `public` | Frei exportierbar | Artikelkatalog |
| `internal` | Intern, mit Logging | Qualitaetsprotokolle |
| `confidential` | Nur mit Freigabe | Buchungsbelege, Eingangsrechnungen |
| `restricted` | Gesperrt (personenbezogen) | Kundenstammdaten |

### GoBD-Pflichtregeln (automatisch aktiviert)

| data_type | retention_years | zone | classification |
|-----------|----------------|------|----------------|
| `ap_invoice` | 10 | `de` | `confidential` |
| `harvest_acceptance` | 10 | `de` | `internal` |
| `customer_master` | 7 | `eu` | `restricted` |
| `quality_protocol` | 5 | `de` | `internal` |

---

## Verifikation

```
pytest tests/test_process_kernel_wave2_governance.py -q
python -m py_compile app/core/tenant_governance.py app/api/v1/endpoints/tenant_governance.py
```

Ergebnis: 19 tests passed

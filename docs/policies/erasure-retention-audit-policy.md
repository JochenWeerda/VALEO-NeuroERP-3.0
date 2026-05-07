# Policy-Rahmen: ERP/CRM Erasure, Retention & Audit

**Status:** Entwurf zur Abnahme durch Architektur, Legal, Datenschutz, ERP-Fachbereich (bei Bedarf zusätzlich Finance/FiBu)

**Geltung:** CRM, ERP-Domain, FiBu, Rechnungen, Angebote, Anfragen, Kontakte, Audit-Logs, Exporte, Backups

---

## Normsatz (verbindlicher Leitkompass)

Produktive Löschung, Anonymisierung, Pseudonymisierung oder Entkopplung personenbezogener Daten ist nur zulässig, wenn zuvor eine **versionierte Policy-Entscheidung** erzeugt, **auditierbar persistiert** und durch die **erlaubte Execute-Aktion** umgesetzt wurde. Bei möglichem **ERP-, FiBu-, Rechnungs-, GoBD-, Steuer-, Vertrags-, Legal-Hold- oder Auditbezug** ist **Hard-Delete standardmäßig gesperrt**.

**Grundsatz:** Kein produktiver Hard-Delete bei möglichem GoBD-/FiBu-/Rechnungs-/Auditbezug **ohne** vorgelagerte Policy-Entscheidung.

**Architektur-Verweis:** [ADR: Erasure Decision API + Audit](../architecture/adr-2026-05-06-erasure-decision-api-and-audit.md)

---

## 1. Rechts- und Standardbasis

*Hinweis: Keine Rechtsberatung. Konkrete Auslegung, Fristenstarts und Einzelfälle durch Legal/Steuer freizugeben.*

### 1.1 DSGVO

- **Datenminimierung, Speicherbegrenzung, Integrität/Vertraulichkeit, Rechenschaft** — personenbezogene Daten nur so lange **identifizierbar** speichern, wie für die Zwecke erforderlich; der Verantwortliche muss die Einhaltung **nachweisen** können.
- **Recht auf Löschung** (Art. 17 DSGVO) ist **nicht schrankenlos**; Ausnahmen u. a. bei **rechtlichen Pflichten** oder **Rechtsansprüchen** (Geltendmachung, Ausübung, Verteidigung).
- **Einschränkung der Verarbeitung** (Art. 18 DSGVO), u. a. wenn Daten für Rechtsansprüche benötigt werden oder statt Löschung die Nutzung eingeschränkt werden soll.
- **BDSG § 35** ergänzt: unter bestimmten Umständen kann an die Stelle einer Löschung die **Einschränkung der Verarbeitung** treten, **insbesondere** wenn **Aufbewahrungspflichten** entgegenstehen.

### 1.2 AO, HGB, UStG, GoBD

- **AO § 147:** geordnete Aufbewahrung **steuerlich relevanter** Unterlagen; u. a. Bücher/Aufzeichnungen/Inventare/Jahresabschlüsse und bestimmte zollbezogene Unterlagen **zehn Jahre**, Buchungsbelege **acht Jahre**, andere steuerlich relevante Unterlagen in der Regel **sechs Jahre**; digitale Daten während der Frist **verfügbar, lesbar, maschinell auswertbar**.
- **HGB § 257:** handelsrechtlich relevante Unterlagen; u. a. Bücher, Inventare, Jahresabschlüsse und Organisationsunterlagen **zehn Jahre**, Buchungsbelege **acht Jahre**, empfangene/abgesandte Handelsbriefe **sechs Jahre**.
- **UStG § 14b:** Aufbewahrung ausgestellter und empfangener Rechnungen grundsätzlich **acht Jahre**; Fristbeginn regelmäßig mit **Schluss des Kalenderjahres**, in dem die Rechnung ausgestellt wurde (Detail mit Legal).
- **AO § 146 / HGB § 239:** **Unveränderbarkeit** — Buchungen und Aufzeichnungen vollständig, richtig, zeitgerecht und geordnet; **Änderungen** dürfen den ursprünglichen Inhalt **nicht unkenntlich machen**.
- **GoBD:** vom BMF u. a. **2024 und 2025** angepasst; als **aktueller Referenzrahmen** für elektronische Bücher, Aufzeichnungen, Unterlagen und Datenzugriff zu behandeln — **Auslegung** durch Legal/FiBu.

### 1.3 BSI / IT-Grundschutz

Systematischer Rahmen für Informationssicherheit — für diesen Policy-Rahmen insbesondere:

| Baustein | Relevanz |
|----------|----------|
| **CON.2** | Datenschutz — Verknüpfung Datenschutz ↔ IT-Grundschutz |
| **CON.3** | Datensicherungskonzept — Backups, Wiederherstellung, rechtliche Anforderungen, Löschanforderungen |
| **CON.6** | Löschen und Vernichten |
| **OPS.1.1.5** | Protokollierung — Erhebung, Speicherung, Auswertung, Entsorgung |
| **OPS.1.2.2** | Archivierung — langfristig, sicher, unveränderbar |
| **ORP.4** | Identitäts- und Berechtigungsmanagement |

**BSI Mindeststandard** Protokollierung/Detektion (Stand-Updates, u. a. 2024): Speicherfristen und Löschung von Protokolldaten sind explizit zu berücksichtigen.

---

## 2. Verbindliche Policy-Grundsätze

### P1 — Retention schlägt Hard-Delete

Wenn Daten unter **AO, HGB, UStG, GoBD**, **Legal Hold**, **offene Forderungen**, **laufende Verträge**, **steuerliche Relevanz** oder **Auditpflicht** fallen, ist **Hard-Delete verboten**.

**Zulässige Alternativen (Policy-Aktionen, nicht technische Implementierungsnamen):**

- `restrict_processing`
- `pseudonymize_reference`
- `anonymize_non_required_contact_fields`
- `unlink_crm_profile`
- `mark_for_delete_after_retention`
- `manual_legal_review_required`

### P2 — CRM-Kontakt und ERP-Geschäftsvorfall werden getrennt

- **CRM-Kontakt** darf gelöscht oder anonymisiert werden, wenn **keine** eigene Aufbewahrungspflicht entgegensteht.
- **ERP-/FiBu-Belege** bleiben erhalten, wenn sie **aufbewahrungspflichtig** sind.

**Beispiel:**

| Bereich | Inhalt |
|---------|--------|
| **CRM** | Name, Telefonnummer, Marketingdaten: löschbar/anonymisierbar (wenn Policy) |
| **ERP/FiBu** | Rechnung, Buchungsbeleg, Zahlungsreferenz: aufbewahrungspflichtig; Personenbezug soweit möglich **pseudonymisieren/minimieren** |

### P3 — Keine Löschung ohne Evaluate/Execute-Split

Produktive Löschung läuft **niemals** direkt.

**Pflichtprozess:**

`request` → `identify_subject` → `discover_data` → `evaluate_policy` → `create_decision` → `execute_allowed_action` → `persist_audit` → `verify_result` → `close_request`

### P4 — Unklare Datenlage bedeutet keine Löschung

Wenn ein Service nicht erreichbar ist, Datenklassifikation fehlt oder der ERP-/FiBu-Bezug **nicht sicher ausgeschlossen** werden kann:

- `decision` = `insufficient_information`
- `action` = `manual_legal_review_required`
- `hard_delete` = **blockiert**

### P5 — Audit ist Teil der Rechtsfähigkeit

Eine Entscheidung, die **nicht auditierbar** ist, gilt technisch als **nicht erfolgt**.

Wenn **Audit-Persistenz** fehlschlägt:

- `execute` = **failed**
- `result` = **not_legally_effective**

---

## 3. Datenklassifikation

### 3.1 Klassen

| Klasse | Beispiele | Default-Policy |
|--------|-----------|----------------|
| CRM-Marketingdaten | Kampagnen, Newsletter, Tags, Consent-Metadaten | löschbar/anonymisierbar, sofern kein Nachweiszweck entgegensteht |
| CRM-Kontaktdaten | Name, E-Mail, Telefon, Adresse | löschbar/anonymisierbar, wenn kein ERP-/Rechtsbezug |
| Consent-Nachweise | Opt-in, Double-Opt-in, Widerruf | aufbewahren, solange Nachweis erforderlich |
| Vertragsdaten | Angebote, Aufträge, aktive Vereinbarungen | kein Hard-Delete bei **aktivem** Vorgang |
| ERP-Belege | Rechnung, Lieferschein, Buchungsbeleg | kein Hard-Delete während Aufbewahrung |
| FiBu-Daten | Journal, Konten, Periodenabschluss, Buchung | kein Hard-Delete während Aufbewahrung |
| Handels-/Geschäftsbriefe | empfangene/gesendete Geschäftsbriefe | Aufbewahrung nach HGB/AO |
| Audit-Logs | Entscheidungen, Actor, Tenant, Policy-Version | nicht unkontrolliert löschbar |
| Security-Logs | Login, Rechte, Sicherheitsereignisse | nach Log-Policy speichern/löschen |
| Backups | DB-Dumps, Snapshots, Archive | eigene Backup-/Retention-Policy |

---

## 4. Aufbewahrungsrahmen

### 4.1 Mindestfristen als technische Defaults

*Rechtlich zu bestätigen; als technische Default-Policy im System hinterlegbar.*

| Datenart | Default-Frist | Quelle (Rahmen) |
|----------|---------------|------------------|
| Handelsbücher, Inventare, Jahresabschlüsse, Organisationsunterlagen | 10 Jahre | AO/HGB |
| Steuerlich relevante Bücher und Aufzeichnungen | 10 Jahre | AO |
| Buchungsbelege | 8 Jahre | AO/HGB |
| Rechnungen | 8 Jahre | UStG |
| Handels-/Geschäftsbriefe | 6 Jahre | AO/HGB |
| CRM-Marketingdaten ohne Nachweispflicht | zweckgebunden, kurz | DSGVO Speicherbegrenzung |
| Consent-/Widerrufsnachweise | solange Nachweis erforderlich | DSGVO Rechenschaftspflicht |
| Security-/Protokolldaten | nach Log-Policy | BSI/DSGVO |
| Backups | nach Backup-Konzept | BSI CON.3 |

Die Frist beginnt bei AO/HGB/UStG **regelmäßig** mit dem **Schluss des Kalenderjahres**, in dem der relevante Vorgang entstand (Buchung, Beleg, Handelsbrief, Rechnung — **Detail Legal**).

---

## 5. Decision Matrix

*Kern der fachlichen Abstimmung; Zellen mit ERP-Fachbereich/Legal konkretisieren.*

| Situation | Entscheidung | Erlaubte Aktion | Blockierte Aktion |
|-----------|--------------|----------------|-------------------|
| CRM-only Kontakt, kein Consent-/ERP-/FiBu-/Vertragsbezug | `delete_allowed` | Delete oder Anonymisierung | — |
| CRM-Kontakt mit Marketing-Consent-Nachweis | `anonymize_allowed` oder `restrict_processing` | Kontakt anonymisieren; Nachweis **minimiert** halten | unkontrollierter Hard-Delete des Nachweises |
| Kontakt mit Angebot ohne Folgebeleg | `manual_legal_review_required` oder `anonymize_allowed` | je nach Status anonymisieren | automatischer Hard-Delete |
| Kontakt mit Auftrag/Lieferung/offenem Vorgang | `deny_due_to_open_business_process` | Verarbeitung einschränken | Hard-Delete |
| Kontakt mit Rechnung/Buchung/FiBu-Beleg | `deny_due_to_retention` | ERP-Referenz pseudonymisieren, CRM entkoppeln | Hard-Delete |
| Aktiver Legal Hold | `deny_due_to_legal_hold` | keine manipulative Änderung der Nachweisfähigkeit | Delete/Anonymize/Pseudonymize, wenn Nachweis beeinträchtigt |
| Unklare Datenlage | `insufficient_information` | manuelle Prüfung | Delete |
| Retention abgelaufen, kein Legal Hold, kein offener Anspruch | `delete_allowed` oder `anonymize_allowed` | Delete/Anonymize | — |
| Audit-Log mit personenbezogenen Klartextdaten | `pseudonymize_allowed` | Klartext minimieren; Hash/Pseudonym behalten | Audit-Spur zerstören |

**Hinweis (Decision vs. Ausführungsaktion):** **Minimierung** ist **keine** eigene `decision`, sondern eine **erlaubte Ausführungsaktion** innerhalb von **Pseudonymisierung**, **Anonymisierung** oder **Verarbeitungseinschränkung**. Fachlich für Audit-Protokolle: der Eintrag **bleibt erhalten**; Personenbezug wird **minimiert**, **pseudonymisiert** oder **redaktionell reduziert**, soweit die **Nachweisfähigkeit** nicht zerstört wird. *(Ein eigener Wert `minimize_allowed` wird nicht geführt — er würde die Decision-Taxonomie mit `anonymize_allowed`, `pseudonymize_allowed`, `restrict_processing` und teils `delete_allowed` überlappen.)*

---

## 6. Erlaubte Entscheidungswerte

**Nur** diese Werte sind für die Decision API zulässig:

`delete_allowed`
`anonymize_allowed`
`pseudonymize_allowed`
`restrict_processing`
`deny_due_to_retention`
`deny_due_to_legal_hold`
`deny_due_to_open_business_process`
`deny_due_to_legal_claims`
`manual_legal_review_required`
`insufficient_information`

**Nicht erlaubt:**

`maybe` · `best_effort` · `partial_delete_unknown` · `force_delete` · `delete_anyway`

### 6.1 Decision vs. `allowed_actions` / `blocked_actions`

**Architektur:** [ADR: Erasure Decision API + Audit](../architecture/adr-2026-05-06-erasure-decision-api-and-audit.md) — insbesondere **A2** (evaluate/execute), **§7** (Decision-Taxonomie) und der Unterabschnitt *Decision vs. allowed_actions / blocked_actions*.

**Decision** = fachlich-rechtliche Grundentscheidung; **`allowed_actions`** = konkrete technische Maßnahmen; **`blocked_actions`** = explizit verbotene technische Maßnahmen.

Die **Decision-Werte** beschreiben diese Grundentscheidung (ob ein Vorgang erlaubt, eingeschränkt, blockiert oder einer manuellen Prüfung zugeführt wird). Konkrete Maßnahmen — etwa `minimize_personal_fields`, `mask_personal_fields`, `redact_free_text`, `mask_email`, `replace_actor_with_hash`, `unlink_crm_profile`, `pseudonymize_subject_reference`, `remove_optional_metadata`, `preserve_audit_integrity` — werden über **`allowed_actions`** / **`blocked_actions`** geführt und **nicht** als eigene Decision-Werte modelliert.

Ein eigener Decision-Wert **`minimize_allowed`** wird **nicht** geführt; Minimierung ist eine **Aktion**.

Bei besonders schützenswerten Auditdaten kann die Grundentscheidung statt **`pseudonymize_allowed`** auch **`restrict_processing`** sein; die konkrete Minimierung (z. B. **`mask_personal_fields`**) bleibt auf der **Aktionsseite**. Der Audit-Eintrag selbst bleibt erhalten, soweit die **Nachweisfähigkeit** es erfordert.

**Beispiel (Evaluate-Response, Audit-Klartext):**

```json
{
  "decision": "pseudonymize_allowed",
  "allowed_actions": [
    "minimize_personal_fields",
    "redact_free_text",
    "replace_actor_with_hash",
    "preserve_audit_integrity"
  ],
  "blocked_actions": [
    "delete_audit_event",
    "delete_financial_trace"
  ]
}
```

---

## 7. Technische Mindestanforderungen

*Pfad- und Phasenmodell (evaluate/execute, keine direkte Orchestrierung als Compliance-Endzustand):* [ADR A2, A3, A5](../architecture/adr-2026-05-06-erasure-decision-api-and-audit.md). *Zuordnung Decision ↔ technische Maßnahmen:* siehe §6.1 — **kein** eigener Decision-Wert `minimize_allowed`.

### 7.1 Evaluate API

`POST /privacy/erasure-requests/{request_id}/evaluate`

**Mindest-Response (Beispiel):**

```json
{
  "request_id": "era_123",
  "tenant_id": "tenant_001",
  "subject_id": "subject_abc",
  "decision": "deny_due_to_retention",
  "allowed_actions": [
    "restrict_processing",
    "pseudonymize_contact_fields"
  ],
  "blocked_actions": [
    "hard_delete"
  ],
  "reasons": [
    {
      "code": "GOBD_RETENTION_ACTIVE",
      "entity": "invoice",
      "retention_until": "2033-12-31"
    }
  ],
  "policy_version": "retention-policy-2026-05",
  "requires_manual_review": false,
  "correlation_id": "corr_789"
}
```

### 7.2 Execute API

`POST /privacy/erasure-requests/{request_id}/execute`

**Pflichtregeln — execute darf nur laufen, wenn:**

- `decision_id` existiert
- Entscheidung **nicht abgelaufen** ist
- Entscheidung zur **action** passt
- **actor** berechtigt ist
- **tenant** passt
- **audit pre-write** erfolgreich war

### 7.3 Idempotenz

**Pflicht-Key:** `tenant_id` + `request_id` + `decision_id` + `action`

Wiederholte Ausführung muss **dasselbe fachliche Ergebnis** liefern.

---

## 8. Audit Policy

### 8.1 Was gespeichert werden muss

```json
{
  "audit_id": "aud_123",
  "request_id": "era_123",
  "decision_id": "dec_456",
  "tenant_id": "tenant_001",
  "subject_ref": "subject_hash_abc",
  "actor_id": "actor_123",
  "actor_type": "user",
  "policy_version": "retention-policy-2026-05",
  "decision": "deny_due_to_retention",
  "reason_codes": [
    "GOBD_RETENTION_ACTIVE"
  ],
  "allowed_actions": [
    "restrict_processing"
  ],
  "blocked_actions": [
    "hard_delete"
  ],
  "executed_action": null,
  "result": "blocked",
  "timestamp": "2026-05-06T10:15:00Z",
  "correlation_id": "corr_789"
}
```

### 8.2 Was nicht gespeichert werden sollte

- Klartext-Personendaten, sofern nicht zwingend nötig
- vollständige Rechnungsinhalte im **Privacy-Audit**
- komplette Request-Payloads mit unnötigen personenbezogenen Details
- Passwörter, Tokens, Session-Daten

### 8.3 Schutz des Audits

Audit-Daten müssen:

- **append-only** oder **manipulationsgeschützt** sein
- vor unkontrollierter Änderung geschützt sein
- **zeitlich synchronisiert** erzeugt werden
- **mandantenfähig** getrennt sein
- auswertbar sein
- einer **eigenen Retention** unterliegen

Anschluss **BSI OPS.1.1.5:** Protokolldaten sicher erheben, speichern, auswerten, ordnungsgemäß entsorgen; unkontrolliertes Löschen/Verändern technisch unterbinden.

---

## 9. Backup- und Archiv-Policy

Backups sind **nicht** gleich Produktivtabellen.

| Regel | Inhalt |
|-------|--------|
| **B1** | Löschungen werden **nicht** einzeln in **immutable** Backups „nachgezogen“ |
| **B2** | Wiederherstellung aus Backup darf gelöschte/gesperrte Daten **nicht** ungeprüft reaktivieren |
| **B3** | Nach **Restore** muss ein **Reconciliation-Job** laufen |
| **B4** | Backup-Retention muss **dokumentiert** sein |
| **B5** | Backup-Löschung/Vernichtung folgt **BSI CON.3** und **CON.6** |

**CON.3:** rechtliche Anforderungen, Lösch-/Vernichtungsanforderungen, Zuständigkeiten für Datensicherungen **erheben und dokumentieren**.

---

## 10. GoBD-/ERP-spezifische Policy

### 10.1 Unveränderbarkeit

Für ERP-/FiBu-relevante Daten gilt:

- keine **überschreibende** Änderung des Beleginhalts
- keine **physische Löschung** während Retention
- Korrektur nur durch **Storno**, **Gegenbuchung**, **Statuswechsel** oder **neue Version** (fachlich mit FiBu abstimmen)
- ursprünglicher Inhalt muss **feststellbar** bleiben

Bezug **AO § 146** / **HGB § 239**.

### 10.2 ERP-Pseudonymisierung statt Beleglöschung

- CRM-Kontakt darf anonymisiert/gelöscht werden (wenn Policy).
- ERP-Beleg bleibt erhalten.
- Personenbezug **minimieren**.
- Referenz **pseudonymisieren**, soweit fachlich und rechtlich zulässig.
- Beleg-Snapshot bleibt, wenn **aufbewahrungspflichtig**.

### 10.3 Keine Löschung dieser Objekte während Retention

`invoice` · `invoice_line` · `booking_entry` · `journal_entry` · `payment_reference` · `tax_relevant_document` · `audit_event` · `period_closure` · `delivery_note_if_tax_relevant` · `commercial_letter_if_business_relevant`

*Namensmapping auf konkrete Tabellen/Entitäten im ERP-Fachmodell durch ERP-Fachbereich.*

---

## 11. Legal-Hold-Policy

Ein **Legal Hold** blockiert u. a.:

`delete` · `anonymize` · `pseudonymize` · `unlink` · `archive_purge` · `backup_purge`

— **sofern** die Maßnahme **Nachweisfähigkeit**, **Beweissicherung** oder **Verteidigung von Ansprüchen** beeinträchtigen kann.

**Pflichtfelder (Beispiel):**

```json
{
  "legal_hold_id": "lh_123",
  "scope": "subject|contract|invoice|tenant|case",
  "reason": "legal_claims",
  "created_by": "legal_actor",
  "created_at": "2026-05-06T10:00:00Z",
  "review_until": "2026-12-31",
  "status": "active"
}
```

---

## 12. Sicherheits- und Berechtigungsrahmen

### 12.1 Rollen (Beispielkatalog)

`privacy_requester` · `privacy_operator` · `data_protection_officer` · `legal_reviewer` · `erp_domain_owner` · `finance_reviewer` · `security_admin` · `system_service`

### 12.2 Vier-Augen-Prinzip

Pflicht u. a. bei:

- `manual_legal_review_required`
- `force_restrict` (falls als Aktion eingeführt — nur mit ADR-Revision)
- `retention_override`
- `policy_change`
- `bulk_erasure`
- `tenant_wide_action`

### 12.3 Technische Zugriffsvorgaben

- **Tenant-Kontext** ist Pflicht.
- **Actor-Kontext** ist Pflicht.
- **Service-Accounts** benötigen explizite Scopes.
- **Execute** braucht **stärkere** Rechte als **Evaluate**.
- **Policy-Änderungen** sind **versioniert** und **auditpflichtig**.

**ORP.4:** Zugriff auf schützenswerte Ressourcen nur für berechtigte Identitäten/Komponenten.

---

## 13. Repo-Einbindung

**Datei im Repository:** `docs/policies/erasure-retention-audit-policy.md`

Diese Datei ist der **zentrale Policy-Rahmen** für Erasure, Retention und Audit im Repository. Änderungen am Normsatz oder an der Decision-Matrix lösen ein **Stakeholder-Review** aus (wie ADR-Revision).

---

## 14. Go-Live-Gate

Produktivfreigabe nur, wenn **alle** Punkte erfüllt sind:

- [ ] Datenklassenmatrix liegt vor
- [ ] Retention-Matrix liegt vor
- [ ] Evaluate/Execute-Split umgesetzt
- [ ] Hard-Delete technisch blockiert bei Retention/Legal Hold
- [ ] Audit-Persistenz produktiv aktiv
- [ ] Policy-Versionierung umgesetzt
- [ ] Tenant-/Actor-Kontext verpflichtend
- [ ] Backup-/Restore-Verhalten dokumentiert
- [ ] Restore-Reconciliation umgesetzt
- [ ] CRM-Orchestrierung hängt hinter Execute
- [ ] Direkte Delete-Endpunkte geschützt oder deaktiviert
- [ ] Legal hat Policy-Matrix abgenommen
- [ ] Datenschutz hat Betroffenenprozess abgenommen
- [ ] ERP-Fachbereich hat Beleg-/Geschäftsvorfallregeln abgenommen
- [ ] FiBu hat Buchungs-/Periodenregeln abgenommen
- [ ] Architektur hat Schnittstellenmodell abgenommen

---

## 15. Klare Vorgabe für VALEO-NeuroERP

1. Bestehende CRM-HTTP-Orchestrierung bleibt **nur Übergang**.
2. **Kein** produktiver Delete **ohne** Erasure Decision API.
3. ERP-/FiBu-/Rechnungsdaten werden **nicht physisch gelöscht**, solange **Retention aktiv** ist.
4. CRM-Daten dürfen gelöscht/anonymisiert werden, wenn **kein** Nachweis-, ERP-, FiBu-, Legal- oder Vertragsbezug besteht (Policy entscheidet).
5. Bei Belegbezug: CRM **entkoppeln**, ERP **pseudonymisieren/minimieren**, **nicht** Beleg löschen.
6. Jeder **Ablehnungsgrund** wird als **Audit-Entscheidung** gespeichert.
7. **Unklare Datenlage** → manuelle Prüfung, **nicht** Löschung.
8. Backups folgen **eigener** Retention; Restore muss gelöschte/gesperrte Daten erneut **sperren/anonymisieren** (Reconciliation).
9. Policy-Änderungen sind **versioniert** und **abnahmepflichtig**.
10. Go-Live **ohne** Legal-/Datenschutz-/ERP-/FiBu-/Architektur-Abnahme ist **blockiert**.

**Kernaussage:** Hard-Delete ist die **Ausnahme**. Policy-Entscheidung, Einschränkung, Pseudonymisierung, Audit und Retention sind der **Standard**.

---

*Stand: Entwurf 2026-05-06 — Abnahme durch genannte Stakeholder ausstehend.*

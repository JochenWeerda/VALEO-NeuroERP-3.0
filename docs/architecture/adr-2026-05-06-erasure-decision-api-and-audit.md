# ADR: Erasure Decision API + Audit

| Feld | Inhalt |
|------|--------|
| **Status** | Entwurf |
| **Abnahme erforderlich durch** | Architektur, Legal, Datenschutz, ERP-Fachbereich |
| **Gültigkeit** | **Nicht produktionsfreigebend** ohne formale vierseitige Abnahme dieser Vorgaben (bzw. des nach Revision „akzeptiert“ markierten ADR mit identischem Kern). |
| **Datum** | 2026-05-06 |
| **Meilenstein-Bezug** | [TODO-SPRINT-001](../agent-ops/slices/TODO-SPRINT-001.yaml) (M3.0–M3.4); Ergänzung zu M-08/M-09 (GDPR Export / Löschung) |

## Einordnung (verbindlich für diesen Entwurf)

Die bestehende **HTTP-Orchestrierung** darf als **Übergangs-/Demonstrationsweg** bestehen bleiben, gilt aber **nicht** als finale Architektur für **GoBD-, FiBu-, Rechnungs- oder Audit-Daten**.

**Rechtlicher Rahmen (keine Rechtsberatung; fachliche Leitplanke für Produktgestaltung):**

- Die **DSGVO** kennt ein Recht auf Löschung (**Art. 17**), jedoch **unter Bedingungen und Ausnahmen**, u. a. wenn Verarbeitung zur **Erfüllung rechtlicher Pflichten** oder zur **Geltendmachung/Verteidigung von Rechtsansprüchen** erforderlich ist.
- Nach **deutschem Recht, einschließlich BDSG-Relevanz**, kann unter bestimmten Umständen an die Stelle einer Löschung die **Einschränkung der Verarbeitung** treten, etwa wenn **Aufbewahrungsfristen** entgegenstehen.
- Für **GoBD-relevante elektronische Unterlagen**: **aufbewahrungspflichtige Daten** dürfen **vor Ablauf** der Aufbewahrungsfrist **nicht gelöscht** werden und müssen **unveränderbar** erhalten bleiben (Auslegung und konkrete Fristen durch **Legal/Steuer** freizugeben; dieses Dokument nimmt keine finale GoBD-Auslegung vor).

---

## Kontext

Lösch-, Anonymisierungs-, Pseudonymisierungs- und Verarbeitungs­einschränkungs-Anfragen für Daten mit möglichem **ERP-/FiBu-/GoBD-/Auditbezug** sind **keine** trivialen DELETE-Calls. Sie erfordern **policy-gestützte Entscheidungen**, versionierte Dokumentation, ein **evaluate/execute-Split** und **revisionssichere Audits**.

**Ziel dieses ADR:** Architektur-, Compliance- und Abnahme-Vorgaben **vor** breitem Prototyping verbindlich festhalten, damit **Demo-Orchestrierung nicht** versehentlich als **Compliance-Endarchitektur** interpretiert wird.

---

## Verbindliche Produktfrei­gabe-Leitplanke (Roadmap‑Satz)

> **Produktive** Löschung, Anonymisierung oder Entkopplung personenbezogener Daten mit **möglichem ERP-, FiBu-, Rechnungs-, GoBD- oder Auditbezug** ist erst zulässig, wenn eine **versionierte Policy-Entscheidung** vorliegt, der **evaluate/execute-Split** umgesetzt ist, **jede** relevante Entscheidung **auditierbar persistiert** wird und **Architektur, Legal, Datenschutz** sowie **ERP-Fachbereich** die Policy-Matrix abgenommen haben.

**Kurzfassung:** Demo-Orchestrierung ja. Produktive Compliance-Löschung erst nach **Decision API**, **Policy**, **Statusmodell**, **Audit** und **fachlicher Abnahme**.

---

## 1. Vorgaben Architektur

### A1 — Kein produktiver Hard-Delete ohne Decision

Es darf **keinen direkten produktiven Löschpfad** wie

- `DELETE /contacts/{id}`
- `DELETE /customers/{id}`
- `DELETE /erp-subjects/{id}`

geben, wenn **ERP-, FiBu-, Beleg-, Rechnungs-, Vertrags- oder Auditbezug möglich** ist (Klassifikation durch Policy/Datenklassen; konservativ bei Unklarheit).

**Pflichtketten­modell:**

`evaluate` → **decision** → `execute` → **audit** → **verify**

### A2 — Evaluate/Execute-Split ist Pflicht

Jede Lösch-, Anonymisierungs-, Pseudonymisierungs- oder Einschränkungsaktion läuft **zweiphasig**:

- `POST /privacy/erasure-requests/{id}/evaluate`
- `POST /privacy/erasure-requests/{id}/execute`

**evaluate** liefert u. a. **`decision`**, **`allowed_actions`** und **`blocked_actions`**; technische Maßnahmen (Minimierung, Maskierung, Redaction u. ä.) gehören in die Aktionslisten, **nicht** in die Decision-Taxonomie — siehe **§7** (Unterabschnitt *Decision vs. allowed_actions / blocked_actions*) und [Policy §6.1](../policies/erasure-retention-audit-policy.md).

**execute** darf nur laufen, wenn eine **gültige, nicht abgelaufene und auditierte** Entscheidung existiert (Details Speicherung/Lifetime: bei Implementierung festzulegen und hier zu ergänzen).

### A3 — Policy Engine oder Policy-Modul als zentrale Instanz

Es muss eine **zentrale Entscheidungsschicht** existieren (anfangs bewusst einfach, aber **konzeptionell** klar abgegrenzt).

**Minimaler Rückgabewert (strukturiert, erweiterbar):**

```json
{
  "decision": "deny_due_to_retention",
  "allowed_actions": ["restrict_processing", "pseudonymize_contact_fields"],
  "blocked_actions": ["hard_delete"],
  "policy_version": "retention-policy-draft-001",
  "requires_manual_review": false
}
```

### A4 — Entscheidungen sind versioniert

Jede Entscheidung muss persistierbar dokumentieren (für Audit und Nachweis):

| Feld | Beschreibung |
|------|----------------|
| Policy-Version | z. B. `retention-policy-draft-001` |
| Zeitpunkt | UTC o. ä. |
| Tenant | Tenant-Kontext |
| Actor | handelndes Subjekt (s. Security-Vorgaben) |
| geprüfte Datenquellen | welche Systeme/Domänen einbezogen wurden |
| Entscheidungsgrund | normierter Code + ggf. erläuternder Text |
| erlaubte Aktionen | Liste |
| blockierte Aktionen | Liste |
| Correlation-ID | durchgängige Korrelation Request↔Audit |

### A5 — Bestehende HTTP-Orchestrierung nur hinter Decision Layer

| Nicht erlaubt | Erlaubt |
|---------------|---------|
| Request → HTTP-Orchestrierung löscht **direkt** | Request → **evaluate** → Decision erlaubt Aktion → **execute** ruft Orchestrierung auf |

---

## 2. Vorgaben Legal

### L1 — Keine finale Rechtslogik nur als verstreute if-Statements

Aufbewahrungsfristen, Legal Holds und Ablehnungsgründe müssen in einer **pflegbaren Policy-Matrix** (oder gleichwertigem, review-fähigem Regelwerk) abbildbar sein, **nicht** ausschließlich als implizite Verzweigungen in Einzelservices.

Beispiel-Spalten: **Datenklasse** | **Bedingung** | **Aktion** | **Freigabe erforderlich**

### L2 — GoBD-/FiBu-Bezug blockiert Hard-Delete (Standard)

Sobald ein Subjekt mit **Rechnungen, Buchungen, Belegen, steuerlich relevanten Dokumenten** oder **Auditnachweisen** verbunden ist, ist **produktiver Hard-Delete standardmäßig zu blockieren**.

**Zulässige Alternativen** (Auswahl durch Policy, nicht technisch willkürlich):

- Verarbeitung einschränken
- Kontaktfelder anonymisieren
- ERP-Referenzen pseudonymisieren
- CRM-Profil entkoppeln
- Löschung nach Ablauf der Retention **vormerken**

### L3 — Legal Hold übersteuert Löschfreigabe

Bei **aktivem Legal Hold** darf keine Löschung, Anonymisierung oder Entkopplung erfolgen, die **Beweissicherung**, **Nachweisbarkeit** oder **Verfahrensfähigkeit** beeinträchtigt (genaue Definition mit Legal).

### L4 — Manuelle Prüfung als offizieller Entscheidungszustand

Unklare Fälle dürfen **nicht** technisch „best effort“ gelöscht werden. **Pflichtzustand:** `manual_legal_review_required` (s. auch erlaubte Decision-Werte unten).

---

## 3. Vorgaben Datenschutz

### D1 — Betroffenenrechte als Prozess

Ein Löschersuchen ist ein **Datenschutzprozess**, kein technischer Delete-Call.

**Minimal-Status (konsolidiert; exakte Übergänge mit Legal/DSB abstimmen):**

`REQUESTED` → `IDENTITY_VERIFIED` → `DISCOVERY_RUNNING` → `POLICY_EVALUATED` →
`APPROVED_FOR_DELETE` | `APPROVED_FOR_ANONYMIZATION` | `APPROVED_FOR_PSEUDONYMIZATION` | `APPROVED_FOR_RESTRICTION` | `DENIED_RETENTION` | `LEGAL_REVIEW_REQUIRED` →
`EXECUTING` → `EXECUTED` | `FAILED` → `VERIFIED` → `CLOSED`

### D2 — Datenminimierung im Audit

**Erlaubt (Beispiel):**

```json
{
  "subject_ref": "subj_hash_123",
  "actor_ref": "actor_hash_456",
  "decision": "DENIED_RETENTION",
  "reason": "GOBD_RETENTION_ACTIVE"
}
```

**Nicht empfohlen:** unnötige Klartexte (Name, E-Mail, Rechnungsnummer im Audit-Event).

### D3 — Transparente Ablehnung

Bei Blockaden muss die API **fachlich erklärbar** antworten, z. B.:

```json
{
  "status": "not_deleted",
  "reason": "RETENTION_ACTIVE",
  "effective_action": "processing_restricted",
  "message": "Hard delete is blocked because retention obligations apply."
}
```

### D4 — Keine stillen Teillöschungen

Wenn nur ein Teil der Daten verändert werden darf, muss das **explizit** dokumentiert werden (Antwort + Audit), z. B.:

- CRM-Kontakt anonymisiert
- ERP-Belegreferenz erhalten
- Verarbeitung eingeschränkt
- Hard-Delete blockiert

---

## 4. Vorgaben ERP-Fachbereich

### E1 — ERP-Belegkette bleibt intakt

Rechnungen, Buchungen, Angebote mit Folgebelegen, Lieferscheine, Audit-Events und steuerlich relevante Dokumente dürfen **nicht** so verändert werden, dass die **fachliche Nachvollziehbarkeit** verloren geht.

### E2 — Kontaktprofil und Geschäftsvorfall trennen

- **CRM-Kontakt:** Name, E-Mail, Telefon löschbar/anonymisierbar (wenn Policy es erlaubt).
- **ERP Invoice Snapshot:** belegrelevante Informationen bleiben erhalten.
- **ERP Subject Reference:** pseudonymisierte Referenz statt Klartextkontakt.

### E3 — Fachstatus beeinflusst Entscheidung

Die Policy muss mindestens solche **fachlichen Zustände** berücksichtigen (Erweiterung mit ERP-Fachbereich):

- offene Anfrage
- aktives Angebot
- Auftrag in Bearbeitung
- offene Lieferung
- offene Rechnung
- bezahlte Rechnung innerhalb Aufbewahrung
- abgeschlossene Retention
- aktiver Streitfall
- aktiver Vertrag
- aktiver Audit-/Prüfungsfall

### E4 — Pseudonym im Core statt Kontakt-Delete (bevorzugtes Muster)

- Kontakt löschen/anonymisieren im **CRM**
- **ERP-Core** behält **pseudonyme Subject-Referenz**
- Beleg-/Auditdaten bleiben **fachlich nachvollziehbar**

---

## 5. Vorgaben Security / Betrieb

### S1 — Execute braucht Berechtigung

**execute** nur für berechtigte Rollen oder explizite Service-Accounts.

**Pflichtfelder im Ausführungskontext (Minimum):**

```json
{
  "actor_id": "actor_123",
  "actor_type": "user",
  "tenant_id": "tenant_001",
  "correlation_id": "corr_789"
}
```

### S2 — Idempotenz ist Pflicht

Wiederholtes Ausführen desselben logischen Vorgangs darf **keine inkonsistenten Zustände** erzeugen.

**Pflicht:** `request_id` + `decision_id` + `action` = **Idempotency Key** (konkrete technische Abbildung: bei Implementierung).

### S3 — Backups und Replikate

Produktivdaten, **Backups**, Logs, Suchindizes und Exporte sind in der **Datenklassifikation** zu berücksichtigen. **Backup-Löschung ≠ Produktivdatenlöschung** ohne eigene Regeln.

---

## 6. Vorgaben QA / Abnahme

### Q1 — Mindest-Testfälle

| Fall | Erwartung |
|------|-----------|
| CRM-only Kontakt ohne ERP-Bezug | Delete oder Anonymisierung möglich (wenn Policy) |
| Kontakt mit Rechnung | Hard-Delete blockiert |
| Kontakt mit offener Rechnung | Hard-Delete blockiert; Verarbeitung ggf. eingeschränkt |
| Kontakt mit Legal Hold | Manuelle/Legal-Prüfung erforderlich |
| Unbekannte Datenlage | Keine Löschung; Review erforderlich |
| Wiederholter execute-Call | Idempotentes Ergebnis |
| Fehlender Actor | Execute abgelehnt |
| Fehlender Tenant | Evaluate/Execute abgelehnt |
| Policy-Version fehlt | Entscheidung ungültig |
| Audit-Persistenz schlägt fehl | Execute darf nicht als erfolgreich gelten |

### Q2 — Go-Live-Gate

Produktiver Go-Live ist **blockiert**, solange nicht erfüllt:

- [ ] Architektur hat **evaluate/execute-Split** abgenommen
- [ ] Legal hat **Policy-Matrix** freigegeben
- [ ] Datenschutz hat **Betroffenenprozess** freigegeben
- [ ] ERP-Fachbereich hat **Datenklassifikation** freigegeben
- [ ] **Audit-Persistenz** ist produktiv aktiv
- [ ] Direkte produktive **Delete-Pfade** sind deaktiviert oder geschützt
- [ ] Testfälle für **Retention/GoBD/FiBu** sind grün

---

## 7. Gemeinsame verbindliche Entscheidungswerte

Die **kanonische** Liste inkl. Matrix, API-Beispiele und Go-Live-Gate:
**[Policy: Erasure, Retention & Audit](../policies/erasure-retention-audit-policy.md)**.

Das ADR übernimmt hier nur die **Minimalmenge**; Änderungen am Wertekatalog **synchron** mit Policy und Abnahme durchführen.

Die Decision API darf **nur** definierte Werte zurückgeben (Erweiterung nur per **ADR-Revision + Policy-Revision** + Legal/DSB):

| Erlaubt | Kurzbeschreibung |
|---------|------------------|
| `delete_allowed` | Hard-Delete für diesen Scope explizit erlaubt |
| `anonymize_allowed` | Anonymisierung erlaubt |
| `pseudonymize_allowed` | Pseudonymisierung erlaubt |
| `restrict_processing` | Verarbeitungseinschränkung als wirksame Maßnahme |
| `deny_due_to_retention` | Block wegen Aufbewahrung |
| `deny_due_to_legal_hold` | Block wegen Legal Hold |
| `deny_due_to_open_business_process` | Block wegen offenem Geschäftsvorgang |
| `deny_due_to_legal_claims` | Block wegen Rechts-/Anspruchs-/Verteidigungskontext (Policy-Detail) |
| `manual_legal_review_required` | Pflichtmanuelle juristische Prüfung |
| `insufficient_information` | Nicht löschen/umsetzen ohne weitere Daten |

**Nicht erlaubt** (keine schwammigen Produktentscheidungen):

`maybe`, `partial_success`, `best_effort_delete`, `unknown_but_deleted`, `best_effort`, `partial_delete_unknown`, `force_delete`, `delete_anyway`

### Decision vs. `allowed_actions` / `blocked_actions`

**Normativ deckungsgleich mit der Policy:** **Decision** = fachlich-rechtliche Grundentscheidung; **`allowed_actions`** = konkrete technische Maßnahmen; **`blocked_actions`** = explizit verbotene technische Maßnahmen. Ausführlichere Abgrenzung und zweites Evaluate-Beispiel: [Erasure-Policy §6.1](../policies/erasure-retention-audit-policy.md).

Die **Decision** beschreibt die fachlich-rechtliche Grundentscheidung. Sie legt fest, ob ein Vorgang grundsätzlich erlaubt, eingeschränkt, blockiert oder einer manuellen Prüfung zugeführt wird.

Konkrete technische Maßnahmen werden **nicht** als eigene Decision-Werte modelliert, sondern über **`allowed_actions`** und **`blocked_actions`** ausgedrückt (v. a. in der **Evaluate**-Antwort; **Execute** wählt eine zulässige Aktion unter Maßgabe der Decision).

Beispiele für `allowed_actions`:

- `minimize_personal_fields`
- `mask_personal_fields`
- `redact_free_text`
- `replace_actor_with_hash`
- `unlink_crm_profile`
- `pseudonymize_subject_reference`
- `preserve_audit_integrity`

Damit bleibt die Decision-Taxonomie **stabil** und **fachlich prüfbar**. Maßnahmen wie Datenminimierung, Maskierung oder Redaction sind **Ausführungsdetails** innerhalb von Entscheidungen wie **`pseudonymize_allowed`**, **`anonymize_allowed`** oder **`restrict_processing`**.

Ein eigener Decision-Wert **`minimize_allowed`** wird **bewusst nicht** geführt; Minimierung ist eine **Aktion**, keine Decision.

Für besonders schützenswerte **Auditdaten** kann die Entscheidung beispielsweise **`restrict_processing`** lauten, während **`allowed_actions`** nur Maskierung oder Reduktion personenbezogener Felder erlauben. Der Audit-Eintrag selbst bleibt erhalten, damit die **Nachweisfähigkeit** nicht zerstört wird.

**Beispiel (Evaluate-Response, gekürzt):**

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

## 8. Nicht-Ziele dieses Entwurfs

Dieser Entwurf ist **nicht**:

- Rechtsberatung
- finale Datenschutzfreigabe
- finale GoBD-Auslegung
- produktive Löschfreigabe
- vollständige Policy-Matrix
- Implementierungsfreigabe für Hard-Delete

Dieser Entwurf **ist**:

**Architektur- und Fachvorgabe zur Abnahme** durch Architektur, Legal, Datenschutz und ERP-Fachbereich.

---

## Konsequenzen (technisch/strategisch)

- Übergangs-Orchestrierung bleibt technisch möglich, darf aber **nicht** als Produktions-Compliance-Pfad für betroffene Domänen dienen.
- Implementierung erst nach **Abnahme** dieses ADR bzw. nach explizitem „akzeptiert“ mit ggf. Anhang (Policy-Matrix-Version).

## Nächste Schritte (nach Abnahme)

1. Policy-Matrix und Blocker-Katalog (Legal/ERP) versionieren.
2. Prototyp: **evaluate** / **execute** mit Platzhalter-Policy; **execute** nur bei gültiger Decision; Audit-Schnittstelle von Anfang an.
3. ADR-Status auf **akzeptiert** setzen; Go-Live-Gate Q2 abarbeiten.

## Links

- [TODO-SPRINT-001](../agent-ops/slices/TODO-SPRINT-001.yaml) (M3.0–M3.4)
- **[Policy-Rahmen: Erasure, Retention & Audit](../policies/erasure-retention-audit-policy.md)** (Datenklassen, Retention-Defaults, Matrix, API-/Audit-Vorgaben)
- [ADR: Auth- und Tenant-Kontext](adr-2026-04-24-auth-tenant-context.md)

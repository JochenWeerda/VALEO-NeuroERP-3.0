# DOM-DOC-004 — Revisionssicherer Nachweisraum (2026-06-10)

Sprint-Ziel: durchgängige GoBD-Nachweiskette (Upload→Typ→Vorgangsbezug→Version→
Freigabe→Audit→Bescheid/Rückmeldung→Artefaktstatus→revisionssichere Ablage).
Erster Slice (004.1): read-only **Nachweis-/Artefakt-Spine** auf dem bestehenden
Docflow.

## Ist-Befund (kartiert)
`domain_docflow` ist vorhanden und befüllt:
| Tabelle | Inhalt |
|---|---|
| `document_headers` | Dokument/Vorgang (doc_type, doc_number, status, version, source, printed/exported-Audit) |
| `document_artifacts` | **revisionssichere Ablage**: `content_hash_sha256`, `storage_key`, file_name |
| `document_links` | Vorgangskette (from/to header, relation_type) |
| `document_postings` | Buchungsbezug (journal_entry_id, posted_at) |

## Slice 004.1 — Nachweis-Spine (umgesetzt, read-only)
- Service: `app/services/docflow_evidence_service.py`
  - `evidence(doc)` — Header + Artefakte (mit Hash) + Vorgangskette + Buchungen +
    Druck-/Export-Audit + **Lücken** (reine `evaluate_gaps`: kein Artefakt, Artefakt
    ohne SHA-256, Rechnung nicht gebucht/exportiert).
  - `list_documents()` — Picker mit Vollständigkeits-Flags (Artefakt/revisionssicher/gebucht).
- API: `GET /docflow/evidence/detail?doc=…` + `GET /docflow/evidence/documents`
  (Pfad `evidence/detail`, NICHT `/docflow/evidence` — letzteres kollidiert mit
  dem bestehenden `/docflow/{id}` des großen docflow-Routers).
- Frontend: `pages/docflow/nachweisraum.tsx` (Picker + Artefakte/Hash + Vorgangskette
  + Buchungen + Lücken) + Hooks `lib/api/docflow-evidence.ts` + Nav „Nachweisraum
  (DMS/GoBD)" (finance.tsx) + Route-Alias.
- Tests: `tests/test_docflow_evidence.py` (5 grün).

### Verifiziert (echte Docflow-Daten)
- `PYTEST-…`: 2 PDF-Artefakte mit SHA-256 → revisionssicher, 0 Lücken.
- `SIV-2026-000005` (sales_invoice, reversed): 0 Artefakte → Lücken „Kein Artefakt"
  + „kein GoBD-Export"; Vorgangskette zeigt Lieferschein→Rechnung.

## Folge-Slices
- **004.2** Artefakt-Upload + Versionierung + Freigabe-Status-Transitions (write).
- **004.3** Bescheid-/Rückmeldungspfad + Wiedervorlage am Vorgang.
- **004.4** GoBD-Exportpaket je Vorgang + DMS-/Paperless-Liveprobe.
- **004.5** Browser-E2E + UAT-Nachweispaket.

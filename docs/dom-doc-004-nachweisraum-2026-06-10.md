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

## Slice 004.2 — Artefakt-Upload + Versionierung + Freigabe (umgesetzt, 2026-06-11)
- Migration `doc_artifact_version_20260611` — `document_artifacts` +`version`,
  +`freigabe_status` (entwurf→freigegeben→archiviert) + Freigabe-Audit. Idempotent.
- Service: `app/services/docflow_artifact_service.py` — reine `next_version`,
  `valid_transition` (entwurf→freigegeben→archiviert), `sha256_hex`. `upload_artifact`
  (SHA-256 über Inhalt, laufende Version je Header/Typ, storage_key generiert),
  `set_freigabe` (Transition-Guard), `list_artifacts` (Versionen + „aktuell"-Flag).
- API (unter `/docflow/evidence/artifacts`, NICHT `/docflow/{id}`): `GET .../artifacts`,
  `POST .../artifacts`, `POST .../artifacts/{id}/freigabe`.
- Frontend: `pages/docflow/artefakt-freigabe.tsx` (Dokument-Picker + Upload-Form +
  Artefakt-Liste mit Version/Hash/Freigabe-Aktionen) + Hooks `lib/api/docflow-artifact.ts`
  + Nav „Artefakt-Upload & Freigabe" + Route.
- Tests: `tests/test_docflow_artifact.py` (4 grün).

### Verifiziert (Live, mit Restore)
SIV-2026-000005: Upload v1 + v2 (gleicher Typ, Versionierung), v2 entwurf→freigegeben
→archiviert; archiviert→freigegeben → 422; Liste zeigt v2 „aktuell".

## Folge-Slices
- **004.3** Bescheid-/Rückmeldungspfad + Wiedervorlage am Vorgang.
- **004.4** GoBD-Exportpaket je Vorgang + DMS-/Paperless-Liveprobe.
- **004.5** Browser-E2E + UAT-Nachweispaket.

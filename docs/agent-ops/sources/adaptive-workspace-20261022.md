<a id="adaptive-workspace-20261022"></a>

## Adaptive Workspace (ADAPTIVE-WORKSPACE-20261022)

Stand 2026-10-23. Slice-Status bleibt **in Arbeit**. Dieser Abschnitt ist die Quelle; `python scripts/generate_agent_handbuch.py` setzt ihn in den Index. Kein Abschluss.

### Im Code

- Registry mit den vier Ebenen `personal`, `situational`, `proactive`, `dialog`. Priorisierung liefert Reason-Codes. Der Pin wird im Effect persistiert; die Storage-Keys von Overlay und Composition tragen Mandant und `sub`.
- Die Dialogebene oeffnet die bestehende Palette mit Strg+K. Katalog-Aliase laufen als `dryRun` und loesen kein Auto-Submit aus.
- Die Inbox traegt `document_kind`. Prefill gibt es nur fuer die Eingangsrechnung. Oeffnen ohne Art bleibt aus. Approve antwortet 409 (`booking_not_from_inbox`). Pruefcodes aus Unsicherheiten und Dubletten stehen an der Rangzeile. Kontrakt-Match (Kon/Agrar) und `linked_document_id` (nur `documents.id`-Join) sind verdrahtet.
- Die Composition filtert Inbox und offene Abrufe. Das Dispo-Board sitzt im Renderer und in der Studio-Composition. Ein Drop ist keine Mengenbuchung.
- SSE (`/api/events?stream=workspace`) und NATS verwenden die Ist-Namen. Die Soll-Namen `assignment_confirmed`, `document_proposed` und `document_posted` sind Annotation und werden nicht als Subject publiziert.
- Agrar-Schritte erscheinen in der Rangliste nur, wenn der Server sie liefert.
- Die MCP-Tools `workspace.fachaktion.katalog` und `workspace.fachaktion.resolve` schreiben nicht in die Datenbank.

### Offen

- Browser: SSO manuell ok (synthetische Kennung frueher abgewiesen). Live-Confirm/Screenshot braucht Session.
- Positionszeilen: Regex-Fixtures ok; Live-Tesseract oft leer; Claude nur Fallback.
- Kontrakt-Abgleich: verdrahtet wenn Extrakt `contract_id` liefert und Kon/Agrar-Stamm trifft; sonst Gap `kontrakt_abgleich_nur_bei_kontraktnummer_im_extrakt`.
- `linked_document_id`: nur bei eindeutigem `documents.id`-Dubletten-Treffer; sonst Gap `linked_document_id_nur_bei_eindeutigem_documents_treffer`.
- Gutschrift/Lieferschein ohne Detailroute trotz ggf. gesetzter ID; Wiegeschein nur mit ID.
- Kon-Abrechnung ohne QS-Feld.
- Verladung-Sicherheit bleibt Codex-Besitz; Basiskarte aussen.
- KI-Ranking bleibt noop.
- Keine Katalog-Tastaturkuerzel.

### Screenshot

Relative Pfade von dieser Quelle (`docs/agent-ops/sources/`):

- [Start / Handlungsbedarf](../../../evidence/screenshots/adaptive-workspace-start-handlungsbedarf.png)
- [Command Center / Strg+K](../../../evidence/screenshots/adaptive-workspace-command-center.png)
- [Inbox (Queue leer)](../../../evidence/screenshots/adaptive-workspace-inbox.png)
- [Dispositionstafel](../../../evidence/screenshots/adaptive-workspace-disposition.png)
- [Studio Composition Preview](../../../evidence/screenshots/adaptive-workspace-studio.png)
- **Nicht vorhanden:** `adaptive-workspace-inbox-queue.png` (Labels an Queue-Zeile) — STOP ohne Mayan-OCR-Eingang.

Handbuch-Index-Abschnitt manuell mit denselben Links gepflegt; Generator nicht voll ausgefuehrt.

"""SPEC-P1-06 Welle 11: Mail-Arbeitsplatz, TAPI, WhatsApp-Inbox."""

from datetime import datetime

import pytest

from app.api.v1.endpoints import mail_workspace as mail_module
from app.api.v1.endpoints import tapi as tapi_module
from app.api.v1.endpoints import whatsapp_intake as wa_module
from app.api.v1.schemas import crm_channel_bundle_schemas as crm

pytestmark = pytest.mark.unit

WELLE11_MODULE = [mail_module, tapi_module, wa_module]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in getattr(route, "methods", []) or []:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = getattr(route, "response_model", None)
    return out


@pytest.mark.parametrize("module", WELLE11_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        if model is None:
            continue
        text = str(model)
        if (
            model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


def test_mail_workspace_shapes():
    _assert_kein_feldverlust(
        crm.MailMessagePageOut,
        {
            "items": [
                {
                    "id": "m1",
                    "role_key": "sales",
                    "message_id": "msg-1",
                    "direction": "incoming",
                    "status": "received",
                    "from_address": "a@b.de",
                    "to_addresses": ["c@d.de"],
                    "subject": "Betreff",
                    "contact_id": None,
                    "document_type": None,
                    "document_ref": None,
                    "document_route": None,
                    "assigned_to": None,
                    "provider_ref": None,
                    "error_message": None,
                    "received_at": datetime(2026, 9, 1),
                    "sent_at": None,
                    "created_at": datetime(2026, 9, 1),
                    "updated_at": datetime(2026, 9, 1),
                    "attachment_count": 1,
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
        },
    )
    _assert_kein_feldverlust(
        crm.MailAttachmentOut,
        {
            "id": "a1",
            "message_id": "m1",
            "filename": "x.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 10,
            "sha256": "abc",
            "transfer_status": "pending",
            "dms_document_id": None,
            "created_at": datetime(2026, 9, 1),
            "subject": "Betreff",
            "role_key": "sales",
        },
    )
    _assert_kein_feldverlust(
        crm.MailDraftCreatedOut,
        {"id": "m1", "status": "draft", "message_id": "draft-1@valeo.local"},
    )
    _assert_kein_feldverlust(
        crm.MailAssignOut,
        {
            "id": "m1",
            "status": "received",
            "contact_id": "K-1",
            "document_type": "auftrag",
            "document_ref": "A-1",
            "document_route": "/verkauf",
            "assigned_to": "u1",
        },
    )
    _assert_kein_feldverlust(
        crm.MailQueueOut,
        {"id": "m1", "status": "queued", "provider_ref": "p1"},
    )
    _assert_kein_feldverlust(
        crm.MailTransferOut,
        {"id": "a1", "status": "transferred", "dms_document_id": "dms-1"},
    )


def test_tapi_and_whatsapp_shapes():
    call = {
        "id": "c1",
        "caller": "012345",
        "called": "0678",
        "richtung": "ein",
        "kunden_nr": "K-1",
        "kunde_name": "Hof",
        "status": "neu",
        "acked": False,
        "created_at": "2026-09-01T10:00:00",
    }
    _assert_kein_feldverlust(crm.TapiCallOut, call)
    _assert_kein_feldverlust(crm.TapiAckOut, {"ok": True})
    _assert_kein_feldverlust(
        crm.WhatsAppInboxOut,
        {
            "id": "w1",
            "raw_text": "2t Weizen",
            "absender": "+49",
            "quelle": "whatsapp",
            "eingegangen_am": "2026-09-01T10:00:00",
            "status": "geparst",
            "parsed": {"kunde": "Hof", "positionen": []},
            "kunden_nr": "K-1",
            "kunde_text": "Hof",
            "beleg_typ": None,
            "beleg_ref": None,
            "engine": "heuristic",
            "confidence": 0.8,
        },
    )

"""Launcher-Inbox-Vertrag auf der vorhandenen Beleg-/DMS-Pipeline.

Kein zweites Belegwesen. Die Inbox klassifiziert Eingang, bewertet Konfidenz
und zeigt den Weg in die bestehende Belegmaske. Buchungen entstehen hier nicht.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import quote

from app.auth.beleg_roles import darf
from app.core.dms_ocr_contracts import DokumentTyp, klassifiziere_dokument

# Spiegel von packages/frontend-web/src/lib/workflow/document-entry-policy.ts
# (eingehende Scan-Wege). Zielrouten bleiben die produktiven Belegmasken.
BELEG_POLICIES: dict[str, dict[str, Any]] = {
    "incoming-supplier-invoice": {
        "policy_id": "incoming-supplier-invoice",
        "label": "Rechnungseingang erfassen",
        "document_type": "supplier_invoice",
        "direction": "incoming",
        "party_role": "supplier",
        "target_route": "/einkauf/rechnung-eingang-erfassung",
        "match_keys": ("supplierId", "supplierNumber", "purchaseOrderId", "goodsReceiptId", "deliveryNoteId"),
        "required_parsed": ("invoice_number",),
    },
    "incoming-delivery-note": {
        "policy_id": "incoming-delivery-note",
        "label": "Lieferschein Eingang erfassen",
        "document_type": "supplier_delivery_note",
        "direction": "incoming",
        "party_role": "supplier",
        "target_route": "/einkauf/lieferschein-erfassung",
        "match_keys": ("supplierId", "supplierNumber", "purchaseOrderId", "deliveryAdviceId"),
        "required_parsed": (),
    },
    "incoming-goods-receipt": {
        "policy_id": "incoming-goods-receipt",
        "label": "Wareneingang erfassen",
        "document_type": "goods_receipt",
        "direction": "incoming",
        "party_role": "supplier",
        "target_route": "/einkauf/wareneingang",
        "match_keys": ("supplierId", "supplierNumber", "purchaseOrderId", "deliveryAdviceId"),
        "required_parsed": (),
    },
    "incoming-delivery-advice": {
        "policy_id": "incoming-delivery-advice",
        "label": "Anlieferavis erfassen",
        "document_type": "delivery_advice",
        "direction": "incoming",
        "party_role": "supplier",
        "target_route": "/einkauf/anlieferavis/neu",
        "match_keys": ("supplierId", "supplierNumber", "purchaseOrderId", "contractId"),
        "required_parsed": (),
    },
}

_DEFAULT_POLICY_ID = "incoming-supplier-invoice"

_HINT_TO_POLICY = {
    "supplier_invoice": "incoming-supplier-invoice",
    "invoice": "incoming-supplier-invoice",
    "eingangsrechnung": "incoming-supplier-invoice",
    "rechnung": "incoming-supplier-invoice",
    "delivery_note": "incoming-delivery-note",
    "supplier_delivery_note": "incoming-delivery-note",
    "lieferschein": "incoming-delivery-note",
    "goods_receipt": "incoming-goods-receipt",
    "wareneingang": "incoming-goods-receipt",
    "delivery_advice": "incoming-delivery-advice",
    "anlieferavis": "incoming-delivery-advice",
    "avis": "incoming-delivery-advice",
}

PREFILL_SCHEMA = "valeo.inbox.prefill.v1"
PREFILL_STORAGE_KEY = "valeo.inbox.prefill"

# Policy-document_type → Belegvertrag-Art (nur echte Eintraege, nichts erfinden).
# supplier_delivery_note / delivery_advice → goods_receipt: Einkaufs-Eingangskette
# (Lieferschein, Anlieferavis) nutzt die vorhandene Wareneingangs-Belegart
# (BELEGARTEN); keine neue Rolle. Kein Mapping fuer Gutschrift/Wiegeschein-
# document_type — die laufen ueber document_kind + Uebersichtsrouten; Beleg-
# oeffnen braucht linked_document_id (Quelle fehlt).
_POLICY_DOCUMENT_TO_BELEGART: dict[str, str] = {
    "supplier_invoice": "purchase_invoice",
    "supplier_delivery_note": "goods_receipt",
    "delivery_advice": "goods_receipt",
    "goods_receipt": "goods_receipt",
}

# Ist-Werte von klassifiziere_dokument.erkannter_typ — keine neuen Patterns.
_DOCUMENT_KIND_FROM_EXISTING = {
    DokumentTyp.EINGANGSRECHNUNG,
    DokumentTyp.LIEFERSCHEIN,
    DokumentTyp.GUTSCHRIFT,
    DokumentTyp.WIEGESCHEIN,
}
# Oeffnen der Erfassungsmaske = Beleg bearbeiten (anlegen), nicht nur lesen.
_OPEN_MASK_RECHT = "bearbeiten"

# Bekannte Luecken der vorhandenen Pipeline — nicht verschleiern.
# Queue und Webhook-Schreibpfad nutzen tenant_id aus dem verifizierten Claim;
# Altbestand vor der Spalte bleibt legacy-unassigned und ist in der Queue unsichtbar.
PIPELINE_GAPS = (
    "create_from_inbox_bucht_nicht",
    "keine_ki_klassifikation_an_dms_inbox",
    # Kontrakt-Abgleich nur, wenn Extrakt eine Kontraktnummer liefert
    # (dms_parser contract_id) und Stamm (Kon/Agrar) einen Treffer hat.
    "kontrakt_abgleich_nur_bei_kontraktnummer_im_extrakt",
    # linked_document_id nur aus documents.id bei eindeutigem Dubletten-Treffer.
    "linked_document_id_nur_bei_eindeutigem_documents_treffer",
    # Artikel-Abgleich nur, wenn Extrakt echte Positionszeilen liefert.
    # dms_parser liefert nur Kopf; Zeilen kommen aus position_extraction
    # (Claude hinter EINKAUF_OCR_ENGINE=claude) → parsed_fields.positionen.
    "artikel_abgleich_nur_bei_positionszeilen",
    "dms_parser_ohne_positionszeilen",
    "positionsextraktion_engine_nicht_claude",
    "positionsextraktion_ohne_llm_key",
    "positionsextraktion_regex_keine_zeilen",
    "dubletten_nur_ueber_belegnummer",
)

BOOKING_BLOCKED_REASON = (
    "Buchungen laufen ausschliesslich ueber autorisierte Domaenendienste. "
    "Die Inbox oeffnet die bestehende Belegmaske und bereitet einen Vorschlag vor."
)

# Vorhandene Domänen-APIs / Masken — Inbox ruft sie nicht schreibend auf.
SUPPLIER_CREATE_API = "POST /api/v1/einkauf/lieferanten"
SUPPLIER_CREATE_BP_API = "POST /api/v1/crm/business-partners/"
SUPPLIER_STAMM_ROUTE = "/einkauf/lieferanten"
ARTICLE_CREATE_API = "POST /api/v1/articles/"
ARTICLE_STAMM_ROUTE = "/artikel/neu"
ARTICLE_IMAGE_ENRICH_API = "POST /api/v1/articles/enrich-images"
ARTICLE_IMAGE_SERVICE = "app.services.article_image_enrichment.resolve_image_for_article"

_LINE_ITEM_KEYS = ("positionen", "positions", "lines", "items", "line_items")


def confidence_band(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    if score >= 0.25:
        return "low"
    return "review"


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def classify_document(
    parsed_fields: Mapping[str, Any] | None,
    ocr_text: str | None = None,
) -> dict[str, Any]:
    """Deterministische Klassifikation. Kein LLM, keine erfundenen Belegarten."""
    fields = dict(parsed_fields or {})
    hints: list[str] = []
    for key in ("domain", "document_type", "belegart", "type"):
        raw = _clean(fields.get(key))
        if raw:
            hints.append(raw.lower())
    blob = " ".join(hints)
    if ocr_text:
        blob = f"{blob} {ocr_text[:800]}".lower()

    policy_id = _DEFAULT_POLICY_ID
    source = "default-incoming-invoice"
    for hint, mapped in _HINT_TO_POLICY.items():
        if hint in blob or hint in hints:
            policy_id = mapped
            source = "parsed-or-ocr-hint"
            break

    policy = dict(BELEG_POLICIES[policy_id])
    policy["classification_source"] = source
    return policy


def document_kind_from_existing(ocr_text: str | None, item_id: str = "") -> str | None:
    """Mappt klassifiziere_dokument.erkannter_typ. Keine neue Heuristik, kein Routing."""
    text = _clean(ocr_text)
    if not text:
        return None
    result = klassifiziere_dokument(item_id or "inbox", text)
    if result.manuell_pruefen or not result.gematchte_schlagwoerter:
        return None
    if result.erkannter_typ not in _DOCUMENT_KIND_FROM_EXISTING:
        return None
    return result.erkannter_typ.value


def field_completeness(parsed_fields: Mapping[str, Any] | None, required: Sequence[str]) -> float:
    fields = parsed_fields or {}
    if not required:
        filled = sum(1 for key in ("invoice_number", "supplier", "date", "total") if _clean(fields.get(key)))
        return min(1.0, filled / 4.0)
    hits = sum(1 for key in required if _clean(fields.get(key)))
    return hits / len(required)


def blend_confidence(
    ocr_confidence: float | None,
    completeness: float,
    duplicate_count: int,
) -> float:
    ocr = max(0.0, min(1.0, float(ocr_confidence or 0.0)))
    score = (ocr * 0.65) + (completeness * 0.35)
    if duplicate_count:
        score = max(0.0, score - 0.2)
    return round(min(1.0, score), 4)


def match_values(parsed_fields: Mapping[str, Any] | None) -> dict[str, str]:
    fields = parsed_fields or {}
    mapping = {
        "supplierId": ("supplier_id", "supplierId", "kreditor"),
        "supplierNumber": ("supplier_id", "supplierNumber", "lieferantennummer"),
        "invoiceNumber": ("invoice_number", "number"),
        "purchaseOrderId": ("purchase_order", "purchaseOrderId", "bestellnummer"),
        "deliveryNoteId": ("delivery_note", "deliveryNoteId", "lieferschein"),
        "goodsReceiptId": ("goods_receipt", "goodsReceiptId"),
        "contractId": ("contract_id", "contractId", "kontrakt"),
        "date": ("date",),
        "total": ("total",),
        "supplierName": ("supplier", "supplier_name", "lieferant"),
    }
    values: dict[str, str] = {}
    for target, keys in mapping.items():
        for key in keys:
            value = _clean(fields.get(key))
            if value:
                values[target] = value
                break
    return values


def duplicate_hints(
    invoice_number: str | None,
    existing: Iterable[Mapping[str, Any]],
) -> list[dict[str, str]]:
    needle = _clean(invoice_number)
    if not needle:
        return []
    found: list[dict[str, str]] = []
    for row in existing:
        number = _clean(row.get("doc_number") or row.get("number"))
        if number and number.casefold() == needle.casefold():
            hint: dict[str, str] = {
                "doc_type": str(row.get("doc_type") or ""),
                "doc_number": number,
            }
            # Nur wenn der Dokumentspeicher eine echte PK liefert — nie aus OCR raten.
            doc_id = _clean(row.get("id") or row.get("document_id"))
            if doc_id:
                hint["id"] = doc_id
            found.append(hint)
    return found


def verified_linked_document_id(
    duplicates: Sequence[Mapping[str, Any]],
) -> str | None:
    """ERP-Beleg-ID nur bei eindeutigem documents.id-Treffer. Kein OCR-/DMS-Raten."""
    ids: list[str] = []
    for row in duplicates:
        doc_id = _clean(row.get("id") or row.get("document_id"))
        if doc_id:
            ids.append(doc_id)
    unique = sorted(set(ids))
    if len(unique) == 1:
        return unique[0]
    return None


def contract_match_from_candidates(
    values: Mapping[str, str],
    candidates: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Waehlt aus vorhandenen Kontrakt-Treffern (Kon/Agrar). Kein Schreibzugriff."""
    uncertainties: list[dict[str, str]] = []
    needle = _clean(values.get("contractId"))
    rows = [dict(row) for row in candidates if row]

    if not needle:
        return None, uncertainties

    if not rows:
        uncertainties.append({
            "code": "kontrakt_nicht_gefunden",
            "detail": "Kein Kontrakt in den Stammdaten zur Extrakt-Nummer gefunden.",
        })
        return None, uncertainties

    exact: list[dict[str, Any]] = []
    needle_cf = needle.casefold()
    for row in rows:
        number = _clean(row.get("contract_number") or row.get("contract_no"))
        contract_id = _clean(row.get("contract_id") or row.get("id"))
        if (number and number.casefold() == needle_cf) or (
            contract_id and contract_id.casefold() == needle_cf
        ):
            exact.append(row)

    chosen = exact[0] if len(exact) == 1 else (rows[0] if len(rows) == 1 else None)
    if chosen is None:
        uncertainties.append({
            "code": "kontrakt_mehrdeutig",
            "detail": f"{len(rows)} Kontrakt-Treffer — manuell in der Belegmaske waehlen.",
        })
        return {
            "kind": "contract",
            "status": "ambiguous",
            "candidates": [
                {
                    "contract_id": _clean(row.get("contract_id") or row.get("id")),
                    "contract_number": _clean(
                        row.get("contract_number") or row.get("contract_no")
                    ),
                    "source": _clean(row.get("source")),
                }
                for row in rows[:5]
            ],
        }, uncertainties

    how = "contract_number" if exact else str(chosen.get("matched_by") or "lookup")
    return {
        "kind": "contract",
        "status": "matched",
        "matched_by": how,
        "source": _clean(chosen.get("source")),
        "contract_id": _clean(chosen.get("contract_id") or chosen.get("id")),
        "contract_number": _clean(
            chosen.get("contract_number") or chosen.get("contract_no")
        ),
    }, uncertainties


def partner_match_from_candidates(
    values: Mapping[str, str],
    candidates: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Waehlt aus vorhandenen BusinessPartner-Treffern. Kein Schreibzugriff."""
    uncertainties: list[dict[str, str]] = []
    supplier_id = _clean(values.get("supplierId") or values.get("supplierNumber"))
    supplier_name = _clean(values.get("supplierName"))
    rows = [dict(row) for row in candidates if row]

    if not rows:
        if supplier_id or supplier_name:
            uncertainties.append({
                "code": "partner_nicht_gefunden",
                "detail": "Kein Lieferant in den Stammdaten zum Extrakt gefunden.",
            })
        else:
            uncertainties.append({
                "code": "partner_fehlt",
                "detail": "Extrakt liefert weder Lieferantennummer noch -name.",
            })
        return None, uncertainties

    exact: list[dict[str, Any]] = []
    if supplier_id:
        needle = supplier_id.casefold()
        for row in rows:
            number = _clean(row.get("partner_number"))
            partner_id = _clean(row.get("partner_id"))
            if (number and number.casefold() == needle) or (partner_id and partner_id.casefold() == needle):
                exact.append(row)

    chosen = exact[0] if len(exact) == 1 else (rows[0] if len(rows) == 1 else None)
    if chosen is None:
        uncertainties.append({
            "code": "partner_mehrdeutig",
            "detail": f"{len(rows)} Lieferanten-Treffer — manuell in der Belegmaske waehlen.",
        })
        return {
            "kind": "business_partner",
            "status": "ambiguous",
            "candidates": [
                {
                    "partner_id": _clean(row.get("partner_id")),
                    "partner_number": _clean(row.get("partner_number")),
                    "name": _clean(row.get("name")),
                }
                for row in rows[:5]
            ],
        }, uncertainties

    how = "partner_number" if exact else str(chosen.get("matched_by") or "name_search")
    match = {
        "kind": "business_partner",
        "status": "matched",
        "matched_by": how,
        "partner_id": _clean(chosen.get("partner_id")),
        "partner_number": _clean(chosen.get("partner_number")),
        "name": _clean(chosen.get("name")),
    }
    if how == "name_search" and supplier_name and match.get("name"):
        if match["name"].casefold() != supplier_name.casefold():
            uncertainties.append({
                "code": "partner_name_ungenau",
                "detail": "Lieferantenname nur ungefaehr gematcht — bitte pruefen.",
            })
    return match, uncertainties


def extract_line_items(parsed_fields: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """Liest nur vorhandene Positionsarrays. Erfindet keine Zeilen aus OCR-Fliesstext."""
    fields = parsed_fields or {}
    for key in _LINE_ITEM_KEYS:
        raw = fields.get(key)
        if not isinstance(raw, list):
            continue
        rows: list[dict[str, Any]] = []
        for index, row in enumerate(raw):
            if not isinstance(row, Mapping):
                continue
            name = _clean(
                row.get("artikel")
                or row.get("artikel_name")
                or row.get("name")
                or row.get("bezeichnung")
                or row.get("description")
                or row.get("article_name")
            )
            number = _clean(
                row.get("article_number")
                or row.get("artikel_nr")
                or row.get("artikelnummer")
                or row.get("sku")
            )
            ean = _clean(row.get("ean") or row.get("ean_code") or row.get("barcode"))
            quantity = _clean(row.get("menge") or row.get("quantity") or row.get("qty"))
            unit = _clean(row.get("einheit") or row.get("unit") or row.get("uom"))
            if not (name or number):
                continue
            rows.append({
                "index": index,
                "name": name,
                "article_number": number,
                "ean": ean,
                "quantity": quantity,
                "unit": unit,
            })
        return rows
    return []


def article_match_from_candidates(
    line: Mapping[str, Any],
    candidates: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Waehlt aus vorhandenen Artikel-Treffern (WhatsAppIntakeService-Muster). Kein Write."""
    uncertainties: list[dict[str, str]] = []
    rows = [dict(row) for row in candidates if row]
    needle_number = _clean(line.get("article_number"))
    needle_name = _clean(line.get("name"))
    if not rows:
        if needle_number or needle_name:
            uncertainties.append({
                "code": "artikel_nicht_gefunden",
                "detail": "Kein Artikel in den Stammdaten zum Positions-Extrakt gefunden.",
            })
        return None, uncertainties
    exact: list[dict[str, Any]] = []
    if needle_number:
        needle = needle_number.casefold()
        for row in rows:
            number = _clean(row.get("article_number"))
            if number and number.casefold() == needle:
                exact.append(row)
    chosen = exact[0] if len(exact) == 1 else (rows[0] if len(rows) == 1 else None)
    if chosen is None:
        uncertainties.append({
            "code": "artikel_mehrdeutig",
            "detail": f"{len(rows)} Artikel-Treffer — manuell in der Maske waehlen.",
        })
        return {
            "kind": "article",
            "status": "ambiguous",
            "candidates": [
                {
                    "article_number": _clean(row.get("article_number")),
                    "name": _clean(row.get("name")),
                }
                for row in rows[:5]
            ],
        }, uncertainties
    return {
        "kind": "article",
        "status": "matched",
        "matched_by": "article_number" if exact else "name_search",
        "article_number": _clean(chosen.get("article_number")),
        "name": _clean(chosen.get("name")),
    }, uncertainties


def build_image_research_slot(line: Mapping[str, Any]) -> dict[str, Any]:
    """Vorschlag-Slot fuer vorhandenes Image-Enrichment — Inbox fuehrt es nicht aus."""
    ean = _clean(line.get("ean"))
    name = _clean(line.get("name"))
    if ean or name:
        return {
            "status": "propose",
            "executed": False,
            "booking": False,
            "service": ARTICLE_IMAGE_SERVICE,
            "api": ARTICLE_IMAGE_ENRICH_API,
            "inputs": {"ean": ean, "name": name},
            "reason": (
                "Vorhandener Pfad article_image_enrichment (Open Food Facts / Wikipedia / "
                "Kategorie-Map). Inbox startet keinen Download — Anreichern nur ueber "
                f"{ARTICLE_IMAGE_ENRICH_API} nach Artikelanlage."
            ),
        }
    return {
        "status": "gap",
        "executed": False,
        "booking": False,
        "service": ARTICLE_IMAGE_SERVICE,
        "api": ARTICLE_IMAGE_ENRICH_API,
        "code": "kein_ean_oder_name_fuer_bildsuche",
        "reason": (
            "Bild-Research-Pfad existiert, aber Positions-Extrakt liefert weder EAN noch Name."
        ),
    }


def build_supplier_create_proposal(
    values: Mapping[str, str],
    partner_uncertainties: Sequence[Mapping[str, str]],
    parsed_fields: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """Lieferanten-Stammdaten-Vorschlag bei partner_nicht_gefunden. Kein Write."""
    codes = {str(row.get("code") or "") for row in partner_uncertainties}
    if "partner_nicht_gefunden" not in codes:
        return None
    fields = parsed_fields or {}
    name = _clean(values.get("supplierName")) or _clean(fields.get("supplier")) or _clean(
        fields.get("supplier_name")
    )
    number = (
        _clean(values.get("supplierNumber"))
        or _clean(values.get("supplierId"))
        or _clean(fields.get("supplier_id"))
        or _clean(fields.get("lieferantennummer"))
    )
    if not name and not number:
        return None
    payload = {
        "firmenname": name or number,
        "lieferantennummer": number,
        "strasse": _clean(fields.get("strasse") or fields.get("street") or fields.get("address")),
        "plz": _clean(fields.get("plz") or fields.get("postal_code")),
        "ort": _clean(fields.get("ort") or fields.get("city")),
        "land": _clean(fields.get("land") or fields.get("country")) or "Deutschland",
        "email": _clean(fields.get("email")),
        "telefon": _clean(fields.get("telefon") or fields.get("phone")),
        "ust_id": _clean(fields.get("ust_id") or fields.get("vat_id")),
    }
    gaps: list[str] = []
    if not payload["lieferantennummer"]:
        gaps.append("lieferantennummer_fehlt_im_extrakt")
    if not payload["strasse"] and not payload["plz"] and not payload["ort"]:
        gaps.append("lieferant_adresse_fehlt_im_extrakt")
    return {
        "kind": "supplier_create",
        "status": "propose",
        "booking": False,
        "executable": False,
        "domain_api": SUPPLIER_CREATE_API,
        "alternate_api": SUPPLIER_CREATE_BP_API,
        "target_route": SUPPLIER_STAMM_ROUTE,
        "fachaktion_catalog_id": "einkauf.lieferant.create",
        "reason": (
            "Kein Lieferant-Match — Stammdaten-Vorschlag aus Extrakt. "
            f"Anlegen nur ueber {SUPPLIER_CREATE_API} bzw. {SUPPLIER_CREATE_BP_API} "
            "(Maske/prepare-command), nie aus der Inbox."
        ),
        "payload": payload,
        "gaps": gaps,
    }


def build_article_create_proposals(
    lines: Sequence[Mapping[str, Any]],
    article_candidates_by_index: Mapping[int, Sequence[Mapping[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Artikel-Vorschlaege aus echten Positionszeilen. Ohne Zeilen: ehrlicher STOP."""
    if not lines:
        return [{
            "kind": "article_create",
            "status": "blocked",
            "booking": False,
            "executable": False,
            "code": "keine_positionszeilen_im_extrakt",
            "detail": (
                "Keine Positionszeilen in parsed_fields (dms_parser nur Kopf; "
                "Claude-Zeilen nur bei EINKAUF_OCR_ENGINE=claude + Key/PDF/OCR). "
                "Artikel-Vorschlag wird nicht erfunden. Lieferanten-Header-Vorschlag "
                "bleibt unabhaengig davon moeglich."
            ),
            "domain_api": ARTICLE_CREATE_API,
            "target_route": ARTICLE_STAMM_ROUTE,
            "fachaktion_catalog_id": "artikel.stamm.create",
        }]

    candidates_map = article_candidates_by_index or {}
    proposals: list[dict[str, Any]] = []
    for line in lines:
        index = int(line.get("index") or 0)
        match, unclear = article_match_from_candidates(line, candidates_map.get(index) or ())
        if match and match.get("status") == "matched":
            proposals.append({
                "kind": "article_match",
                "status": "matched",
                "booking": False,
                "executable": False,
                "line_index": index,
                "match": match,
                "uncertainties": unclear,
            })
            continue
        name = _clean(line.get("name"))
        number = _clean(line.get("article_number"))
        proposals.append({
            "kind": "article_create",
            "status": "propose",
            "booking": False,
            "executable": False,
            "line_index": index,
            "domain_api": ARTICLE_CREATE_API,
            "target_route": ARTICLE_STAMM_ROUTE,
            "fachaktion_catalog_id": "artikel.stamm.create",
            "reason": (
                "Kein eindeutiger Artikel-Match — Stammdaten-Vorschlag aus Positions-Extrakt. "
                f"Anlegen nur ueber {ARTICLE_CREATE_API} (Maske/prepare-command), nie aus der Inbox."
            ),
            "payload": {
                "name": name,
                "article_number": number,
                "ean_code": _clean(line.get("ean")),
                "quantity_hint": _clean(line.get("quantity")),
                "unit_hint": _clean(line.get("unit")),
            },
            "match": match,
            "uncertainties": unclear,
            "image_research": build_image_research_slot(line),
            "gaps": (
                ["artikelnummer_fehlt_im_extrakt"] if not number else []
            ) + (["artikelname_fehlt_im_extrakt"] if not name else []),
        })
    return proposals


def build_master_data_proposals(
    *,
    values: Mapping[str, str],
    partner_uncertainties: Sequence[Mapping[str, str]],
    parsed_fields: Mapping[str, Any] | None,
    article_candidates_by_index: Mapping[int, Sequence[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Aggregiert Lieferanten-/Artikel-Vorschlaege. executable/booking immer false."""
    lines = extract_line_items(parsed_fields)
    supplier = build_supplier_create_proposal(values, partner_uncertainties, parsed_fields)
    articles = build_article_create_proposals(lines, article_candidates_by_index)
    return {
        "booking": False,
        "executable": False,
        "line_item_count": len(lines),
        "supplier": supplier,
        "articles": articles,
    }


def _parse_amount(value: Any) -> float | None:
    """Parst Parser-/Extrakt-Betraege (bereits bereinigt oder DE-Format). None wenn unbrauchbar."""
    text = _clean(value)
    if text is None:
        return None
    normalized = text.replace(" ", "").replace("€", "").replace("EUR", "")
    if "," in normalized and normalized.rfind(",") > normalized.rfind("."):
        normalized = normalized.replace(".", "").replace(",", ".")
    else:
        normalized = normalized.replace(",", "")
    try:
        return float(normalized)
    except ValueError:
        return None


def header_plausibility_uncertainties(
    parsed_fields: Mapping[str, Any] | None,
) -> list[dict[str, str]]:
    """Stufe 5: Pflicht/Plausibilitaet der vorhandenen Kopffelder — keine Positionszeilen."""
    fields = parsed_fields or {}
    items: list[dict[str, str]] = []

    if not (_clean(fields.get("invoice_number")) or _clean(fields.get("number"))):
        items.append({
            "code": "pflicht_invoice_number",
            "detail": "Pflichtfeld invoice_number fehlt im Extrakt.",
        })
    if not _clean(fields.get("date")):
        items.append({
            "code": "pflicht_date",
            "detail": "Pflichtfeld date fehlt im Extrakt.",
        })
    if not (_clean(fields.get("supplier")) or _clean(fields.get("supplier_id"))):
        items.append({
            "code": "pflicht_supplier",
            "detail": "Pflichtfeld supplier/supplier_id fehlt im Extrakt.",
        })

    total_raw = _clean(fields.get("total"))
    total_value: float | None = None
    if not total_raw:
        items.append({
            "code": "pflicht_total",
            "detail": "Pflichtfeld total fehlt im Extrakt.",
        })
    else:
        total_value = _parse_amount(total_raw)
        if total_value is None:
            items.append({
                "code": "plausi_total_nicht_numerisch",
                "detail": f"total ist nicht numerisch: {total_raw}",
            })

    tax_raw = _clean(fields.get("tax"))
    tax_value: float | None = None
    if not tax_raw:
        items.append({
            "code": "pflicht_tax",
            "detail": "Pflichtfeld tax fehlt im Extrakt.",
        })
    else:
        tax_value = _parse_amount(tax_raw)
        if tax_value is None:
            items.append({
                "code": "plausi_tax_nicht_numerisch",
                "detail": f"tax ist nicht numerisch: {tax_raw}",
            })
        elif total_value is not None and tax_value > total_value:
            items.append({
                "code": "plausi_tax_groesser_total",
                "detail": f"tax ({tax_raw}) ist groesser als total ({total_raw}).",
            })

    return items


def collect_uncertainties(
    *,
    duplicates: Sequence[Mapping[str, Any]],
    partner_uncertainties: Sequence[Mapping[str, str]],
    confidence: float,
    parsed_fields: Mapping[str, Any] | None = None,
    contract_uncertainties: Sequence[Mapping[str, str]] = (),
) -> list[dict[str, str]]:
    """Unklarheiten am Vorschlag — keine erfundenen KI-Hinweise."""
    items = [dict(row) for row in partner_uncertainties]
    items.extend(dict(row) for row in contract_uncertainties)
    if duplicates:
        items.append({
            "code": "dublette",
            "detail": "Belegnummer existiert bereits im Dokumentspeicher des Mandanten.",
        })
    if confidence < 0.5:
        items.append({
            "code": "konfidenz_niedrig",
            "detail": "Konfidenz unter Schwelle — Extrakt und Zuordnung pruefen.",
        })
    partner_codes = {row["code"] for row in items}
    for hint in header_plausibility_uncertainties(parsed_fields):
        # partner_fehlt deckt denselben Kopf-Mangel ab — nicht doppelt listen
        if hint["code"] == "pflicht_supplier" and (
            "partner_fehlt" in partner_codes or "partner_nicht_gefunden" in partner_codes
        ):
            continue
        items.append(hint)
    # Gaps aus position_extraction (Claude hinter EINKAUF_OCR_ENGINE) — ehrlich surfacing.
    raw_gaps = (parsed_fields or {}).get("position_extraction_gaps")
    if isinstance(raw_gaps, list):
        for code in raw_gaps:
            text = _clean(code)
            if not text:
                continue
            items.append({
                "code": text,
                "detail": f"Positions-Extraktion: {text}",
            })
    return items


def blockers_for(
    policy: Mapping[str, Any],
    parsed_fields: Mapping[str, Any] | None,
    duplicates: Sequence[Mapping[str, Any]],
    confidence: float,
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for key in policy.get("required_parsed") or ():
        if not _clean((parsed_fields or {}).get(key)):
            blockers.append({
                "code": "pflichtfeld",
                "detail": f"Pflichtfeld {key} fehlt im Extrakt.",
            })
    if duplicates:
        blockers.append({
            "code": "dublette",
            "detail": "Belegnummer ist im Dokumentspeicher bereits vorhanden.",
        })
    if confidence < 0.25:
        blockers.append({
            "code": "konfidenz",
            "detail": "Konfidenz zu niedrig fuer eine automatische Vorbelegung.",
        })
    return blockers


def build_prefill(
    *,
    item_id: str,
    policy: Mapping[str, Any],
    parsed_fields: Mapping[str, Any] | None,
    confidence: float,
    dms_document_id: Any = None,
    classification_source: str | None = None,
    partner_match: Mapping[str, Any] | None = None,
    contract_match: Mapping[str, Any] | None = None,
    duplicates: Sequence[Mapping[str, Any]] = (),
    uncertainties: Sequence[Mapping[str, str]] = (),
) -> dict[str, Any]:
    """Vorschlag fuer die Zielmaske. Kein Beleg-Create, keine Buchung."""
    fields = parsed_fields or {}
    values = dict(match_values(fields))
    partner_id = values.get("supplierId")
    partner_number = values.get("supplierNumber") or values.get("supplierId")
    partner_name = values.get("supplierName")
    if partner_match and partner_match.get("status") == "matched":
        partner_id = _clean(partner_match.get("partner_id")) or partner_id
        partner_number = _clean(partner_match.get("partner_number")) or partner_number
        partner_name = _clean(partner_match.get("name")) or partner_name
        if partner_id:
            values["supplierId"] = partner_id
        if partner_number:
            values["supplierNumber"] = partner_number
        if partner_name:
            values["supplierName"] = partner_name
    if contract_match and contract_match.get("status") == "matched":
        contract_number = _clean(contract_match.get("contract_number"))
        contract_id = _clean(contract_match.get("contract_id"))
        if contract_number:
            values["contractId"] = contract_number
        elif contract_id:
            values["contractId"] = contract_id
    return {
        "schema": PREFILL_SCHEMA,
        "documentId": item_id,
        "documentNumber": values.get("invoiceNumber"),
        "partner": {
            "id": partner_id,
            "number": partner_number,
            "name": partner_name,
            "role": policy["party_role"],
        },
        "amounts": {
            "total": values.get("total"),
            "tax": _clean(fields.get("tax")),
            "currency": _clean(fields.get("currency")) or "EUR",
        },
        "source": {
            "kind": "dms_inbox",
            "id": item_id,
            "dmsDocumentId": dms_document_id,
            "classification": classification_source or policy.get("classification_source"),
        },
        "confidence": confidence,
        "confidenceBand": confidence_band(confidence),
        "policyId": policy["policy_id"],
        "documentType": policy["document_type"],
        "targetRoute": policy["target_route"],
        "booking": False,
        "matchValues": values,
        "match": dict(partner_match) if partner_match else None,
        "contractMatch": dict(contract_match) if contract_match else None,
        "duplicates": [dict(row) for row in duplicates],
        "uncertainties": [dict(row) for row in uncertainties],
        "storageKey": PREFILL_STORAGE_KEY,
        # Create-Host rechnung-eingang-erfassung-neu liest sessionStorage und
        # mappt Kopffelder — kein Booking, nur Vorbelegung.
        "maskConsumesPrefill": True,
    }


def open_mask_href(target_route: str, item_id: str) -> str:
    return f"{target_route}?inbox={quote(str(item_id), safe='')}"


def belegart_for_policy(policy: Mapping[str, Any]) -> str | None:
    doc_type = str(policy.get("document_type") or "")
    return _POLICY_DOCUMENT_TO_BELEGART.get(doc_type)


def evaluate_can_open(
    policy: Mapping[str, Any],
    nutzer: Any | None,
) -> tuple[bool, list[dict[str, str]], str | None]:
    """Ob die Zielmaske geoeffnet werden darf — aus Anmeldungsrollen, nie aus Client-Body."""
    belegart = belegart_for_policy(policy)
    if belegart is None:
        return False, [{
            "code": "maske_ohne_belegrecht",
            "detail": (
                f"Fuer document_type={policy.get('document_type')!s} gibt es "
                "keine Belegvertrags-Art — Oeffnen gesperrt."
            ),
        }], None
    if nutzer is None:
        return False, [{
            "code": "keine_anmeldung",
            "detail": "Ohne verifizierte Anmeldung darf die Zielmaske nicht geoeffnet werden.",
        }], belegart
    if darf(nutzer, _OPEN_MASK_RECHT, belegart):
        return True, [], belegart
    return False, [{
        "code": "keine_berechtigung_maske",
        "detail": f"Keine Berechtigung: Belegart {belegart} {_OPEN_MASK_RECHT}.",
    }], belegart


def prepare_command(
    *,
    item_id: str,
    policy: Mapping[str, Any],
    parsed_fields: Mapping[str, Any] | None,
    confidence: float,
    duplicates: Sequence[Mapping[str, Any]],
    dms_document_id: Any = None,
    classification_source: str | None = None,
    partner_match: Mapping[str, Any] | None = None,
    contract_match: Mapping[str, Any] | None = None,
    uncertainties: Sequence[Mapping[str, str]] = (),
) -> dict[str, Any]:
    """Validierter Fachvorschlag. executable bleibt immer false."""
    blockers = blockers_for(policy, parsed_fields, duplicates, confidence)
    prefill = build_prefill(
        item_id=item_id,
        policy=policy,
        parsed_fields=parsed_fields,
        confidence=confidence,
        dms_document_id=dms_document_id,
        classification_source=classification_source,
        partner_match=partner_match,
        contract_match=contract_match,
        duplicates=duplicates,
        uncertainties=uncertainties,
    )
    return {
        "command": "document.capture.open",
        "executable": False,
        "booking": False,
        "reason": BOOKING_BLOCKED_REASON,
        "policy_id": policy["policy_id"],
        "document_type": policy["document_type"],
        "target_route": policy["target_route"],
        "prefill": prefill,
        "confidence": confidence,
        "confidence_band": confidence_band(confidence),
        "blockers": list(blockers),
        "match": prefill.get("match"),
        "contract_match": prefill.get("contractMatch"),
        "duplicates": list(prefill.get("duplicates") or []),
        "uncertainties": list(prefill.get("uncertainties") or []),
        "source": prefill["source"],
        "gaps": list(PIPELINE_GAPS),
    }


def item_actions(
    policy: Mapping[str, Any],
    command: Mapping[str, Any],
    item_id: str,
    *,
    can_open: bool,
    master_data: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = [
        {
            "key": "open_mask",
            "label": "Beleg öffnen",
            "kind": "primary",
            "href": open_mask_href(policy["target_route"], item_id) if can_open else None,
            "enabled": can_open,
            "booking": False,
        },
        {
            "key": "prepare",
            "label": "Vorschlag pruefen",
            "kind": "secondary",
            "booking": False,
            "enabled": True,
            "command": command["command"],
        },
    ]
    md = master_data or {}
    supplier = md.get("supplier") if isinstance(md.get("supplier"), Mapping) else None
    if supplier and supplier.get("status") == "propose":
        actions.append({
            "key": "propose_supplier_create",
            "label": "Lieferant anlegen",
            "kind": "secondary",
            # UI ruft POST /api/v1/einkauf/lieferanten nach Bestaetigung;
            # href bleibt Stamm-Uebersicht als Fallback/Deep-Link, kein Approve.
            "href": open_mask_href(SUPPLIER_STAMM_ROUTE, item_id),
            "enabled": True,
            "booking": False,
            "command": "stammdaten.lieferant.create",
            "domain_api": SUPPLIER_CREATE_API,
        })
    for row in md.get("articles") or []:
        if isinstance(row, Mapping) and row.get("kind") == "article_create" and row.get("status") == "propose":
            actions.append({
                "key": "propose_article_create",
                "label": "Artikel vorschlagen",
                "kind": "secondary",
                "href": open_mask_href(ARTICLE_STAMM_ROUTE, item_id),
                "enabled": True,
                "booking": False,
                "command": "stammdaten.artikel.prepare",
            })
            break
    return actions


def build_queue_item(
    *,
    entry: Mapping[str, Any],
    existing_documents: Sequence[Mapping[str, Any]] = (),
    partner_candidates: Sequence[Mapping[str, Any]] = (),
    contract_candidates: Sequence[Mapping[str, Any]] = (),
    article_candidates_by_index: Mapping[int, Sequence[Mapping[str, Any]]] | None = None,
    nutzer: Any | None = None,
) -> dict[str, Any]:
    parsed = entry.get("parsed_fields") if isinstance(entry.get("parsed_fields"), Mapping) else {}
    policy = classify_document(parsed, _clean(entry.get("ocr_text")))
    values = match_values(parsed)
    invoice_number = values.get("invoiceNumber") or _clean(parsed.get("invoice_number"))
    duplicates = duplicate_hints(invoice_number, existing_documents)
    linked_document_id = verified_linked_document_id(duplicates)
    partner_match, partner_uncertainties = partner_match_from_candidates(values, partner_candidates)
    contract_match, contract_uncertainties = contract_match_from_candidates(
        values, contract_candidates,
    )
    completeness = field_completeness(parsed, policy.get("required_parsed") or ())
    confidence = blend_confidence(entry.get("confidence"), completeness, len(duplicates))
    uncertainties = collect_uncertainties(
        duplicates=duplicates,
        partner_uncertainties=partner_uncertainties,
        contract_uncertainties=contract_uncertainties,
        confidence=confidence,
        parsed_fields=parsed,
    )
    can_open, auth_uncertainties, belegart = evaluate_can_open(policy, nutzer)
    uncertainties = [*uncertainties, *auth_uncertainties]
    item_id = str(entry.get("id") or "")
    if partner_match and partner_match.get("status") == "matched":
        if partner_match.get("partner_id"):
            values = {**values, "supplierId": str(partner_match["partner_id"])}
        if partner_match.get("partner_number"):
            values = {**values, "supplierNumber": str(partner_match["partner_number"])}
        if partner_match.get("name"):
            values = {**values, "supplierName": str(partner_match["name"])}
    if contract_match and contract_match.get("status") == "matched":
        contract_number = _clean(contract_match.get("contract_number"))
        contract_pk = _clean(contract_match.get("contract_id"))
        if contract_number:
            values = {**values, "contractId": contract_number}
        elif contract_pk:
            values = {**values, "contractId": contract_pk}
    master_data = build_master_data_proposals(
        values=values,
        partner_uncertainties=partner_uncertainties,
        parsed_fields=parsed,
        article_candidates_by_index=article_candidates_by_index,
    )
    for article_row in master_data.get("articles") or []:
        if not isinstance(article_row, Mapping):
            continue
        if article_row.get("status") == "blocked" and article_row.get("code"):
            uncertainties.append({
                "code": str(article_row["code"]),
                "detail": str(article_row.get("detail") or article_row["code"]),
            })
        for hint in article_row.get("uncertainties") or []:
            if isinstance(hint, Mapping) and hint.get("code"):
                uncertainties.append({
                    "code": str(hint["code"]),
                    "detail": str(hint.get("detail") or hint["code"]),
                })
    command = prepare_command(
        item_id=item_id,
        policy=policy,
        parsed_fields=parsed,
        confidence=confidence,
        duplicates=duplicates,
        dms_document_id=entry.get("dms_document_id"),
        classification_source=policy["classification_source"],
        partner_match=partner_match,
        contract_match=contract_match,
        uncertainties=uncertainties,
    )
    command["can_open"] = can_open
    command["master_data_proposals"] = master_data
    document_kind = document_kind_from_existing(_clean(entry.get("ocr_text")), item_id)
    return {
        "id": item_id,
        "dms_document_id": entry.get("dms_document_id"),
        "dms_url": entry.get("dms_url"),
        # Nur documents.id bei eindeutigem Dubletten-Treffer — nie Inbox-/DMS-/OCR-ID.
        "linked_document_id": linked_document_id,
        "status": str(entry.get("status") or "pending"),
        "created_at": entry.get("created_at"),
        "ocr_excerpt": (_clean(entry.get("ocr_text")) or "")[:240] or None,
        "parsed_fields": dict(parsed),
        "match_values": values,
        "match": partner_match,
        "contract_match": contract_match,
        "confidence": confidence,
        "confidence_band": confidence_band(confidence),
        "source": policy["classification_source"],
        "proposal": {
            "policy_id": policy["policy_id"],
            "label": policy["label"],
            "document_type": policy["document_type"],
            "document_kind": document_kind,
            "direction": policy["direction"],
            "target_route": policy["target_route"],
            "belegart": belegart,
            "can_open": can_open,
            "reason": (
                "Deterministische Klassifikation aus OCR-/Parserfeldern. "
                "Keine Buchung, nur Einstieg in die bestehende Belegmaske."
            ),
        },
        "duplicates": duplicates,
        "uncertainties": uncertainties,
        "blockers": command["blockers"],
        "master_data_proposals": master_data,
        "actions": item_actions(
            policy, command, item_id, can_open=can_open, master_data=master_data,
        ),
        "command": command,
        "can_open": can_open,
        "booking_allowed": False,
    }

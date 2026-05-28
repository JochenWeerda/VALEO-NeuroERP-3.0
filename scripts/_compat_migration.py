"""One-shot migration: replace weak response_model=dict in compat.py with typed schemas."""
import re

with open("app/api/v1/endpoints/compat.py", encoding="utf-8") as f:
    content = f.read()

SCHEMA_BLOCK = '''
from app.api.v1.schemas.base import BaseSchema, StatusResponse
from pydantic import ConfigDict as _ConfigDict


# ---------------------------------------------------------------------------
# Compat-specific response schemas
# ConfigDict(extra="allow") forwards dynamic fields while providing typed
# OpenAPI documentation for the known key columns.
# ---------------------------------------------------------------------------

class CsvImportResponse(BaseSchema):
    created: int = 0
    updated: int = 0
    errors: list[str] = []


class PurchaseOrderListOut(BaseSchema):
    data: list[dict] = []
    page: int = 1
    pageSize: int = 50
    total: int = 0
    totalPages: int = 1


class PurchaseOrderOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""
    status: Optional[str] = None


class EinkaufDocOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""


class InventoryOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class AnnahmeEntryOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""


class PortalOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class SetupFirmaOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class FieldServiceTaskOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")
    id: str = ""
    status: Optional[str] = None


class CrmOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class SanktionsPruefungOut(BaseSchema):
    geprueft: bool
    treffer: bool
    name: str
    land: str
    listen: list[str] = []
    ergebnis: str = ""
    geprueft_am: str = ""
    hinweis: str = ""


class NewsletterOut(BaseSchema):
    initiiert: bool = True
    empfaenger_gesamt: int = 0
    empfaenger_gueltig: int = 0
    empfaenger_ungueltig: int = 0
    betreff: str = ""
    typ: str = ""
    status: str = ""
    hinweis: str = ""


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


'''

content = content.replace(
    '\nrouter = APIRouter(tags=["compat"])',
    SCHEMA_BLOCK + '\nrouter = APIRouter(tags=["compat"])',
    1,
)

# Each tuple: (old_fragment, new_fragment) — unique enough to identify one endpoint
PATCHES = [
    # CRM
    ('@router.get("/crm/dashboard", response_model=dict,', '@router.get("/crm/dashboard", response_model=CrmOut,'),
    ('@router.get("/crm/suppliers", response_model=dict,', '@router.get("/crm/suppliers", response_model=CrmOut,'),
    ('@router.patch("/crm/lieferanten/{lieferant_id}", response_model=dict,', '@router.patch("/crm/lieferanten/{lieferant_id}", response_model=CrmOut,'),
    ('@router.patch("/crm/kunden/{kunden_id}", response_model=dict,', '@router.patch("/crm/kunden/{kunden_id}", response_model=CrmOut,'),
    ('@router.post("/crm/sanktionspruefung", response_model=dict,', '@router.post("/crm/sanktionspruefung", response_model=SanktionsPruefungOut,'),
    ('@router.post("/crm/kommunikation/newsletter", response_model=dict,', '@router.post("/crm/kommunikation/newsletter", response_model=NewsletterOut,'),
    # CSV imports
    ('@router.post("/crm/import/kunden", response_model=dict,', '@router.post("/crm/import/kunden", response_model=CsvImportResponse,'),
    ('@router.post("/finance/import/debitoren", response_model=dict,', '@router.post("/finance/import/debitoren", response_model=CsvImportResponse,'),
    ('@router.post("/futter/import/einzelfuttermittel", response_model=dict,', '@router.post("/futter/import/einzelfuttermittel", response_model=CsvImportResponse,'),
    ('@router.post("/futter/import/mischfuttermittel", response_model=dict,', '@router.post("/futter/import/mischfuttermittel", response_model=CsvImportResponse,'),
    ('@router.post("/futter/import/chargen", response_model=dict,', '@router.post("/futter/import/chargen", response_model=CsvImportResponse,'),
    # Purchase orders
    ('@router.get("/purchase-orders", response_model=dict,', '@router.get("/purchase-orders", response_model=PurchaseOrderListOut,'),
    ('@router.get("/purchase-orders/{po_id}", response_model=dict,', '@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderOut,'),
    ('@router.post("/purchase-orders", response_model=dict, status_code=201,', '@router.post("/purchase-orders", response_model=PurchaseOrderOut, status_code=201,'),
    ('@router.patch("/purchase-orders/{po_id}", response_model=dict,', '@router.patch("/purchase-orders/{po_id}", response_model=PurchaseOrderOut,'),
    ('@router.post("/purchase-orders/{po_id}/approve", response_model=dict,', '@router.post("/purchase-orders/{po_id}/approve", response_model=PurchaseOrderOut,'),
    ('@router.post("/purchase-orders/{po_id}/cancel-with-reason", response_model=dict,', '@router.post("/purchase-orders/{po_id}/cancel-with-reason", response_model=PurchaseOrderOut,'),
    ('@router.get("/purchase-orders/statistics", response_model=dict,', '@router.get("/purchase-orders/statistics", response_model=CompatFlexOut,'),
    ('@router.post("/purchase-orders/{po_id}/communications", response_model=dict, status_code=201,', '@router.post("/purchase-orders/{po_id}/communications", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.post("/purchase-orders/{po_id}/communications/email", response_model=dict, status_code=201,', '@router.post("/purchase-orders/{po_id}/communications/email", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.post("/purchase-orders/{po_id}/communications/portal", response_model=dict, status_code=201,', '@router.post("/purchase-orders/{po_id}/communications/portal", response_model=EinkaufDocOut, status_code=201,'),
    # Sales bridge
    ('@router.get("/sales/{doc_type}", response_model=dict,', '@router.get("/sales/{doc_type}", response_model=CompatFlexOut,'),
    # Einkauf
    ('@router.post("/einkauf/goods-receipts", response_model=dict, status_code=201,', '@router.post("/einkauf/goods-receipts", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.get("/einkauf/anfragen/{anfrage_id}", response_model=dict,', '@router.get("/einkauf/anfragen/{anfrage_id}", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/anfragen/{anfrage_id}/convert-to-order", response_model=dict,', '@router.post("/einkauf/anfragen/{anfrage_id}/convert-to-order", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/angebote/{angebot_id}/review", response_model=dict,', '@router.post("/einkauf/angebote/{angebot_id}/review", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/angebote/{angebot_id}/approve", response_model=dict,', '@router.post("/einkauf/angebote/{angebot_id}/approve", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/angebote/{angebot_id}/reject", response_model=dict,', '@router.post("/einkauf/angebote/{angebot_id}/reject", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/angebote/{angebot_id}/convert-to-order", response_model=dict,', '@router.post("/einkauf/angebote/{angebot_id}/convert-to-order", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/anlieferavis/{avis_id}/{action}", response_model=dict,', '@router.post("/einkauf/anlieferavis/{avis_id}/{action}", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/auftragsbestaetigungen/{bestaetigung_id}/{action}", response_model=dict,', '@router.post("/einkauf/auftragsbestaetigungen/{bestaetigung_id}/{action}", response_model=EinkaufDocOut,'),
    ('@router.get("/einkauf/reports", response_model=dict,', '@router.get("/einkauf/reports", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/retouren", response_model=dict, status_code=201,', '@router.post("/einkauf/retouren", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.get("/futter/statistik", response_model=dict,', '@router.get("/futter/statistik", response_model=CompatFlexOut,'),
    ('@router.get("/einkauf/supplier-ratings", response_model=dict,', '@router.get("/einkauf/supplier-ratings", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/supplier-ratings/{supplier_id}", response_model=dict,', '@router.post("/einkauf/supplier-ratings/{supplier_id}", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/suppliers/{supplier_id}/documents", response_model=dict, status_code=201,', '@router.post("/einkauf/suppliers/{supplier_id}/documents", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.delete("/einkauf/suppliers/{supplier_id}/documents/{doc_id}", response_model=dict,', '@router.delete("/einkauf/suppliers/{supplier_id}/documents/{doc_id}", response_model=EinkaufDocOut,'),
    ('@router.get("/einkauf/retouren/{retour_id}", response_model=dict,', '@router.get("/einkauf/retouren/{retour_id}", response_model=EinkaufDocOut,'),
    ('@router.patch("/einkauf/retouren/{retour_id}", response_model=dict,', '@router.patch("/einkauf/retouren/{retour_id}", response_model=EinkaufDocOut,'),
    ('@router.get("/einkauf/service-entry-sheets", response_model=dict,', '@router.get("/einkauf/service-entry-sheets", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/service-entry-sheets", response_model=dict, status_code=201,', '@router.post("/einkauf/service-entry-sheets", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.patch("/einkauf/service-entry-sheets/{ses_id}", response_model=dict,', '@router.patch("/einkauf/service-entry-sheets/{ses_id}", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/credit-memos", response_model=dict, status_code=201,', '@router.post("/einkauf/credit-memos", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.post("/einkauf/debit-memos", response_model=dict, status_code=201,', '@router.post("/einkauf/debit-memos", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.post("/einkauf/credit-memos/{memo_id}/settle", response_model=dict,', '@router.post("/einkauf/credit-memos/{memo_id}/settle", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/debit-memos/{memo_id}/settle", response_model=dict,', '@router.post("/einkauf/debit-memos/{memo_id}/settle", response_model=EinkaufDocOut,'),
    ('@router.get("/einkauf/reports/standard", response_model=dict,', '@router.get("/einkauf/reports/standard", response_model=EinkaufDocOut,'),
    ('@router.get("/einkauf/audit-trail/{doc_type}/{doc_id}", response_model=dict,', '@router.get("/einkauf/audit-trail/{doc_type}/{doc_id}", response_model=EinkaufDocOut,'),
    ('@router.get("/einkauf/edi/messages", response_model=dict,', '@router.get("/einkauf/edi/messages", response_model=EinkaufDocOut,'),
    ('@router.post("/einkauf/edi/messages", response_model=dict, status_code=201,', '@router.post("/einkauf/edi/messages", response_model=EinkaufDocOut, status_code=201,'),
    ('@router.post("/einkauf/edi/messages/{msg_id}/ack", response_model=dict,', '@router.post("/einkauf/edi/messages/{msg_id}/ack", response_model=EinkaufDocOut,'),
    # Contracts
    ('@router.get("/contracts/{contract_id}", response_model=dict,', '@router.get("/contracts/{contract_id}", response_model=CompatFlexOut,'),
    # Inventory
    ('@router.get("/inventory/inventur", response_model=dict,', '@router.get("/inventory/inventur", response_model=InventoryOut,'),
    ('@router.post("/inventory/inventur/complete", response_model=dict,', '@router.post("/inventory/inventur/complete", response_model=InventoryOut,'),
    ('@router.get("/inventory/mhd-warnings", response_model=dict,', '@router.get("/inventory/mhd-warnings", response_model=InventoryOut,'),
    ('@router.get("/inventory/top-sellers", response_model=dict,', '@router.get("/inventory/top-sellers", response_model=InventoryOut,'),
    ('@router.get("/inventory/slow-movers", response_model=dict,', '@router.get("/inventory/slow-movers", response_model=InventoryOut,'),
    ('@router.get("/inventory/lots", response_model=dict,', '@router.get("/inventory/lots", response_model=InventoryOut,'),
    ('@router.get("/inventory/lots/{lot_id}", response_model=dict,', '@router.get("/inventory/lots/{lot_id}", response_model=InventoryOut,'),
    # Annahme
    ('@router.get("/annahme/warteschlange", response_model=dict,', '@router.get("/annahme/warteschlange", response_model=AnnahmeEntryOut,'),
    ('@router.get("/annahme/warteschlange/{reg_id}", response_model=dict,', '@router.get("/annahme/warteschlange/{reg_id}", response_model=AnnahmeEntryOut,'),
    ('@router.patch("/annahme/warteschlange/{reg_id}", response_model=dict,', '@router.patch("/annahme/warteschlange/{reg_id}", response_model=AnnahmeEntryOut,'),
    ('@router.post("/annahme/warteschlange/{reg_id}/repair-article", response_model=dict,', '@router.post("/annahme/warteschlange/{reg_id}/repair-article", response_model=AnnahmeEntryOut,'),
    # Portal
    ('@router.get("/portal/dashboard", response_model=dict,', '@router.get("/portal/dashboard", response_model=PortalOut,'),
    ('@router.get("/portal/products", response_model=dict,', '@router.get("/portal/products", response_model=PortalOut,'),
    ('@router.get("/portal/orders", response_model=dict,', '@router.get("/portal/orders", response_model=PortalOut,'),
    ('@router.get("/portal/orders/{order_id}", response_model=dict,', '@router.get("/portal/orders/{order_id}", response_model=PortalOut,'),
    ('@router.post("/portal/orders", response_model=dict,', '@router.post("/portal/orders", response_model=PortalOut,'),
    # Setup/firma (has tags after response_model)
    ('@router.get("/setup/firma", response_model=dict, tags=["setup"],', '@router.get("/setup/firma", response_model=SetupFirmaOut, tags=["setup"],'),
    ('@router.put("/setup/firma", response_model=dict, tags=["setup"],', '@router.put("/setup/firma", response_model=SetupFirmaOut, tags=["setup"],'),
]

MULTILINE_PATCHES = [
    # Field service tasks and search/benachrichtigungen have response_model on next line
    (
        '@router.get("/agribusiness/field-service-tasks/{task_id}", summary="Field service task abrufen",\n    response_model=dict\n)',
        '@router.get("/agribusiness/field-service-tasks/{task_id}", summary="Field service task abrufen",\n    response_model=FieldServiceTaskOut\n)',
    ),
    (
        '@router.post("/agribusiness/field-service-tasks", summary="Field service task anlegen",\n    response_model=dict\n)',
        '@router.post("/agribusiness/field-service-tasks", summary="Field service task anlegen",\n    response_model=FieldServiceTaskOut\n)',
    ),
    (
        '@router.put("/agribusiness/field-service-tasks/{task_id}", summary="Field service task aktualisieren",\n    response_model=dict\n)',
        '@router.put("/agribusiness/field-service-tasks/{task_id}", summary="Field service task aktualisieren",\n    response_model=FieldServiceTaskOut\n)',
    ),
    (
        '@router.delete("/agribusiness/field-service-tasks/{task_id}", summary="Field service task löschen",\n    response_model=dict\n)',
        '@router.delete("/agribusiness/field-service-tasks/{task_id}", summary="Field service task löschen",\n    response_model=FieldServiceTaskOut\n)',
    ),
    (
        '@router.post("/agribusiness/field-service-tasks/{task_id}/cancel", summary="Field service task stornieren",\n    response_model=dict\n)',
        '@router.post("/agribusiness/field-service-tasks/{task_id}/cancel", summary="Field service task stornieren",\n    response_model=FieldServiceTaskOut\n)',
    ),
    (
        '@router.get("/benachrichtigungen", summary="Benachrichtigungen auflisten",\n    response_model=dict\n)',
        '@router.get("/benachrichtigungen", summary="Benachrichtigungen auflisten",\n    response_model=CompatFlexOut\n)',
    ),
    (
        '@router.get("/search", summary="Search global",\n    response_model=dict\n)',
        '@router.get("/search", summary="Search global",\n    response_model=CompatFlexOut\n)',
    ),
]

# Also handle bestellungen multi-line (lines 630, 644, 658)
BESTELLUNGEN_PATCH = (
    '    response_model=dict\n',
    '    response_model=EinkaufDocOut\n',
)

missed = []
for old, new in PATCHES:
    if old in content:
        content = content.replace(old, new, 1)
    else:
        missed.append(old[:70])

for old, new in MULTILINE_PATCHES:
    if old in content:
        content = content.replace(old, new, 1)
    else:
        missed.append(old[:70])

# The remaining response_model=dict lines (3 bestellungen multi-line and any others)
# Replace all remaining bare "    response_model=dict\n" lines (indented, standalone)
content = re.sub(r'^(\s+)response_model=dict\n', r'\1response_model=EinkaufDocOut\n', content, flags=re.MULTILINE)

with open("app/api/v1/endpoints/compat.py", "w", encoding="utf-8") as f:
    f.write(content)

if missed:
    print("MISSED patterns:")
    for m in missed:
        print(" ", m)
else:
    print("All patterns replaced successfully")

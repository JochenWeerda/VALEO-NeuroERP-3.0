"""
Helper Functions für Document Router
Zentrale Funktionen für DB/In-Memory Fallback
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.documents.repository import DocumentRepository
import logging

logger = logging.getLogger(__name__)

# In-Memory Store (Fallback)
_DB: Dict[str, dict] = {}
_USE_DB = True


def get_repository(db: Session = None) -> Optional[DocumentRepository]:
    """Holt Repository oder None wenn DB nicht verfügbar"""
    if _USE_DB and db:
        try:
            return DocumentRepository(db)
        except Exception as e:
            logger.warning(f"Repository creation failed: {e}")
            return None
    return None


def save_to_store(doc_type: str, doc_number: str, data: dict, repo: Optional[DocumentRepository] = None) -> dict:
    """Speichert Dokument in DB oder In-Memory Store"""
    if repo:
        try:
            return repo.save_document(doc_type, doc_number, data)
        except Exception as e:
            logger.warning(f"DB save failed, using in-memory: {e}")
    
    # Fallback zu In-Memory
    _DB[doc_number] = data
    logger.info(f"Saved {doc_type} (in-memory): {doc_number}")
    return {"ok": True, "number": doc_number}


def get_from_store(doc_type: str, doc_number: str, repo: Optional[DocumentRepository] = None) -> Optional[dict]:
    """Holt Dokument aus DB oder In-Memory Store"""
    if repo:
        try:
            return repo.get_document(doc_type, doc_number)
        except Exception as e:
            logger.warning(f"DB get failed, using in-memory: {e}")
    
    # Fallback zu In-Memory
    return _DB.get(doc_number)


def list_from_store(
    doc_type: str, 
    skip: int = 0, 
    limit: int = 100,
    filters: Optional[Dict] = None,
    repo: Optional[DocumentRepository] = None
) -> Dict:
    """Listet Dokumente aus DB oder In-Memory Store.

    Rückgabe: ``{"ok": bool, "data": list[dict], "total": int, "skip": int, "limit": int}``.
    Caller müssen über die Liste in ``result["data"]`` iterieren — nicht über ``result``.

    **Wichtig:** ``repo`` immer per Keyword übergeben (``repo=...``), wenn ``skip``/``limit``
    weggelassen werden — der zweite *positions*elle Parameter ist ``skip``, nicht ``repo``.
    """
    if repo:
        try:
            docs = repo.list_documents(doc_type, skip, limit, filters)
            total = repo.count_documents(doc_type, filters)
            return {
                "ok": True,
                "data": docs,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.warning(f"DB list failed, using in-memory: {e}")
    
    # Fallback zu In-Memory - Filtere nach Typ
    filtered_docs = []
    for key, value in _DB.items():
        type_prefixes = {
            "customer_inquiry": ["INQ-"],
            "sales_offer": ["SO-", "ANG-"],
            "sales_order": ["SO-"],
            "sales_delivery": ["DL-"],
            "sales_invoice": ["INV-"],
            "payment_received": ["PAY-"],
            "purchase_request": ["PR-"],
            "purchase_offer": ["POF-"],
            "purchase_order": ["PO-", "EK-"],
            "credit_memo": ["CM-"],
            "debit_memo": ["DM-"],
            "service_entry_sheet": ["SES-"],
            "edi_message": ["EDI-"],
            "supplier_rating": ["SUPR-"],
            "ap_invoice": ["APINV-", "ER-", "RE-"],
        }
        
        prefixes = type_prefixes.get(doc_type, [])
        if any(key.startswith(prefix) for prefix in prefixes):
            if not filters:
                filtered_docs.append(value)
            else:
                def _match(item_key: str, item_value: object) -> bool:
                    if item_key == "tenantId":
                        # Backward compatibility for legacy docs without tenant
                        return value.get(item_key) in {item_value, None, ""}
                    return value.get(item_key) == item_value

                if all(_match(k, v) for k, v in filters.items()):
                    filtered_docs.append(value)
    
    total = len(filtered_docs)
    paginated_docs = filtered_docs[skip:skip + limit]
    
    return {
        "ok": True,
        "data": paginated_docs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


def delete_from_store(doc_type: str, doc_number: str, repo: Optional[DocumentRepository] = None) -> bool:
    """Löscht Dokument aus DB oder In-Memory Store"""
    if repo:
        try:
            return repo.delete_document(doc_type, doc_number)
        except Exception as e:
            logger.warning(f"DB delete failed, using in-memory: {e}")
    
    # Fallback zu In-Memory
    if doc_number in _DB:
        del _DB[doc_number]
        return True
    return False


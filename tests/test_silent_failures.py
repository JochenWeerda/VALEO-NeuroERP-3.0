"""Vertraege gegen zwei Ausfaelle, die sich frueher als Erfolg getarnt haben.

1. Die Dokumentablage meldete einen fehlgeschlagenen Schreibvorgang als Erfolg
   und wich in den Prozessspeicher aus. Genau das hat den kaputten SQL-Cast aus
   SQL-BIND-CAST-20260914 monatelang verdeckt.
2. Sechs Dienste haben die Auth-Middleware stillschweigend weggelassen, wenn
   ``auth_shared`` nicht importierbar war - protokolliert wurde nur der
   Erfolgsfall.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pytest

from app.documents import router_helpers

pytestmark = pytest.mark.unit

REPO = Path(__file__).resolve().parents[1]

AUTH_DIENSTE = [
    "services/ai/main.py",
    "services/crm/main.py",
    "services/finance/main.py",
    "services/finance/fibu-gateway/main.py",
    "services/inventory/main.py",
    "services/workflow/main.py",
]


class _RepoDasFehlschlaegt:
    """Steht fuer eine konfigurierte, aber gestoerte Datenbank."""

    def save_document(self, doc_type, doc_number, data):
        raise RuntimeError("INSERT fehlgeschlagen")

    def get_document(self, doc_type, doc_number):
        raise RuntimeError("SELECT fehlgeschlagen")

    def list_documents(self, doc_type, skip, limit, filters):
        raise RuntimeError("SELECT fehlgeschlagen")

    def count_documents(self, doc_type, filters):
        raise RuntimeError("COUNT fehlgeschlagen")


def test_schreibfehler_wird_nicht_als_erfolg_gemeldet() -> None:
    with pytest.raises(RuntimeError, match="INSERT fehlgeschlagen"):
        router_helpers.save_to_store("sales_invoice", "INV-1", {"a": 1}, repo=_RepoDasFehlschlaegt())


def test_lesefehler_wird_nicht_zu_nicht_vorhanden_umgedeutet() -> None:
    with pytest.raises(RuntimeError, match="SELECT fehlgeschlagen"):
        router_helpers.get_from_store("sales_invoice", "INV-1", repo=_RepoDasFehlschlaegt())


def test_listenfehler_liefert_keine_halbe_liste() -> None:
    with pytest.raises(RuntimeError):
        router_helpers.list_from_store("sales_invoice", repo=_RepoDasFehlschlaegt())


def test_ohne_datenbank_bleibt_der_prozessspeicher_und_sagt_es() -> None:
    """Ohne konfigurierte Datenbank ist der Prozessspeicher gewollt - aber er
    behauptet nicht, persistiert zu haben."""
    ergebnis = router_helpers.save_to_store("sales_invoice", "INV-OHNE-DB", {"a": 1}, repo=None)
    assert ergebnis["ok"] is True
    assert ergebnis["persisted"] is False
    assert router_helpers.get_from_store("sales_invoice", "INV-OHNE-DB", repo=None) == {"a": 1}


@pytest.mark.parametrize("relpath", AUTH_DIENSTE)
def test_auth_faellt_nicht_mehr_stillschweigend_aus(relpath: str) -> None:
    quelle = io.open(REPO / relpath, encoding="utf-8").read()

    assert "AuthMiddleware" in quelle, f"{relpath}: unerwartet keine Auth-Einbindung mehr"

    # Der Fehlerzweig muss den Grund festhalten ...
    assert "AUTH_IMPORT_ERROR" in quelle, f"{relpath}: Importfehler wird nicht festgehalten"
    # ... und darf nicht mehr folgenlos bleiben.
    assert "ALLOW_UNAUTHENTICATED_SERVICE" in quelle, f"{relpath}: kein ausdruecklicher Ausweg"
    assert re.search(r"raise RuntimeError\(", quelle), f"{relpath}: Start wird nicht verweigert"
    assert "logger.critical" in quelle, f"{relpath}: Ausweg wird nicht protokolliert"


@pytest.mark.parametrize("relpath", AUTH_DIENSTE)
def test_kein_stilles_weglassen_der_middleware(relpath: str) -> None:
    """Das alte Muster war: einhaengen, wenn vorhanden - sonst nichts."""
    quelle = io.open(REPO / relpath, encoding="utf-8").read()
    stelle = quelle.index("if AuthMiddleware is not None:")
    rest = quelle[stelle:]
    # Direkt nach dem Erfolgszweig muss ein elif/else folgen, kein Leerlauf.
    assert re.search(r"if AuthMiddleware is not None:.*?\n(elif|else)\b", rest, re.S), (
        f"{relpath}: fehlender Gegenzweig - die Middleware wuerde still entfallen"
    )

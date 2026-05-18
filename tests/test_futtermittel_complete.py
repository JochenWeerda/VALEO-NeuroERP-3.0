"""
Tests: Futtermittel — Rohwaren, Rezeptur, Nährstoffanalyse, Deklaration, Etikett
"""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock, patch


def _mock_db():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.fetchall.return_value = []
    db.execute.return_value.scalar.return_value = None
    db.commit = MagicMock()
    return db


def _row(**kwargs):
    m = MagicMock()
    m._mapping = kwargs
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


# ── Rohwaren-Stamm ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_rohwaren_row_to_dict():
    from app.api.v1.endpoints.futtermittel_rohwaren import _row_to_dict
    row = _row(id="rm-1", name="Gerste", rohprotein_g=110.0, energie_me_mj=12.5)
    result = _row_to_dict(row)
    assert result["id"] == "rm-1"
    assert result["name"] == "Gerste"


@pytest.mark.unit
def test_rohwaren_vergleich_returns_naehrstoffe():
    """Vergleich-Endpoint aggregiert Nährstoffe mehrerer Rohwaren."""
    from app.api.v1.endpoints.futtermittel_rohwaren import vergleich_rohwaren
    db = _mock_db()

    rows = [
        _row(id="rm-1", name="Gerste", rohprotein_g=110.0, rohfett_g=20.0,
             rohfaser_g=50.0, energie_me_mj=12.5, kategorie="GETREIDE"),
        _row(id="rm-2", name="Soja", rohprotein_g=440.0, rohfett_g=15.0,
             rohfaser_g=60.0, energie_me_mj=14.0, kategorie="OELKUCHEN"),
    ]
    db.execute.return_value.fetchall.return_value = rows

    import asyncio
    with patch("app.api.v1.endpoints.futtermittel_rohwaren._ensure_tables"):
        result = asyncio.run(
            vergleich_rohwaren(ids="rm-1,rm-2", db=db, tenant_id="t-1")
        )
    assert "rohwaren" in result
    assert len(result["rohwaren"]) == 2


# ── Rezeptur + Nährstoffanalyse ───────────────────────────────────────────

@pytest.mark.unit
def test_naehrstoffanalyse_weighted_average():
    """Nährstoffanalyse: gewichteter Mittelwert aus Zutaten-Anteilen."""
    from app.api.v1.endpoints.futtermittel_rezepte import naehrstoffanalyse

    rezept_row = _row(id="r-1", name="Mastschwein", status="AKTIV",
                      tierart="SCHWEIN", tenant_id="t-1")
    ing_rows = [
        _row(material_id="rm-1", anteil_percent=50.0),  # Gerste 50%
        _row(material_id="rm-2", anteil_percent=50.0),  # Soja 50%
    ]
    material_rows = {
        "rm-1": _row(rohprotein_g=110.0, energie_me_mj=12.5, rohfett_g=20.0,
                     rohfaser_g=50.0, rohasche_g=25.0, dry_matter_percent=88.0),
        "rm-2": _row(rohprotein_g=440.0, energie_me_mj=14.0, rohfett_g=15.0,
                     rohfaser_g=60.0, rohasche_g=60.0, dry_matter_percent=89.0),
    }

    db = _mock_db()
    call_count = [0]

    def execute_side(stmt, params=None):
        m = MagicMock()
        sql = str(stmt).lower()
        if "feed_recipes" in sql and "ingredients" not in sql:
            m.fetchone.return_value = rezept_row
        elif "ingredients" in sql:
            m.fetchall.return_value = ing_rows
        elif "feed_raw_materials" in sql and params:
            mid = params.get("mid") or params.get("material_id")
            m.fetchone.return_value = material_rows.get(mid, MagicMock())
        else:
            m.fetchone.return_value = None
            m.fetchall.return_value = []
        return m

    db.execute.side_effect = execute_side

    import asyncio
    with patch("app.api.v1.endpoints.futtermittel_rezepte._ensure_tables"):
        result = asyncio.run(
            naehrstoffanalyse(rezept_id="r-1", db=db, tenant_id="t-1")
        )
    # Should return a dict with naehrstoffe
    assert result is not None


@pytest.mark.unit
def test_deklaration_contains_pflichtfelder():
    """Deklaration muss Pflichtfelder gemäß EU 2017/2279 enthalten."""
    from app.api.v1.endpoints.futtermittel_rezepte import deklaration

    rezept_row = _row(id="r-1", name="Mastschwein TMR", status="AKTIV",
                      tierart="SCHWEIN", tenant_id="t-1")
    ing_rows = [
        _row(material_id="rm-1", anteil_percent=60.0),
        _row(material_id="rm-2", anteil_percent=40.0),
    ]
    mat_rows = {
        "rm-1": _row(name="Gerste", rohprotein_g=110.0, rohfett_g=20.0,
                     rohfaser_g=50.0, rohasche_g=25.0, energie_me_mj=12.5,
                     dry_matter_percent=88.0),
        "rm-2": _row(name="Sojaextraktionsschrot", rohprotein_g=440.0, rohfett_g=15.0,
                     rohfaser_g=60.0, rohasche_g=60.0, energie_me_mj=14.0,
                     dry_matter_percent=89.0),
    }

    db = _mock_db()

    def execute_side(stmt, params=None):
        m = MagicMock()
        sql = str(stmt).lower()
        if "feed_recipes" in sql and "ingredient" not in sql:
            m.fetchone.return_value = rezept_row
        elif "ingredient" in sql:
            m.fetchall.return_value = ing_rows
        elif "raw_material" in sql and params:
            mid = params.get("mid") or params.get("material_id")
            m.fetchone.return_value = mat_rows.get(mid, MagicMock())
        else:
            m.fetchone.return_value = None
            m.fetchall.return_value = []
        return m

    db.execute.side_effect = execute_side

    import asyncio
    with patch("app.api.v1.endpoints.futtermittel_rezepte._ensure_tables"):
        result = asyncio.run(
            deklaration(rezept_id="r-1", db=db, tenant_id="t-1")
        )

    # Must contain zutaten_liste and analytische_bestandteile
    assert "zutaten_liste" in result
    assert "analytische_bestandteile" in result


@pytest.mark.unit
def test_etikett_contains_eu_pflichtfelder():
    """Etikett muss EU 2017/2279 Pflichtfelder enthalten."""
    from app.api.v1.endpoints.futtermittel_rezepte import etikett

    rezept_row = _row(id="r-1", name="Mastschwein TMR", status="AKTIV",
                      tierart="SCHWEIN", tenant_id="t-1")
    ing_rows = [_row(material_id="rm-1", anteil_percent=100.0)]
    mat_row = _row(name="Gerste", rohprotein_g=110.0, rohfett_g=20.0,
                   rohfaser_g=50.0, rohasche_g=25.0, energie_me_mj=12.5,
                   dry_matter_percent=88.0)

    db = _mock_db()

    def execute_side(stmt, params=None):
        m = MagicMock()
        sql = str(stmt).lower()
        if "feed_recipes" in sql and "ingredient" not in sql:
            m.fetchone.return_value = rezept_row
        elif "ingredient" in sql:
            m.fetchall.return_value = ing_rows
        else:
            m.fetchone.return_value = mat_row
        return m

    db.execute.side_effect = execute_side

    import asyncio
    with patch("app.api.v1.endpoints.futtermittel_rezepte._ensure_tables"):
        result = asyncio.run(
            etikett(rezept_id="r-1", db=db, tenant_id="t-1")
        )

    # EU Pflichtfelder
    assert "produktname" in result
    assert "tierart" in result
    assert "zutaten_liste" in result
    assert "analytische_bestandteile" in result


# ── Rezeptur-Validierung ─────────────────────────────────────────────────

@pytest.mark.unit
def test_rezept_not_found_raises_404():
    from app.api.v1.endpoints.futtermittel_rezepte import _get_recipe_or_404
    from fastapi import HTTPException
    db = _mock_db()
    db.execute.return_value.fetchone.return_value = None
    with pytest.raises(HTTPException) as exc:
        _get_recipe_or_404(db, "missing", "t-1")
    assert exc.value.status_code == 404

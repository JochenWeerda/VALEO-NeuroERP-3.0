from __future__ import annotations

from app.xml import DatMLResBuilder


def test_datml_res_builder_creates_xml():
    res_xml = DatMLResBuilder("submission-1", batch=None).build(errors=["Fehler 1"])
    assert "DatML-RES-D" in res_xml
    assert "Fehler 1" in res_xml

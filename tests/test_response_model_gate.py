"""Structural gate regressions, independent of DB and backend imports."""
import pytest

from scripts.check_response_models import _count_untyped


@pytest.mark.parametrize("model", ["Item", "list[Item]", "dict[str, Any]"])
def test_nested_dependencies_do_not_hide_declared_models(model):
    source = f'@router.post("/items", dependencies=[Depends(require_roles("write"))], response_model={model})\ndef create(): pass'
    assert _count_untyped(source) == (0, 1)


@pytest.mark.parametrize("annotation", ["Item", "dict[str, Any]", "'list[Item]'"])
def test_fastapi_return_models_are_recognized(annotation):
    assert _count_untyped(f'@router.get("/items")\ndef get() -> {annotation}: pass') == (0, 1)


@pytest.mark.parametrize("annotation", ["", " -> Any", " -> object", " -> None"])
def test_untyped_json_remains_a_gap(annotation):
    assert _count_untyped(f'@router.get("/items")\ndef get(){annotation}: pass') == (1, 1)


def test_download_aliases_and_bodyless_response_are_route_local():
    source = '''
from fastapi.responses import Response as FileBytes, PlainTextResponse
@router.get("/pdf", response_class=FileBytes)
def pdf(): pass
@router.get("/csv")
def csv() -> PlainTextResponse: pass
@router.delete("/item", status_code=204)
def delete(): pass
@router.get("/missing")
def missing(): pass
'''
    assert _count_untyped(source) == (1, 4)


def test_explicit_none_and_comments_do_not_mask_other_routes():
    source = '''
# @router.get("/comment", response_model=None)
@router.get("/raw", response_model=None)
def raw(): pass
@router.get("/missing")
def missing(): pass
'''
    assert _count_untyped(source) == (1, 2)


def test_stacked_routes_are_counted_individually():
    assert _count_untyped('@router.get("/a", response_model=Item)\n@router.get("/b")\ndef get(): pass') == (1, 2)


def test_malformed_source_cannot_pass_the_gate():
    with pytest.raises(SyntaxError):
        _count_untyped('@router.get("/broken"\ndef broken(): pass')


def test_utf8_bom_is_valid_python_source():
    assert _count_untyped('\ufeff@router.get("/item", response_model=Item)\ndef get(): pass') == (0, 1)

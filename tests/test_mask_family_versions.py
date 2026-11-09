"""Maskenfamilien: gleichartige Masken als Varianten einer Maske, versioniert wie die Belegfamilie (08.11.2026).

Geprueft wird der Mechanismus (unveraenderliche Historie, gebundene Fassungen) und der Bestand: Jede Familie
materialisiert ihre Builder unveraendert, jede Variante besteht die Gates A/B/C/E und ist Studio-Draft-clean,
und die Registry liefert die versionierte Fassung aus, nicht den Builder.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from app.core.mask_family_versions import (
    check_registry,
    extend_registry,
    family_definition,
    family_names,
    is_family_screen,
    resolve_variant,
    spec_for,
    versioned_screen_ids,
)
from app.core.studio_release import definition_hash
from scripts.generate_mask_family_versions import check, current_matches, family_builders

pytestmark = pytest.mark.unit


def _varianten() -> dict:
    return family_builders()["kontrakt"]()


def test_jede_familie_hat_builder_und_aktuelles_release():
    assert check() == []
    assert set(family_names()) == set(family_builders())


@pytest.mark.parametrize("family", sorted(family_builders()))
def test_registry_laeuft_gleich_mit_den_buildern(family):
    from app.core.mask_family_versions import load_registry

    assert current_matches(load_registry(family), family_builders()[family]())


def test_varianten_teilen_eine_basis_und_unterscheiden_sich_im_patch():
    registry = extend_registry(_varianten(), "1.0.0", spec=spec_for("kontrakt"))
    basis = registry["bases"]["1.0.0"]["definition"]
    assert {"domain", "mode", "performance"} <= set(basis)
    patches = {v: registry["variants"][v]["1.0.0"]["patch"] for v in registry["current"]}
    # Reiter, Aktionen und Kennzahlen sind je Variante verschieden, nie in der Basis.
    for key in ("tabs", "actions", "summary", "variant"):
        assert key not in basis and all(key in p for p in patches.values())


def test_neues_release_laesst_die_historie_unveraendert():
    spec = spec_for("kontrakt")
    erstes = extend_registry(_varianten(), "1.0.0", spec=spec)
    vorher = deepcopy(erstes)
    alt = resolve_variant(erstes, "fixierung")
    geaendert = _varianten()
    geaendert["fixierung"]["title"] = "Fixierung neu"
    zweites = extend_registry(geaendert, "1.1.0", erstes, spec=spec)
    assert erstes == vorher
    assert resolve_variant(zweites, "fixierung")["title"] == "Fixierung neu"
    assert resolve_variant(zweites, "fixierung", "1.0.0", expected=alt["maskVariant"]) == alt


@pytest.mark.parametrize("aenderung", ["basis", "patch", "alias"])
def test_geaenderter_inhalt_bricht_die_bindung(aenderung):
    registry = extend_registry(_varianten(), "1.0.0", spec=spec_for("kontrakt"))
    bindung = resolve_variant(registry, "erfuellung")["maskVariant"]
    if aenderung == "basis":
        registry["bases"]["1.0.0"]["definition"]["mode"] = "list"
    elif aenderung == "patch":
        registry["variants"]["erfuellung"]["1.0.0"]["patch"]["title"] = "Ungeprueft"
    else:
        registry["current"]["erfuellung"] = "9.0.0"
    with pytest.raises(ValueError, match="^mask_family_"):
        resolve_variant(registry, "erfuellung", expected=bindung)


def test_variante_muss_zur_familie_gehoeren():
    varianten = _varianten()
    varianten["fixierung"]["variant"] = {"family": "kontrakt-liste", "id": "fixierung"}
    with pytest.raises(ValueError, match="variant_mismatch"):
        extend_registry(varianten, "1.0.0", spec=spec_for("kontrakt"))


def test_release_nummern_steigen_und_ueberschreiben_nie():
    spec = spec_for("kontrakt")
    registry = extend_registry(_varianten(), "1.1.0", spec=spec)
    with pytest.raises(ValueError, match="already_exists"):
        extend_registry(_varianten(), "1.1.0", registry, spec=spec)
    with pytest.raises(ValueError, match="must_advance"):
        extend_registry(_varianten(), "1.0.0", registry, spec=spec)


def test_beleg_ist_keine_allgemeine_familie():
    with pytest.raises(ValueError, match="name_invalid"):
        spec_for("beleg")


def test_ausgeliefert_wird_die_versionierte_fassung():
    from app.core.screen_definitions import get_screen_definition

    for sid, (family, variant) in versioned_screen_ids().items():
        geliefert = get_screen_definition(sid)
        assert geliefert is not None, sid
        bindung = geliefert["maskVariant"]
        assert (bindung["family"], bindung["variantId"]) == (family, variant)
        roh = family_definition(family, variant)
        roh.pop("maskVariant")
        assert bindung["materializedHash"] == definition_hash(roh)
        assert is_family_screen(sid)


def test_familien_stehen_nicht_im_nativen_katalog():
    from app.core.studio_screen_versions import load_registry

    katalog = load_registry()["screens"]
    assert not set(versioned_screen_ids()) & set(katalog)


def test_jede_variante_besteht_die_gates_und_ist_draft_clean():
    from app.services.made_by_studio_gates import evaluate_screen, load_registered_definitions

    definitionen = load_registered_definitions()
    befunde = {}
    for sid in versioned_screen_ids():
        bericht = evaluate_screen(sid, definitionen[sid])
        offen = {g: r.issues for g, r in bericht.gates.items() if not r.passed}
        if offen or bericht.studio_draft_violations:
            befunde[sid] = (offen, bericht.studio_draft_violations)
    assert befunde == {}


def test_registry_ist_gueltig():
    from app.core.mask_family_versions import load_registry

    for family in family_names():
        check_registry(load_registry(family))

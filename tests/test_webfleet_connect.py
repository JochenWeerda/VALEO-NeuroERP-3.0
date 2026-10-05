"""showVehicleReportExtern: Mikrograd, Status A, kein Passwort in der URL."""

from app.services import webfleet_connect as wf


def setup_function() -> None:
    wf._cache = None


def test_mikrograd_werden_zu_wgs84() -> None:
    punkt = wf.punkt_aus_fahrzeug({"latitude": 53_550_000, "longitude": 8_580_000})
    assert punkt is not None
    assert round(punkt[0], 5) == 53.55
    assert round(punkt[1], 5) == 8.58


def test_status_ausser_a_ist_kein_fix() -> None:
    zeile = {"latitude": 53_550_000, "longitude": 8_580_000, "status": "L"}
    assert wf.punkt_aus_fahrzeug(zeile) is None
    assert wf.punkt_aus_fahrzeug({**zeile, "status": "A"}) is not None


def test_fehlermeldung_bleibt_ohne_position(monkeypatch) -> None:
    def transport(account: str, user: str, password: str, apikey: str) -> list[dict]:
        raise RuntimeError("falsches Passwort")

    for name, wert in (
        ("WEBFLEET_ACCOUNT", "konto"),
        ("WEBFLEET_USER", "api"),
        ("WEBFLEET_PASSWORD", "geheim"),
        ("WEBFLEET_APIKEY", "schluessel"),
    ):
        monkeypatch.setenv(name, wert)
    monkeypatch.setattr(wf, "_abruf", transport)
    assert wf.positionen() == {}


def test_abruf_hoechstens_einmal_pro_minute(monkeypatch) -> None:
    import os

    aufrufe: list[str] = []

    def transport(account: str, user: str, password: str, apikey: str) -> list[dict]:
        aufrufe.append(password)
        return [{"objectname": "EL-AB 123", "latitude": 53_100_000, "longitude": 8_200_000, "status": "A"}]

    for name, wert in (
        ("WEBFLEET_ACCOUNT", "konto"),
        ("WEBFLEET_USER", "api"),
        ("WEBFLEET_PASSWORD", "geheim"),
        ("WEBFLEET_APIKEY", "schluessel"),
    ):
        monkeypatch.setenv(name, wert)
    erste = wf.fahrzeugbericht(jetzt=10.0, transport=transport)
    zweite = wf.fahrzeugbericht(jetzt=20.0, transport=transport)
    assert erste == zweite
    assert aufrufe == ["geheim"]
    assert "geheim" not in wf.BASIS
    assert wf.AKTION == "showVehicleReportExtern"

"""Vertrag der Preisansichten ohne erfundene Daten."""

from fastapi.testclient import TestClient


def test_preisansichten_melden_fehlende_quelle_ohne_datenbankzugriff():
    from fastapi import FastAPI
    from app.api.v1.endpoints.mask_frontend_bridges import router
    from app.core.database import get_db
    from app.core.exceptions import register_domain_exception_handlers
    from app.core.tenant import get_tenant_id

    class KeineDatenbank:
        def __getattr__(self, name):
            raise AssertionError(f"Unerwarteter Datenbankzugriff: {name}")

    test_app = FastAPI()
    register_domain_exception_handlers(test_app)
    test_app.include_router(router, prefix="/api/v1")
    test_app.dependency_overrides[get_tenant_id] = lambda: "test-mandant"
    test_app.dependency_overrides[get_db] = lambda: KeineDatenbank()
    for route in router.routes:
        if route.path in {"/preise/historie", "/preise/konditionen"}:
            abhaengigkeiten = {dependency.call for dependency in route.dependant.dependencies}
            assert get_tenant_id in abhaengigkeiten
            assert get_db in abhaengigkeiten
    schema = test_app.openapi()
    fehler = schema["components"]["schemas"]["PreisansichtNichtVerfuegbar"]
    assert set(fehler["required"]) == {"type", "title", "status", "detail", "instance", "error"}
    assert fehler["properties"]["detail"]["type"] == "string"
    for pfad in ("historie", "konditionen"):
        antworten = schema["paths"][f"/api/v1/preise/{pfad}"]["get"]["responses"]
        assert "200" not in antworten
        assert antworten["404"]["content"]["application/problem+json"]["schema"] == {
            "$ref": "#/components/schemas/PreisansichtNichtVerfuegbar"
        }
    with TestClient(test_app) as preis_client:
        for pfad, detail in (
            ("historie", "Fuer diese Ansicht ist keine passende Preishistorie angebunden."),
            ("konditionen", "Fuer diese Ansicht ist keine passende Kundenpreiskondition angebunden."),
        ):
            response = preis_client.get(f"/api/v1/preise/{pfad}")
            assert response.status_code == 404
            assert response.headers["content-type"] == "application/problem+json"
            assert response.json() == {
                "type": "https://valeo-erp.de/errors/not-found",
                "title": "Nicht gefunden",
                "status": 404,
                "detail": detail,
                "instance": f"/api/v1/preise/{pfad}",
                "error": "NOT_FOUND",
            }



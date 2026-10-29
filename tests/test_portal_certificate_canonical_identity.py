from app.core.screen_definitions import get_screen_definition
from app.core.screen_definitions_domain_batch15 import build_portal_zertifikate_screen_definition
from app.core.screen_definitions_stamm import STAMM_ROUTEN, STAMM_SCREEN_BUILDERS, STAMM_SYNONYME


def test_portal_certificate_has_only_customer_scoped_list_screen():
    assert "portal/zertifikat" not in STAMM_SCREEN_BUILDERS
    assert "portal/zertifikat" not in STAMM_ROUTEN
    assert "portal/zertifikat" not in STAMM_SYNONYME
    assert get_screen_definition("portal/zertifikat") is None

    definition = build_portal_zertifikate_screen_definition()
    assert definition["id"] == "portal/zertifikate"
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/portal/zertifikate"
    assert definition["tables"][0]["dataSourceKey"] == "list"
    assert "rowRouteTemplate" not in definition["tables"][0]

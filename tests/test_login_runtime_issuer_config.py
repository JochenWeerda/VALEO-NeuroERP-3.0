"""Development issuer and JWKS have deliberately different transports."""
from pathlib import Path
import yaml


def test_development_public_issuer_and_internal_jwks():
    compose = yaml.safe_load(Path("docker-compose.yml").read_text(encoding="utf-8"))
    environment = compose["services"]["backend"]["environment"]
    assert environment["OIDC_ISSUER_URL"] == "${OIDC_ISSUER_URL:-http://localhost:8080/realms/valeo-neuro-erp}"
    assert environment["OIDC_JWKS_URL"] == "${OIDC_JWKS_URL:-http://keycloak:8080/realms/valeo-neuro-erp/protocol/openid-connect/certs}"

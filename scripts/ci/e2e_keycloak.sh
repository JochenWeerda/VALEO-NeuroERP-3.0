#!/usr/bin/env bash
# Wegwerf-Keycloak fuer E2E-Laeufe in GitHub Actions (seit 12.10.2026 gibt es keinen Dev-Token mehr).
#
# Startet Keycloak 22 (wie docker-compose.yml) ohne Datenbank, richtet den Realm ueber den regulaeren Weg
# scripts/provision_identity_provider.py ein und legt mit scripts/ci/e2e_identitaeten.py drei synthetische
# Kennungen an. Alle Kennwoerter entstehen hier je Lauf zufaellig, werden maskiert und nur ueber $GITHUB_ENV an die
# folgenden Schritte gegeben — nichts davon steht im Repository.
set -euo pipefail

if [ "${CI:-}" != "true" ] || [ -z "${GITHUB_ENV:-}" ]; then
  echo "Nur in GitHub Actions: dieser Schritt oeffnet den Password Grant am Frontend-Client." >&2
  exit 1
fi

geheim() { openssl rand -base64 30 | tr -d '/+=' | cut -c1-28; }
ADMIN_PASS="$(geheim)"; PASS_ADMIN="$(geheim)"; PASS_POWER="$(geheim)"; PASS_READ="$(geheim)"
for wert in "$ADMIN_PASS" "$PASS_ADMIN" "$PASS_POWER" "$PASS_READ"; do echo "::add-mask::$wert"; done

docker run -d --name e2e-keycloak -p 8080:8080 \
  -e KEYCLOAK_ADMIN=ci-identity-bootstrap -e KEYCLOAK_ADMIN_PASSWORD="$ADMIN_PASS" -e KC_FEATURES=declarative-user-profile \
  quay.io/keycloak/keycloak:22.0 start-dev >/dev/null
timeout 180 bash -c 'until curl -fsS http://localhost:8080/realms/master >/dev/null 2>&1; do sleep 3; done' || {
  docker logs e2e-keycloak | tail -50; exit 1; }

export VALEO_IDP_ADMIN_USERNAME=ci-identity-bootstrap VALEO_IDP_ADMIN_PASSWORD="$ADMIN_PASS"
python scripts/provision_identity_provider.py --url http://localhost:8080
export VALEO_IDP_URL=http://localhost:8080
export VALEO_USER_ADMIN=e2e-admin@valeo.invalid VALEO_PASS_ADMIN="$PASS_ADMIN"
export VALEO_USER_POWER=e2e-power@valeo.invalid VALEO_PASS_POWER="$PASS_POWER"
export VALEO_USER_READ=e2e-readonly@valeo.invalid VALEO_PASS_READ="$PASS_READ"
python scripts/ci/e2e_identitaeten.py

{
  echo "VALEO_USER_ADMIN=$VALEO_USER_ADMIN"; echo "VALEO_PASS_ADMIN=$PASS_ADMIN"
  echo "VALEO_USER_POWER=$VALEO_USER_POWER"; echo "VALEO_PASS_POWER=$PASS_POWER"
  echo "VALEO_USER_READ=$VALEO_USER_READ"; echo "VALEO_PASS_READ=$PASS_READ"
} >> "$GITHUB_ENV"

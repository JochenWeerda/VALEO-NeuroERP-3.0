"""Testkennungen fuer E2E-Laeufe in CI — nur gegen einen Wegwerf-Keycloak auf dieser Maschine.

Seit 12.10.2026 gibt es keinen Dev-Token mehr; das Backend nimmt nur signierte Tokens des konfigurierten
Anbieters mit Mandant und Sitzung. Die Playwright-Laeufe brauchen deshalb echte Anmeldungen. Dieser Schritt laeuft
**nach** ``scripts/provision_identity_provider.py`` (derselbe Realm wie lokal und in Staging) und legt nur fuer den
CI-Lauf an:

* drei synthetische Kennungen (Verwaltung, Bearbeitung, nur Lesen) im Testmandanten, Kennwoerter aus der Umgebung;
* Password Grant am Frontend-Client, damit Playwright ohne Browser-Umweg ein Token holen kann;
* eine Token-Lebensdauer, die einen ganzen Lauf traegt (Spezifikationen holen ihr Token einmal je Lauf).

Beides sind Lockerungen, die es ausserhalb eines Wegwerf-Containers nie geben darf. Deshalb bricht das Skript ab,
wenn es nicht in CI laeuft (``CI=true``) oder der Anbieter nicht auf dieser Maschine liegt.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from urllib.parse import urlparse

import httpx

REALM = "valeo-neuro-erp"
FRONTEND = "valeo-neuro-erp-frontend"
TESTMANDANT = "00000000-0000-0000-0000-000000000001"

# Rollen je Kennung. Verwaltung bekommt den ganzen Katalog, damit Smoke-Wege nicht an einer fehlenden Fachrolle
# scheitern; die beiden anderen bilden die Abstufungen der Testfaelle ab.
KENNUNGEN = {
    "admin": {"env_user": "VALEO_USER_ADMIN", "env_pass": "VALEO_PASS_ADMIN", "rollen": "*", "scopes": ["admin:all"]},
    "power": {"env_user": "VALEO_USER_POWER", "env_pass": "VALEO_PASS_POWER",
              "rollen": ("manager", "_BEARBEITEN", "_LESEN"), "scopes": []},
    "readonly": {"env_user": "VALEO_USER_READ", "env_pass": "VALEO_PASS_READ",
                 "rollen": ("user", "_LESEN"), "scopes": []},
}


def wegwerf_umgebung(url: str) -> None:
    if os.environ.get("CI") != "true":
        raise SystemExit("Nur in CI: lockert den Anbieter (Password Grant) und legt Kennungen an.")
    if urlparse(url).hostname not in {"localhost", "127.0.0.1"}:
        raise SystemExit("Nur gegen einen Anbieter auf dieser Maschine.")


def passt(rolle: str, muster) -> bool:
    if muster == "*":
        return True
    return any(rolle == m or (m.startswith("_") and rolle.endswith(m)) for m in muster)


def main() -> None:
    url = os.environ.get("VALEO_IDP_URL", "http://127.0.0.1:8080")
    wegwerf_umgebung(url)
    admin_user = os.environ["VALEO_IDP_ADMIN_USERNAME"]
    admin_pass = os.environ["VALEO_IDP_ADMIN_PASSWORD"]
    lebensdauer = int(os.environ.get("VALEO_E2E_TOKEN_SECONDS", "3600"))
    with httpx.Client(base_url=url, timeout=20) as c:
        login = c.post("/realms/master/protocol/openid-connect/token", data={
            "grant_type": "password", "client_id": "admin-cli", "username": admin_user, "password": admin_pass})
        login.raise_for_status()
        h = {"Authorization": "Bearer " + login.json()["access_token"]}
        basis = f"/admin/realms/{REALM}"

        realm = c.get(basis, headers=h).json()
        realm["accessTokenLifespan"] = lebensdauer
        c.put(basis, headers=h, json=realm).raise_for_status()

        gefunden = c.get(f"{basis}/clients", headers=h, params={"clientId": FRONTEND}).json()
        if len(gefunden) != 1:
            raise SystemExit("Frontend-Client fehlt oder ist mehrdeutig")
        client = c.get(f"{basis}/clients/{gefunden[0]['id']}", headers=h).json()
        client["directAccessGrantsEnabled"] = True
        client["webOrigins"] = sorted(set(client.get("webOrigins") or []) | {"http://127.0.0.1:4173"})
        c.put(f"{basis}/clients/{client['id']}", headers=h, json=client).raise_for_status()

        alle_rollen = [r for r in c.get(f"{basis}/roles", headers=h, params={"max": 500}).json()
                       if not r["name"].startswith("default-roles-") and r["name"] not in {"offline_access", "uma_authorization"}]
        ergebnis = {}
        for name, k in KENNUNGEN.items():
            benutzer, kennwort = os.environ[k["env_user"]], os.environ[k["env_pass"]]
            antwort = c.post(f"{basis}/users", headers=h, json={
                "username": benutzer, "email": benutzer if "@" in benutzer else f"{benutzer}@e2e.invalid", "emailVerified": True,
                "enabled": True, "firstName": "E2E", "lastName": name, "requiredActions": [],
                "attributes": {"tenant_id": [TESTMANDANT], "identity_type": ["human"], "erp_scopes": k["scopes"]},
                "credentials": [{"type": "password", "temporary": False, "value": kennwort}]})
            if antwort.status_code != 201:
                raise SystemExit(f"Kennung {name} nicht angelegt ({antwort.status_code}): {antwort.text[:300]}")
            uid = antwort.headers["location"].rstrip("/").split("/")[-1]
            rollen = [r for r in alle_rollen if passt(r["name"], k["rollen"])]
            c.post(f"{basis}/users/{uid}/role-mappings/realm", headers=h, json=rollen).raise_for_status()

            # Gegenprobe: das Token muss Mandant, Zielgruppe und Rollen tragen, sonst scheitert jeder Test spaeter
            # mit einem unklaren 401/403.
            probe = c.post(f"/realms/{REALM}/protocol/openid-connect/token", data={
                "grant_type": "password", "client_id": FRONTEND, "username": benutzer, "password": kennwort,
                "scope": "openid"})
            probe.raise_for_status()
            teil = probe.json()["access_token"].split(".")[1]
            claims = json.loads(base64.urlsafe_b64decode(teil + "=" * (-len(teil) % 4)))
            aud = claims.get("aud") if isinstance(claims.get("aud"), list) else [claims.get("aud")]
            if claims.get("tenant_id") != TESTMANDANT or "valeo-neuro-erp-backend" not in aud:
                raise SystemExit(f"Token der Kennung {name} ohne Mandant oder Zielgruppe: "
                                 f"{sorted(k for k in claims if k not in {'jti', 'sid', 'session_state'})}")
            ergebnis[name] = len(rollen)
    print(json.dumps({"kennungen": ergebnis, "token_sekunden": lebensdauer}))


if __name__ == "__main__":
    sys.exit(main())

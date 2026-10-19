"""Role-restricted document scopes from the existing ERP authorization tuples."""
from __future__ import annotations

import httpx

from app.auth.beleg_roles import rollen_fuer
from app.core.belegvertrag import BELEGARTEN

ERP_CLIENT_IDS = frozenset({"valeo-neuro-erp-frontend", "valeo-neuro-erp-backend", "valeo-erp-staging",
                            "valeo-neuro-erp-cli"})

# Project the existing domain decisions; never maintain a parallel role list.
DOCUMENT_SCOPE_ROLES = {
    "belege:read": tuple(sorted(set().union(*(rollen_fuer("lesen", art) for art in BELEGARTEN)))),
    "belege:write": tuple(sorted(set().union(*(
        rollen_fuer(recht, art) for art in BELEGARTEN
        for recht in ("bearbeiten", "ausstellen", "buchen", "stornieren")
    )))),
}


def document_scopes() -> list[dict]:
    return [{"name": name, "protocol": "openid-connect",
             "attributes": {"include.in.token.scope": "true", "display.on.consent.screen": "true"},
             "protocolMappers": []} for name in DOCUMENT_SCOPE_ROLES]


def reconcile_document_scope_roles(client: httpx.Client, headers: dict, realm: str,
                                   scopes: dict[str, str]) -> None:
    """Bind before client assignment. Never grant a new ERP role to a user here."""
    for name, names in DOCUMENT_SCOPE_ROLES.items():
        route = f"/admin/realms/{realm}/client-scopes/{scopes[name]}/scope-mappings/realm"
        response = client.get(route, headers=headers)
        response.raise_for_status()
        records = response.json()
        existing = {r["name"] for r in records}
        # Explicit retirement, not a general cleanup of unknown permissions.
        retired = [r for r in records if r["name"] == "manager" and r["name"] not in names]
        if existing - set(names) - {r["name"] for r in retired}:
            raise RuntimeError("Document scope has undeclared role mappings")
        if retired:
            if any(not r.get("id") for r in retired):
                raise RuntimeError("Retired document scope role was not verified")
            removed = client.request("DELETE", route, headers=headers, json=retired)
            if removed.status_code != 204:
                raise RuntimeError("Retired document scope role removal failed")
            response = client.get(route, headers=headers)
            response.raise_for_status()
            existing = {r["name"] for r in response.json()}
            if existing - set(names):
                raise RuntimeError("Retired document scope role removal did not persist")
        roles = []
        for role in names:
            response = client.get(f"/admin/realms/{realm}/roles/{role}", headers=headers)
            response.raise_for_status()
            record = response.json()
            if record.get("name") != role or not record.get("id"):
                raise RuntimeError("Document scope role was not verified")
            if role not in existing:
                roles.append(record)
        if roles:
            response = client.post(route, headers=headers, json=roles)
            if response.status_code != 204:
                raise RuntimeError("Document scope role mapping failed")
        verified = client.get(route, headers=headers)
        verified.raise_for_status()
        if {r["name"] for r in verified.json()} != set(names):
            raise RuntimeError("Document scope role mapping did not persist")
        # A previously imported scope may have been excluded from the token.
        scope_route = f"/admin/realms/{realm}/client-scopes/{scopes[name]}"
        response = client.get(scope_route, headers=headers)
        response.raise_for_status()
        current = response.json()
        if current.get("name") != name or current.get("protocol") != "openid-connect":
            raise RuntimeError("Document scope representation mismatch")
        attrs = current.setdefault("attributes", {})
        if attrs.get("include.in.token.scope") != "true":
            attrs["include.in.token.scope"] = "true"
            response = client.put(scope_route, headers=headers, json=current)
            if response.status_code != 204:
                raise RuntimeError("Document token scope activation failed")
            verified = client.get(scope_route, headers=headers)
            verified.raise_for_status()
            if verified.json().get("attributes", {}).get("include.in.token.scope") != "true":
                raise RuntimeError("Document token scope activation did not persist")

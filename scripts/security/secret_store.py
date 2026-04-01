#!/usr/bin/env python3
"""
Lokale Secret-Verwaltung fuer VALEO NeuroERP.

Default-Provider ist das OS-Keyring, falls das Python-Paket ``keyring``
verfuegbar ist. Alternativ kann bewusst ``memory`` verwendet werden.
"""

from __future__ import annotations

import argparse
import json
import sys

from app.services.secrets_vault import (
    SecretProvider,
    SecretType,
    check_health,
    delete_secret,
    get_secret,
    list_secrets,
    store_secret,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VALEO local secret store")
    sub = parser.add_subparsers(dest="command", required=True)

    set_cmd = sub.add_parser("set", help="Secret speichern")
    set_cmd.add_argument("key")
    set_cmd.add_argument("value")
    set_cmd.add_argument("--type", choices=[item.value for item in SecretType], default=SecretType.API_KEY.value)
    set_cmd.add_argument("--provider", choices=[item.value for item in SecretProvider], default=SecretProvider.KEYRING.value)
    set_cmd.add_argument("--description", default="")

    get_cmd = sub.add_parser("get", help="Secret lesen")
    get_cmd.add_argument("key")

    delete_cmd = sub.add_parser("delete", help="Secret loeschen")
    delete_cmd.add_argument("key")

    sub.add_parser("list", help="Gespeicherte Secret-Metadaten listen")
    sub.add_parser("health", help="Vault-Health anzeigen")

    config_cmd = sub.add_parser("config", help="Aktive Secret-Konfiguration anzeigen")
    config_cmd.add_argument("--json", action="store_true", help="Als JSON ausgeben")

    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    try:
        if args.command == "set":
            metadata = store_secret(
                args.key,
                args.value,
                secret_type=SecretType(args.type),
                provider=SecretProvider(args.provider),
                description=args.description,
            )
            print(json.dumps(metadata.to_dict(), indent=2))
            return 0

        if args.command == "get":
            value = get_secret(args.key, accessor="secret_store_cli")
            if value is None:
                print(f"Secret '{args.key}' nicht gefunden.", file=sys.stderr)
                return 1
            print(value)
            return 0

        if args.command == "delete":
            deleted = delete_secret(args.key, deleted_by="secret_store_cli")
            if not deleted:
                print(f"Secret '{args.key}' nicht gefunden.", file=sys.stderr)
                return 1
            print(f"Secret '{args.key}' geloescht.")
            return 0

        if args.command == "list":
            print(json.dumps([item.to_dict() for item in list_secrets()], indent=2))
            return 0

        if args.command == "health":
            print(json.dumps(check_health(), indent=2))
            return 0

        if args.command == "config":
            from app.core.config import settings

            payload = {
                "secret_provider": settings.SECRET_PROVIDER,
                "require_external_secrets_in_production": settings.REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION,
                "hashicorp_vault_addr": settings.HASHICORP_VAULT_ADDR,
                "hashicorp_vault_mount": settings.HASHICORP_VAULT_MOUNT,
                "hashicorp_vault_path_prefix": settings.HASHICORP_VAULT_PATH_PREFIX,
            }
            print(json.dumps(payload, indent=2))
            return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

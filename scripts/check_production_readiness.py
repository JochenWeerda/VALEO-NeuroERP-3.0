from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml


PLACEHOLDER_PATTERNS = (
    r"(?i)\bchangeme\b",
    r"(?i)\bchange[-_ ]?me\b",
    r"(?i)\bdev-token\b",
    r"(?i)\badmin123!?\b",
    r"(?i)\btest123!?\b",
    r"(?i)\bpassword\b",
    r"(?i)\breplace[-_ ]?me\b",
    r"(?i)\bexample\.test\b",
)
SECRET_KEYS = (
    "password",
    "secret",
    "token",
    "private_key",
    "api_key",
    "client_secret",
)
REQUIRED_RUNTIME_ENV = (
    "APP_ENV",
    "DATABASE_URL",
    "OIDC_ISSUER_URL",
    "OIDC_CLIENT_ID",
)


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return data


def _walk(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, nested
            yield from _walk(nested, path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            path = f"{prefix}[{index}]"
            yield path, nested
            yield from _walk(nested, path)


def _is_placeholder(value: str) -> bool:
    return any(re.search(pattern, value) for pattern in PLACEHOLDER_PATTERNS)


def validate_compose(path: Path, environment: str) -> list[str]:
    data = _load_yaml(path)
    findings: list[str] = []
    services = data.get("services")
    if not isinstance(services, dict) or not services:
        return [f"{path}: services fehlen"]

    for service_name, service in services.items():
        if not isinstance(service, dict):
            continue
        command = service.get("command")
        command_text = " ".join(command) if isinstance(command, list) else str(command or "")
        if "--reload" in command_text or "start-dev" in command_text:
            findings.append(f"{path}:{service_name}: Development-Command in {environment}")
        environment_values = service.get("environment", {})
        if isinstance(environment_values, list):
            pairs = {}
            for entry in environment_values:
                key, _, value = str(entry).partition("=")
                pairs[key] = value
            environment_values = pairs
        if isinstance(environment_values, dict):
            for key, value in environment_values.items():
                text = str(value or "")
                key_lower = str(key).lower()
                if key_lower in {"debug", "demo_mode"} and text.lower() in {"1", "true", "yes"}:
                    findings.append(f"{path}:{service_name}:{key} darf in {environment} nicht aktiv sein")
                if key == "API_DEV_TOKEN" and text:
                    findings.append(f"{path}:{service_name}: API_DEV_TOKEN ist produktiv verboten")
                if any(token in key_lower for token in SECRET_KEYS):
                    if text and not re.fullmatch(r"\$\{[A-Z0-9_]+(?::[?-].*)?\}", text):
                        findings.append(f"{path}:{service_name}:{key} muss aus Secret-Injection kommen")
                if _is_placeholder(text):
                    findings.append(f"{path}:{service_name}:{key} enthaelt einen Platzhalter/Default")
                if key in {"ALLOWED_HOSTS", "CORS_ORIGINS"} and "*" in text:
                    findings.append(f"{path}:{service_name}:{key} darf keinen Wildcard-Host enthalten")
        ports = service.get("ports", [])
        if service_name.lower() in {"postgres", "redis", "nats", "postgres-keycloak"} and ports:
            findings.append(f"{path}:{service_name}: Infrastruktur-Port darf produktiv nicht am Host exponiert sein")
    return findings


def validate_helm(path: Path) -> list[str]:
    data = _load_yaml(path)
    findings: list[str] = []
    image = data.get("image", {})
    backend_tag = image.get("tag") if isinstance(image, dict) else None
    immutable_tag = r"sha-(?:[0-9a-f]{40}|required-by-release-workflow)"
    if not isinstance(backend_tag, str) or not re.fullmatch(immutable_tag, backend_tag):
        findings.append(f"{path}: Backend-Image-Tag muss sha-<40-stelliger Git-SHA> sein")
    frontend = data.get("frontend", {})
    if not isinstance(frontend, dict) or frontend.get("enabled") is not True:
        findings.append(f"{path}: produktives Frontend ist nicht aktiviert")
    frontend_image = frontend.get("image", {}) if isinstance(frontend, dict) else {}
    frontend_tag = frontend_image.get("tag") if isinstance(frontend_image, dict) else None
    if not isinstance(frontend_tag, str) or not re.fullmatch(immutable_tag, frontend_tag):
        findings.append(f"{path}: Frontend-Image-Tag muss sha-<40-stelliger Git-SHA> sein")
    if data.get("postgresql", {}).get("enabled") is True:
        findings.append(f"{path}: produktive Datenbank muss extern/operativ verwaltet werden")
    if data.get("redis", {}).get("enabled") is True:
        findings.append(f"{path}: produktives Redis muss extern/operativ verwaltet werden")
    if data.get("keycloak", {}).get("enabled") is True:
        findings.append(f"{path}: produktives OIDC muss extern/operativ verwaltet werden")
    if not data.get("externalSecret", {}).get("name"):
        findings.append(f"{path}: externalSecret.name fehlt")
    backup = data.get("backup", {})
    if not backup.get("enabled"):
        findings.append(f"{path}: Backup-CronJob ist nicht aktiviert")
    if not backup.get("restoreTest", {}).get("enabled"):
        findings.append(f"{path}: Restore-Test-CronJob ist nicht aktiviert")
    for key_path, value in _walk(data):
        if isinstance(value, str) and _is_placeholder(value):
            findings.append(f"{path}:{key_path} enthaelt einen Platzhalter/Default")
    return findings


def validate_runtime_env(environment: str) -> list[str]:
    findings: list[str] = []
    for key in REQUIRED_RUNTIME_ENV:
        value = os.getenv(key, "")
        if not value:
            findings.append(f"Runtime: {key} fehlt")
        elif _is_placeholder(value):
            findings.append(f"Runtime: {key} enthaelt einen Platzhalter")
    if os.getenv("APP_ENV", "").lower() != environment.lower():
        findings.append(f"Runtime: APP_ENV muss {environment} sein")
    if os.getenv("DEBUG", "").lower() in {"1", "true", "yes"}:
        findings.append("Runtime: DEBUG muss false sein")
    if os.getenv("API_DEV_TOKEN"):
        findings.append("Runtime: API_DEV_TOKEN muss leer sein")
    for key in ("ALLOWED_HOSTS", "CORS_ORIGINS"):
        if "*" in os.getenv(key, ""):
            findings.append(f"Runtime: {key} darf keinen Wildcard-Host enthalten")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed production readiness preflight")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--compose-file", type=Path, required=True)
    parser.add_argument("--helm-values", type=Path, required=True)
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    findings = [
        *validate_compose(args.compose_file, args.environment),
        *validate_helm(args.helm_values),
    ]
    if not args.contract_only:
        findings.extend(validate_runtime_env(args.environment))

    result = {
        "environment": args.environment,
        "status": "blocked" if findings else "ready",
        "findings": findings,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())

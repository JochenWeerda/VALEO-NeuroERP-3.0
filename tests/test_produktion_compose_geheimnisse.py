"""M5: Die Produktions-Compose startet nicht ohne gesetzte Geheimnisse und kennt kein Dev-Token (24.11.2026).

``${VAR}`` wird bei fehlender Variable still leer - ein Postgres-, Keycloak- oder Grafana-Konto haette dann ein leeres
Kennwort. ``${VAR:?...}`` bricht den Start mit einer Meldung ab.
"""
from __future__ import annotations

import re
from pathlib import Path

COMPOSE = Path(__file__).resolve().parents[1] / "docker-compose.production.yml"
GEHEIM = re.compile(r"PASSWORD|SECRET|_ADMIN\b|TOKEN|_KEY\b")


def test_jedes_geheimnis_ist_pflicht():
    text = COMPOSE.read_text(encoding="utf-8")
    verweise = re.findall(r"\$\{([A-Z0-9_]+)(:[?-][^}]*)?\}", text)
    offen = sorted({name for name, rest in verweise if GEHEIM.search(name) and not (rest or "").startswith(":?")})
    assert not offen, f"Geheimnisse ohne Pflichtpruefung (${{VAR:?...}}): {offen}"


def test_keine_vorgabe_fuer_geheimnisse_und_kein_dev_token():
    text = COMPOSE.read_text(encoding="utf-8")
    vorgaben = sorted({n for n, rest in re.findall(r"\$\{([A-Z0-9_]+)(:-[^}]*)\}", text) if GEHEIM.search(n)})
    assert not vorgaben, f"Geheimnisse mit Vorgabewert: {vorgaben}"
    assert "API_DEV_TOKEN" not in text

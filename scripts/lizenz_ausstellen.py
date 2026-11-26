#!/usr/bin/env python3
"""Lizenzen fuer VALEO ausstellen (Herstellerseite, M7) - Gegenstueck zu app/core/lizenz.py.

    python scripts/lizenz_ausstellen.py schluessel --ziel C:/Hersteller/valeo_lizenz      # einmalig: Schluesselpaar
    python scripts/lizenz_ausstellen.py ausstellen --privat C:/Hersteller/valeo_lizenz.privat \\
        --kunde "Landhandel Muster eG" --module core agrar --gueltig-bis 2027-12-31 --ziel lizenz.json

Der private Schluessel bleibt beim Hersteller (nie ins Repository, nie auf den Kundenserver). Beim Kunden liegen nur die
Lizenzdatei (``VALEO_LIZENZ_DATEI``) und der oeffentliche Schluessel (``VALEO_LIZENZ_OEFFENTLICHER_SCHLUESSEL``).
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def schluesselpaar(ziel: Path) -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    privat = Ed25519PrivateKey.generate()
    roh = privat.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                               serialization.NoEncryption())
    oeffentlich = privat.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ziel.with_suffix(".privat").write_bytes(base64.b64encode(roh))
    return base64.b64encode(oeffentlich).decode()


def ausstellen(privat_b64: str, *, kunde: str, module: list[str], gueltig_bis: date,
               mandanten: list[str] | None = None, ausgestellt: date | None = None) -> dict:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from app.core.lizenz import kanonisch

    inhalt = {"kunde": kunde, "module": sorted(set(module)), "mandanten": sorted(mandanten) if mandanten else None,
              "gueltig_bis": gueltig_bis.isoformat(), "ausgestellt": (ausgestellt or date.today()).isoformat()}
    schluessel = Ed25519PrivateKey.from_private_bytes(base64.b64decode(privat_b64))
    return {"lizenz": inhalt, "signatur": base64.b64encode(schluessel.sign(kanonisch(inhalt))).decode()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    unter = parser.add_subparsers(dest="befehl", required=True)
    s = unter.add_parser("schluessel")
    s.add_argument("--ziel", type=Path, required=True)
    a = unter.add_parser("ausstellen")
    a.add_argument("--privat", type=Path, required=True)
    a.add_argument("--kunde", required=True)
    a.add_argument("--module", nargs="+", required=True)
    a.add_argument("--mandanten", nargs="*")
    a.add_argument("--gueltig-bis", type=date.fromisoformat, required=True)
    a.add_argument("--ziel", type=Path, required=True)
    args = parser.parse_args()
    if args.befehl == "schluessel":
        print("Oeffentlicher Schluessel (VALEO_LIZENZ_OEFFENTLICHER_SCHLUESSEL):", schluesselpaar(args.ziel))
        print(f"Privater Schluessel: {args.ziel.with_suffix('.privat')} - sicher verwahren, nie ins Repository.")
        return 0
    dokument = ausstellen(args.privat.read_text().strip(), kunde=args.kunde, module=args.module,
                          gueltig_bis=args.gueltig_bis, mandanten=args.mandanten)
    args.ziel.write_text(json.dumps(dokument, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Lizenz geschrieben: {args.ziel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

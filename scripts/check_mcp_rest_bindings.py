#!/usr/bin/env python
"""CI gate: live production OpenAPI vs Process-Kernel read-tool parameters."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core.mcp_rest_binding import check_read_binding
from app.core.mcp_tool_contracts import get_process_kernel_mcp_tools


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, help="Explicit OpenAPI input; default regenerates production app spec")
    args = parser.parse_args()
    if args.spec:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
    else:
        from scripts.generate_openapi import build_spec
        spec = build_spec()
    tools = get_process_kernel_mcp_tools().tools
    errors = [error for tool in tools for error in check_read_binding(spec, tool)]
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    count = sum(tool.api_endpoint.startswith(("GET ", "HEAD ")) for tool in tools)
    print(f"OK: {count} read-tool REST bindings checked; POST/approval/CLI parity not covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

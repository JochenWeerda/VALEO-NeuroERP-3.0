#!/usr/bin/env python3
"""Gate FastAPI routes without a declared response contract.

Inspect each decorator structurally, including FastAPI's inferred return models
and native file/text responses. Malformed source fails rather than hiding gaps.
"""

from __future__ import annotations

import argparse
import ast
import os
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"

_METHODS = {"get", "post", "put", "patch", "delete"}
_NATIVE_RESPONSES = {
    "Response", "StreamingResponse", "FileResponse", "PlainTextResponse",
    "HTMLResponse", "RedirectResponse",
}


def _symbol(node: ast.expr | None) -> str:
    return ast.unparse(node) if node is not None else ""


def _has_model(node: ast.expr | None) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        # FastAPI resolves postponed/quoted return annotations too.
        node = ast.parse(node.value, mode="eval").body
    return node is not None and _symbol(node) not in {"None", "Any", "typing.Any", "object"}


def _count_untyped(content: str) -> tuple[int, int]:
    """Return (untyped, total); exemptions never affect another route."""
    tree = ast.parse(content.removeprefix("\ufeff"))
    native = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in {"fastapi", "fastapi.responses", "starlette.responses"}:
            native.update(alias.asname or alias.name for alias in node.names if alias.name in _NATIVE_RESPONSES)
    untyped = total = 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                    and isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == "router"
                    and decorator.func.attr in _METHODS):
                continue
            total += 1
            options = {kw.arg: kw.value for kw in decorator.keywords}
            if "response_model" in options:
                # Explicit None is FastAPI's intentional disabled-model contract.
                covered = _symbol(options["response_model"]) == "None" or _has_model(options["response_model"])
            else:
                status = options.get("status_code")
                no_body = isinstance(status, ast.Constant) and status.value in {204, 205, 304}
                covered = (no_body or _symbol(options.get("response_class")) in native
                           or _symbol(node.returns) in native or _has_model(node.returns))
            untyped += not covered
    return untyped, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", type=int, default=0,
        help="Max allowed routes without a response contract (default: 0)",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    total_untyped = 0
    total_routes = 0
    files_with_gaps: list[tuple[str, int, int]] = []

    for fname in sorted(os.listdir(ENDPOINTS_DIR)):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(ENDPOINTS_DIR, fname)
        content = open(path, encoding="utf-8").read()
        untyped, total = _count_untyped(content)
        total_untyped += untyped
        total_routes += total
        if untyped > 0:
            files_with_gaps.append((fname, untyped, total))

    typed = total_routes - total_untyped
    pct = round(100 * typed / total_routes, 1) if total_routes else 0

    print(f"Response model coverage: {typed}/{total_routes} routes ({pct}%)")
    print(f"Untyped routes: {total_untyped} (threshold: {args.threshold})")

    if args.verbose:
        print("\nFiles with untyped routes (top 20):")
        for fname, u, t in sorted(files_with_gaps, key=lambda x: -x[1])[:20]:
            print(f"  {fname:50s} {u:4d}/{t:4d}")

    if total_untyped > args.threshold:
        print(
            f"\nFAIL: {total_untyped} untyped routes exceeds threshold {args.threshold}.",
            file=sys.stderr,
        )
        print(
            "Response contract coverage REGRESSED. Declare response_model or a valid return/response contract.",
            file=sys.stderr,
        )
        return 1

    print("OK — no regression in response model coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

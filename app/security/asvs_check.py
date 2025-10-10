***REMOVED***!/usr/bin/env python3
"""
OWASP ASVS Compliance Check
Minimal automated check for ASVS Level 2 controls
"""

import sys
import requests
from typing import Dict, Callable

***REMOVED*** Target URL (override via env)
import os
TARGET = os.environ.get("ASVS_TARGET", "http://localhost:8000/health")

def check_hsts(value: str) -> bool:
    """Check HSTS header"""
    return "max-age=" in value and int(value.split("max-age=")[1].split(";")[0]) >= 31536000

def check_csp(value: str) -> bool:
    """Check CSP header"""
    return "default-src" in value and "'self'" in value

def check_nosniff(value: str) -> bool:
    """Check X-Content-Type-Options"""
    return value.lower() == "nosniff"

def check_referrer(value: str) -> bool:
    """Check Referrer-Policy"""
    valid_policies = [
        "strict-origin",
        "strict-origin-when-cross-origin",
        "no-referrer",
    ]
    return value in valid_policies

def check_frame_options(value: str) -> bool:
    """Check X-Frame-Options"""
    return value.upper() in ["DENY", "SAMEORIGIN"]


***REMOVED*** ASVS Controls Map
CHECKS: Dict[str, Callable[[str], bool]] = {
    "Strict-Transport-Security": check_hsts,
    "Content-Security-Policy": check_csp,
    "X-Content-Type-Options": check_nosniff,
    "Referrer-Policy": check_referrer,
    "X-Frame-Options": check_frame_options,
}


def main():
    """Run ASVS checks"""
    print(f"🔍 Running ASVS checks against: {TARGET}")
    
    try:
        response = requests.get(TARGET, timeout=10)
        headers = response.headers
    except Exception as e:
        print(f"❌ Failed to connect to target: {e}")
        sys.exit(1)

    failed = []
    passed = []

    for header_name, check_fn in CHECKS.items():
        value = headers.get(header_name)
        
        if not value:
            failed.append(f"{header_name} (missing)")
            continue
        
        if not check_fn(value):
            failed.append(f"{header_name} (weak: {value[:50]}...)")
            continue
        
        passed.append(header_name)

    ***REMOVED*** Results
    print(f"\n✅ Passed: {len(passed)}/{len(CHECKS)}")
    for h in passed:
        print(f"  ✓ {h}")

    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(CHECKS)}")
        for h in failed:
            print(f"  ✗ {h}")
        sys.exit(1)

    print("\n🎉 All ASVS header checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())


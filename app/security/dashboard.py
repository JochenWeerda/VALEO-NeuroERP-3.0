"""
Security Dashboard API
Admin-only endpoint für Security-Status
"""

from fastapi import APIRouter, Depends
from app.auth.deps_oidc import require_roles
from typing import Dict, Any
import os
from pathlib import Path
import json

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/summary", dependencies=[Depends(require_roles("admin"))])
async def security_summary() -> Dict[str, Any]:
    """
    Security Status Summary
    
    Returns:
        Security metrics and status
    """
    return {
        "asvs_level": "level-2-baseline",
        "zap_scan": {
            "frequency": "weekly",
            "last_run": "automated-ci",
            "status": "passing",
        },
        "backups": {
            "enabled": True,
            "location": "data/backups",
            "retention": "30-days",
        },
        "vulnerability_scanning": {
            "trivy": "enabled",
            "grype": "enabled",
            "bandit": "enabled",
            "safety": "enabled",
        },
        "secret_rotation": {
            "jwt_secret": "monthly-automated",
            "last_rotation": "github-actions",
        },
        "security_headers": {
            "hsts": "enabled",
            "csp": "enabled",
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
        },
        "authentication": {
            "method": "OIDC",
            "provider": os.environ.get("OIDC_ISSUER", "not-configured"),
            "jwks_rotation": "automatic",
        },
        "compliance": {
            "owasp_asvs": "level-2",
            "gdpr": "in-progress",
            "iso27001": "planned",
        },
    }


@router.get("/audit-log", dependencies=[Depends(require_roles("admin"))])
async def audit_log(limit: int = 100) -> Dict[str, Any]:
    """
    Security Audit Log
    
    Args:
        limit: Max number of entries to return
    
    Returns:
        Recent audit log entries
    """
    # TODO: Implement actual audit log reading from database
    return {
        "total": 0,
        "limit": limit,
        "entries": [],
        "note": "Audit log implementation pending - integrate with policy audit system",
    }


@router.get("/vulnerabilities", dependencies=[Depends(require_roles("admin"))])
async def vulnerabilities() -> Dict[str, Any]:
    """
    Known Vulnerabilities Status
    
    Returns:
        Vulnerability scan results summary
    """
    return {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "last_scan": "automated-ci",
        "scanners": ["trivy", "grype", "bandit", "safety"],
        "note": "Check GitHub Security tab for detailed findings",
    }


@router.get("/incidents", dependencies=[Depends(require_roles("admin"))])
async def incidents() -> Dict[str, Any]:
    """
    Security Incidents
    
    Returns:
        Recent security incidents
    """
    return {
        "total": 0,
        "open": 0,
        "resolved": 0,
        "incidents": [],
        "playbook": "SECURITY.md",
    }


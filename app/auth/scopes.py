"""
RBAC Scopes Definition
Scope-basierte Zugriffskontrolle für alle Endpoints
"""

from typing import Dict, List

# Scope-Definitionen
SCOPES = {
    # Sales
    "sales:read": "Verkaufsbelege lesen",
    "sales:write": "Verkaufsbelege erstellen/bearbeiten",
    "sales:approve": "Verkaufsbelege freigeben",
    "sales:post": "Verkaufsbelege buchen",
    
    # Purchase
    "purchase:read": "Einkaufsbelege lesen",
    "purchase:write": "Einkaufsbelege erstellen/bearbeiten",
    "purchase:approve": "Einkaufsbelege freigeben",
    "purchase:post": "Einkaufsbelege buchen",
    
    # Documents
    "docs:export": "Dokumente exportieren (CSV/XLSX)",
    "docs:print": "Dokumente drucken",
    "docs:archive": "Archiv verwalten",
    
    # Policy
    "policy:read": "Policies lesen",
    "policy:write": "Policies erstellen/bearbeiten/löschen",
    
    # Admin
    "admin:all": "Vollzugriff (Admin)",
}

# Rollen → Scopes Mapping
ROLE_SCOPES: Dict[str, List[str]] = {
    "admin": [
        "admin:all",
        "sales:read", "sales:write", "sales:approve", "sales:post",
        "purchase:read", "purchase:write", "purchase:approve", "purchase:post",
        "docs:export", "docs:print", "docs:archive",
        "policy:read", "policy:write",
    ],
    "manager": [
        "sales:read", "sales:write", "sales:approve",
        "purchase:read", "purchase:write", "purchase:approve",
        "docs:export", "docs:print",
        "policy:read",
    ],
    "controller": [
        "sales:read", "sales:approve", "sales:post",
        "purchase:read", "purchase:approve", "purchase:post",
        "docs:export",
    ],
    "operator": [
        "sales:read", "sales:write",
        "purchase:read", "purchase:write",
        "docs:print",
    ],
}


def get_scopes_for_roles(roles: List[str]) -> List[str]:
    """Holt alle Scopes für gegebene Rollen"""
    scopes = set()
    for role in roles:
        scopes.update(ROLE_SCOPES.get(role, []))
    return list(scopes)


def has_scope(user_scopes: List[str], required_scope: str) -> bool:
    """Prüft ob User einen Scope hat"""
    # admin:all gibt alle Rechte
    if "admin:all" in user_scopes:
        return True
    return required_scope in user_scopes


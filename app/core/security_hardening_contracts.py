"""
security_hardening_contracts.py — Security-Hardening-Contracts (Wave 34, Gap 049)

Modelliert Security-Controls, RBAC-Permission-Checks und Secret-Klassifikation
als Core-Contracts ohne IAM-/ORM-Abhaengigkeit.

Gap 049: Security-Hardening (OIDC, RBAC fein, Secrets, Audit) — 0 kritische Pentest-Findings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SecurityControlKategorie(str, Enum):
    """OWASP-basierte Kontrollkategorie."""
    AUTHENTIFIZIERUNG    = "AUTHENTIFIZIERUNG"   # A01/A07: Auth-Kontrollen
    AUTORISIERUNG        = "AUTORISIERUNG"        # A01: Access Control
    KRYPTOGRAPHIE        = "KRYPTOGRAPHIE"        # A02: Crypto Failures
    INJECTION_SCHUTZ     = "INJECTION_SCHUTZ"     # A03: Injection
    FEHLERMANAGEMENT     = "FEHLERMANAGEMENT"     # A05: Security Misconfig
    LOGGING_MONITORING   = "LOGGING_MONITORING"   # A09: Logging & Monitoring
    SECRETS_MANAGEMENT   = "SECRETS_MANAGEMENT"  # A02: Sensitive Data
    TENANT_ISOLATION     = "TENANT_ISOLATION"     # Mandantentrennung


class SecurityControlStatus(str, Enum):
    """Implementierungsstand eines Security-Controls."""
    IMPLEMENTIERT     = "IMPLEMENTIERT"      # Vollstaendig umgesetzt
    TEILWEISE         = "TEILWEISE"          # Grundgeruest vorhanden, lueckenhaft
    GEPLANT           = "GEPLANT"            # Noch nicht implementiert
    NICHT_ANWENDBAR   = "NICHT_ANWENDBAR"   # Nicht relevant fuer dieses System


class SecurityFindingSchwere(str, Enum):
    """Schweregrad eines Security-Findings."""
    KRITISCH  = "KRITISCH"   # CVSS >= 9.0 — sofort beheben
    HOCH      = "HOCH"       # CVSS 7.0-8.9
    MITTEL    = "MITTEL"     # CVSS 4.0-6.9
    NIEDRIG   = "NIEDRIG"    # CVSS < 4.0
    INFO      = "INFO"       # Keine direkte Verwundbarkeit


class RBACPermission(str, Enum):
    """Feingranulaere RBAC-Berechtigungen im Canonical-Modell."""
    # Kontrakt
    KONTRAKT_LESEN       = "KONTRAKT_LESEN"
    KONTRAKT_ERSTELLEN   = "KONTRAKT_ERSTELLEN"
    KONTRAKT_AENDERN     = "KONTRAKT_AENDERN"
    KONTRAKT_STORNIEREN  = "KONTRAKT_STORNIEREN"
    # Settlement
    SETTLEMENT_LESEN     = "SETTLEMENT_LESEN"
    SETTLEMENT_FREIGEBEN = "SETTLEMENT_FREIGEBEN"
    SETTLEMENT_STORNIEREN = "SETTLEMENT_STORNIEREN"
    # Finance
    ZAHLUNGSLAUF_STARTEN  = "ZAHLUNGSLAUF_STARTEN"
    ZAHLUNGSLAUF_FREIGEBEN = "ZAHLUNGSLAUF_FREIGEBEN"
    BUCHUNG_ERSTELLEN     = "BUCHUNG_ERSTELLEN"
    # Compliance
    MELDUNG_EINREICHEN    = "MELDUNG_EINREICHEN"
    MELDUNG_STORNIEREN    = "MELDUNG_STORNIEREN"
    # Administration
    TENANT_KONFIGURIEREN  = "TENANT_KONFIGURIEREN"
    BENUTZER_VERWALTEN    = "BENUTZER_VERWALTEN"
    AUDIT_EINSEHEN        = "AUDIT_EINSEHEN"
    # Agent
    AGENT_AKTION_AUSFUEHREN = "AGENT_AKTION_AUSFUEHREN"
    AGENT_APPROVAL_GEBEN    = "AGENT_APPROVAL_GEBEN"


class SecretKlassifikation(str, Enum):
    """Klassifikation von Secrets fuer Logging/Speicherung."""
    OEFFENTLICH        = "OEFFENTLICH"        # Darf geloggt werden
    INTERN             = "INTERN"             # Nur interne Systeme sehen
    VERTRAULICH        = "VERTRAULICH"        # Verschluesselt speichern, nicht loggen
    STRENG_VERTRAULICH = "STRENG_VERTRAULICH" # Niemals loggen, HSM/Vault


# ---------------------------------------------------------------------------
# Security-Control
# ---------------------------------------------------------------------------

@dataclass
class SecurityControl:
    """
    Definition eines Security-Controls.

    Modelliert den Implementierungsstand ohne direkten Code-Bezug —
    dient als pruefbarer Kontrakt fuer Security-Reviews und Pentests.
    """
    control_id: str
    kategorie: SecurityControlKategorie
    titel: str
    beschreibung: str
    status: SecurityControlStatus
    owasp_referenz: str = ""        # z.B. "A01:2021"
    pruef_frage: str = ""           # Wie wird der Control verifiziert?
    implementiert_in: list[str] = field(default_factory=list)  # Module/Pfade
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "control_id": self.control_id,
            "kategorie": self.kategorie.value,
            "titel": self.titel,
            "beschreibung": self.beschreibung,
            "status": self.status.value,
            "owasp_referenz": self.owasp_referenz,
            "pruef_frage": self.pruef_frage,
            "implementiert_in": self.implementiert_in,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Security-Finding
# ---------------------------------------------------------------------------

@dataclass
class SecurityFinding:
    """Konkretes Security-Finding (aus Review oder Pentest)."""
    finding_id: str
    control_id: str
    titel: str
    beschreibung: str
    schwere: SecurityFindingSchwere
    status_offen: bool = True
    empfehlung: str = ""
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "control_id": self.control_id,
            "titel": self.titel,
            "beschreibung": self.beschreibung,
            "schwere": self.schwere.value,
            "status_offen": self.status_offen,
            "empfehlung": self.empfehlung,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# RBAC-Permission-Check
# ---------------------------------------------------------------------------

@dataclass
class RBACPermissionCheck:
    """
    Typisierte RBAC-Pruefanfrage.
    Kein Datenbankzugriff — evaluiert gegen Policy-Regeln.
    """
    user_id: str
    tenant_id: str
    rolle: str                      # z.B. "sachbearbeiter", "buchhaltung", "admin"
    permission: RBACPermission
    ressource_id: str = ""          # Optionale Ressourcen-ID fuer Row-Level-Security


@dataclass
class RBACPermissionResult:
    """Ergebnis der RBAC-Pruefung."""
    erlaubt: bool
    user_id: str
    rolle: str
    permission: RBACPermission
    begruendung: str
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "erlaubt": self.erlaubt,
            "user_id": self.user_id,
            "rolle": self.rolle,
            "permission": self.permission.value,
            "begruendung": self.begruendung,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Rollen-Permission-Matrix (Default)
# ---------------------------------------------------------------------------

_ROLLEN_PERMISSIONS: dict[str, set[RBACPermission]] = {
    "sachbearbeiter": {
        RBACPermission.KONTRAKT_LESEN,
        RBACPermission.KONTRAKT_ERSTELLEN,
        RBACPermission.SETTLEMENT_LESEN,
        RBACPermission.MELDUNG_EINREICHEN,
    },
    "buchhaltung": {
        RBACPermission.KONTRAKT_LESEN,
        RBACPermission.SETTLEMENT_LESEN,
        RBACPermission.SETTLEMENT_FREIGEBEN,
        RBACPermission.ZAHLUNGSLAUF_STARTEN,
        RBACPermission.BUCHUNG_ERSTELLEN,
        RBACPermission.AUDIT_EINSEHEN,
    },
    "leiter": {
        RBACPermission.KONTRAKT_LESEN,
        RBACPermission.KONTRAKT_ERSTELLEN,
        RBACPermission.KONTRAKT_AENDERN,
        RBACPermission.KONTRAKT_STORNIEREN,
        RBACPermission.SETTLEMENT_LESEN,
        RBACPermission.SETTLEMENT_FREIGEBEN,
        RBACPermission.SETTLEMENT_STORNIEREN,
        RBACPermission.ZAHLUNGSLAUF_STARTEN,
        RBACPermission.ZAHLUNGSLAUF_FREIGEBEN,
        RBACPermission.BUCHUNG_ERSTELLEN,
        RBACPermission.MELDUNG_EINREICHEN,
        RBACPermission.MELDUNG_STORNIEREN,
        RBACPermission.AUDIT_EINSEHEN,
        RBACPermission.AGENT_APPROVAL_GEBEN,
    },
    "admin": {p for p in RBACPermission},  # Alle Permissions
    "agent_system": {
        RBACPermission.KONTRAKT_LESEN,
        RBACPermission.SETTLEMENT_LESEN,
        RBACPermission.AGENT_AKTION_AUSFUEHREN,
    },
}


def evaluate_rbac_permission(check: RBACPermissionCheck) -> RBACPermissionResult:
    """
    Prueft deterministisch ob eine Rolle die angefragte Permission hat.

    Args:
        check: Die Pruefanfrage mit Rolle und Permission.

    Returns:
        RBACPermissionResult.
    """
    erlaubte = _ROLLEN_PERMISSIONS.get(check.rolle.lower(), set())
    erlaubt = check.permission in erlaubte

    if erlaubt:
        begruendung = (
            f"Rolle '{check.rolle}' besitzt Permission '{check.permission.value}'."
        )
    else:
        begruendung = (
            f"Rolle '{check.rolle}' hat KEINE Permission '{check.permission.value}'. "
            f"Zulaessige Permissions: {sorted(p.value for p in erlaubte)[:5]}"
            + (" ..." if len(erlaubte) > 5 else "")
        )

    return RBACPermissionResult(
        erlaubt=erlaubt,
        user_id=check.user_id,
        rolle=check.rolle,
        permission=check.permission,
        begruendung=begruendung,
    )


# ---------------------------------------------------------------------------
# Secret-Klassifikations-Registry
# ---------------------------------------------------------------------------

@dataclass
class SecretKlassifikationsRegel:
    """Regel zur Klassifikation eines Datenfeldes als Secret."""
    feld_muster: str                    # Feldname oder Pattern (z.B. "password", "iban")
    klassifikation: SecretKlassifikation
    loggen_erlaubt: bool                # Darf der Wert in Logs erscheinen?
    beschreibung: str

    def as_dict(self) -> dict:
        return {
            "feld_muster": self.feld_muster,
            "klassifikation": self.klassifikation.value,
            "loggen_erlaubt": self.loggen_erlaubt,
            "beschreibung": self.beschreibung,
        }


def get_default_secret_classifications() -> list[SecretKlassifikationsRegel]:
    """Liefert Default-Klassifikationsregeln fuer VALEO-Datenfelder."""
    return [
        SecretKlassifikationsRegel(
            "password", SecretKlassifikation.STRENG_VERTRAULICH, False,
            "Passwoerter niemals loggen oder persistieren",
        ),
        SecretKlassifikationsRegel(
            "api_key", SecretKlassifikation.STRENG_VERTRAULICH, False,
            "API-Keys sind Credentials — niemals loggen",
        ),
        SecretKlassifikationsRegel(
            "iban", SecretKlassifikation.VERTRAULICH, False,
            "IBAN ist Finanzdatum — verschluesselt speichern, nicht loggen",
        ),
        SecretKlassifikationsRegel(
            "bic", SecretKlassifikation.INTERN, True,
            "BIC kann intern geloggt werden (kein direktes Risiko)",
        ),
        SecretKlassifikationsRegel(
            "access_token", SecretKlassifikation.STRENG_VERTRAULICH, False,
            "JWT/OAuth-Token niemals loggen",
        ),
        SecretKlassifikationsRegel(
            "steuernummer", SecretKlassifikation.VERTRAULICH, False,
            "Steuernummer ist DSGVO-relevant — verschluesselt, nicht loggen",
        ),
        SecretKlassifikationsRegel(
            "tenant_id", SecretKlassifikation.INTERN, True,
            "Tenant-ID kann intern geloggt werden",
        ),
        SecretKlassifikationsRegel(
            "email", SecretKlassifikation.INTERN, True,
            "E-Mail-Adressen intern loggbar, extern anonymisieren",
        ),
        SecretKlassifikationsRegel(
            "kontonummer", SecretKlassifikation.VERTRAULICH, False,
            "Kontonummer verschluesselt speichern",
        ),
        SecretKlassifikationsRegel(
            "user_id", SecretKlassifikation.INTERN, True,
            "User-ID ist intern loggbar",
        ),
    ]


# ---------------------------------------------------------------------------
# Security-Posture-Evaluation
# ---------------------------------------------------------------------------

@dataclass
class SecurityPostureResult:
    """Gesamtbewertung des Security-Posture."""
    implementiert_count: int
    teilweise_count: int
    geplant_count: int
    offene_kritische_findings: int
    offene_hohe_findings: int
    gesamtbewertung: str               # "GUT", "AUSREICHEND", "KRITISCH"
    meldungen: list[str]
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "implementiert_count": self.implementiert_count,
            "teilweise_count": self.teilweise_count,
            "geplant_count": self.geplant_count,
            "offene_kritische_findings": self.offene_kritische_findings,
            "offene_hohe_findings": self.offene_hohe_findings,
            "gesamtbewertung": self.gesamtbewertung,
            "meldungen": self.meldungen,
            "schema_version": self.schema_version,
        }


def evaluate_security_posture(
    controls: list[SecurityControl],
    findings: list[SecurityFinding] | None = None,
) -> SecurityPostureResult:
    """
    Bewertet den aktuellen Security-Posture anhand der Controls und Findings.

    Args:
        controls: Liste aller Security-Controls.
        findings: Optionale Liste bekannter Findings.

    Returns:
        SecurityPostureResult.
    """
    findings = findings or []
    impl = sum(1 for c in controls if c.status == SecurityControlStatus.IMPLEMENTIERT)
    teil = sum(1 for c in controls if c.status == SecurityControlStatus.TEILWEISE)
    gep = sum(1 for c in controls if c.status == SecurityControlStatus.GEPLANT)

    offene_findings = [f for f in findings if f.status_offen]
    kritisch = sum(1 for f in offene_findings if f.schwere == SecurityFindingSchwere.KRITISCH)
    hoch = sum(1 for f in offene_findings if f.schwere == SecurityFindingSchwere.HOCH)

    meldungen: list[str] = []
    if kritisch > 0:
        meldungen.append(f"{kritisch} kritische Finding(s) offen — sofortiger Handlungsbedarf.")
    if hoch > 0:
        meldungen.append(f"{hoch} hohe Finding(s) offen.")
    if gep > 0:
        meldungen.append(f"{gep} Control(s) noch nicht implementiert.")
    if teil > 0:
        meldungen.append(f"{teil} Control(s) nur teilweise implementiert.")

    total = len([c for c in controls if c.status != SecurityControlStatus.NICHT_ANWENDBAR])
    if kritisch > 0:
        bewertung = "KRITISCH"
    elif hoch > 2 or (total > 0 and impl / total < 0.5):
        bewertung = "AUSREICHEND"
    else:
        bewertung = "GUT"

    return SecurityPostureResult(
        implementiert_count=impl,
        teilweise_count=teil,
        geplant_count=gep,
        offene_kritische_findings=kritisch,
        offene_hohe_findings=hoch,
        gesamtbewertung=bewertung,
        meldungen=meldungen,
    )


# ---------------------------------------------------------------------------
# Default-Security-Controls
# ---------------------------------------------------------------------------

def get_default_security_controls() -> list[SecurityControl]:
    """
    Liefert den Default-Katalog der VALEO-Security-Controls.

    Abdeckung: OIDC, RBAC, Secrets, Injection, Tenant-Isolation,
    Logging/Monitoring, Fehlerbehandlung.
    """
    return [
        SecurityControl(
            control_id="SC-AUTH-001",
            kategorie=SecurityControlKategorie.AUTHENTIFIZIERUNG,
            titel="OIDC Bearer-Token-Enforcement",
            beschreibung="Alle API-Endpunkte validieren Bearer-Token via OIDC/JWKS. "
                         "Kein API-Key-only-Zugang in Produktion.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A07:2021",
            pruef_frage="Schlaegt /api/v1/* ohne Token mit 401 fehl?",
            implementiert_in=["app/core/security.py", "app/middleware/"],
        ),
        SecurityControl(
            control_id="SC-AUTH-002",
            kategorie=SecurityControlKategorie.AUTHENTIFIZIERUNG,
            titel="Dev-Token-Bypass nur in Entwicklung",
            beschreibung="API_DEV_TOKEN darf in Produktion nicht gesetzt sein. "
                         "Startup-Check blockiert Start wenn DEV_TOKEN + PRODUCTION.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A05:2021",
            pruef_frage="Startet die App in PRODUCTION mit API_DEV_TOKEN?",
            implementiert_in=["app/main.py", "app/core/config.py"],
        ),
        SecurityControl(
            control_id="SC-AUTHZ-001",
            kategorie=SecurityControlKategorie.AUTORISIERUNG,
            titel="Tenant-Isolation per X-Tenant-ID Header",
            beschreibung="Alle Datenbankabfragen filtern nach Tenant-ID. "
                         "Cross-Tenant-Zugriff ist auf Middleware-Ebene blockiert.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A01:2021",
            pruef_frage="Kann Tenant A Daten von Tenant B lesen?",
            implementiert_in=["app/core/tenant_context.py", "app/middleware/"],
        ),
        SecurityControl(
            control_id="SC-AUTHZ-002",
            kategorie=SecurityControlKategorie.AUTORISIERUNG,
            titel="Feingranulaere RBAC-Permissions",
            beschreibung="Jede kritische Aktion (Settlement freigeben, Zahlungslauf starten) "
                         "prueft Rollenberechtigungen gegen RBACPermission-Enum.",
            status=SecurityControlStatus.TEILWEISE,
            owasp_referenz="A01:2021",
            pruef_frage="Kann Sachbearbeiter einen Zahlungslauf starten?",
            implementiert_in=["app/core/security_hardening_contracts.py"],
        ),
        SecurityControl(
            control_id="SC-CRYPTO-001",
            kategorie=SecurityControlKategorie.KRYPTOGRAPHIE,
            titel="Secrets nur via Vault/Env — niemals im Code",
            beschreibung="DATABASE_URL, REDIS_URL, API-Keys ausschliesslich ueber "
                         "Umgebungsvariablen oder Secret-Manager. Kein Hardcoding.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A02:2021",
            pruef_frage="Sind Credentials im Git-Repository?",
            implementiert_in=["app/core/config.py", ".env.example"],
        ),
        SecurityControl(
            control_id="SC-CRYPTO-002",
            kategorie=SecurityControlKategorie.KRYPTOGRAPHIE,
            titel="IBAN/Kontonummer verschluesselt gespeichert",
            beschreibung="Sensible Finanzdaten (IBAN, Kontonummer, Steuernummer) "
                         "werden AES-256 verschluesselt in der Datenbank gespeichert.",
            status=SecurityControlStatus.GEPLANT,
            owasp_referenz="A02:2021",
            pruef_frage="Liegt IBAN im Klartext in der DB?",
            implementiert_in=[],
        ),
        SecurityControl(
            control_id="SC-INJ-001",
            kategorie=SecurityControlKategorie.INJECTION_SCHUTZ,
            titel="ORM-only Datenbankzugriff (kein Raw SQL in Endpunkten)",
            beschreibung="Alle Datenbankabfragen laufen ueber SQLAlchemy ORM. "
                         "Raw-SQL nur in signierten Migrationsskripten.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A03:2021",
            pruef_frage="Gibt es f-String-SQL in Endpunkten?",
            implementiert_in=["app/infrastructure/repositories/"],
        ),
        SecurityControl(
            control_id="SC-INJ-002",
            kategorie=SecurityControlKategorie.INJECTION_SCHUTZ,
            titel="Input-Laengenbegrenzung vor Regex-Matching",
            beschreibung="Alle Pattern-Validierungen (DQ-Regeln) pruefen Eingabelaenge "
                         "vor re.fullmatch() — ReDoS-Schutz.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A03:2021",
            pruef_frage="Ist re.fullmatch() auf unbegrenzte Eingaben?",
            implementiert_in=["app/core/data_quality_rules.py"],
        ),
        SecurityControl(
            control_id="SC-ERR-001",
            kategorie=SecurityControlKategorie.FEHLERMANAGEMENT,
            titel="Strukturierte Fehlerantworten statt Stack-Traces",
            beschreibung="Alle 5xx-Fehler geben JSON-Fehlerstruktur zurueck. "
                         "Stack-Traces nur in Debug-Mode (nicht Produktion).",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A05:2021",
            pruef_frage="Gibt es Stack-Traces in API-Antworten in Produktion?",
            implementiert_in=["app/middleware/", "app/core/query_fallback_contracts.py"],
        ),
        SecurityControl(
            control_id="SC-LOG-001",
            kategorie=SecurityControlKategorie.LOGGING_MONITORING,
            titel="Audit-Trail fuer alle kritischen Aktionen",
            beschreibung="Settlement-Freigaben, Zahlungslaeufe, Policy-Overrides "
                         "werden mit SHA-256-Hash-Kette auditiert (GoBD-faehig).",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A09:2021",
            pruef_frage="Gibt es nicht-auditierte kritische Aktionen?",
            implementiert_in=["app/core/settlement_audit_chain.py", "app/core/action_idempotency.py"],
        ),
        SecurityControl(
            control_id="SC-LOG-002",
            kategorie=SecurityControlKategorie.LOGGING_MONITORING,
            titel="Secrets nicht in Logs",
            beschreibung="Passwort, IBAN, API-Key, Access-Token werden vor dem Logging "
                         "maskiert (SecretKlassifikation.STRENG_VERTRAULICH).",
            status=SecurityControlStatus.TEILWEISE,
            owasp_referenz="A09:2021",
            pruef_frage="Erscheinen Passwoerter oder Tokens in Logs?",
            implementiert_in=["app/core/security_hardening_contracts.py"],
        ),
        SecurityControl(
            control_id="SC-TENANT-001",
            kategorie=SecurityControlKategorie.TENANT_ISOLATION,
            titel="Tenant-Rate-Limits und Cache-Isolation",
            beschreibung="Jeder Tenant hat eigenen Rate-Limit-Zaehler und Cache-Namespace. "
                         "Cross-Tenant-Cache-Poisoning ist strukturell ausgeschlossen.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A01:2021",
            pruef_frage="Kann Tenant A den Cache von Tenant B beeinflussen?",
            implementiert_in=["app/core/tenant_rate_limits.py"],
        ),
        SecurityControl(
            control_id="SC-SECRET-001",
            kategorie=SecurityControlKategorie.SECRETS_MANAGEMENT,
            titel="Secret-Klassifikations-Registry",
            beschreibung="Alle Felder mit Finanzdaten, Credentials und PII sind "
                         "klassifiziert (SecretKlassifikation). Logging-Entscheidung "
                         "erfolgt programmatisch, nicht manuell.",
            status=SecurityControlStatus.IMPLEMENTIERT,
            owasp_referenz="A02:2021",
            pruef_frage="Gibt es nicht-klassifizierte Felder mit Finanzdaten?",
            implementiert_in=["app/core/security_hardening_contracts.py"],
        ),
    ]

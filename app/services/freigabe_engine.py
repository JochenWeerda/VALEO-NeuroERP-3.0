"""Die zentrale Approval Engine (APPROVAL-001).

Jeder buchungs- oder stornorelevante Vorgang fragt hier, ob er die Freigabe einer zweiten Person braucht und ob
eine gueltige vorliegt — gleich aus welchem Speicher der Beleg kommt und ueber welchen Zugang er ausgeloest wird.
Die Regel steht in ``app/core/freigabe.py``; diese Klasse setzt sie durch.

Ein Bereich schliesst sich an, indem er ``FreigabeEngine`` erbt und ``vorgang`` liefert: was der Vorgang ist
(Belegart, Betrag, Stand, Ersteller, freigaberelevanter Inhalt). Alles andere ist fuer alle gleich:

* Eine Freigabe ist an Mandant, Vorgang, Version, Aktion, Betrag und Ablaufzeit gebunden. Ihr Abdruck ist der
  freigaberelevante Inhalt; aendert sich davon etwas, ist sie ungueltig.
* Funktionstrennung: Wer den Vorgang angelegt oder die Freigabe angefragt hat, entscheidet nicht — auch nicht als
  Administrator. Ein technisches Konto entscheidet nie.
* Eine erteilte Freigabe wird beim Ausfuehren verbraucht, in der Transaktion des Kommandos.
* Jede Anfrage, Entscheidung, Ablehnung und jeder Verbrauch steht im unveraenderlichen Freigabeprotokoll
  (``domain_docflow.approval_log``).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.beleg_roles import darf, rollen_von
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.freigabe import AKTIONEN, GRUPPE, GUELTIGKEIT_STUNDEN, Anforderung, anforderung, wirksame_grenze


@dataclass
class Vorgang:
    """Was die Engine ueber einen Vorgang wissen muss — vom Bereich geliefert."""

    subject_id: str
    belegart: str  # eine Belegart des Belegvertrags; sie bestimmt Matrix und Rechte
    brutto: Decimal
    gebucht: bool
    beendet: bool = False  # storniert oder abgebrochen
    version: int = 1
    ersteller: Optional[str] = None
    inhalt: dict[str, Any] = field(default_factory=dict)  # alles Freigaberelevante
    abgleich_in_ordnung: bool = True
    abgleich_hinweis: str = ""
    brutto_des_vorgangs: Optional[Decimal] = None


class FreigabeEngine:
    SUBJEKT = ""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Vom Bereich zu liefern ────────────────────────────────────────────────

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        """Der Vorgang in seinem jetzigen Zustand. ``EntityNotFoundError``, wenn es ihn im Mandanten nicht gibt."""
        raise NotImplementedError

    def protokolliere_am_vorgang(self, subject_id: str, kommando: str, akteur: Optional[str], daten: dict[str, Any]) -> None:
        """Zusaetzlicher Eintrag in der Historie des Bereichs (z. B. Kommandoprotokoll des Belegs)."""

    # ── Regel ─────────────────────────────────────────────────────────────────

    def grenze(self, belegart: str) -> Optional[Decimal]:
        gruppe = GRUPPE.get(belegart)
        if gruppe is None:
            return None
        roh = self.db.execute(
            text("SELECT property_value FROM domain_shared.system_properties WHERE tenant_id = :t AND property_key = :k"),
            {"t": self.tenant_id, "k": f"freigabe.grenze.{gruppe}"},
        ).scalar()
        try:
            eigener = Decimal(str(roh)) if roh not in (None, "") else None
        except InvalidOperation:
            eigener = None  # Ein unlesbarer Wert lockert nichts: Es gilt die Systemvorgabe.
        return wirksame_grenze(gruppe, eigener)

    def anforderung(self, v: Vorgang, aktion: str) -> Anforderung:
        return anforderung(
            v.belegart, aktion, brutto=v.brutto, gebucht=v.gebucht, grenze=self.grenze(v.belegart),
            abgleich_in_ordnung=v.abgleich_in_ordnung, abgleich_hinweis=v.abgleich_hinweis,
            brutto_des_vorgangs=v.brutto_des_vorgangs,
        )

    def abdruck(self, v: Vorgang, aktion: str) -> str:
        inhalt = {"subjekt": self.SUBJEKT, "id": v.subject_id, "art": v.belegart, "aktion": aktion, "inhalt": v.inhalt}
        return hashlib.sha256(json.dumps(inhalt, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    # ── Lesen ─────────────────────────────────────────────────────────────────

    def liste(self, subject_id: str) -> list[dict[str, Any]]:
        zeilen = self.db.execute(
            text(
                "SELECT id, action, risk, amount, status, reason, requested_by, requested_at, decided_by, decided_at, "
                "decision_note, expires_at, consumed_at, subject_version, fingerprint FROM domain_docflow.approvals "
                "WHERE tenant_id = :t AND subject_type = :s AND subject_id = :id ORDER BY requested_at, id"
            ),
            {"t": self.tenant_id, "s": self.SUBJEKT, "id": subject_id},
        ).mappings().all()
        return [dict(z) for z in zeilen]

    def _passende(self, v: Vorgang, aktion: str, status: str) -> Optional[dict[str, Any]]:
        abdruck, jetzt = self.abdruck(v, aktion), datetime.now(timezone.utc)
        for f in reversed(self.liste(v.subject_id)):
            if f["action"] == aktion and f["status"] == status and f["fingerprint"] == abdruck and f["expires_at"] > jetzt:
                return f
        return None

    def gueltige_fuer(self, v: Vorgang, aktion: str) -> Optional[dict[str, Any]]:
        """Die erteilte, nicht abgelaufene Freigabe fuer genau diesen Inhalt — oder keine."""
        return self._passende(v, aktion, "granted")

    def offene_fuer(self, v: Vorgang, aktion: str) -> Optional[dict[str, Any]]:
        return self._passende(v, aktion, "requested")

    # ── Schreiben ─────────────────────────────────────────────────────────────

    def _protokoll(self, subject_id: str, kommando: str, akteur: Optional[str], daten: dict[str, Any]) -> None:
        self.db.execute(
            text(
                "INSERT INTO domain_docflow.approval_log (tenant_id, subject_type, subject_id, approval_id, event, actor, payload) "
                "VALUES (:t, :s, :id, :fid, :e, :a, CAST(:p AS jsonb))"
            ),
            {"t": self.tenant_id, "s": self.SUBJEKT, "id": subject_id, "fid": daten.get("approval_id"), "e": kommando,
             "a": akteur, "p": json.dumps(daten, default=str)},
        )
        self.protokolliere_am_vorgang(subject_id, kommando, akteur, daten)

    def beantrage(self, subject_id: str, aktion: str, antragsteller: str, grund: Optional[str] = None) -> dict[str, Any]:
        if aktion not in AKTIONEN:
            raise ValidationFailedError(f"Unbekannte Aktion: {aktion}")
        if not (antragsteller or "").strip():
            raise ValidationFailedError("Eine Freigabe braucht einen Antragsteller aus der Anmeldung.")
        v = self.vorgang(subject_id, aktion)
        bedarf = self.anforderung(v, aktion)
        if not bedarf.zweitfreigabe:
            raise ValidationFailedError(f"Dieser Vorgang braucht keine Freigabe durch eine zweite Person. {bedarf.grund}")
        if v.beendet:
            raise ValidationFailedError("Der Beleg ist storniert.")
        vorhanden = self.offene_fuer(v, aktion) or self.gueltige_fuer(v, aktion)
        if vorhanden:
            return {**vorhanden, "bereits_vorhanden": True}
        # Aeltere Anfragen und Freigaben zu einem anderen Inhalt gelten nicht mehr.
        self.db.execute(
            text(
                "UPDATE domain_docflow.approvals SET status = 'invalidated' WHERE tenant_id = :t AND subject_type = :s "
                "AND subject_id = :id AND action = :a AND status IN ('requested', 'granted')"
            ),
            {"t": self.tenant_id, "s": self.SUBJEKT, "id": subject_id, "a": aktion},
        )
        ablauf = datetime.now(timezone.utc) + timedelta(hours=GUELTIGKEIT_STUNDEN)
        neu = self.db.execute(
            text(
                "INSERT INTO domain_docflow.approvals (tenant_id, subject_type, subject_id, subject_version, action, amount, "
                "risk, fingerprint, reason, requested_by, expires_at) "
                "VALUES (:t, :s, :id, :v, :a, :betrag, :risk, :fp, :grund, :wer, :ablauf) RETURNING id"
            ),
            {"t": self.tenant_id, "s": self.SUBJEKT, "id": subject_id, "v": v.version, "a": aktion, "betrag": v.brutto,
             "risk": bedarf.risiko, "fp": self.abdruck(v, aktion), "grund": grund, "wer": antragsteller, "ablauf": ablauf},
        ).scalar()
        self._protokoll(subject_id, "approval_request", antragsteller,
                        {"approval_id": neu, "action": aktion, "risk": bedarf.risiko, "why": bedarf.grund})
        self.db.commit()
        return next(f for f in self.liste(subject_id) if f["id"] == neu)

    def entscheide(self, subject_id: str, freigabe_id: str, entscheider: Any, erteilt: bool,
                   notiz: Optional[str] = None) -> dict[str, Any]:
        """Erteilen oder ablehnen. ``entscheider`` ist das Benutzerobjekt der geprueften Anmeldung."""
        wer = str((entscheider or {}).get("sub") or "").strip() if isinstance(entscheider, dict) else ""
        if not wer:
            raise ValidationFailedError("Eine Freigabe entscheidet nur eine angemeldete Person.")
        freigabe = next((f for f in self.liste(subject_id) if f["id"] == freigabe_id), None)
        if freigabe is None:
            raise EntityNotFoundError("Approval", freigabe_id)
        v = self.vorgang(subject_id, str(freigabe["action"]))

        def ablehnen(grund: str, fehler: type[Exception] = ConflictError) -> None:
            self._protokoll(subject_id, "approval_refused", wer, {"approval_id": freigabe_id, "why": grund})
            self.db.commit()
            raise fehler(grund)

        if freigabe["status"] != "requested":
            ablehnen(f"Die Anfrage ist nicht mehr offen ({freigabe['status']}).")
        if freigabe["expires_at"] <= datetime.now(timezone.utc):
            self.db.execute(text("UPDATE domain_docflow.approvals SET status = 'expired' WHERE id = :id"), {"id": freigabe_id})
            ablehnen("Die Anfrage ist abgelaufen.")
        if freigabe["fingerprint"] != self.abdruck(v, freigabe["action"]):
            self.db.execute(text("UPDATE domain_docflow.approvals SET status = 'invalidated' WHERE id = :id"), {"id": freigabe_id})
            ablehnen("Der Beleg wurde seit der Anfrage geändert; die Anfrage gilt nicht mehr.")
        # Funktionstrennung — vor dem Rollenrecht, damit sie auch fuer Administratoren gilt.
        if wer in {str(freigabe["requested_by"]), str(v.ersteller or "")}:
            ablehnen("Funktionstrennung: Wer den Beleg angelegt oder die Freigabe angefragt hat, entscheidet nicht.",
                     ValidationFailedError)
        if technisches_konto(entscheider):
            ablehnen("Ein technisches Konto erteilt keine Freigabe.", ValidationFailedError)
        recht = "freigeben_erhoeht" if freigabe["risk"] == "R4" else "freigeben"
        if not darf(entscheider, recht, v.belegart):
            ablehnen(f"Keine Berechtigung für diese Freigabe ({freigabe['risk']}).", ValidationFailedError)

        self.db.execute(
            text(
                "UPDATE domain_docflow.approvals SET status = :st, decided_by = :wer, decided_at = clock_timestamp(), "
                "decision_note = :notiz WHERE id = :id AND tenant_id = :t AND status = 'requested'"
            ),
            {"st": "granted" if erteilt else "denied", "wer": wer, "notiz": notiz, "id": freigabe_id, "t": self.tenant_id},
        )
        self._protokoll(subject_id, "approval_grant" if erteilt else "approval_deny", wer,
                        {"approval_id": freigabe_id, "action": freigabe["action"], "risk": freigabe["risk"],
                         "roles": sorted(rollen_von(entscheider))})
        self.db.commit()
        return next(f for f in self.liste(subject_id) if f["id"] == freigabe_id)

    def verlange_fuer(self, v: Vorgang, aktion: str, akteur: Optional[str]) -> Optional[str]:
        """Vor dem Ausfuehren: Braucht der Vorgang eine Zweitfreigabe, muss eine gueltige vorliegen.

        Verbraucht die Freigabe — ohne Commit, in der Transaktion des Kommandos. Scheitert das Kommando danach,
        bleibt die Freigabe erteilt.
        """
        bedarf = self.anforderung(v, aktion)
        if not bedarf.zweitfreigabe:
            return None
        freigabe = self.gueltige_fuer(v, aktion)
        if freigabe is None:
            raise ConflictError(f"Freigabe erforderlich ({bedarf.risiko}): {bedarf.grund}")
        self.db.execute(
            text("UPDATE domain_docflow.approvals SET status = 'consumed', consumed_at = clock_timestamp() WHERE id = :id"),
            {"id": freigabe["id"]},
        )
        self._protokoll(v.subject_id, "approval_consume", akteur,
                        {"approval_id": freigabe["id"], "action": aktion, "risk": bedarf.risiko,
                         "decided_by": freigabe["decided_by"]})
        return str(freigabe["id"])


def technisches_konto(nutzer: Any) -> bool:
    """Dienstkonten des Anmeldeanbieters (Client-Credentials) sind keine zweite Person."""
    roh = nutzer.get("raw") if isinstance(nutzer, dict) else None
    name = str((roh or {}).get("preferred_username") or (nutzer.get("name") if isinstance(nutzer, dict) else "") or "")
    return name.startswith("service-account-") or bool((roh or {}).get("client_id") and not (roh or {}).get("preferred_username"))

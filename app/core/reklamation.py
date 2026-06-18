from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ReklamationsTyp(str, Enum):
    QUALITAET = "qualitaet"
    MENGE = "menge"
    PREIS = "preis"
    LIEFERTERMIN = "liefertermin"
    SONSTIGE = "sonstige"


class ReklamationsStatus(str, Enum):
    OFFEN = "offen"
    IN_PRUEFUNG = "in_pruefung"
    TEILWEISE_ANERKANNT = "teilweise_anerkannt"
    ANERKANNT = "anerkannt"
    ABGELEHNT = "abgelehnt"
    GESCHLOSSEN = "geschlossen"


class ReklamationsSLAStatus(str, Enum):
    IN_FRIST = "in_frist"
    BALD_FAELLIG = "bald_faellig"
    UEBERFAELLIG = "ueberfaellig"
    ERLEDIGT = "erledigt"


class ReklamationsAuditTyp(str, Enum):
    ERSTELLT = "erstellt"
    CRM_REFERENZ_VERKNUEPFT = "crm_referenz_verknuepft"
    DMS_REFERENZ_VERKNUEPFT = "dms_referenz_verknuepft"
    STATUS_GEAENDERT = "status_geaendert"
    SLA_BERECHNET = "sla_berechnet"


_GUELTIGE_UEBERGAENGE: dict[ReklamationsStatus, list[ReklamationsStatus]] = {
    ReklamationsStatus.OFFEN: [ReklamationsStatus.IN_PRUEFUNG, ReklamationsStatus.ABGELEHNT],
    ReklamationsStatus.IN_PRUEFUNG: [
        ReklamationsStatus.ANERKANNT,
        ReklamationsStatus.TEILWEISE_ANERKANNT,
        ReklamationsStatus.ABGELEHNT,
    ],
    ReklamationsStatus.TEILWEISE_ANERKANNT: [ReklamationsStatus.GESCHLOSSEN],
    ReklamationsStatus.ANERKANNT: [ReklamationsStatus.GESCHLOSSEN],
    ReklamationsStatus.ABGELEHNT: [ReklamationsStatus.GESCHLOSSEN],
    ReklamationsStatus.GESCHLOSSEN: [],
}


class ReklamationsPosition(BaseModel):
    artikel_id: str
    charge_id: Optional[str] = None
    beanstandete_menge: float
    anerkannte_menge: float = 0.0
    beanstandeter_wert_eur: float
    begruendung: str
    schema_version: int = 1


class ReklamationsCRMReferenz(BaseModel):
    crm_system: str
    crm_case_id: str
    crm_ticket_id: Optional[str] = None
    crm_status: Optional[str] = None
    crm_url: Optional[str] = None
    zugewiesen_am: datetime = Field(default_factory=datetime.utcnow)
    schema_version: int = 1


class ReklamationsDMSReferenz(BaseModel):
    dokument_id: str
    dokument_typ: Optional[str] = None
    dateiname: Optional[str] = None
    checksum: Optional[str] = None
    source_uri: Optional[str] = None
    hochgeladen_am: datetime = Field(default_factory=datetime.utcnow)
    schema_version: int = 1


class ReklamationsAuditEintrag(BaseModel):
    eintrag_id: str
    reklamation_id: str
    aktion: ReklamationsAuditTyp
    zeitstempel: datetime
    aktor_id: str
    vor_status: Optional[ReklamationsStatus] = None
    nach_status: Optional[ReklamationsStatus] = None
    beschreibung: str
    metadaten: dict[str, str] = Field(default_factory=dict)
    vorgaenger_hash: str = ""
    eintrag_hash: str = ""
    schema_version: int = 1

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "eintrag_hash", self._berechne_hash())

    def _berechne_hash(self) -> str:
        payload = json.dumps(
            {
                "eintrag_id": self.eintrag_id,
                "reklamation_id": self.reklamation_id,
                "aktion": self.aktion.value,
                "zeitstempel": self.zeitstempel.isoformat(),
                "aktor_id": self.aktor_id,
                "vor_status": self.vor_status.value if self.vor_status else None,
                "nach_status": self.nach_status.value if self.nach_status else None,
                "beschreibung": self.beschreibung,
                "metadaten": self.metadaten,
                "vorgaenger_hash": self.vorgaenger_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def pruefe_integritaet(self) -> bool:
        return self.eintrag_hash == self._berechne_hash()


class Reklamation(BaseModel):
    reklamation_id: str
    tenant_id: str
    kontrakt_id: Optional[str] = None
    lieferant_id: str
    typ: ReklamationsTyp
    status: ReklamationsStatus = ReklamationsStatus.OFFEN
    positionen: list[ReklamationsPosition]
    zustaendiger: str
    frist_datum: date
    erstellt_am: datetime
    crm_referenz: Optional[ReklamationsCRMReferenz] = None
    dms_referenzen: list[ReklamationsDMSReferenz] = Field(default_factory=list)
    gobd_beleg_id: Optional[str] = None
    audit_trail: list[ReklamationsAuditEintrag] = Field(default_factory=list)
    letzte_statusaenderung_am: Optional[datetime] = None
    geschlossen_am: Optional[datetime] = None
    sla_warnschwelle_tage: int = 3
    schema_version: int = 1

    @property
    def gesamtwert_beanstandet_eur(self) -> float:
        return sum(p.beanstandeter_wert_eur for p in self.positionen)

    @property
    def gesamtwert_anerkannt_eur(self) -> float:
        return sum(
            p.anerkannte_menge * (p.beanstandeter_wert_eur / p.beanstandete_menge)
            for p in self.positionen
            if p.beanstandete_menge > 0
        )

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status == ReklamationsStatus.GESCHLOSSEN

    @property
    def hat_crm_bezug(self) -> bool:
        return self.crm_referenz is not None

    @property
    def hat_dms_bezug(self) -> bool:
        return len(self.dms_referenzen) > 0

    def tage_bis_frist(self, as_of: date | None = None) -> int:
        bezugsdatum = as_of or date.today()
        return (self.frist_datum - bezugsdatum).days

    def berechne_sla_status(self, as_of: date | None = None) -> ReklamationsSLAStatus:
        if self.ist_abgeschlossen:
            return ReklamationsSLAStatus.ERLEDIGT
        tage = self.tage_bis_frist(as_of=as_of)
        if tage < 0:
            return ReklamationsSLAStatus.UEBERFAELLIG
        if tage <= self.sla_warnschwelle_tage:
            return ReklamationsSLAStatus.BALD_FAELLIG
        return ReklamationsSLAStatus.IN_FRIST

    def ist_ueberfaellig(self, as_of: date | None = None) -> bool:
        return self.berechne_sla_status(as_of=as_of) == ReklamationsSLAStatus.UEBERFAELLIG

    def audit_integritaet_ok(self) -> bool:
        vorgaenger_hash = ""
        for eintrag in self.audit_trail:
            if eintrag.vorgaenger_hash != vorgaenger_hash:
                return False
            if not eintrag.pruefe_integritaet():
                return False
            vorgaenger_hash = eintrag.eintrag_hash
        return True

    def as_dict(self, as_of: date | None = None) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        data.update(
            {
                "gesamtwert_beanstandet_eur": self.gesamtwert_beanstandet_eur,
                "gesamtwert_anerkannt_eur": self.gesamtwert_anerkannt_eur,
                "sla_status": self.berechne_sla_status(as_of=as_of).value,
                "tage_bis_frist": self.tage_bis_frist(as_of=as_of),
                "ist_ueberfaellig": self.ist_ueberfaellig(as_of=as_of),
                "hat_crm_bezug": self.hat_crm_bezug,
                "hat_dms_bezug": self.hat_dms_bezug,
                "audit_integritaet_ok": self.audit_integritaet_ok(),
                "audit_eintrag_anzahl": len(self.audit_trail),
            }
        )
        return data


class ReklamationZustandsmaschine:
    @staticmethod
    def erlaubte_statuswechsel(status: ReklamationsStatus) -> list[ReklamationsStatus]:
        return list(_GUELTIGE_UEBERGAENGE.get(status, []))

    @staticmethod
    def pruefe_statuswechsel(aktueller_status: ReklamationsStatus, neuer_status: ReklamationsStatus) -> None:
        erlaubt = _GUELTIGE_UEBERGAENGE.get(aktueller_status, [])
        if neuer_status not in erlaubt:
            raise ValueError(
                f"Ungueltiger Uebergang: {aktueller_status.value} -> {neuer_status.value}. "
                f"Erlaubt: {[s.value for s in erlaubt]}"
            )

    @staticmethod
    def transition(reklamation: Reklamation, neuer_status: ReklamationsStatus) -> Reklamation:
        erlaubt = _GUELTIGE_UEBERGAENGE.get(reklamation.status, [])
        if neuer_status not in erlaubt:
            raise ValueError(
                f"Ungültiger Übergang: {reklamation.status} → {neuer_status}. "
                f"Erlaubt: {[s.value for s in erlaubt]}"
            )
        reklamation.status = neuer_status
        reklamation.letzte_statusaenderung_am = datetime.utcnow()
        if neuer_status == ReklamationsStatus.GESCHLOSSEN:
            reklamation.geschlossen_am = reklamation.letzte_statusaenderung_am
        return reklamation


class ReklamationStore(BaseModel):
    reklamationen: dict[str, Reklamation] = Field(default_factory=dict)
    schema_version: int = 1

    def clear(self) -> None:
        self.reklamationen.clear()

    def add(self, r: Reklamation, *, aktor_id: str = "system") -> Reklamation:
        bereits_vorhanden = r.reklamation_id in self.reklamationen
        self.reklamationen[r.reklamation_id] = r
        self.record_event(
            reklamation_id=r.reklamation_id,
            aktion=ReklamationsAuditTyp.ERSTELLT if not bereits_vorhanden else ReklamationsAuditTyp.STATUS_GEAENDERT,
            aktor_id=aktor_id,
            beschreibung="Reklamation angelegt" if not bereits_vorhanden else "Reklamation aktualisiert",
            vor_status=None if not bereits_vorhanden else r.status,
            nach_status=r.status,
            metadaten=self._build_reference_metadata(r),
        )
        return r

    def get(self, reklamation_id: str) -> Optional[Reklamation]:
        return self.reklamationen.get(reklamation_id)

    def by_lieferant(self, lieferant_id: str) -> list[Reklamation]:
        return [r for r in self.reklamationen.values() if r.lieferant_id == lieferant_id]

    def by_kontrakt(self, kontrakt_id: str) -> list[Reklamation]:
        return [r for r in self.reklamationen.values() if r.kontrakt_id == kontrakt_id]

    def by_crm_case(self, crm_case_id: str) -> list[Reklamation]:
        return [
            r
            for r in self.reklamationen.values()
            if r.crm_referenz is not None and r.crm_referenz.crm_case_id == crm_case_id
        ]

    def offene(self, tenant_id: str) -> list[Reklamation]:
        return [
            r
            for r in self.reklamationen.values()
            if r.tenant_id == tenant_id and not r.ist_abgeschlossen
        ]

    def ueberfaellige(self, tenant_id: str, as_of: date | None = None) -> list[Reklamation]:
        return [
            r
            for r in self.reklamationen.values()
            if r.tenant_id == tenant_id and r.ist_ueberfaellig(as_of=as_of)
        ]

    def record_event(
        self,
        *,
        reklamation_id: str,
        aktion: ReklamationsAuditTyp,
        aktor_id: str,
        beschreibung: str,
        vor_status: ReklamationsStatus | None = None,
        nach_status: ReklamationsStatus | None = None,
        metadaten: dict[str, str] | None = None,
        zeitstempel: datetime | None = None,
    ) -> ReklamationsAuditEintrag:
        reklamation = self.get(reklamation_id)
        if reklamation is None:
            raise KeyError(f"Reklamation {reklamation_id!r} nicht gefunden")
        vorgaenger_hash = reklamation.audit_trail[-1].eintrag_hash if reklamation.audit_trail else ""
        eintrag = ReklamationsAuditEintrag(
            eintrag_id=f"REK-AUD-{uuid.uuid4()}",
            reklamation_id=reklamation_id,
            aktion=aktion,
            zeitstempel=zeitstempel or datetime.utcnow(),
            aktor_id=aktor_id,
            vor_status=vor_status,
            nach_status=nach_status,
            beschreibung=beschreibung,
            metadaten=metadaten or {},
            vorgaenger_hash=vorgaenger_hash,
        )
        reklamation.audit_trail.append(eintrag)
        return eintrag

    def transition(
        self,
        reklamation_id: str,
        neuer_status: ReklamationsStatus,
        *,
        aktor_id: str = "system",
        kommentar: str | None = None,
    ) -> Reklamation:
        reklamation = self.get(reklamation_id)
        if reklamation is None:
            raise KeyError(f"Reklamation {reklamation_id!r} nicht gefunden")
        alter_status = reklamation.status
        ReklamationZustandsmaschine.transition(reklamation, neuer_status)
        self.record_event(
            reklamation_id=reklamation_id,
            aktion=ReklamationsAuditTyp.STATUS_GEAENDERT,
            aktor_id=aktor_id,
            beschreibung=kommentar or f"Status {alter_status.value} -> {neuer_status.value}",
            vor_status=alter_status,
            nach_status=neuer_status,
            metadaten={"neuer_status": neuer_status.value},
        )
        return reklamation

    def set_crm_referenz(
        self,
        reklamation_id: str,
        crm_referenz: ReklamationsCRMReferenz,
        *,
        aktor_id: str = "system",
    ) -> Reklamation:
        reklamation = self.get(reklamation_id)
        if reklamation is None:
            raise KeyError(f"Reklamation {reklamation_id!r} nicht gefunden")
        reklamation.crm_referenz = crm_referenz
        self.record_event(
            reklamation_id=reklamation_id,
            aktion=ReklamationsAuditTyp.CRM_REFERENZ_VERKNUEPFT,
            aktor_id=aktor_id,
            beschreibung=f"CRM Fall {crm_referenz.crm_case_id} verknuepft",
            nach_status=reklamation.status,
            metadaten={
                "crm_system": crm_referenz.crm_system,
                "crm_case_id": crm_referenz.crm_case_id,
            },
        )
        return reklamation

    def add_dms_referenzen(
        self,
        reklamation_id: str,
        dms_referenzen: list[ReklamationsDMSReferenz],
        *,
        aktor_id: str = "system",
    ) -> Reklamation:
        reklamation = self.get(reklamation_id)
        if reklamation is None:
            raise KeyError(f"Reklamation {reklamation_id!r} nicht gefunden")
        for referenz in dms_referenzen:
            reklamation.dms_referenzen.append(referenz)
            if reklamation.gobd_beleg_id is None:
                reklamation.gobd_beleg_id = referenz.dokument_id
            self.record_event(
                reklamation_id=reklamation_id,
                aktion=ReklamationsAuditTyp.DMS_REFERENZ_VERKNUEPFT,
                aktor_id=aktor_id,
                beschreibung=f"DMS Dokument {referenz.dokument_id} verknuepft",
                nach_status=reklamation.status,
                metadaten={
                    "dokument_id": referenz.dokument_id,
                    "dokument_typ": referenz.dokument_typ or "",
                },
            )
        return reklamation

    def audit_trail(self, reklamation_id: str) -> list[ReklamationsAuditEintrag]:
        reklamation = self.get(reklamation_id)
        if reklamation is None:
            raise KeyError(f"Reklamation {reklamation_id!r} nicht gefunden")
        return list(reklamation.audit_trail)

    def _build_reference_metadata(self, reklamation: Reklamation) -> dict[str, str]:
        metadata: dict[str, str] = {
            "tenant_id": reklamation.tenant_id,
            "lieferant_id": reklamation.lieferant_id,
            "typ": reklamation.typ.value,
        }
        if reklamation.kontrakt_id:
            metadata["kontrakt_id"] = reklamation.kontrakt_id
        if reklamation.crm_referenz is not None:
            metadata["crm_case_id"] = reklamation.crm_referenz.crm_case_id
        if reklamation.gobd_beleg_id:
            metadata["gobd_beleg_id"] = reklamation.gobd_beleg_id
        metadata["dms_count"] = str(len(reklamation.dms_referenzen))
        return metadata

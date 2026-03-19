"""
Wave 69 - Central Knowledge Core Contracts.
Pure domain layer for a versioned, agent-ready enterprise knowledge store.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class KnowledgeObjectTyp(str, Enum):
    SOP = "SOP"
    PRODUKTWISSEN = "PRODUKTWISSEN"
    KOMMUNIKATIONSRICHTLINIE = "KOMMUNIKATIONSRICHTLINIE"
    SUPPORTWISSEN = "SUPPORTWISSEN"
    MARKTDATEN = "MARKTDATEN"
    KENNZAHL = "KENNZAHL"
    PROZESSDEFINITION = "PROZESSDEFINITION"


class KnowledgeStatus(str, Enum):
    ENTWURF = "ENTWURF"
    FREIGEGEBEN = "FREIGEGEBEN"
    ARCHIVIERT = "ARCHIVIERT"


class KnowledgeFormat(str, Enum):
    MARKDOWN = "MARKDOWN"
    JSON = "JSON"
    TABELLE = "TABELLE"
    RELATIONALE_DATEN = "RELATIONALE_DATEN"
    API_RESOURCE = "API_RESOURCE"
    PDF = "PDF"
    WORD = "WORD"


class KnowledgeChannel(str, Enum):
    CHAT = "CHAT"
    TEAMS = "TEAMS"
    SLACK = "SLACK"
    WEB = "WEB"
    VOICE = "VOICE"


AGENTENFAEHIGE_FORMATE = {
    KnowledgeFormat.MARKDOWN,
    KnowledgeFormat.JSON,
    KnowledgeFormat.TABELLE,
    KnowledgeFormat.RELATIONALE_DATEN,
    KnowledgeFormat.API_RESOURCE,
}


@dataclass(frozen=True)
class KnowledgeVersion:
    version: int
    format: KnowledgeFormat
    inhalt: str
    strukturierte_daten: dict[str, Any] = field(default_factory=dict)
    erstellt_am: datetime = field(default_factory=datetime.now)
    quelle: str = "system"

    def kurztext(self, max_laenge: int = 180) -> str:
        text = " ".join(self.inhalt.split())
        if len(text) <= max_laenge:
            return text
        return text[: max_laenge - 3].rstrip() + "..."


@dataclass
class KnowledgeObject:
    knowledge_id: str
    titel: str
    typ: KnowledgeObjectTyp
    status: KnowledgeStatus
    tenant_id: str = "system"
    beschreibung: str = ""
    tags: list[str] = field(default_factory=list)
    zielrollen: list[str] = field(default_factory=list)
    versionen: list[KnowledgeVersion] = field(default_factory=list)
    agentenfreigabe: bool = True

    def aktive_version(self) -> KnowledgeVersion:
        if not self.versionen:
            raise ValueError(f"KnowledgeObject {self.knowledge_id!r} hat keine Versionen")
        return max(self.versionen, key=lambda version: version.version)

    def hole_version(self, version: int | None = None) -> KnowledgeVersion:
        if version is None:
            return self.aktive_version()
        for vorhandene_version in self.versionen:
            if vorhandene_version.version == version:
                return vorhandene_version
        raise ValueError(f"Version {version!r} fuer {self.knowledge_id!r} nicht gefunden")

    def ist_agentenfaehig(self, version: int | None = None) -> bool:
        if self.status != KnowledgeStatus.FREIGEGEBEN or not self.agentenfreigabe:
            return False
        return self.hole_version(version).format in AGENTENFAEHIGE_FORMATE

    def passt_zu_rolle(self, rolle: str | None) -> bool:
        if not rolle:
            return True
        if not self.zielrollen:
            return True
        rolle_normalisiert = rolle.strip().lower()
        return rolle_normalisiert in {eintrag.lower() for eintrag in self.zielrollen}

    def suchtext(self, version: int | None = None) -> str:
        wissensversion = self.hole_version(version)
        teile = [
            self.knowledge_id,
            self.titel,
            self.beschreibung,
            " ".join(self.tags),
            " ".join(self.zielrollen),
            wissensversion.inhalt,
            " ".join(f"{key} {value}" for key, value in wissensversion.strukturierte_daten.items()),
        ]
        return " ".join(teil for teil in teile if teil).lower()

    def relevanz_score(self, query: str, version: int | None = None) -> float:
        tokens = [token for token in query.lower().split() if token]
        if not tokens:
            return 1.0
        suchraum = self.suchtext(version)
        score = 0.0
        for token in tokens:
            if token in suchraum:
                score += 1.0
            if token in self.titel.lower():
                score += 0.5
            if token in {tag.lower() for tag in self.tags}:
                score += 0.25
        return score / len(tokens)

    def as_dict(self, version: int | None = None) -> dict[str, Any]:
        wissensversion = self.hole_version(version)
        return {
            "knowledge_id": self.knowledge_id,
            "titel": self.titel,
            "typ": self.typ.value,
            "status": self.status.value,
            "tenant_id": self.tenant_id,
            "tags": self.tags,
            "zielrollen": self.zielrollen,
            "agentenfreigabe": self.agentenfreigabe,
            "agentenfaehig": self.ist_agentenfaehig(wissensversion.version),
            "aktive_version": self.aktive_version().version,
            "version": wissensversion.version,
            "format": wissensversion.format.value,
            "kurztext": wissensversion.kurztext(),
            "strukturierte_daten": wissensversion.strukturierte_daten,
        }


@dataclass(frozen=True)
class KnowledgeRetrievalRequest:
    query: str = ""
    typen: list[KnowledgeObjectTyp] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    tenant_id: str | None = None
    status: KnowledgeStatus | None = KnowledgeStatus.FREIGEGEBEN
    nur_agentenfaehig: bool = False
    rolle: str | None = None
    limit: int = 10


@dataclass(frozen=True)
class KnowledgeContextPack:
    rolle: str
    kanal: KnowledgeChannel
    tenant_id: str | None
    capability_key: str | None = None
    query: str = ""
    knowledge_ids: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    wissensobjekte: list[dict[str, Any]] = field(default_factory=list)
    prompt_hinweise: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rolle": self.rolle,
            "kanal": self.kanal.value,
            "tenant_id": self.tenant_id,
            "capability_key": self.capability_key,
            "query": self.query,
            "knowledge_ids": self.knowledge_ids,
            "standards": self.standards,
            "wissensobjekte": self.wissensobjekte,
            "prompt_hinweise": self.prompt_hinweise,
        }


def _default_knowledge_objects() -> list[KnowledgeObject]:
    return [
        KnowledgeObject(
            knowledge_id="KNW-SOP-001",
            titel="SOP Angebotsfreigabe",
            typ=KnowledgeObjectTyp.SOP,
            status=KnowledgeStatus.FREIGEGEBEN,
            beschreibung="Freigabeschritte fuer Angebotsdokumente und Sales-Prozesse.",
            tags=["angebot", "freigabe", "sales"],
            zielrollen=["vertrieb", "geschaeftsfuehrung"],
            versionen=[
                KnowledgeVersion(
                    version=1,
                    format=KnowledgeFormat.PDF,
                    inhalt="Historische PDF-Fassung der Angebotsfreigabe mit manuellen Notizen.",
                    quelle="legacy-dms",
                ),
                KnowledgeVersion(
                    version=2,
                    format=KnowledgeFormat.MARKDOWN,
                    inhalt=(
                        "Angebote ab 25000 EUR benoetigen Vier-Augen-Freigabe. "
                        "Standardtexte folgen dem Markenstil und muessen vor Versand geprueft werden."
                    ),
                    strukturierte_daten={
                        "freigabe_grenze_eur": 25000,
                        "prozess_owner": "vertrieb",
                    },
                    quelle="knowledge-core",
                ),
            ],
        ),
        KnowledgeObject(
            knowledge_id="KNW-COM-001",
            titel="Kommunikationsrichtlinie Vertrieb",
            typ=KnowledgeObjectTyp.KOMMUNIKATIONSRICHTLINIE,
            status=KnowledgeStatus.FREIGEGEBEN,
            beschreibung="Formulierungs- und Stilvorgaben fuer externe Kundenkommunikation.",
            tags=["kommunikation", "vertrieb", "markenstil"],
            zielrollen=["vertrieb", "marketing", "support"],
            versionen=[
                KnowledgeVersion(
                    version=1,
                    format=KnowledgeFormat.MARKDOWN,
                    inhalt=(
                        "Kundennutzen zuerst. Keine unbelegten Versprechen. "
                        "Antworten klar, verbindlich und mit naechstem Schritt formulieren."
                    ),
                    strukturierte_daten={"tonalitaet": "klar-verbindlich"},
                )
            ],
        ),
        KnowledgeObject(
            knowledge_id="KNW-PROD-001",
            titel="VALEO NeuroERP Produktwissen",
            typ=KnowledgeObjectTyp.PRODUKTWISSEN,
            status=KnowledgeStatus.FREIGEGEBEN,
            beschreibung="Produktkern fuer agentenfaehige ERP- und Wissensinfrastruktur.",
            tags=["produkt", "neuroerp", "agenten", "erp"],
            zielrollen=["vertrieb", "support", "it"],
            versionen=[
                KnowledgeVersion(
                    version=1,
                    format=KnowledgeFormat.JSON,
                    inhalt="VALEO NeuroERP verbindet ERP-Prozesse, Skills, APIs und Wissensspeicher.",
                    strukturierte_daten={
                        "kernmodule": ["workflow", "knowledge-core", "agent-layer"],
                        "zielbild": "mensch-agent-kollaboration",
                    },
                )
            ],
        ),
        KnowledgeObject(
            knowledge_id="KNW-SUP-001",
            titel="Supportwissen OIDC Anmeldung",
            typ=KnowledgeObjectTyp.SUPPORTWISSEN,
            status=KnowledgeStatus.FREIGEGEBEN,
            beschreibung="Standardwissen fuer haeufige Login- und Berechtigungsprobleme.",
            tags=["support", "oidc", "login", "berechtigung"],
            zielrollen=["support", "it"],
            versionen=[
                KnowledgeVersion(
                    version=1,
                    format=KnowledgeFormat.MARKDOWN,
                    inhalt=(
                        "Bei Login-Fehlern zuerst Tenant-Zuordnung und Rollenmapping pruefen. "
                        "OIDC-Scopes muessen mit dem Zielsystem abgeglichen werden."
                    ),
                    strukturierte_daten={"eskalation_team": "it-platform"},
                )
            ],
        ),
        KnowledgeObject(
            knowledge_id="KNW-KPI-001",
            titel="Kennzahl Umsatz Quartal",
            typ=KnowledgeObjectTyp.KENNZAHL,
            status=KnowledgeStatus.FREIGEGEBEN,
            beschreibung="Definition und Interpretation der Quartalsumsatz-KPI.",
            tags=["controlling", "umsatz", "quartal", "kpi"],
            zielrollen=["controlling", "geschaeftsfuehrung"],
            versionen=[
                KnowledgeVersion(
                    version=1,
                    format=KnowledgeFormat.RELATIONALE_DATEN,
                    inhalt="Quartalsumsatz = Summe fakturierter Umsaetze je Quartal.",
                    strukturierte_daten={
                        "sql_view": "finance_quarterly_revenue_v",
                        "kennzahl_typ": "quantitativ",
                    },
                )
            ],
        ),
        KnowledgeObject(
            knowledge_id="KNW-MKT-001",
            titel="Marktdaten Getreidepreise",
            typ=KnowledgeObjectTyp.MARKTDATEN,
            status=KnowledgeStatus.ENTWURF,
            beschreibung="Noch nicht freigegebene Rohdaten fuer Preisbeobachtung.",
            tags=["markt", "preise", "getreide"],
            zielrollen=["controlling", "einkauf"],
            versionen=[
                KnowledgeVersion(
                    version=1,
                    format=KnowledgeFormat.WORD,
                    inhalt="Rohnotizen aus einem Marktbriefing ohne finale Validierung.",
                    quelle="externes-briefing",
                )
            ],
            agentenfreigabe=False,
        ),
    ]


def get_default_knowledge_objects() -> list[KnowledgeObject]:
    return _default_knowledge_objects()


def get_knowledge_object(knowledge_id: str, objects: list[KnowledgeObject] | None = None) -> KnowledgeObject:
    kandidaten = objects or get_default_knowledge_objects()
    for obj in kandidaten:
        if obj.knowledge_id == knowledge_id:
            return obj
    raise ValueError(f"KnowledgeObject {knowledge_id!r} nicht gefunden")


def retrieve_knowledge_objects(
    request: KnowledgeRetrievalRequest,
    objects: list[KnowledgeObject] | None = None,
) -> list[dict[str, Any]]:
    kandidaten = objects or get_default_knowledge_objects()
    tag_filter = {tag.lower() for tag in request.tags}
    ergebnisse: list[tuple[float, KnowledgeObject]] = []

    for obj in kandidaten:
        if request.tenant_id and obj.tenant_id not in {request.tenant_id, "system", "global"}:
            continue
        if request.status and obj.status != request.status:
            continue
        if request.typen and obj.typ not in request.typen:
            continue
        if tag_filter and not tag_filter.issubset({tag.lower() for tag in obj.tags}):
            continue
        if request.nur_agentenfaehig and not obj.ist_agentenfaehig():
            continue
        if request.rolle and not obj.passt_zu_rolle(request.rolle):
            continue

        score = obj.relevanz_score(request.query)
        if request.query and score <= 0:
            continue
        ergebnisse.append((score, obj))

    ergebnisse.sort(key=lambda eintrag: (eintrag[0], eintrag[1].aktive_version().version), reverse=True)
    return [
        {
            **obj.as_dict(),
            "relevanz_score": score,
        }
        for score, obj in ergebnisse[: max(1, request.limit)]
    ]


def build_onboarding_bundle(
    rolle: str,
    tenant_id: str | None = None,
    limit: int = 5,
    objects: list[KnowledgeObject] | None = None,
) -> dict[str, Any]:
    request = KnowledgeRetrievalRequest(
        query="",
        tenant_id=tenant_id,
        status=KnowledgeStatus.FREIGEGEBEN,
        nur_agentenfaehig=True,
        rolle=rolle,
        limit=limit,
    )
    bundle = retrieve_knowledge_objects(request, objects=objects)
    return {
        "rolle": rolle,
        "tenant_id": tenant_id or "alle",
        "wissensobjekte": bundle,
        "anzahl": len(bundle),
    }


def build_context_pack(
    rolle: str,
    kanal: KnowledgeChannel = KnowledgeChannel.CHAT,
    tenant_id: str | None = None,
    capability_key: str | None = None,
    query: str = "",
    limit: int = 4,
    objects: list[KnowledgeObject] | None = None,
) -> KnowledgeContextPack:
    suchbegriffe = [query.strip()] if query.strip() else []
    if capability_key:
        suchbegriffe.append(capability_key.replace("_", " "))

    retrieval_request = KnowledgeRetrievalRequest(
        query=" ".join(begriff for begriff in suchbegriffe if begriff),
        tenant_id=tenant_id,
        status=KnowledgeStatus.FREIGEGEBEN,
        nur_agentenfaehig=True,
        rolle=rolle,
        limit=limit,
    )
    wissensobjekte = retrieve_knowledge_objects(retrieval_request, objects=objects)

    standards: list[str] = []
    prompt_hinweise = [
        f"Nutze nur freigegebenes Wissen fuer Rolle '{rolle}'.",
        "Beziehe Unternehmensstandards automatisch ein und erfinde keinen fehlenden Kontext.",
    ]

    if kanal in {KnowledgeChannel.TEAMS, KnowledgeChannel.SLACK, KnowledgeChannel.CHAT}:
        prompt_hinweise.append("Antworte kurz, arbeitsnah und mit naechstem Schritt.")
    elif kanal == KnowledgeChannel.VOICE:
        prompt_hinweise.append("Formuliere sprechbar, knapp und ohne Tabellenballast.")
    else:
        prompt_hinweise.append("Verweise bei Bedarf auf strukturierte Daten und Quellenobjekte.")

    if capability_key:
        prompt_hinweise.append(
            f"Capability-Kontext aktiv: {capability_key}."
        )

    for obj in wissensobjekte:
        if obj["typ"] == KnowledgeObjectTyp.KOMMUNIKATIONSRICHTLINIE.value:
            standards.append(f"Kommunikationsstandard aus {obj['knowledge_id']}")
        elif obj["typ"] == KnowledgeObjectTyp.SOP.value:
            standards.append(f"Prozessstandard aus {obj['knowledge_id']}")
        elif obj["typ"] == KnowledgeObjectTyp.KENNZAHL.value:
            standards.append(f"Kennzahlzugriff aus {obj['knowledge_id']}")

    return KnowledgeContextPack(
        rolle=rolle,
        kanal=kanal,
        tenant_id=tenant_id,
        capability_key=capability_key,
        query=query,
        knowledge_ids=[obj["knowledge_id"] for obj in wissensobjekte],
        standards=standards,
        wissensobjekte=wissensobjekte,
        prompt_hinweise=prompt_hinweise,
    )

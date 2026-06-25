"""P2.3 — Lokale KI-Datenklassen fuer VALEO NeuroERP.

Definiert welche Datenkategorien an externe KI-Modelle gesendet werden duerfen,
welche nur lokal verarbeitet werden duerfen und welche niemals in einen Modell-Kontext
gelangen duerfen.

Grundlage: DSGVO Art. 5, 25, 32; GoBD §147 AO; Berufsgeheimnisse;
           Bankgeheimnis; Steuergeheimnis; Betriebsgeheimnisse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DataClass(str, Enum):
    """KI-Daten-Zugriffsklassen (aufsteigend restriktiv)."""
    C0_OEFFENTLICH = "C0_oeffentlich"
    C1_EXTERN_KI_ERLAUBT = "C1_extern_ki_erlaubt"
    C2_EU_API_ONLY = "C2_eu_api_only"
    C3_NUR_LOKAL = "C3_nur_lokal"
    C4_ANONYMISIERT_OK = "C4_anonymisiert_ok"
    C5_NIE_MODELLKONTEXT = "C5_nie_modellkontext"


@dataclass
class DataCategoryRule:
    category_id: str
    name: str
    data_class: DataClass
    beispiele: list[str] = field(default_factory=list)
    rechtsgrundlage: list[str] = field(default_factory=list)
    erlaubte_ki_modelle: list[str] = field(default_factory=list)
    verbotene_aktionen: list[str] = field(default_factory=list)
    anonymisierung_ausreichend: bool = False
    kommentar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "category_id": self.category_id,
            "name": self.name,
            "data_class": self.data_class.value,
            "data_class_label": _CLASS_LABELS[self.data_class],
            "beispiele": self.beispiele,
            "rechtsgrundlage": self.rechtsgrundlage,
            "erlaubte_ki_modelle": self.erlaubte_ki_modelle,
            "verbotene_aktionen": self.verbotene_aktionen,
            "anonymisierung_ausreichend": self.anonymisierung_ausreichend,
            "kommentar": self.kommentar,
        }


_CLASS_LABELS: dict[DataClass, str] = {
    DataClass.C0_OEFFENTLICH: "Oeffentlich — keine Einschraenkung",
    DataClass.C1_EXTERN_KI_ERLAUBT: "Externes KI-Modell erlaubt (auch US-Anbieter)",
    DataClass.C2_EU_API_ONLY: "Nur EU-Rechenzentrum / EU-API",
    DataClass.C3_NUR_LOKAL: "Nur lokales KI-Modell (kein Cloud-API)",
    DataClass.C4_ANONYMISIERT_OK: "Anonymisiert/synthetisch fuer externes Modell OK",
    DataClass.C5_NIE_MODELLKONTEXT: "Niemals in Modellkontext — kein KI-Zugriff",
}

_RULES: list[DataCategoryRule] = [

    # ── C0 — Oeffentlich ──────────────────────────────────────────────────────
    DataCategoryRule(
        category_id="cat-pub-001",
        name="Oeffentliche Artikelstammdaten",
        data_class=DataClass.C0_OEFFENTLICH,
        beispiele=["Artikelbezeichnung", "Einheit", "Produktkategorie", "Marktpreise (publiziert)"],
        rechtsgrundlage=[],
        erlaubte_ki_modelle=["*"],
        kommentar="Keine personenbezogenen oder vertraulichen Daten.",
    ),

    # ── C1 — Externes KI erlaubt ──────────────────────────────────────────────
    DataCategoryRule(
        category_id="cat-crm-sum-001",
        name="Anonymisierte CRM-Zusammenfassungen",
        data_class=DataClass.C1_EXTERN_KI_ERLAUBT,
        beispiele=["Kundensegment", "Umsatzklasse (EUR-Bereich)", "Branche", "Region (PLZ-Bereich)"],
        rechtsgrundlage=["DSGVO Art. 6 Abs. 1 f"],
        erlaubte_ki_modelle=["claude-*", "gpt-*", "gemini-*"],
        anonymisierung_ausreichend=True,
        kommentar="Kein Name, keine kunden_nr, keine konkreten Betraege.",
    ),
    DataCategoryRule(
        category_id="cat-agr-pub-001",
        name="Marktdaten / Boersenkurse (MATIF, LIFFE)",
        data_class=DataClass.C1_EXTERN_KI_ERLAUBT,
        beispiele=["MATIF-Weizenpreis", "Rapspreis", "LIFFE-Kontrakt"],
        rechtsgrundlage=[],
        erlaubte_ki_modelle=["*"],
        kommentar="Publizierte Marktdaten ohne Bezug zu Tenants oder Kunden.",
    ),

    # ── C2 — EU API Only ──────────────────────────────────────────────────────
    DataCategoryRule(
        category_id="cat-fibu-buch-001",
        name="Buchungsdaten (nicht personenbezogen)",
        data_class=DataClass.C2_EU_API_ONLY,
        beispiele=["Kontonummer (SKR03)", "Buchungsbetrag", "Kostenstelle", "Buchungstext ohne Kundenbezug"],
        rechtsgrundlage=["GoBD §147 AO", "HGB §257"],
        erlaubte_ki_modelle=["claude-*@eu", "azure-openai@westeurope"],
        verbotene_aktionen=["Modelltraining auf Echtbuchungen", "Weitergabe an US-API ohne SCCs"],
        kommentar="FIBU-Daten benoetigen EU-Datenzentrum wegen GoBD und Steuergeheimnis.",
    ),

    # ── C3 — Nur lokal ────────────────────────────────────────────────────────
    DataCategoryRule(
        category_id="cat-personal-001",
        name="Personalstammdaten",
        data_class=DataClass.C3_NUR_LOKAL,
        beispiele=["Name", "Geburtsdatum", "Gehalt", "Sozialversicherungsnummer", "Bankverbindung Mitarbeiter"],
        rechtsgrundlage=["DSGVO Art. 9", "BetrVG", "BDSG §26"],
        erlaubte_ki_modelle=["ollama@localhost", "llama.cpp@localhost"],
        verbotene_aktionen=["Weitergabe an Cloud-API", "Speicherung in Vektordatenbank ohne Anonymisierung"],
        kommentar="Besondere Kategorien personenbezogener Daten. Nur lokale Modelle.",
    ),
    DataCategoryRule(
        category_id="cat-kunde-detail-001",
        name="Kundenstammdaten (vollstaendig)",
        data_class=DataClass.C3_NUR_LOKAL,
        beispiele=["Vollstaendiger Name", "Adresse", "kunden_nr", "IBAN", "Umsaetze je Kunde"],
        rechtsgrundlage=["DSGVO Art. 5 Abs. 1 b", "§ 241a HGB Buchfuehrungspflicht"],
        erlaubte_ki_modelle=["ollama@localhost"],
        verbotene_aktionen=["Weitergabe an US-KI-API", "Prompt mit Kundenprofil an externem Modell"],
        anonymisierung_ausreichend=False,
        kommentar="Kunden sind meist Unternehmen (B2B), trotzdem vertraulich wegen Betriebsgeheimnissen.",
    ),
    DataCategoryRule(
        category_id="cat-kontrakt-001",
        name="Kontraktdaten / Preisvereinbarungen",
        data_class=DataClass.C3_NUR_LOKAL,
        beispiele=["Kontraktpreis", "Menge", "Liefertermin", "Kontrahent", "MATIF-Basis"],
        rechtsgrundlage=["Betriebsgeheimnis", "GewSchG"],
        erlaubte_ki_modelle=["ollama@localhost"],
        verbotene_aktionen=["Weitergabe an externes Modell", "Logging in Cloud-Traces"],
        kommentar="Hochsensibel — Wettbewerbsvorteil, Betriebsgeheimnis.",
    ),

    # ── C4 — Anonymisiert OK ──────────────────────────────────────────────────
    DataCategoryRule(
        category_id="cat-qs-anon-001",
        name="QS-Labordaten (anonymisiert)",
        data_class=DataClass.C4_ANONYMISIERT_OK,
        beispiele=["Feuchte-Messwerte (ohne Lot-Bezug)", "Proteinwerte-Verteilung", "Mykotoxin-Statistik"],
        rechtsgrundlage=["DSGVO Art. 11 (anonymisiert = kein PbD mehr)"],
        erlaubte_ki_modelle=["*"],
        anonymisierung_ausreichend=True,
        kommentar="Anonymisierte QS-Statistiken sind kein Personenbezug mehr und erlauben externes Modell.",
    ),
    DataCategoryRule(
        category_id="cat-cov-synth-001",
        name="Synthetische Testdaten (E2E / Staging)",
        data_class=DataClass.C4_ANONYMISIERT_OK,
        beispiele=["Fiktive Kunden (e2e-kunde-*)", "Testkontrakts", "Synthetische Buchungen"],
        rechtsgrundlage=[],
        erlaubte_ki_modelle=["*"],
        anonymisierung_ausreichend=True,
        kommentar="Synthetische Daten enthalten keine echten Personen oder Geschaeftsvorgaenge.",
    ),

    # ── C5 — Niemals Modellkontext ────────────────────────────────────────────
    DataCategoryRule(
        category_id="cat-tse-001",
        name="TSE-Signaturen und POS-Protokolldaten",
        data_class=DataClass.C5_NIE_MODELLKONTEXT,
        beispiele=["TSE-Signatur-Bytes", "DSFinV-K-Exportdaten", "Kassenprotokoll (unveraenderlich)"],
        rechtsgrundlage=["§ 146a AO KassenSichV", "GoBD"],
        erlaubte_ki_modelle=[],
        verbotene_aktionen=["Modellkontext", "Vektordatenbank", "Log-Forwarding", "KI-Analyse"],
        kommentar="Revisionssichere Kassendaten duerfen nicht durch KI interpretiert oder veraendert werden.",
    ),
    DataCategoryRule(
        category_id="cat-passwort-001",
        name="Passwoerter / API-Secrets / Tokens",
        data_class=DataClass.C5_NIE_MODELLKONTEXT,
        beispiele=["Datenbankpasswort", "API_DEV_TOKEN", "OIDC-Client-Secret", "AWS-Secret-Key"],
        rechtsgrundlage=["DSGVO Art. 32", "BSI IT-Grundschutz ORP.4"],
        erlaubte_ki_modelle=[],
        verbotene_aktionen=["Jede KI-Verarbeitung", "Logging", "Prompt-Einbettung"],
        kommentar="Niemals in Prompts, Kontext, Logs oder Vektordatenbanken.",
    ),
    DataCategoryRule(
        category_id="cat-elster-001",
        name="ELSTER-Steuerdaten",
        data_class=DataClass.C5_NIE_MODELLKONTEXT,
        beispiele=["USt-Voranmeldung", "Jahressteuererklaerung", "eBilanz-XML"],
        rechtsgrundlage=["§ 30 AO Steuergeheimnis", "DSGVO Art. 9"],
        erlaubte_ki_modelle=[],
        verbotene_aktionen=["Weitergabe an jedes KI-Modell", "Vektordatenbank", "Cloud-Logging"],
        kommentar="Steuergeheimnis absolut — kein KI-Zugriff, auch nicht lokal ohne explizite rechtliche Pruefung.",
    ),
    DataCategoryRule(
        category_id="cat-bankkonto-001",
        name="Bankkonten / IBAN / SWIFT / CAMT",
        data_class=DataClass.C5_NIE_MODELLKONTEXT,
        beispiele=["IBAN", "SWIFT-BIC", "Kontoauszug CAMT.053", "Zahlungsauftrag SEPA"],
        rechtsgrundlage=["Bankgeheimnis", "ZAG §67", "DSGVO Art. 32"],
        erlaubte_ki_modelle=[],
        verbotene_aktionen=["KI-Kontext", "Logging ohne Maskierung", "Cloud-Transfer"],
        kommentar="Bankgeheimnis — kein KI-Zugriff ohne ausgedrueckliche rechtliche Grundlage.",
    ),
]


class AiDataClassificationService:
    """Auskunft ueber KI-Datenzugriffsklassen und Verwendungsregeln."""

    def list_categories(self, data_class: DataClass | None = None) -> list[dict[str, Any]]:
        rules = _RULES
        if data_class:
            rules = [r for r in rules if r.data_class == data_class]
        return [r.to_dict() for r in rules]

    def get_category(self, category_id: str) -> dict[str, Any]:
        for r in _RULES:
            if r.category_id == category_id:
                return r.to_dict()
        raise KeyError(f"Kategorie '{category_id}' nicht gefunden")

    def check_model_allowed(self, category_id: str, model_pattern: str) -> dict[str, Any]:
        for r in _RULES:
            if r.category_id == category_id:
                if r.data_class == DataClass.C5_NIE_MODELLKONTEXT:
                    return {"allowed": False, "reason": "C5 — niemals in Modellkontext", "data_class": r.data_class.value}
                if r.data_class == DataClass.C3_NUR_LOKAL:
                    local = any("localhost" in m or "lokal" in m for m in r.erlaubte_ki_modelle)
                    is_local = "localhost" in model_pattern or "lokal" in model_pattern
                    return {"allowed": local and is_local, "reason": "C3 — nur lokales Modell", "data_class": r.data_class.value}
                if "*" in r.erlaubte_ki_modelle:
                    return {"allowed": True, "reason": "Keine Einschraenkung", "data_class": r.data_class.value}
                allowed = any(model_pattern.startswith(m.replace("*", "").rstrip("@eu")) for m in r.erlaubte_ki_modelle)
                return {"allowed": allowed, "reason": f"Erlaubte Modelle: {r.erlaubte_ki_modelle}", "data_class": r.data_class.value}
        raise KeyError(f"Kategorie '{category_id}' nicht gefunden")

    def summary(self) -> dict[str, Any]:
        by_class: dict[str, int] = {c.value: 0 for c in DataClass}
        for r in _RULES:
            by_class[r.data_class.value] += 1
        return {
            "total_categories": len(_RULES),
            "by_class": by_class,
            "nie_modellkontext": sum(1 for r in _RULES if r.data_class == DataClass.C5_NIE_MODELLKONTEXT),
            "nur_lokal": sum(1 for r in _RULES if r.data_class == DataClass.C3_NUR_LOKAL),
            "extern_erlaubt": sum(1 for r in _RULES if r.data_class in (DataClass.C0_OEFFENTLICH, DataClass.C1_EXTERN_KI_ERLAUBT)),
        }


ai_data_classification_service = AiDataClassificationService()
